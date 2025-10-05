#!/usr/bin/env python3
import psycopg2
import sys

# ---- Database connection configuration ----
DB_NAME = "housing"
DB_USER = "gpadmin"
DB_HOST = "localhost"
DB_PORT = "5432"

# ---- Connect to Greenplum ----
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
except Exception as e:
    print("❌ Connection failed:", e)
    sys.exit(1)

# ---- Step 1: Create schema ----
print("Creating schema training_silver_hoods ...")
cur.execute("DROP SCHEMA IF EXISTS training_silver_hoods CASCADE;")
cur.execute("CREATE SCHEMA training_silver_hoods;")

# ---- Step 2: Get distinct neighborhoods ----
cur.execute("SELECT DISTINCT neighborhood FROM public.training_bronze ORDER BY neighborhood;")
hoods = [row[0] for row in cur.fetchall()]

print(f"Found {len(hoods)} neighborhoods.")

# ---- Step 3: Loop through each neighborhood ----
for hood in hoods:
    if hood is None:
        continue

    # sanitize name: lowercase, no spaces
    tbl_name = hood.lower().replace(" ", "_")
    full_table = f"training_silver_hoods.{tbl_name}"

    print(f"Creating table for neighborhood: {hood} -> {full_table}")

    create_sql = f"""
        CREATE TABLE {full_table} AS
        SELECT *
        FROM public.training_bronze
        WHERE neighborhood = %s
        DISTRIBUTED RANDOMLY;
    """
    cur.execute(create_sql, (hood,))

print("✅ All neighborhood tables created successfully.")

# ---- Cleanup ----
cur.close()
conn.close()

