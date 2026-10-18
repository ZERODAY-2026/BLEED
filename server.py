"""
DataMind Studio: Cinematic Web API Server
ZeroDay OSS Hacktoberfest 2026 - Problem Statement 1
Serves the Awwwards-tier Dark Mode Web UI & Grounded Query Engine
"""

import os
import sys
import json
import yaml
import time
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.snowflake_client import SnowflakeEngine
from src.gemma_agent import GemmaDataAgent
from src.sql_guard import validate_readonly_sql

# Global Singletons
sf_engine = SnowflakeEngine()
gemma_agent = GemmaDataAgent()

# Cumulative Session Telemetry
session_telemetry = {
    "queries_run": 0,
    "credits_consumed": 0.0,
    "est_usd_cost": 0.0,
    "start_time": time.time()
}

CONFIGS = {
    "climate_energy": "configs/climate_energy.yaml",
    "tpch_benchmark": "configs/tpch_benchmark.yaml"
}

def load_config(config_id="climate_energy"):
    path = CONFIGS.get(config_id, CONFIGS["climate_energy"])
    with open(path, "r") as f:
        return yaml.safe_load(f)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class DataMindAPIHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local testing if needed
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_file("web/index.html", "text/html")
        elif self.path.startswith("/api/config"):
            self.handle_get_config()
        elif self.path.startswith("/api/health"):
            self.handle_get_health()
        elif self.path.startswith("/api/telemetry"):
            self.handle_get_telemetry()
        elif self.path.startswith("/web/"):
            rel_path = self.path.lstrip("/")
            mime_type, _ = mimetypes.guess_type(rel_path)
            self.serve_file(rel_path, mime_type or "application/octet-stream")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/query":
            self.handle_post_query()
        elif self.path == "/api/mutate":
            self.handle_post_mutate()
        else:
            self.send_error(404, "Endpoint not found")

    def serve_file(self, filepath, content_type):
        if not os.path.exists(filepath):
            self.send_error(404, f"File not found: {filepath}")
            return
        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_get_config(self):
        cfg = load_config("climate_energy")
        schema_text = sf_engine.introspect_schema(cfg["database"], cfg["schema"], cfg["allowed_tables"])
        resp = {
            "dataset_id": cfg.get("dataset_id"),
            "dataset_name": cfg.get("dataset_name"),
            "database": cfg.get("database"),
            "schema": cfg.get("schema"),
            "allowed_tables": cfg.get("allowed_tables"),
            "sample_questions": cfg.get("sample_questions", []),
            "schema_introspection": schema_text,
            "engine_mode": "snowflake_live" if sf_engine.is_connected else "reproducible_mock",
            "ai_provider": gemma_agent.provider
        }
        self.send_json(resp)

    def handle_get_health(self):
        cfg = load_config("climate_energy")
        health_reports = {}
        for tbl in cfg.get("allowed_tables", []):
            health_reports[tbl] = sf_engine.profile_data_health(cfg["database"], cfg["schema"], tbl)
        self.send_json({"health": health_reports})

    def handle_get_telemetry(self):
        self.send_json(session_telemetry)

    def handle_post_query(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len)
        try:
            req = json.loads(post_body.decode("utf-8"))
        except Exception:
            self.send_json({"error": "Invalid JSON"}, 400)
            return

        question = req.get("question", "").strip()
        config_id = req.get("config_id", "climate_energy")

        if not question:
            self.send_json({"error": "Empty question"}, 400)
            return

        config = load_config(config_id)
        schema_text = sf_engine.introspect_schema(config["database"], config["schema"], config["allowed_tables"])

        # 1. Gemma Reasoning & SQL Planning
        plan = gemma_agent.plan_and_generate_sql(
            question=question,
            schema_context=schema_text,
            config=config,
            history=[]
        )

        if plan.get("status") == "UNSUPPORTED":
            self.send_json({
                "status": "UNSUPPORTED",
                "message": plan.get("refusal_or_clarification_message", "Request unsupported within read-only boundaries."),
                "assumptions": plan.get("assumptions_made", [])
            })
            return

        raw_sql = plan.get("sql_query", "")

        # 2. AST Read-Only Gate
        is_safe, validated_sql = validate_readonly_sql(raw_sql, config["allowed_tables"])
        if not is_safe:
            self.send_json({
                "status": "SECURITY_BLOCKED",
                "error": validated_sql,
                "raw_sql": raw_sql
            })
            return

        # 3. Snowflake Execution
        exec_res = sf_engine.execute_with_trace(
            sql=validated_sql,
            database=config["database"],
            schema=config["schema"]
        )

        # Agentic Self-Correction Loop
        if not exec_res["success"]:
            corrected_plan = gemma_agent.fix_sql_after_error(
                question=question,
                failed_sql=validated_sql,
                error_message=exec_res["error"],
                schema_context=schema_text,
                config=config
            )
            safe_retry, retry_sql = validate_readonly_sql(corrected_plan.get("sql_query", ""), config["allowed_tables"])
            if safe_retry:
                exec_res = sf_engine.execute_with_trace(
                    sql=retry_sql,
                    database=config["database"],
                    schema=config["schema"]
                )
                validated_sql = retry_sql

        if not exec_res["success"]:
            self.send_json({
                "status": "EXECUTION_ERROR",
                "error": exec_res["error"],
                "sql": validated_sql
            })
            return

        # 4. Grounded Synthesis
        df = exec_res["dataframe"]
        records = df.to_dict(orient="records")
        synthesis = gemma_agent.synthesize_grounded_answer(
            question=question,
            sql_query=validated_sql,
            query_id=exec_res["query_id"],
            df_records=records,
            assumptions=plan.get("assumptions_made", [])
        )

        # Telemetry updates
        credits = exec_res.get("credits_consumed", 0.0)
        cost = exec_res.get("est_usd_cost", 0.0)
        session_telemetry["queries_run"] += 1
        session_telemetry["credits_consumed"] += credits
        session_telemetry["est_usd_cost"] += cost

        resp = {
            "status": "SUCCESS",
            "question": question,
            "grounded_answer": synthesis.get("grounded_answer", ""),
            "methodology": synthesis.get("methodology_explanation", ""),
            "assumptions": plan.get("assumptions_made", []),
            "data_gaps": synthesis.get("data_gaps_or_warnings", "None detected"),
            "snowflake": {
                "query_id": exec_res["query_id"],
                "elapsed_ms": exec_res["elapsed_ms"],
                "credits_consumed": credits,
                "est_usd_cost": cost,
                "row_count": exec_res["row_count"],
                "mode": exec_res.get("mode", "reproducible_mock"),
                "sql": validated_sql
            },
            "data": {
                "columns": list(df.columns),
                "rows": records
            },
            "telemetry": session_telemetry
        }
        self.send_json(resp)

    def handle_post_mutate(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len)
        try:
            req = json.loads(post_body.decode("utf-8"))
            new_val = float(req.get("value", 24.8))
        except Exception:
            self.send_json({"error": "Invalid value"}, 400)
            return

        sf_engine.update_mock_value("ENERGY_METRICS", "RENEWABLE_SHARE_PCT", new_val, "COUNTRY_CODE", "IND")
        self.send_json({"success": True, "updated_to": new_val})

def run(port=8000):
    for candidate_port in (port, 8001, 8080, 8081):
        try:
            server_address = ('', candidate_port)
            httpd = ThreadedHTTPServer(server_address, DataMindAPIHandler)
            print(f"✨ DataMind Studio Web Server listening at http://localhost:{candidate_port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nStopping server...")
                httpd.server_close()
            return
        except OSError as e:
            if e.errno == 48:  # Address already in use
                continue
            raise e

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
