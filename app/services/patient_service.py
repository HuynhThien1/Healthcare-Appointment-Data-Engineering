from app.db import fetch_all, fetch_one, execute_query


# ==============================
# GET ALL
# ==============================
def get_all_patients():
    return fetch_all("""
        SELECT *
        FROM patient
        ORDER BY patient_id;
    """)


# ==============================
# GET BY ID
# ==============================
def get_patient_by_id(patient_id: int):
    return fetch_one("""
        SELECT *
        FROM patient
        WHERE patient_id = %s;
    """, (patient_id,))

# ==============================
# GET ALL INSURANCE NUMBERS
# ==============================
def get_all_insurance_numbers():
    rows = fetch_all("""
        SELECT insurance_number
        FROM patient
        WHERE insurance_number IS NOT NULL
        ORDER BY insurance_number;
    """)

    # optional: return list thuần thay vì list dict
    return rows

# ==============================
# CREATE
# ==============================
def create_patient(data: dict):
    result = fetch_one("""
        INSERT INTO patient (
            patient_name,
            address,
            phone_number,
            email,
            insurance_number,
            date_of_birth,
            gender
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING patient_id;
    """, (
        data["patient_name"],
        data.get("address"),
        data["phone_number"],
        data.get("email"),
        data.get("insurance_number"),
        data.get("date_of_birth"),
        data.get("gender")
    ))

    return result["patient_id"]

# ==============================
# UPDATE
# ==============================
def update_patient(patient_id: int, data: dict):
    execute_query("""
        UPDATE patient
        SET
            patient_name = %s,
            address = %s,
            phone_number = %s,
            email = %s,
            insurance_number = %s,
            date_of_birth = %s,
            gender = %s,
            updated_at = NOW()
        WHERE patient_id = %s;
    """, (
        data.get("patient_name"),
        data.get("address"),
        data.get("phone_number"),
        data.get("email"),
        data.get("insurance_number"),
        data.get("date_of_birth"),
        data.get("gender"),
        patient_id
    ))


# ==============================
# DELETE
# ==============================
def delete_patient(patient_id: int):
    execute_query("""
        DELETE FROM patient
        WHERE patient_id = %s;
    """, (patient_id,))