from app.db import fetch_all, fetch_one, execute_query, get_app_connection
from datetime import datetime


# ==============================
# GET ALL
# ==============================
def get_all_appointments():
    return fetch_all(
        """
        SELECT *
        FROM appointment
        ORDER BY appointment_id;
    """
    )


# ==============================
# GET BY ID
# ==============================
def get_appointment_by_id(appointment_id: int):
    return fetch_one(
        """
        SELECT *
        FROM appointment
        WHERE appointment_id = %s;
    """,
        (appointment_id,),
    )


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

            # =========================
            # 0. VALIDATE INPUT
            # =========================
            slot_id = data.get("slot_id")
            patient_id = data.get("patient_id")

            if not slot_id or not patient_id:
                raise Exception("Missing slot_id or patient_id")

            # =========================
            # 1. LOCK SLOT + CHECK STATUS
            # =========================
            cur.execute(
                """
                SELECT slot_status, admin_status
                FROM doctor_slot
                WHERE slot_id = %s
                FOR UPDATE;
            """,
                (slot_id,),
            )

            row = cur.fetchone()

            if not row:
                raise Exception("Slot not found")

            slot_status, admin_status = row

            if admin_status == "BLOCKED":
                raise Exception("Slot blocked by admin")

            if slot_status == "BLOCKED":
                raise Exception("That slot is blocked")

            if slot_status == "BOOKED":
                raise Exception("Slot already booked")

            # =========================
            # 2. INSERT TRANSACTION
            # =========================
            cur.execute(
                """
                INSERT INTO appointment_transaction (
                    slot_id,
                    patient_id,
                    action,
                    created_at
                )
                VALUES (%s, %s, 'BOOKED', NOW())
                RETURNING transaction_id;
            """,
                (slot_id, patient_id),
            )

            txn_id = cur.fetchone()[0]

            # =========================
            # 3. INSERT APPOINTMENT
            # =========================
            cur.execute(
                """
                INSERT INTO appointment (
                    booking_ref,
                    slot_id,
                    patient_id,
                    booked_at
                )
                VALUES (%s, %s, %s, NOW())
                RETURNING appointment_id;
            """,
                (txn_id, slot_id, patient_id),
            )

            appointment_id = cur.fetchone()[0]

            # =========================
            # 4. UPDATE SLOT STATUS
            # =========================
            cur.execute(
                """
                UPDATE doctor_slot
                SET slot_status = 'BOOKED'
                WHERE slot_id = %s;
            """,
                (slot_id,),
            )

        conn.commit()

        return {
            "success": True,
            "appointment_id": appointment_id,
            "booking_ref": txn_id,
            "message": "Booked successfully",
        }

    except Exception as e:
        conn.rollback()

        # =========================
        # RETURN CLEAN ERROR
        # =========================
        return {"success": False, "message": str(e)}

    finally:
        conn.close()


# ==============================
# DELETE (ADMIN ONLY)
# ==============================
def delete_appointment(appointment_id: int):
    execute_query(
        """
        DELETE FROM appointment
        WHERE appointment_id = %s;
    """,
        (appointment_id,),
    )


# ==============================
# CANCEL (PATIENT)
# ==============================
def cancel_appointment(slot_id: str, insurance_number: str):
    conn = get_app_connection()

    try:
        with conn.cursor() as cur:

            # 1. CHECK OWNERSHIP (insurance → patient → appointment)
            cur.execute(
                """
                SELECT a.appointment_id, a.patient_id
                FROM appointment a
                JOIN patient p 
                    ON a.patient_id = p.patient_id
                WHERE a.slot_id = %s
                AND p.insurance_number = %s;
            """,
                (slot_id, insurance_number),
            )

            appt = cur.fetchone()

            if not appt:
                raise Exception("Not your booking")

            appointment_id = appt[0]
            patient_id = appt[1]

            # 2. LOG TRANSACTION
            cur.execute(
                """
                INSERT INTO appointment_transaction (
                    slot_id,
                    patient_id,
                    action,
                    created_at
                )
                VALUES (%s, %s, 'CANCELLED', NOW())
                RETURNING transaction_id;
            """,
                (slot_id, patient_id),
            )

            cancel_txn = cur.fetchone()[0]

            # 3. DELETE APPOINTMENT
            cur.execute(
                """
                DELETE FROM appointment
                WHERE appointment_id = %s;
            """,
                (appointment_id,),
            )

            # 4. UPDATE SLOT
            cur.execute(
                """
                UPDATE doctor_slot
                SET slot_status = 'AVAILABLE'
                WHERE slot_id = %s;
            """,
                (slot_id,),
            )

        conn.commit()

        return {"message": "Cancelled", "cancel_transaction": cancel_txn}

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
