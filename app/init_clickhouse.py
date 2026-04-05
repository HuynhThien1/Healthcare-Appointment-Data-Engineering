from pathlib import Path
from typing import List

from clickhouse_driver import Client
from app.config import (
    CLICKHOUSE_DB,
    CLICKHOUSE_HOST,
    CLICKHOUSE_NATIVE_PORT,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
)

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "clickhouse" / "sql"


def get_client() -> Client:
    return Client(
        host=CLICKHOUSE_HOST,
        port=int(CLICKHOUSE_NATIVE_PORT),
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )


def split_sql_statements(sql: str) -> List[str]:
    """
    Split SQL script into statements by semicolon, ignoring semicolons inside strings.
    """
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    escape = False

    for ch in sql:
        current.append(ch)

        if escape:
            escape = False
            continue

        if ch == "\\":
            escape = True
            continue

        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            continue

        if ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            continue

        if ch == ";" and not in_single_quote and not in_double_quote:
            stmt = "".join(current).strip()
            if stmt:
                # bỏ dấu ; cuối câu
                stmt = stmt[:-1].strip() if stmt.endswith(";") else stmt
                if stmt:
                    statements.append(stmt)
            current = []

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)

    return statements


def read_sql_file(sql_file: Path) -> str:
    sql = sql_file.read_text(encoding="utf-8").strip()
    if not sql:
        return ""
    return sql.format(db=CLICKHOUSE_DB)


def run_sql_file(client: Client, sql_file: Path) -> None:
    sql = read_sql_file(sql_file)
    if not sql:
        print(f"Skipping empty file: {sql_file.name}")
        return

    statements = split_sql_statements(sql)
    print(f"\n=== Running {sql_file.name} ({len(statements)} statement(s)) ===")

    for idx, stmt in enumerate(statements, start=1):
        try:
            print(f"[{sql_file.name}] statement #{idx}")
            client.execute(stmt)
        except Exception as e:
            print("\n--- ERROR DETAILS ---")
            print(f"File      : {sql_file.name}")
            print(f"Statement : #{idx}")
            print("SQL:")
            print(stmt)
            print("---------------------\n")
            raise e


def get_sql_files() -> List[Path]:
    if not SQL_DIR.exists():
        raise FileNotFoundError(f"SQL directory not found: {SQL_DIR}")

    files = sorted(SQL_DIR.glob("*.sql"))
    if not files:
        raise FileNotFoundError(f"No .sql files found in: {SQL_DIR}")

    return files


def verify_core_objects(client: Client) -> None:
    """
    Verify that important objects exist after init.
    Adjust this list if your schema changes.
    """
    expected_objects = [
        f"{CLICKHOUSE_DB}.stg_doctor",
        f"{CLICKHOUSE_DB}.stg_patient",
        f"{CLICKHOUSE_DB}.stg_slot_code_template",
        f"{CLICKHOUSE_DB}.stg_doctor_slot",
        f"{CLICKHOUSE_DB}.stg_appointment",
        f"{CLICKHOUSE_DB}.stg_appointment_transaction",
        f"{CLICKHOUSE_DB}.stg_medical_record",
        f"{CLICKHOUSE_DB}.dim_doctor",
        f"{CLICKHOUSE_DB}.dim_patient",
        f"{CLICKHOUSE_DB}.dim_slot_code",
        f"{CLICKHOUSE_DB}.dim_doctor_slot",
        f"{CLICKHOUSE_DB}.fact_appointment",
        f"{CLICKHOUSE_DB}.fact_appointment_transaction",
        f"{CLICKHOUSE_DB}.fact_slot_daily",
        f"{CLICKHOUSE_DB}.fact_medical_record",
        f"{CLICKHOUSE_DB}.vw_dim_doctor_current",
        f"{CLICKHOUSE_DB}.vw_dim_patient_current",
        f"{CLICKHOUSE_DB}.vw_dim_slot_code_current",
        f"{CLICKHOUSE_DB}.vw_dim_doctor_slot_current",
    ]

    missing = []
    for obj in expected_objects:
        db_name, table_name = obj.split(".", 1)
        result = client.execute(
            f"EXISTS TABLE {db_name}.{table_name}"
        )
        exists_flag = result[0][0] if result else 0
        if exists_flag != 1:
            missing.append(obj)

    if missing:
        print("\nMissing objects after init:")
        for obj in missing:
            print(f" - {obj}")
        raise RuntimeError("ClickHouse init completed but some objects are missing.")

    print("\nAll core ClickHouse objects exist.")


def init_clickhouse() -> None:
    client = get_client()
    sql_files = get_sql_files()

    print(f"ClickHouse host     : {CLICKHOUSE_HOST}:{CLICKHOUSE_NATIVE_PORT}")
    print(f"ClickHouse database : {CLICKHOUSE_DB}")
    print(f"SQL directory       : {SQL_DIR}")
    print("Files to execute:")
    for f in sql_files:
        print(f" - {f.name}")

    for sql_file in sql_files:
        run_sql_file(client, sql_file)

    verify_core_objects(client)
    print(f"\nInitialized ClickHouse successfully in database: {CLICKHOUSE_DB}")


if __name__ == "__main__":
    init_clickhouse()