from app.db import fetch_all, fetch_one, execute_query


# ==============================
# GET ALL
# ==============================
def get_all_doctors():
    return fetch_all("""
        SELECT doctor_id, doctor_name, specialty, start_working_date
        FROM doctor
        ORDER BY doctor_id;
    """)


# ==============================
# GET BY ID
# ==============================
def get_doctor_by_id(doctor_id: str):
    return fetch_one("""
        SELECT doctor_id, doctor_name, specialty, start_working_date
        FROM doctor
        WHERE doctor_id = %s;
    """, (doctor_id,))


# ==============================
# GET BY SPECIALTY
# ==============================
def get_doctors_by_specialty_db(specialty: str):
    return fetch_all("""
        SELECT doctor_id, doctor_name, specialty
        FROM doctor
        WHERE specialty = %s;
    """, (specialty,))


# ==============================
# CREATE
# ==============================
def create_doctor(data: dict):
    result = fetch_one("""
        INSERT INTO doctor (
            doctor_name,
            specialty,
            start_working_date
        )
        VALUES (%s, %s, %s)
        RETURNING doctor_id;
    """, (
        data["doctor_name"],
        data["specialty"],
        data.get("start_working_date")
    ))

    return result["doctor_id"]

# ==============================
# UPDATE
# ==============================
def update_doctor(doctor_id: str, data: dict):
    execute_query("""
        UPDATE doctor
        SET
            doctor_name = %s,
            specialty = %s,
            start_working_date = %s
        WHERE doctor_id = %s;
    """, (
        data.get("doctor_name"),
        data.get("specialty"),
        data.get("start_working_date"),
        doctor_id
    ))


# ==============================
# DELETE
# ==============================
def delete_doctor(doctor_id: str):
    execute_query("""
        DELETE FROM doctor
        WHERE doctor_id = %s;
    """, (doctor_id,))