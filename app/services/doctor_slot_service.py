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
# GET SLOTS FOR UI (Đã sửa)
# ==============================
def get_doctor_slots(doctor_id: str, slot_date: str):
    query = """
    SELECT 
        ds.slot_id, 
        ds.slot_code, 
        ds.slot_status, 
        ds.admin_status, 
        a.patient_id
    FROM doctor_slot ds
    LEFT JOIN appointment a ON ds.slot_id = a.slot_id
    WHERE ds.doctor_id = %s AND ds.slot_date = %s;
    """
    rows = fetch_all(query, (doctor_id, slot_date))
    db_slots = {row["slot_code"]: row for row in rows}

    result = []
    for slot in ALL_SLOTS:
        row = db_slots.get(slot)
        
        # Logic tính toán status cuối cùng để gửi về Frontend
        final_status = "NOT_AVAILABLE"
        
        if row:
            if row["patient_id"]:
                final_status = "BOOKED"
            elif row["admin_status"] == "BLOCKED":
                final_status = "BLOCKED"
            elif row["slot_status"] == "AVAILABLE":
                # Chỉ AVAILABLE khi bác sĩ chọn AVAILABLE VÀ admin không BLOCK
                final_status = "AVAILABLE"
            else:
                final_status = "NOT_AVAILABLE"

        result.append({
            "slot_id": row["slot_id"] if row else None,
            "slot_code": slot,
            "slot_status": final_status,
            "admin_status": row["admin_status"] if row else "AVAILABLE",
            "patient_id": row["patient_id"] if row else None,
        })
    return result

def generate_slot_preview(doctor_id: str, year: int, month: int):
    # ==============================
    # FIX MONTH ROLLOVER
    # ==============================
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    prev_month_start = f"{prev_year}-{prev_month:02d}-01"
    curr_month_start = f"{year}-{month:02d}-01"

    query = """
    SELECT
        EXTRACT(ISODOW FROM slot_date) AS dow,
        slot_code,
        COUNT(*) AS cnt
    FROM doctor_slot
    WHERE doctor_id = %s
      AND slot_status = 'AVAILABLE'
      AND slot_date >= %s::date
      AND slot_date < (%s::date)
      AND EXTRACT(ISODOW FROM slot_date) BETWEEN 1 AND 6
    GROUP BY dow, slot_code
    """

    rows = fetch_all(query, (doctor_id, prev_month_start, curr_month_start))

    result = {}

    for r in rows:
        # 🔥 FIX KEY FORMAT (match frontend)
        key = f"{int(r['dow'])}_{r['slot_code']}"

        result[key] = "GREEN" if r["cnt"] >= 2 else "RED"

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
        AND ds.admin_status = 'AVAILABLE'
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

    # 🔥 CHẶN update/insert nếu Admin đã khóa ngày (HOLIDAY)
    day_info = fetch_one("SELECT status FROM calendar_day WHERE date = %s", (slot_date_obj,))
    if day_info and day_info["status"] == "HOLIDAY":
        raise Exception("Cannot modify slots. This date is blocked by Admin.")

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
        slot_id = existing["slot_id"]

        # 🔥 CHECK nếu slot đang BOOKED
        booked = fetch_one("""
            SELECT 1
            FROM appointment
            WHERE slot_id = %s
        """, (slot_id,))

        if booked and status != "BOOKED":
            raise Exception("Cannot change status of a booked slot")

        execute_query(
            """
            UPDATE doctor_slot
            SET slot_status = %s
            WHERE slot_id = %s;
        """,
            (status, slot_id),
        )

        return {"message": "Slot updated", "slot_id": slot_id}

    else:
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
