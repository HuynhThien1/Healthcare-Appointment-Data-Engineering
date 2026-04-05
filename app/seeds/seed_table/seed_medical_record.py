def seed_medical_record():
    from pathlib import Path
    import pandas as pd
    from psycopg2.extras import execute_values
    from app.db import get_app_connection

    file_path = Path(__file__).resolve().parents[1] / "data" / "medical_record.csv"

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    df["updated_at"] = pd.to_datetime(df["updated_at"])

    rows = [
        (
            row["slotID"],
            row["patientID"],
            row["version"],
            row["diagnosis"],
            row["treatment"],
            row["updated_at"],
            row["updated_at"]
        )
        for _, row in df.iterrows()
    ]

    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO medical_record (
                    slot_id,
                    patient_id,
                    version_number,
                    diagnosis_note,
                    prescription_note,
                    created_at,
                    updated_at
                )
                VALUES %s
                ON CONFLICT DO NOTHING;
                """,
                rows
            )
        conn.commit()
        print(f"Seeded medical_record: {len(rows)} rows")
    finally:
        conn.close()