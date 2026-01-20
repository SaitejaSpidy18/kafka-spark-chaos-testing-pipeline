import psycopg2
import os
import sys

pg_host = os.getenv("PG_HOST", "localhost")
pg_port = int(os.getenv("PG_PORT", "5432"))
pg_db = os.getenv("PG_DB", "streamdb")
pg_user = os.getenv("PG_USER", "stream")
pg_pwd = os.getenv("PG_PASSWORD", "stream")

counter_file = "producer/../../producer-data/producer_count.txt"
# For local validation run, override via env or adjust path.

def read_produced_count():
    try:
        with open("producer-data/producer_count.txt", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        print("Producer count file not found.")
        return None

def main():
    produced = read_produced_count()
    if produced is None:
        sys.exit(1)

    conn = psycopg2.connect(
        host=pg_host, port=pg_port, dbname=pg_db, user=pg_user, password=pg_pwd
    )
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(count), 0) FROM event_aggregates;")
    aggregated = cur.fetchone()[0]
    conn.close()

    print(f"Produced events: {produced}")
    print(f"Aggregated events: {aggregated}")

    if aggregated == produced:
        print("Validation PASSED: zero data loss.")
        sys.exit(0)
    else:
        print("Validation FAILED: mismatch detected.")
        sys.exit(1)

if __name__ == "__main__":
    main()
