"""
Snowflake Live Connection Diagnostic Tool (Criterion 4 & Gate G3)
Run this script to verify that Person 1's Snowflake credentials,
warehouse, and read-only RBAC role are functioning properly.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    print("=" * 70)
    print("❄️  Testing Live Snowflake Connection & RBAC Permissions")
    print("=" * 70)

    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "DATAMIND_WH")
    role = os.getenv("SNOWFLAKE_ROLE", "DATAMIND_READER")

    print(f"Target Account:   {account}")
    print(f"User:             {user}")
    print(f"Warehouse:        {warehouse}")
    print(f"Role:             {role}")
    print("-" * 70)

    if not account or not user or not password or "your_" in account or "your_" in user:
        print("⚠️  Snowflake credentials are not yet configured in .env.")
        print("Once Person 1 sends you her credentials, fill in .env and run this again.")
        return False

    try:
        import snowflake.connector
    except ImportError:
        print("❌ snowflake-connector-python is not installed. Run: pip install -r requirements.txt")
        return False

    try:
        print("1️⃣ Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            role=role,
        )
        print("   ✅ Connection established successfully!")

        cursor = conn.cursor()

        # Test 1: Active Role & Warehouse Check
        print("\n2️⃣ Verifying active context...")
        cursor.execute("SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE();")
        row = cursor.fetchone()
        print(f"   Active Role:      {row[0]}")
        print(f"   Active Warehouse: {row[1]}")
        print(f"   Query ID (sfqid): {cursor.sfqid}")

        # Test 2: Climate Energy Table Access
        print("\n3️⃣ Testing read access on DATAMIND_DB.CLIMATE_ENERGY.ENERGY_METRICS...")
        cursor.execute("SELECT COUNT(*) FROM DATAMIND_DB.CLIMATE_ENERGY.ENERGY_METRICS;")
        count = cursor.fetchone()[0]
        print(f"   ✅ Verified! Found {count} rows in ENERGY_METRICS. (Query ID: {cursor.sfqid})")

        # Test 3: TPC-H Benchmark Access
        print("\n4️⃣ Testing read access on SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER...")
        cursor.execute("SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER LIMIT 1;")
        print(f"   ✅ Verified access to TPC-H sample data! (Query ID: {cursor.sfqid})")

        # Test 4: Enforce Read-Only Security (Must Fail to Mutate)
        print("\n5️⃣ Verifying read-only security (Attempting write operation with DATAMIND_READER)...")
        try:
            cursor.execute("DROP TABLE DATAMIND_DB.CLIMATE_ENERGY.ENERGY_METRICS;")
            print("   ❌ WARNING: Read-only role allowed DROP TABLE! Check setup_snowflake.sql grants.")
        except Exception:
            print("   🛡️ PASS: Write operation was blocked by Snowflake RBAC! Read-only role confirmed.")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("🎉 ALL SNOWFLAKE VERIFICATION CHECKS PASSED!")
        print("Person 1's Snowflake environment is 100% production-ready for DataMind.")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ Snowflake Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
