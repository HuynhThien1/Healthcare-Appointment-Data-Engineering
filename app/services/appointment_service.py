from app.db import fetch_all, fetch_one, execute_query, get_app_connection


# ==============================
# GET ALL
# ==============================
def get_all_appointments():
    return fetch_all("""
        SELECT *
        FROM appointment
        ORDER BY appointment_id;
    """)


# ==============================
# GET BY ID
# ==============================
def get_appointment_by_id(appointment_id: int):
    return fetch_one("""
        SELECT *
        FROM appointment
        WHERE appointment_id = %s;
    """, (appointment_id,))

def get_patient_appointments(patient_id: int):
    query = """
        SELECT 
            ds.doctor_id,
            ds.slot_date,
            ds.slot_code,
            a.booking_ref,
            a.booked_at
        FROM appointment a
        JOIN doctor_slot ds 
            ON a.slot_id = ds.slot_id
        WHERE a.patient_id = %s
        ORDER BY ds.slot_date, ds.slot_code;
    """

    return fetch_all(query, (patient_id,))

# ==============================
# CREATE (BOOK SLOT)
# ==============================
def create_appointment(data: dict):
    conn = get_app_connection()

    try:
        with conn.cursor() as cur:

            # 🔒 lock slot
            cur.execute("""
                SELECT slot_id
                FROM doctor_slot
                WHERE slot_id = %s
AND NOT EXISTS (
    SELECT 1 FROM appointment a
    WHERE a.slot_id = doctor_slot.slot_id
)
FOR UPDATE;
            """, (data["slot_id"],))

            if not cur.fetchone():
                raise Exception("Slot already booked")

            # 🔥 insert transaction trước
            cur.execute("""
                INSERT INTO appointment_transaction (
                    slot_id,
                    patient_id,
                    action,
                    created_at
                )
                VALUES (%s, %s, 'BOOKED', NOW())
                RETURNING transaction_id;
            """, (
                data["slot_id"],
                data["patient_id"]
            ))

            txn_id = cur.fetchone()[0]

            # 🔥 insert appointment (booking_ref = txn_id)
            cur.execute("""
                INSERT INTO appointment (
                    booking_ref,
                    slot_id,
                    patient_id,
                    booked_at
                )
                VALUES (%s, %s, %s, NOW())
                RETURNING appointment_id;
            """, (
                txn_id,
                data["slot_id"],
                data["patient_id"]
            ))

            appointment_id = cur.fetchone()[0]

            # 🔥 update slot
            cur.execute("""
                UPDATE doctor_slot
                SET slot_status = 'BOOKED'
                WHERE slot_id = %s;
            """, (data["slot_id"],))

        conn.commit()

        return {
            "appointment_id": appointment_id,
            "booking_ref": txn_id
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

# ==============================
# DELETE (ADMIN ONLY)
# ==============================
def delete_appointment(appointment_id: int):
    execute_query("""
        DELETE FROM appointment
        WHERE appointment_id = %s;
    """, (appointment_id,))


# ==============================
# CANCEL (PATIENT)
# ==============================
def cancel_appointment(slot_id: str, patient_id: int):
    conn = get_app_connection()

    try:
        with conn.cursor() as cur:

            # 🔒 check ownership
            cur.execute("""
                SELECT appointment_id
                FROM appointment
                WHERE slot_id = %s
                AND patient_id = %s;
            """, (slot_id, patient_id))

            appt = cur.fetchone()

            if not appt:
                raise Exception("Not your booking")

            appointment_id = appt[0]

            # 🔥 delete appointment
            cur.execute("""
                DELETE FROM appointment
                WHERE appointment_id = %s;
            """, (appointment_id,))

            # 🔥 insert transaction CANCELLED
            cur.execute("""
                INSERT INTO appointment_transaction (
                    slot_id,
                    patient_id,
                    action,
                    created_at
                )
                VALUES (%s, %s, 'CANCELLED', NOW())
                RETURNING transaction_id;
            """, (
                slot_id,
                patient_id
            ))

            cancel_txn = cur.fetchone()[0]

            # 🔥 update slot
            cur.execute("""
                UPDATE doctor_slot
                SET slot_status = 'AVAILABLE'
                WHERE slot_id = %s;
            """, (slot_id,))

        conn.commit()

        return {
            "message": "Cancelled",
            "cancel_transaction": cancel_txn
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()
        
def get_doctor_appointments(doctor_id: str):
    query = """
        SELECT 
            a.patient_id,
            ds.slot_id,
            ds.slot_date,
            ds.slot_code
        FROM appointment a
        JOIN doctor_slot ds 
            ON a.slot_id = ds.slot_id
        WHERE ds.doctor_id = %s
        ORDER BY ds.slot_date, ds.slot_code;
    """

    return fetch_all(query, (doctor_id,))
