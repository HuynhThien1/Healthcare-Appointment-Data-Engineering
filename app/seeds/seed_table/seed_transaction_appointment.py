def seed_appointment_transaction():
    from pathlib import Path
    import pandas as pd
    from psycopg2.extras import execute_values
    from app.db import get_app_connection

    file_path = Path(__file__).resolve().parents[1] / "data" / "appointment_transaction.csv"

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    df["event_timestamp"] = pd.to_datetime(
        df["event_timestamp"],
        format="%Y-%m-%d %I:%M%p"
    )

    def clean(val):
        return None if pd.isna(val) else val

    rows = [
        (
            clean(row["slotid"]),
            clean(row["patientID"]),
            clean(row["status"]).upper(),
            clean(row["event_timestamp"])
        )
        for _, row in df.iterrows()
    ]

    conn = get_app_connection()
    try:
        with conn.cursor() as cur:

            # =========================
            # 1. INSERT TRANSACTION
            # =========================
            execute_values(
                cur,
                """
                INSERT INTO appointment_transaction (
                    slot_id,
                    patient_id,
                    action,
                    created_at
                )
                VALUES %s;
                """,
                rows,
                page_size=1000
            )

            # 🔥 log transaction rows
            transaction_count = len(rows)

            # =========================
            # 2. REBUILD APPOINTMENT
            # =========================
            cur.execute("DELETE FROM appointment;")

            cur.execute("""
                INSERT INTO appointment (
                    booking_ref,
                    slot_id,
                    patient_id,
                    booked_at
                )
                SELECT
                    t.transaction_id,
                    t.slot_id,
                    t.patient_id,
                    t.created_at
                FROM (
                    SELECT *,
                           ROW_NUMBER() OVER (
                               PARTITION BY slot_id
                               ORDER BY created_at DESC
                           ) as rn
                    FROM appointment_transaction
                ) t
                WHERE t.rn = 1
                AND t.action = 'BOOKED'
                RETURNING appointment_id;
            """)

            inserted = cur.fetchall()
            appointment_count = len(inserted)

        conn.commit()

        # =========================
        # 🔥 LOG RÕ RÀNG
        # =========================
        print(f"✅ Transaction rows inserted: {transaction_count}")
        print(f"✅ Appointment rows created: {appointment_count}")

    finally:
        conn.close()