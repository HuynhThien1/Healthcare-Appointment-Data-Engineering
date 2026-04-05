from pathlib import Path
import pandas as pd
from psycopg2.extras import execute_values

from app.db import get_app_connection


def seed_patients():
    # Path tới CSV
    file_path = Path(__file__).resolve().parents[1] / "data" / "dim_patient.csv"

    # Đọc CSV (giữ encoding tiếng Việt)
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    rows = []

    for _, row in df.iterrows():
        rows.append((
            row["patientName"],
            row["address"],
            row["phoneNumber"],
            row["insuranceNumber"],
            row["dateOfBirth"],
            row["gender"],
            row["email"]
        ))

    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO patient (
                    patient_name,
                    address,
                    phone_number,
                    insurance_number,
                    date_of_birth,
                    gender,
                    email
                )
                VALUES %s;
                """,
                rows
            )
        conn.commit()
        print(f"Seeded patient: {len(rows)} rows")
    finally:
        conn.close()