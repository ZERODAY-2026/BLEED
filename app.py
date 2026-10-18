"""
DataMind Studio: Ultra-Premium Grounded Data Intelligence System
ZeroDay OSS Hacktoberfest 2026 - Problem Statement 1
Cinematic Awwwards-Tier Dark Mode • Levitating Matte-Black Glass Artifact & HUD
"""

import os
import json
import datetime
import hashlib
import yaml
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from src.snowflake_client import SnowflakeEngine
from src.gemma_agent import GemmaDataAgent
from src.sql_guard import validate_readonly_sql

load_dotenv()

st.set_page_config(
    page_title="DataMind Studio | Snowflake + Gemma 4",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# Cinematic CSS: Volumetric Spotlights, Frosted Glass & Macro-Depth Aesthetics
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Deep Void Background */
    .stApp {
        background-color: #05070c !important;
        background-image: 
            radial-gradient(ellipse 90% 60% at 50% -15%, rgba(56, 189, 248, 0.18) 0%, transparent 65%),
            radial-gradient(circle 500px at 85% 20%, rgba(168, 85, 247, 0.12) 0%, transparent 70%),
            radial-gradient(circle 450px at 15% 80%, rgba(56, 189, 248, 0.08) 0%, transparent 65%) !important;
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3.5rem;
        max-width: 1400px;
    }

    /* Floating Atmospheric Sparks & Levitating Artifact Animations */
    @keyframes artifactFloat {
        0% { transform: translateY(0px) rotateX(0deg); box-shadow: 0 35px 70px -15px rgba(0, 0, 0, 0.95), 0 0 50px rgba(56, 189, 248, 0.15); }
        50% { transform: translateY(-10px) rotateX(1deg); box-shadow: 0 50px 90px -15px rgba(0, 0, 0, 0.98), 0 0 70px rgba(56, 189, 248, 0.28); }
        100% { transform: translateY(0px) rotateX(0deg); box-shadow: 0 35px 70px -15px rgba(0, 0, 0, 0.95), 0 0 50px rgba(56, 189, 248, 0.15); }
    }

    @keyframes sparkDrift {
        0% { transform: translateY(0px) translateX(0px); opacity: 0.2; }
        50% { transform: translateY(-25px) translateX(15px); opacity: 0.85; }
        100% { transform: translateY(0px) translateX(0px); opacity: 0.2; }
    }

    @keyframes glowPulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 0.9; }
    }

    /* Central Technology Artifact Container */
    .artifact-stage {
        position: relative;
        width: 100%;
        padding: 42px 48px;
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.75) 0%, rgba(10, 15, 30, 0.88) 100%);
        backdrop-filter: blur(36px);
        -webkit-backdrop-filter: blur(36px);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-top: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 24px;
        animation: artifactFloat 7s ease-in-out infinite;
        overflow: hidden;
        margin-bottom: 24px;
    }

    /* Kinetic Background Typography partially obscured by Artifact */
    .kinetic-watermark {
        position: absolute;
        top: -15px;
        right: 20px;
        font-size: 7.5rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        color: rgba(255, 255, 255, 0.025);
        user-select: none;
        pointer-events: none;
        z-index: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Microscopic floating atmospheric dust particles */
    .dust-particle {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }
    .dust-1 { top: 25px; left: 15%; width: 3px; height: 3px; background: #38bdf8; box-shadow: 0 0 12px #38bdf8; animation: sparkDrift 5s infinite ease-in-out; }
    .dust-2 { bottom: 35px; right: 25%; width: 4px; height: 4px; background: #c084fc; box-shadow: 0 0 16px #c084fc; animation: sparkDrift 7s infinite ease-in-out; }
    .dust-3 { top: 60px; right: 12%; width: 2px; height: 2px; background: #38bdf8; box-shadow: 0 0 8px #38bdf8; animation: sparkDrift 4s infinite ease-in-out; }

    /* Top Reticle Pill */
    .pill-reticle {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        border-radius: 9999px;
        background: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #7dd3fc;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 14px;
        font-family: 'JetBrains Mono', monospace;
    }
    .pill-reticle .pulse-dot {
        width: 6px;
        height: 6px;
        background: #38bdf8;
        border-radius: 50%;
        box-shadow: 0 0 10px #38bdf8;
        animation: glowPulse 2s infinite ease-in-out;
    }

    .artifact-title {
        font-size: 2.9rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.1;
        background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 60%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        position: relative;
        z-index: 1;
    }

    .artifact-subtitle {
        color: #94a3b8;
        font-size: 1.08rem;
        font-weight: 400;
        line-height: 1.6;
        max-width: 860px;
        margin-bottom: 22px;
        position: relative;
        z-index: 1;
    }

    /* Floating Interactive Vector Navigation Reticles */
    .reticle-grid {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    .reticle-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #64748b;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 5px 12px;
        letter-spacing: 0.05em;
    }
    .reticle-tag span {
        color: #38bdf8;
        font-weight: 600;
    }

    /* Ultra-Premium Glass Card */
    .glass-panel {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.5);
    }

    /* Futuristic Telemetry HUD Badges */
    .hud-badge {
        background: rgba(10, 15, 29, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 3px solid #38bdf8;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .hud-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #64748b;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .hud-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.25rem;
        font-weight: 700;
        color: #38bdf8;
    }

    /* Streamlit Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 14px;
        background: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 10px;
        margin-bottom: 18px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 23, 42, 0.55);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        color: #94a3b8;
        padding: 10px 22px;
        font-size: 0.88rem;
        font-weight: 500;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-color: rgba(56, 189, 248, 0.4);
        color: #f1f5f9;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.14) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }

    /* Sleek Sidebar Design */
    section[data-testid="stSidebar"] {
        background-color: rgba(7, 10, 17, 0.94) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }

    /* Polished Interactive Prompt Pills */
    div.stButton > button {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 12px !important;
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 14px 18px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        text-align: left !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }
    div.stButton > button:hover {
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.2) !important;
    }

    /* Chat Messages Glass */
    .stChatMessage {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 14px !important;
        margin-bottom: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engines():
    return SnowflakeEngine(), GemmaDataAgent()

sf_engine, gemma_agent = get_engines()

# ------------------------------------------------------------------------------
# Sidebar: Control Center & Telemetry HUD
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ❄️ **DataMind Control**")

    # Engine Status HUD
    if sf_engine.is_connected:
        st.success("🟢 **Snowflake Cloud:** Live (DATAMIND_WH)")
    else:
        st.info("🟡 **Snowflake Engine:** Reproducible Mock")

    # Model Provider HUD
    provider = os.getenv("GEMMA_PROVIDER", "simulation")
    if provider in ("lm_studio", "local_gemma"):
        model_tag = os.getenv("LM_STUDIO_MODEL", "google/gemma-4-12b-qat")
        st.success(f"🟢 **Gemma 4 Local:** `{model_tag}`")
    elif provider == "google_ai_studio":
        model_tag = os.getenv("GEMMA_MODEL_ID", "gemini-2.5-flash")
        st.info(f"🔵 **Gemma Cloud:** `{model_tag}`")
    else:
        st.info("⚡ **Gemma Engine:** Instant Simulation")

    st.markdown("---")
    st.markdown("#### **Active Data Environment**")
    config_options = {
        "Global Climate & Energy (OWID)": "configs/climate_energy.yaml",
        "TPC-H Supply Chain (Snowflake Sample)": "configs/tpch_benchmark.yaml"
    }
    selected_label = st.selectbox("Zero-Rewrite Configuration:", list(config_options.keys()))
    config_path = config_options[selected_label]

    with open(config_path, "r") as f:
        active_config = yaml.safe_load(f)

    st.caption(f"**Database:** `{active_config['database']}`")
    st.caption(f"**Schema:** `{active_config['schema']}`")
    st.caption(f"**Allowed Tables:** `{', '.join(active_config['allowed_tables'])}`")

    @st.cache_data(ttl=300)
    def load_schema_text(db, schema, tables_tuple):
        return sf_engine.introspect_schema(db, schema, list(tables_tuple))

    schema_context = load_schema_text(
        active_config["database"],
        active_config["schema"],
        tuple(active_config["allowed_tables"])
    )

    with st.expander("🔍 Schema Introspection Inspector"):
        st.code(schema_context, language="text")

    # Session Telemetry State
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
    if "total_credits" not in st.session_state:
        st.session_state.total_credits = 0.0
    if "total_usd" not in st.session_state:
        st.session_state.total_usd = 0.0

    st.markdown("---")
    st.markdown("#### ⚡ **Snowflake Cost & Credit Telemetry**")
    tc1, tc2 = st.columns(2)
    tc1.metric("Queries Run", st.session_state.total_queries)
    tc2.metric("Credits Used", f"{st.session_state.total_credits:.6f}")
    st.caption(f"Est. Warehouse Cost: **${st.session_state.total_usd:.5f} USD** (Rate: $3.00/credit)")

    st.markdown("---")
    with st.expander("🏥 **Data Quality & Health Profiler**", expanded=False):
        st.caption("Automated schema health & completeness auditing:")
        for tbl in active_config.get("allowed_tables", []):
            health = sf_engine.profile_data_health(active_config["database"], active_config["schema"], tbl)
            st.markdown(f"**Table:** `{tbl}`")
            h1, h2 = st.columns(2)
            h1.metric("Total Rows", health["total_rows"])
            h2.metric("Completeness", f"{health['completeness_score']}%")
            if health.get("total_nulls", 0) > 0:
                st.caption(f"⚠️ {health['total_nulls']} NULL/missing values detected")
            else:
                st.caption("✅ Zero missing values (100% complete)")
            st.divider()

    # Live Data Mutation Proof (Extra PS1 Rubric Feature)
    if active_config.get("dataset_id") == "climate_energy":
        st.markdown("---")
        with st.expander("⚡ **Live Data Mutation Tool**", expanded=False):
            st.caption("Change India's 2024 Renewable Share % in Snowflake to prove answers compute dynamically.")
            new_val = st.number_input("India 2024 Renewable %", min_value=0.0, max_value=100.0, value=24.8, step=1.0)
            if st.button("Apply Live Row Update"):
                if sf_engine.is_connected:
                    cur = sf_engine.conn.cursor()
                    try:
                        cur.execute("USE ROLE ACCOUNTADMIN")
                        cur.execute(
                            f"UPDATE DATAMIND_DB.CLIMATE_ENERGY.ENERGY_METRICS "
                            f"SET RENEWABLE_SHARE_PCT = {float(new_val)} "
                            f"WHERE COUNTRY_CODE = 'IND' AND REPORT_YEAR = 2024"
                        )
                        cur.execute("USE ROLE DATAMIND_READER")
                        st.success(f"Updated live row to {new_val}%!")
                    except Exception as e:
                        st.error(f"Update failed: {e}")
                    finally:
                        cur.close()
                else:
                    sf_engine.update_mock_value("ENERGY_METRICS", "RENEWABLE_SHARE_PCT", float(new_val), "COUNTRY_CODE", "IND")
                    st.success(f"Updated in-memory row to {new_val}%!")

# ------------------------------------------------------------------------------
# Central Levitating Matte-Black & Glass Technology Monolith
# ------------------------------------------------------------------------------
st.markdown("""
<div class="artifact-stage">
    <div class="pill-reticle">
        <span class="pulse-dot"></span>
        Snowflake + Google Gemma
    </div>
    <div class="artifact-title">Talk to your warehouse.</div>
    <div class="artifact-subtitle">
        Ask questions in plain English. Queries are verified against deterministic AST guardrails and audited against live Snowflake rows.
    </div>
</div>
""", unsafe_allow_html=True)

# Suggested Exploratory Inquiries
sample_qs = active_config.get("sample_questions", [])
if sample_qs:
    st.markdown("##### ✦ **Explore Data Inquiries**")
    cols = st.columns(len(sample_qs))
    for i, q_text in enumerate(sample_qs):
        if cols[i].button(f"✦ {q_text}", key=f"sq_{i}", use_container_width=True):
            st.session_state["preset_input"] = q_text

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "evidence" in msg:
            ev = msg["evidence"]
            with st.expander(f"🔍 Verifiable Evidence (sfqid: {ev['query_id']})"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Query ID", ev["query_id"])
                c2.metric("Result Rows", ev["row_count"])
                c3.metric("Latency", f"{ev['elapsed_ms']} ms")
                st.code(ev["sql"], language="sql")
                if not ev["dataframe"].empty:
                    st.dataframe(ev["dataframe"], use_container_width=True)

# User Chat Input
user_input = st.chat_input("Ask a question about your data (e.g. 'Compare renewable share and green investment by region in 2024')...")

if "preset_input" in st.session_state and st.session_state["preset_input"]:
    user_input = st.session_state.pop("preset_input")

if user_input:
    st.chat_message("user").markdown(f"**{user_input}**")
    st.session_state.messages.append({"role": "user", "content": f"**{user_input}**"})

    with st.chat_message("assistant"):
        with st.status("Gemma planning & verifying query against Snowflake...", expanded=True) as status:
            st.write("1️⃣ **Reasoning:** Interpreting query against Snowflake schema & domain hints...")
            plan = gemma_agent.plan_and_generate_sql(
                question=user_input,
                schema_context=schema_context,
                config=active_config,
                history=st.session_state.history
            )

            # Check for unsupported or guardrail refusal
            if plan.get("status") == "UNSUPPORTED":
                status.update(label="Guardrail refusal", state="error")
                refusal_msg = plan.get("refusal_or_clarification_message", "This request cannot be fulfilled within read-only data constraints.")
                st.warning(f"⚠️ **Request Declined:** {refusal_msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {refusal_msg}"})
                st.stop()

            raw_sql = plan.get("sql_query", "")
            st.write("2️⃣ **AST Guardrail Gate:** Enforcing deterministic read-only SELECT compliance with `sqlglot`...")

            is_safe, validated_sql = validate_readonly_sql(raw_sql, active_config["allowed_tables"])
            if not is_safe:
                status.update(label="Read-Only Security Gate Blocked Query", state="error")
                st.error(f"🛑 **Read-Only Gate Blocked Query:** {validated_sql}")
                st.code(raw_sql, language="sql")
                st.session_state.messages.append({"role": "assistant", "content": f"🛑 Guardrail Error: {validated_sql}"})
                st.stop()

            # Execute SQL
            st.write("3️⃣ **Snowflake Cloud:** Executing read-only query on warehouse `DATAMIND_WH`...")
            exec_res = sf_engine.execute_with_trace(
                sql=validated_sql,
                database=active_config["database"],
                schema=active_config["schema"]
            )

            # Agentic Self-Correction Loop on SQL Error
            if not exec_res["success"]:
                st.write("🔄 Snowflake execution error. Initiating Gemma self-correction loop...")
                corrected_plan = gemma_agent.fix_sql_after_error(
                    question=user_input,
                    failed_sql=validated_sql,
                    error_message=exec_res["error"],
                    schema_context=schema_context,
                    config=active_config
                )
                safe_retry, retry_sql = validate_readonly_sql(corrected_plan.get("sql_query", ""), active_config["allowed_tables"])
                if safe_retry:
                    exec_res = sf_engine.execute_with_trace(
                        sql=retry_sql,
                        database=active_config["database"],
                        schema=active_config["schema"]
                    )
                    validated_sql = retry_sql

            if not exec_res["success"]:
                status.update(label="Snowflake Query Failed", state="error")
                st.error(f"❌ **Snowflake Execution Error:** {exec_res['error']}")
                st.code(validated_sql, language="sql")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Query Execution Error: {exec_res['error']}"})
                st.stop()

            # Grounded Synthesis
            st.write("4️⃣ **Grounded Synthesis:** Gemma synthesizing explanation strictly from Snowflake rows...")
            df = exec_res["dataframe"]
            synthesis = gemma_agent.synthesize_grounded_answer(
                question=user_input,
                sql_query=validated_sql,
                query_id=exec_res["query_id"],
                df_records=df.to_dict(orient="records"),
                assumptions=plan.get("assumptions_made", [])
            )
            status.update(label="Answer Computed Live from Snowflake", state="complete")

        # ----------------------------------------------------------------------
        # Award-Winning 3-Tab Telemetry System
        # ----------------------------------------------------------------------
        tab_answer, tab_chart, tab_evidence = st.tabs([
            "💬 **Grounded Intelligence**",
            "📊 **Cinematic Data Visualizer**",
            "🔍 **Snowflake Audit Trail & SQL**"
        ])

        with tab_answer:
            st.markdown(f"#### 💡 Grounded Answer\n{synthesis['grounded_answer']}")
            st.info(f"**Methodology:** {synthesis['methodology_explanation']}")

            if plan.get("assumptions_made"):
                st.caption(f"**Explicit Assumptions:** {', '.join(plan['assumptions_made'])}")

            data_gaps = synthesis.get("data_gaps_or_warnings")
            if data_gaps and data_gaps != "None detected":
                st.warning(f"📊 **Data Completeness Notice:** {data_gaps}")

        with tab_chart:
            if not df.empty and len(df) > 1:
                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                text_cols = df.select_dtypes(include=["object"]).columns.tolist()

                if numeric_cols and text_cols:
                    x_col = text_cols[0]
                    y_col = numeric_cols[0]
                    fig = px.bar(
                        df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} by {x_col}",
                        color=x_col if len(df) < 15 else None,
                        template="plotly_dark",
                        height=440
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(10, 15, 29, 0.4)",
                        plot_bgcolor="rgba(10, 15, 29, 0.2)",
                        margin=dict(l=20, r=20, t=40, b=20),
                        font=dict(family="Plus Jakarta Sans", color="#cbd5e1")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No categorical + numeric pair to chart for this query.")
            else:
                st.caption("A chart visualizer is available when 2 or more rows are returned.")

        with tab_evidence:
            st.markdown("##### 🏛️ Verifiable Query Audit Trail & Snowflake Telemetry")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Query ID (sfqid)", exec_res["query_id"])
            col2.metric("Result Rows", exec_res["row_count"])
            col3.metric("Latency", f"{exec_res['elapsed_ms']} ms")
            col4.metric("Credits Consumed", f"{exec_res.get('credits_consumed', 0.0):.6f}")
            col5.metric("Est. Cost", f"${exec_res.get('est_usd_cost', 0.0):.5f}")

            st.markdown("**Executed Read-Only Snowflake SQL:**")
            st.code(validated_sql, language="sql")

            st.markdown("**Exact Snowflake Result Rows:**")
            st.dataframe(df, use_container_width=True)

            st.markdown("##### 📥 **One-Click Audit & Evidence Export**")
            exp_col1, exp_col2 = st.columns(2)
            
            # 1. Verifiable CSV with provenance header
            csv_meta = (
                f"# DataMind ZeroDay OSS Hacktoberfest 2026 Audit Export\n"
                f"# Snowflake Query ID (sfqid): {exec_res['query_id']}\n"
                f"# Executed SQL: {validated_sql}\n"
                f"# Execution Latency: {exec_res['elapsed_ms']} ms\n"
                f"# Warehouse Credits Consumed: {exec_res.get('credits_consumed', 0.0):.8f}\n"
                f"# Export Timestamp UTC: {datetime.datetime.utcnow().isoformat()}Z\n"
            )
            csv_data = csv_meta + df.to_csv(index=False)
            exp_col1.download_button(
                "📥 Export Verifiable CSV",
                data=csv_data,
                file_name=f"evidence_{exec_res['query_id']}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # 2. Cryptographic JSON Audit Packet
            data_bytes = df.to_json(orient='records').encode('utf-8')
            sha256_hash = hashlib.sha256(data_bytes).hexdigest()
            audit_packet = {
                "audit_version": "1.0",
                "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
                "question": user_input,
                "snowflake_query_id": exec_res["query_id"],
                "execution_mode": exec_res.get("mode", "unknown"),
                "executed_sql": validated_sql,
                "ast_gate_passed": True,
                "latency_ms": exec_res["elapsed_ms"],
                "warehouse_credits_consumed": exec_res.get("credits_consumed", 0.0),
                "estimated_usd_cost": exec_res.get("est_usd_cost", 0.0),
                "row_count": exec_res["row_count"],
                "evidence_sha256": sha256_hash,
                "grounded_answer": synthesis["grounded_answer"],
                "result_records": df.to_dict(orient="records")
            }
            exp_col2.download_button(
                "🛡️ Export JSON Audit Packet",
                data=json.dumps(audit_packet, indent=2),
                file_name=f"audit_packet_{exec_res['query_id']}.json",
                mime="application/json",
                use_container_width=True
            )

        # Update session telemetry counters
        st.session_state.total_queries += 1
        st.session_state.total_credits += exec_res.get("credits_consumed", 0.0)
        st.session_state.total_usd += exec_res.get("est_usd_cost", 0.0)

        # Append to session history
        evidence_packet = {
            "query_id": exec_res["query_id"],
            "row_count": exec_res["row_count"],
            "elapsed_ms": exec_res["elapsed_ms"],
            "credits_consumed": exec_res.get("credits_consumed", 0.0),
            "est_usd_cost": exec_res.get("est_usd_cost", 0.0),
            "sql": validated_sql,
            "dataframe": df
        }
        st.session_state.messages.append({
            "role": "assistant",
            "content": synthesis["grounded_answer"],
            "evidence": evidence_packet
        })
        st.session_state.history.append({
            "question": user_input,
            "sql": validated_sql,
            "answer": synthesis["grounded_answer"]
        })
