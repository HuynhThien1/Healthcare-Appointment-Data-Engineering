from app.db import fetch_all, fetch_one, execute_query


# ==============================
# GET ALL
# ==============================
def get_all_records():
    return fetch_all("""
        SELECT *
        FROM medical_record
        ORDER BY slot_id, patient_id, version_number;
    """)


# ==============================
# GET LATEST RECORD
# ==============================
def get_latest_record(slot_id: str, patient_id: int):
    return fetch_one("""
        SELECT *
        FROM medical_record
        WHERE slot_id = %s
        AND patient_id = %s
        ORDER BY version_number DESC
        LIMIT 1;
    """, (slot_id, patient_id))


# ==============================
# CREATE / NEW VERSION
# ==============================
def create_record(data: dict):
    slot_id = data["slot_id"]
    patient_id = data["patient_id"]

    # 🔥 get latest version
    latest = fetch_one("""
        SELECT MAX(version_number) as max_ver
        FROM medical_record
        WHERE slot_id = %s
        AND patient_id = %s;
    """, (slot_id, patient_id))

    next_version = (latest["max_ver"] or 0) + 1

    execute_query("""
        INSERT INTO medical_record (
            slot_id,
            patient_id,
            version_number,
            diagnosis_note,
            prescription_note,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        slot_id,
        patient_id,
        next_version,
        data.get("diagnosis_note"),
        data.get("prescription_note")
    ))

    return {
        "message": "Record created",
        "version": next_version
    }