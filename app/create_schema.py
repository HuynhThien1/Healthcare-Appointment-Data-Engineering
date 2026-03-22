from pathlib import Path
from app.db import get_admin_connection, get_app_connection
from app.config import PG_APP_DB


def create_database():
    # explanation: Tạo application database nếu chưa tồn tại.
    conn = get_admin_connection()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (PG_APP_DB,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(f'CREATE DATABASE "{PG_APP_DB}";')
                print(f"Created database: {PG_APP_DB}")
            else:
                print(f"Database already exists: {PG_APP_DB}")
    finally:
        conn.close()


def create_schema():
    # explanation: Đọc file SQL schema và execute để tạo enum + 7 bảng.
    schema_path = Path("sql/set_up_postgres_db.sql")
    ddl_sql = schema_path.read_text(encoding="utf-8")

    conn = get_app_connection()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(ddl_sql)
            print("Create schema successfully!")
    finally:
        conn.close()


if __name__ == "__main__":
    create_database()
    create_schema()