"""
Unit tests for DataMind SQL Guardrails (Criterion 6 & Gate G5)
Verifies AST validation, keyword blocking, statement chaining defense, and table authorization.
Compatible with both pytest and python -m unittest.
"""

import unittest
from src.sql_guard import validate_readonly_sql

ALLOWED_TABLES = ["ENERGY_METRICS", "POLICY_TARGETS"]

class TestSQLGuardrails(unittest.TestCase):
    def test_valid_select_passes(self):
        sql = "SELECT COUNTRY_NAME, RENEWABLE_SHARE_PCT FROM ENERGY_METRICS WHERE REPORT_YEAR = 2024"
        ok, cleaned = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertTrue(ok)
        self.assertIn("SELECT", cleaned)

    def test_valid_join_passes(self):
        sql = """
        SELECT e.COUNTRY_NAME, e.RENEWABLE_SHARE_PCT, p.ANNUAL_GREEN_INVESTMENT_USD_B
        FROM ENERGY_METRICS e
        JOIN POLICY_TARGETS p ON e.COUNTRY_CODE = p.COUNTRY_CODE
        WHERE e.REPORT_YEAR = 2024
        """
        ok, cleaned = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertTrue(ok)

    def test_cte_query_passes(self):
        sql = """
        WITH TopCountries AS (
            SELECT COUNTRY_CODE, RENEWABLE_SHARE_PCT
            FROM ENERGY_METRICS
            WHERE REPORT_YEAR = 2024
        )
        SELECT * FROM TopCountries WHERE RENEWABLE_SHARE_PCT > 50
        """
        ok, cleaned = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertTrue(ok)

    def test_drop_table_blocked(self):
        sql = "DROP TABLE ENERGY_METRICS;"
        ok, err = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertFalse(ok)
        self.assertIn("DROP", err.upper())

    def test_delete_statement_blocked(self):
        sql = "DELETE FROM POLICY_TARGETS WHERE COUNTRY_CODE = 'IND'"
        ok, err = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertFalse(ok)
        self.assertIn("DELETE", err.upper())

    def test_stacked_injection_blocked(self):
        sql = "SELECT * FROM ENERGY_METRICS; DROP TABLE POLICY_TARGETS;"
        ok, err = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertFalse(ok)
        self.assertIn("MULTIPLE SQL STATEMENTS", err.upper())

    def test_unauthorized_table_blocked(self):
        sql = "SELECT * FROM SECRET_PAYROLL_TABLE WHERE SALARY > 100000"
        ok, err = validate_readonly_sql(sql, ALLOWED_TABLES)
        self.assertFalse(ok)
        self.assertIn("UNAUTHORIZED", err.upper())
        self.assertIn("SECRET_PAYROLL_TABLE", err)

    def test_empty_sql_blocked(self):
        ok, err = validate_readonly_sql("", ALLOWED_TABLES)
        self.assertFalse(ok)
        self.assertIn("EMPTY", err.upper())

if __name__ == "__main__":
    unittest.main()
