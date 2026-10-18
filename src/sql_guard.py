"""
DataMind SQL Guardrails: Deterministic AST-level Read-Only Validator
Implements Criterion 6 & Gate G5: Blocks DDL/DML, statement chaining,
and restricts table access strictly to the dataset's allowed tables.
"""

import re
from typing import Tuple, List, Set

try:
    import sqlglot
    from sqlglot import exp
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False

FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "MERGE", "COPY", "PUT", "REMOVE",
    "EXECUTE", "CALL", "REPLACE"
}

def validate_readonly_sql(sql: str, allowed_tables: List[str]) -> Tuple[bool, str]:
    """
    Deterministically validates that generated SQL is strictly a read-only SELECT
    statement and queries only explicitly permitted tables.

    Returns:
        (is_valid: bool, cleaned_sql_or_error_message: str)
    """
    if not sql or not sql.strip():
        return False, "Query error: Received empty SQL query."

    cleaned_sql = sql.strip().rstrip(";")

    # 1. Reject statement chaining (SQL injection protection)
    if ";" in cleaned_sql:
        return False, "Security violation: Multiple SQL statements (; chaining) are strictly prohibited."

    # 2. Fast regex keyword filter for DDL / DML operations
    tokens = set(re.findall(r"\b[A-Za-z_]+\b", cleaned_sql.upper()))
    illegal_found = tokens.intersection(FORBIDDEN_KEYWORDS)
    if illegal_found:
        return False, f"Security violation: Blocked unsafe non-read-only SQL keywords: {', '.join(sorted(illegal_found))}"

    # 3. Check for SELECT or WITH at the start
    first_keyword_match = re.search(r"^\s*(\w+)", cleaned_sql, re.IGNORECASE)
    if not first_keyword_match or first_keyword_match.group(1).upper() not in ("SELECT", "WITH"):
        return False, f"Security violation: Only SELECT queries are permitted. Found starting keyword: {first_keyword_match.group(1) if first_keyword_match else 'None'}"

    # 4. AST parse with sqlglot if installed
    allowed_upper = {t.upper() for t in allowed_tables}

    if HAS_SQLGLOT:
        try:
            parsed = sqlglot.parse_one(cleaned_sql, read="snowflake")
        except Exception as e:
            return False, f"SQL syntax parsing failed: {str(e)}"

        if not isinstance(parsed, exp.Select):
            return False, f"Security violation: Only SELECT queries are permitted. Found root AST node: {type(parsed).__name__}"

        cte_names: Set[str] = {cte.alias_or_name.upper() for cte in parsed.find_all(exp.CTE)}
        queried_tables: Set[str] = set()
        for tbl in parsed.find_all(exp.Table):
            tbl_name = tbl.name.upper()
            if tbl_name not in cte_names:
                queried_tables.add(tbl_name)

        unauthorized = queried_tables - allowed_upper
        if unauthorized:
            return False, f"Authorization error: Query references unauthorized table(s): {', '.join(sorted(unauthorized))}. Allowed tables: {', '.join(sorted(allowed_upper))}"

        if not parsed.args.get("limit") and not any(isinstance(node, exp.AggFunc) for node in parsed.find_all(exp.AggFunc)):
            cleaned_sql += " LIMIT 50"
    else:
        # Fallback table check using regex pattern when sqlglot is not installed
        cte_matches = set(re.findall(r"\b(?:WITH|,)\s+([A-Za-z0-9_]+)\s+AS", cleaned_sql, re.IGNORECASE))
        cte_upper = {c.upper() for c in cte_matches}

        from_join_matches = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z0-9_\.]+)", cleaned_sql, re.IGNORECASE)
        for tbl in from_join_matches:
            simple_tbl = tbl.split(".")[-1].upper()
            if simple_tbl not in allowed_upper and simple_tbl not in cte_upper:
                return False, f"Authorization error: Query references unauthorized table(s): {simple_tbl}. Allowed tables: {', '.join(sorted(allowed_upper))}"

        if "LIMIT" not in cleaned_sql.upper():
            cleaned_sql += " LIMIT 50"

    return True, cleaned_sql
