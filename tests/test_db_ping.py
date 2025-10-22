# tests/test_db_ping.py
# Test to check if PostgreSQL database is reachable and can execute a simple query.
import os
import time
import psycopg

def test_db_select_one():
    dsn = os.environ["DATABASE_URL"]  # ej: postgresql://appuser:apppass@localhost:5432/appdb
    for _ in range(30):
        try:
            with psycopg.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    assert cur.fetchone()[0] == 1
                    return
        except Exception:
            time.sleep(1)
    raise AssertionError("PostgreSQL is not ready after retries")
