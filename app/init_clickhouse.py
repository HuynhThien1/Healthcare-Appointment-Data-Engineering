from pathlib import Path
from clickhouse_driver import Client
from app.config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
)

SQL_DIR = Path("/app/clickhouse/sql")

def get_client():
    return Client(
        host=CLICKHOUSE_HOST,
        port=9000,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )

def run_sql_file(client, sql_file: Path):
    sql = sql_file.read_text(encoding="utf-8").strip()
    if not sql:
        return
    print(f"Running {sql_file.name} ...")
    client.execute(sql)

def init_clickhouse():
    client = get_client()

    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        run_sql_file(client, sql_file)

    print("ClickHouse initialized successfully.")

if __name__ == "__main__":
    init_clickhouse()