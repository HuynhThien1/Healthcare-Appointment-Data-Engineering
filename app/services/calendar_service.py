# app/services/calendar_service.py

from app.db import execute_query, fetch_all

def get_calendar_range(start_date, end_date):
    return fetch_all("""
        SELECT * FROM calendar_day
        WHERE date BETWEEN %s AND %s
        ORDER BY date
    """, (start_date, end_date))



from app.db import get_app_connection

def update_calendar_status(date, status):
    conn = get_app_connection()

    try:
        with conn.cursor() as cur:

            # =========================
            # 1. UPDATE CALENDAR DAY
            # =========================
            cur.execute("""
                UPDATE calendar_day
                SET status = %s
                WHERE date = %s
            """, (status, date))

            if status == "HOLIDAY":

                # =========================
                # 2. CANCEL TRANSACTIONS
                # =========================
                cur.execute("""
                    UPDATE appointment_transaction
                    SET action = 'CANCELLED'
                    WHERE slot_id IN (
                        SELECT slot_id
                        FROM doctor_slot
                        WHERE slot_date = %s
                    )
                """, (date,))

                # =========================
                # 3. DELETE APPOINTMENTS
                # =========================
                cur.execute("""
                    DELETE FROM appointment
                    WHERE slot_id IN (
                        SELECT slot_id
                        FROM doctor_slot
                        WHERE slot_date = %s
                    )
                """, (date,))

                # =========================
                # 4. BLOCK SLOT + RESET STATUS
                # =========================
                cur.execute("""
                    UPDATE doctor_slot
                    SET 
                        admin_status = 'BLOCKED',
                        slot_status = CASE 
                            WHEN slot_status = 'BOOKED' THEN 'AVAILABLE'::slot_status_enum
                            ELSE slot_status 
                        END
                    WHERE slot_date = %s
                """, (date,))

            else:
                # =========================
                # 5. UNBLOCK SLOT
                # =========================
                cur.execute("""
                    UPDATE doctor_slot
                    SET admin_status = 'AVAILABLE'
                    WHERE slot_date = %s
                """, (date,))

        # =========================
        # COMMIT
        # =========================
        conn.commit()

        return {
            "success": True,
            "message": f"Calendar updated to {status}"
        }

    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        conn.close()

        