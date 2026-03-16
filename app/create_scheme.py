from pathlib import Path
from db import get_admin_connection, get_app_connection

def create_database():
    conn = get_admin_connection()
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'healthcare_booking_realtime';")
    exists = cur.fetchone()

    if not exists: 
        cur.execute("CREATE DATABASE healthcare_booking_realtime;")
        print('Created database: healthcare_booking_realtime')
    else:
        print("Database already exists.")
    
    cur.close()
    conn.close()

def create_schema():
    schema_path = Path("../sql/set_up_postgres_db.sql")
    ddl_sql = schema_path.read_text(encoding="utf-8")

    conn = get_app_connection()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(ddl_sql)

    print("Create schema successfully!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    create_database()
    create_schema()

