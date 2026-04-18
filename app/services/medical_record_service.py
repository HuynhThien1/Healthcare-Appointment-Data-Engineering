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
def get_latest_record(slot_id: str):
    query = """
        SELECT mr.*, p.patient_name, p.patient_id, ds.slot_date
        FROM doctor_slot ds
        JOIN appointment a ON ds.slot_id = a.slot_id
        JOIN patient p ON a.patient_id = p.patient_id
        LEFT JOIN medical_record mr ON ds.slot_id = mr.slot_id
        WHERE ds.slot_id = %s
        ORDER BY mr.version_number DESC LIMIT 1
    """
    return fetch_one(query, (slot_id,))

# ==============================
# CREATE / NEW VERSION
# ==============================
def create_record(data: dict):
    slot_id = data.get("slot_id")
    patient_id = data.get("patient_id")
    diagnosis = data.get("diagnosis_note")
    prescription = data.get("prescription_note")
    
    # Tim version hien tai lon nhat
    current_v = fetch_one(
        "SELECT MAX(version_number) FROM medical_record WHERE slot_id = %s", 
        (slot_id,)
    )
    new_version = (current_v['max'] + 1) if current_v and current_v['max'] else 1

    query = """
        INSERT INTO medical_record (
            slot_id, patient_id, version_number, 
            diagnosis_note, prescription_note, 
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING record_id
    """
    execute_query(query, (slot_id, patient_id, new_version, diagnosis, prescription))
    return {"status": "success", "version": new_version}

def get_records_by_doctor(doctor_id: str):
    # Dùng DISTINCT ON để chỉ lấy bản ghi có version cao nhất cho mỗi slot_id
    query = """
        SELECT DISTINCT ON (mr.slot_id)
            mr.record_id,
            mr.slot_id,
            mr.patient_id,
            p.patient_name,
            mr.version_number,
            mr.diagnosis_note,
            mr.prescription_note,
            ds.slot_date,
            ds.slot_code,
            mr.created_at
        FROM medical_record mr
        JOIN doctor_slot ds ON mr.slot_id = ds.slot_id
        JOIN patient p ON mr.patient_id = p.patient_id
        WHERE ds.doctor_id = %s
        ORDER BY mr.slot_id, mr.version_number DESC;
    """
    return fetch_all(query, (doctor_id,))

def create_new_version(data: dict):
    # Logic tăng version_number như bạn đã viết ở trên
    slot_id = data["slot_id"]
    patient_id = data["patient_id"]
    
    latest = fetch_one("""
        SELECT MAX(version_number) as max_ver 
        FROM medical_record 
        WHERE slot_id = %s AND patient_id = %s
    """, (slot_id, patient_id))
    
    next_version = (latest["max_ver"] or 0) + 1
    
    execute_query("""
        INSERT INTO medical_record (slot_id, patient_id, version_number, diagnosis_note, prescription_note, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
    """, (slot_id, patient_id, next_version, data.get("diagnosis_note"), data.get("prescription_note")))
    
    return next_version

def get_records_by_slot(slot_id: str):
    query = """
        SELECT mr.*, p.patient_name, ds.slot_date, ds.slot_code
        FROM medical_record mr
        JOIN patient p ON mr.patient_id = p.patient_id
        JOIN doctor_slot ds ON mr.slot_id = ds.slot_id
        WHERE mr.slot_id = %s
        ORDER BY mr.version_number DESC
    """
    return fetch_all(query, (slot_id,))

def get_records_by_patient_insurance(insurance_code: str):
    # 1. Lấy patient_id dựa trên insurance_number (tên cột đúng trong Schema)
    patient = fetch_one(
        "SELECT patient_id FROM patient WHERE insurance_number = %s", 
        (insurance_code,)
    )
    
    if not patient:
        return []
    
    patient_id = patient['patient_id']

    # 2. Truy vấn danh sách bản ghi mới nhất (Distinct on slot_id)
    # Sắp xếp theo doctor_id như bạn yêu cầu
    query = """
        SELECT DISTINCT ON (mr.slot_id)
            ds.doctor_id,
            d.doctor_name,
            mr.record_id AS medical_record_id,
            mr.slot_id,
            ds.slot_date AS date,
            ds.slot_code,
            mr.version_number
        FROM medical_record mr
        JOIN doctor_slot ds ON mr.slot_id = ds.slot_id
        JOIN doctor d ON ds.doctor_id = d.doctor_id
        WHERE mr.patient_id = %s
        ORDER BY mr.slot_id, mr.version_number DESC;
    """
    
    # Nếu bạn muốn sort kết quả cuối cùng theo doctor_id ở lớp ứng dụng:
    results = fetch_all(query, (patient_id,))
    if results:
        # Sort theo doctor_id sau khi đã lấy được các bản ghi DISTINCT
        results.sort(key=lambda x: x['doctor_id'])
        
    return results
