
from pathlib import Path
import pandas as pd
from psycopg2.extras import execute_values

from app.db import get_app_connection


def seed_doctors():
    # Path tới CSV
    file_path = Path(__file__).resolve().parents[1] / "data" / "dim_doctor.csv"

    # Đọc CSV (giữ encoding cho tiếng Việt)
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    rows = []

    for _, row in df.iterrows():
        rows.append((
            row["doctorName"],
            row["specialty"],
            row["StartWorkingDate"]
        ))

    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO doctor (
                    doctor_name,
                    specialty,
                    start_working_date
                )
                VALUES %s;
                """,
                rows
            )
        conn.commit()
        print(f"Seeded doctor: {len(rows)} rows")
    finally:
        conn.close()