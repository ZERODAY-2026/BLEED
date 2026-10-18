# 🎥 5-Minute Video Demonstration & Pitch Script (Deliverable S7)

**Project:** DataMind (Problem Statement 1 — ZeroDay OSS Hacktoberfest 2026)  
**Target Duration:** 4:30 – 5:00 Minutes  
**Presenters:** Person 1, Person 2, Person 3 (or Solo Team Lead)

---

## Act 1: Introduction & Architectural Separation (0:00 – 0:50)

- **Visual:** Show GitHub repository (`ZERODAY-2026/BLEED`) with Apache-2.0 license, clean README, and architecture diagram.
- **Voiceover / Talking Points:**
  > "Hello judges! We are Team BLEED, presenting **DataMind**, our solution for Problem Statement 1: Talk to Your Data.
  > Organizations have massive databases, but non-technical decision-makers cannot query them without SQL expertise. Generic chatbots hallucinate plausible-sounding numbers. 
  > DataMind solves this by enforcing a strict **architectural separation of concerns**: Google Gemma handles stochastic natural language reasoning, while Snowflake AI Data Cloud handles deterministic data storage and query execution. Every single answer is 100% computed from real data at question-time with complete claim-to-query-to-row evidence."

---

## Act 2: Natural Language Querying & Live Evidence (0:50 – 2:00)

- **Visual:** Switch to the Streamlit UI (`http://localhost:8501`).
- **Action:** Click the sample query: *"Compare average CO2 emissions and total annual green investment by region for 2024"*.
- **Voiceover / Talking Points:**
  > "Let's ask a complex multi-table question: 'Compare average CO2 emissions and total annual green investment by region in 2024'.
  > Notice what happens:
  > 1. Gemma consults the discovered Snowflake schema and writes a multi-table JOIN query combining `ENERGY_METRICS` and `POLICY_TARGETS`.
  > 2. The query is intercepted and validated by our AST security guardrail.
  > 3. It executes live in Snowflake on warehouse `DATAMIND_WH`.
  > Look at the Evidence Drawer: Here is the unique Snowflake Query ID (`sfqid`), the execution latency in milliseconds, and the exact rows returned.
  > Gemma then synthesizes the grounded answer citing exact numbers without hallucinating, and automatically generates an interactive Plotly visualization."

---

## Act 3: Live Data Mutation Proof (2:00 – 2:50)

- **Visual:** Expand the sidebar tool: **"⚡ Live Data Mutation Tool"**.
- **Action:**
  1. Ask: *"What is India's renewable share in 2024?"* (Result shows 24.8%).
  2. In sidebar, change India's renewable share to **`45.0%`** and click **Apply Live Row Update**.
  3. Re-ask the exact same question.
  4. The answer dynamically updates to **45.0%**!
- **Voiceover / Talking Points:**
  > "The hackathon guidelines explicitly reward demonstrating that answers change dynamically when the underlying data changes, proving the system is not relying on cached or memorized answers.
  > In our sidebar, we'll mutate India's 2024 renewable share live from 24.8% to 45.0%. When we re-ask the exact same question, Gemma and Snowflake immediately compute the new value live. Zero hardcoded data."

---

## Act 4: AST Guardrails & Adversarial Defense (2:50 – 3:35)

- **Visual:** In the chat input, type: `"DROP TABLE ENERGY_METRICS"` or `"Delete all rows where country is USA"`.
- **Action:** Hit Enter. Watch the system block the request.
- **Voiceover / Talking Points:**
  > "Security is a core scoring criterion. What if a user attempts a prompt injection or SQL injection?
  > If someone asks to 'Drop table ENERGY_METRICS' or 'Delete all rows', our AST-level guardrail built on `sqlglot` deterministically intercepts the query before it ever reaches Snowflake. Furthermore, our Snowflake connection operates strictly under the `DATAMIND_READER` role, ensuring defense-in-depth even at the database level."

---

## Act 5: Zero-Rewrite Dataset Switcher & Benchmark (3:35 – 4:30)

- **Visual:** In the sidebar, change the dataset dropdown from **Global Climate & Energy** to **TPC-H Supply Chain (Snowflake Sample)**.
- **Action:** Ask: *"Who are the top 5 customers by total order spend?"*.
- **Voiceover / Talking Points:**
  > "Criterion 7 requires zero-code adaptability across datasets. By simply changing this YAML config dropdown to TPC-H SF1, DataMind instantly introspects the new schema (`CUSTOMER`, `ORDERS`, `LINEITEM`) and generates complex supply-chain queries with zero code changes."
- **Visual:** Show the terminal running `python3 eval/run_benchmark.py` and display the generated report at `eval/benchmark_report.md`.
  > "Finally, we built an automated ground-truth evaluation benchmark testing 10 diverse queries across joins, aggregations, NULL projections, and injections—scoring a verified 10 out of 10 (100% pass rate)."

---

## Conclusion & Outro (4:30 – 5:00)

- **Voiceover / Talking Points:**
  > "DataMind delivers trustworthy, grounded, and secure data intelligence with Snowflake and Google Gemma. All code, setup scripts, benchmark datasets, and documentation are publicly available on GitHub under the Apache-2.0 license. Thank you!"
