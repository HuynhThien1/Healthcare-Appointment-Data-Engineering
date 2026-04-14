from unittest import result

from app.db import fetch_all, execute_query, fetch_one
from datetime import datetime

ALL_SLOTS = [
    "8A",
    "8B",
    "9A",
    "9B",
    "10A",
    "10B",
    "11A",
    "11B",
    "13A",
    "13B",
    "14A",
    "14B",
    "15A",
    "15B",
    "16A",
    "16B",
]


# ==============================
# GET SLOTS FOR UI
# ==============================
def get_doctor_slots(doctor_id: str, slot_date: str):
    query = """
    SELECT 
        ds.slot_id,
        ds.slot_code,
        CASE 
            WHEN a.patient_id IS NOT NULL THEN 'BOOKED'
            ELSE ds.slot_status
        END AS slot_status,
        a.patient_id
    FROM doctor_slot ds
    LEFT JOIN appointment a 
        ON ds.slot_id = a.slot_id
    WHERE ds.doctor_id = %s
    AND ds.slot_date = %s;
"""

    rows = fetch_all(query, (doctor_id, slot_date))

    db_slots = {row["slot_code"]: row for row in rows}

    result = []

    for slot in ALL_SLOTS:
        row = db_slots.get(slot)

        result.append(
            {
                "slot_id": row["slot_id"] if row else None,
                "slot_code": slot,
                "slot_status": row["slot_status"] if row else None,
                "patient_id": row["patient_id"] if row else None,
            }
        )

    return result


# ==============================
# GET PATIENT FROM SLOT
# ==============================
def get_patient_by_slot(doctor_id: str, slot_date: str, slot_code: str):
    query = """
        SELECT a.patient_id
        FROM doctor_slot ds
        JOIN appointment a ON ds.slot_id = a.slot_id
        WHERE ds.doctor_id = %s
        AND ds.slot_date = %s
        AND ds.slot_code = %s
        AND ds.slot_status = 'BOOKED'
    """

    return fetch_one(query, (doctor_id, slot_date, slot_code))


# ==============================
# GET SLOT ID
# ==============================
def get_slot_id(doctor_id: str, slot_date: str, slot_code: str):
    query = """
        SELECT slot_id
        FROM doctor_slot
        WHERE doctor_id = %s
        AND slot_date = %s
        AND slot_code = %s;
    """

    return fetch_one(query, (doctor_id, slot_date, slot_code))


# ==============================
# UPSERT SLOT (CORE LOGIC)
# ==============================
def upsert_doctor_slot(doctor_id: str, slot_date: str, slot_code: str, status: str):
    slot_date_obj = datetime.strptime(slot_date, "%Y-%m-%d").date()

    # check tồn tại
    existing = fetch_one(
        """
        SELECT slot_id
        FROM doctor_slot
        WHERE doctor_id = %s
        AND slot_date = %s
        AND slot_code = %s;
    """,
        (doctor_id, slot_date_obj, slot_code),
    )

    if existing:
        # UPDATE
        execute_query(
            """
            UPDATE doctor_slot
            SET slot_status = %s
            WHERE slot_id = %s;
        """,
            (status, existing["slot_id"]),
        )

        return {"message": "Slot updated", "slot_id": existing["slot_id"]}

    else:
        # CREATE slot_id dạng deterministic
        slot_id = f"{slot_date.replace('-', '')}{doctor_id}{slot_code}"

        execute_query(
            """
            INSERT INTO doctor_slot (
                slot_id,
                doctor_id,
                slot_date,
                slot_code,
                slot_status
            )
            VALUES (%s, %s, %s, %s, %s);
        """,
            (slot_id, doctor_id, slot_date_obj, slot_code, status),
        )

        return {"message": "Slot created", "slot_id": slot_id}


# ==============================
# DELETE
# ==============================
def delete_slot(slot_id: str):
    execute_query("DELETE FROM doctor_slot WHERE slot_id = %s;", (slot_id,))
