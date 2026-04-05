def seed_doctor_slots():
    from pathlib import Path
    import pandas as pd
    from psycopg2.extras import execute_values
    from app.db import get_app_connection

    file_path = Path(__file__).resolve().parents[1] / "data" / "dim_doctor_slot.csv"

    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"]).dt.date

    rows = [
    (
        row["slotID"],        # 🔥 dùng string ID
        row["doctorID"],
        row["date"],
        row["slotCode"],
        "AVAILABLE"
    )
    for _, row in df.iterrows()
    ]

    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO doctor_slot (
                    slot_id,
                    doctor_id,
                    slot_date,
                    slot_code,
                    slot_status
                )
                VALUES %s
                ON CONFLICT DO NOTHING;
                """,
                rows
            )
        conn.commit()
        print(f"Seeded doctor_slot: {len(rows)} rows")
    finally:
        conn.close()