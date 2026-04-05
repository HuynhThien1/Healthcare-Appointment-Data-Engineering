def seed_appointment_actual_from_csv():
    from pathlib import Path
    import pandas as pd
    from psycopg2.extras import execute_values
    from app.db import get_app_connection

    file_path = Path(__file__).resolve().parents[1] / "data" / "actual_appointment.csv"

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # ✅ parse datetime đúng format
    df["booked_at"] = pd.to_datetime(
        df["booked_at"],
        format="%Y-%m-%d %I:%M%p"
    )

    def clean(val):
        return None if pd.isna(val) else val

    rows = [
        (
            clean(row["booking_ref"]),
            clean(row["slotID"]),       # ✅ fix
            clean(row["patientID"]),
            clean(row["booked_at"])
        )
        for _, row in df.iterrows()
    ]

    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO appointment (
                    booking_ref,
                    slot_id,
                    patient_id,
                    booked_at
                )
                VALUES %s
                ON CONFLICT (slot_id) DO NOTHING;
                """,
                rows,
                page_size=1000
            )
        conn.commit()
        print(f"Seeded appointment: {len(rows)} rows")
    finally:
        conn.close()