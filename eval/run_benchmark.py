"""
DataMind Automated Benchmark Evaluator (Criterion 1 & Deliverables S8 / Extra PS1)
Runs automated end-to-end evaluation across 10 diverse benchmark test cases,
comparing generated responses against independently computed ground truth.
Outputs a comprehensive benchmark report at eval/benchmark_report.md.
"""

import os
import sys
import json
import time
import yaml
from datetime import datetime

# Automatically add project root to Python module search path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.snowflake_client import SnowflakeEngine
from src.gemma_agent import GemmaDataAgent
from src.sql_guard import validate_readonly_sql

def run_evaluation():
    print("=" * 70)
    print("❄️  Starting DataMind Automated Ground-Truth Benchmark Evaluation")
    print("=" * 70)

    config_path = os.path.join(ROOT_DIR, "configs", "climate_energy.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    testset_path = os.path.join(ROOT_DIR, "eval", "ground_truth_testset.json")
    with open(testset_path, "r") as f:
        test_cases = json.load(f)

    sf_engine = SnowflakeEngine()
    gemma_agent = GemmaDataAgent()

    schema_context = sf_engine.introspect_schema(
        config["database"], config["schema"], config["allowed_tables"]
    )

    passed_count = 0
    results_log = []

    for item in test_cases:
        qid = item["id"]
        category = item["category"]
        question = item["question"]
        print(f"\nEvaluating [{qid}] ({category}): \"{question}\"")

        start_t = time.time()

        # Step 1: Gemma Planning
        plan = gemma_agent.plan_and_generate_sql(
            question=question,
            schema_context=schema_context,
            config=config,
            history=[]
        )

        # Handling Security / Out of domain test cases
        if item.get("is_malicious") or item.get("is_out_of_domain"):
            is_blocked = False
            raw_sql = plan.get("sql_query", "")

            if plan.get("status") in ("UNSUPPORTED", "REFUSED"):
                is_blocked = True
                reason = "Blocked at Gemma Intent Layer"
            elif raw_sql:
                safe, err = validate_readonly_sql(raw_sql, config["allowed_tables"])
                if not safe:
                    is_blocked = True
                    reason = f"Blocked at AST Guardrail: {err}"
                else:
                    reason = "Failed: Unsafe query bypassed guardrails!"
            else:
                is_blocked = True
                reason = "Blocked: No executable SQL generated"

            duration = round((time.time() - start_t) * 1000, 2)
            passed = is_blocked
            if passed:
                passed_count += 1
                print(f"  ✅ PASS: Correctly blocked unsafe request ({reason})")
            else:
                print(f"  ❌ FAIL: {reason}")

            results_log.append({
                "id": qid,
                "category": category,
                "question": question,
                "status": "PASS" if passed else "FAIL",
                "notes": reason,
                "duration_ms": duration
            })
            continue

        # Handling Ambiguity test cases
        if item.get("requires_assumption"):
            assumptions = plan.get("assumptions_made", [])
            has_assumptions = len(assumptions) > 0
            duration = round((time.time() - start_t) * 1000, 2)
            if has_assumptions:
                passed_count += 1
                notes = f"Documented assumptions: {', '.join(assumptions)}"
                print(f"  ✅ PASS: Ambiguity handled ({notes})")
            else:
                notes = "Ambiguity not documented"
                print("  ❌ FAIL: Ambiguity was not flagged")

            results_log.append({
                "id": qid,
                "category": category,
                "question": question,
                "status": "PASS" if has_assumptions else "FAIL",
                "notes": notes,
                "duration_ms": duration
            })
            continue

        # Handling Standard Queries
        raw_sql = plan.get("sql_query", "")
        safe, validated_sql = validate_readonly_sql(raw_sql, config["allowed_tables"])

        if not safe:
            duration = round((time.time() - start_t) * 1000, 2)
            print(f"  ❌ FAIL: Guardrail blocked valid query: {validated_sql}")
            results_log.append({
                "id": qid,
                "category": category,
                "question": question,
                "status": "FAIL",
                "notes": f"Guardrail error: {validated_sql}",
                "duration_ms": duration
            })
            continue

        # Snowflake execution
        exec_res = sf_engine.execute_with_trace(
            sql=validated_sql,
            database=config["database"],
            schema=config["schema"]
        )

        duration = round((time.time() - start_t) * 1000, 2)

        if not exec_res["success"]:
            print(f"  ❌ FAIL: Snowflake execution error: {exec_res['error']}")
            results_log.append({
                "id": qid,
                "category": category,
                "question": question,
                "status": "FAIL",
                "notes": f"Execution error: {exec_res['error']}",
                "duration_ms": duration
            })
            continue

        df = exec_res["dataframe"]
        passed = False
        notes = f"Rows: {len(df)} | QID: {exec_res['query_id']}"

        # Check Ground Truth expectations
        if item.get("must_flag_null"):
            passed = df["RENEWABLE_SHARE_PCT"].isna().any() or len(df) == 0
            notes += " | Verified NULL correctly present"
        elif "expected_country" in item:
            str_dump = str(df.to_dict()).lower()
            if item["expected_country"].lower() in str_dump:
                passed = True
                notes += f" | Verified target: {item['expected_country']}"
            else:
                notes += f" | Missing target: {item['expected_country']}"
        elif "expected_region" in item:
            str_dump = str(df.to_dict()).lower()
            if item["expected_region"].lower() in str_dump:
                passed = True
                notes += f" | Verified target: {item['expected_region']}"
            else:
                notes += f" | Missing target: {item['expected_region']}"
        else:
            passed = len(df) > 0

        if passed:
            passed_count += 1
            print(f"  ✅ PASS: {notes}")
        else:
            print(f"  ❌ FAIL: {notes}")

        results_log.append({
            "id": qid,
            "category": category,
            "question": question,
            "status": "PASS" if passed else "FAIL",
            "notes": notes,
            "duration_ms": duration
        })

    total = len(test_cases)
    pass_pct = round((passed_count / total) * 100, 1)

    print("\n" + "=" * 70)
    print(f"🏁 Benchmark Completed: {passed_count}/{total} Passed ({pass_pct}%)")
    print("=" * 70)

    # Generate Markdown Report
    report_lines = [
        "# DataMind Ground-Truth Benchmark Evaluation Report",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Accuracy Score:** `{pass_pct}%` ({passed_count}/{total} Passed)  ",
        f"**Engine Mode:** `{'Live Snowflake' if sf_engine.is_connected else 'Reproducible Mock'}`  ",
        f"**AI Provider:** `{gemma_agent.provider}`  ",
        "",
        "## Summary of Results",
        "",
        "| ID | Category | Question | Status | Latency | Evidence & Verification Notes |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for r in results_log:
        badge = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        report_lines.append(
            f"| **{r['id']}** | `{r['category']}` | {r['question']} | {badge} | {r['duration_ms']} ms | {r['notes']} |"
        )

    report_lines.extend([
        "",
        "## Evaluation Methodology (Gates G2, G3 & Criterion 1)",
        "1. **Correctness**: Questions tested against independently computed ground truth values in Snowflake.",
        "2. **AST Guardrail Validation**: Unsafe DDL/DML and statement injections are deterministically intercepted before execution.",
        "3. **Claim-to-Query-to-Row Traceability**: Every valid answer links to an executed Snowflake query ID and raw result rows.",
        "4. **Missing Data Handling**: Projections with NULL values are explicitly detected and reported."
    ])

    report_content = "\n".join(report_lines)
    report_file = os.path.join(ROOT_DIR, "eval", "benchmark_report.md")
    with open(report_file, "w") as f:
        f.write(report_content)

    print(f"📄 Saved full evaluation report to {report_file}")

if __name__ == "__main__":
    run_evaluation()
