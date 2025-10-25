# tests/test_db_ping.py
# Test to check if PostgreSQL database is reachable and can execute a simple query.
import os
import time
import psycopg2


def test_db_select_one():
    dsn = os.environ["DATABASE_URL"]
    last_error = None
    
    for attempt in range(30):
        try:
            with psycopg2.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    assert cur.fetchone()[0] == 1
                    return
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1}/30 failed: {e}")
            time.sleep(1)
    
    raise AssertionError(f"PostgreSQL is not ready after 30 retries. Last error: {last_error}")