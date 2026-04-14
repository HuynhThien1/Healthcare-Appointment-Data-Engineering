from fastapi import APIRouter, HTTPException
from app.services.doctor_service import *

router = APIRouter(prefix="/doctors", tags=["Doctors"])


# ==============================
# GET ALL
# ==============================
@router.get("/")
def get_doctors():
    return get_all_doctors()    


# ==============================
# GET BY ID
# ==============================
@router.get("/{doctor_id}")
def get_doctor(doctor_id: str):
    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


# ==============================
# GET BY SPECIALTY
# ==============================
@router.get("/specialty/{specialty}")
def get_doctors_by_specialty(specialty: str):
    return get_doctors_by_specialty_db(specialty)


# ==============================
# CREATE
# ==============================
@router.post("/")
def create_new_doctor(data: dict):
    doctor_id = create_doctor(data)
    return {
        "doctor_id": doctor_id
    }

# ==============================
# UPDATE
# ==============================
@router.put("/{doctor_id}")
def update_existing_doctor(doctor_id: str, data: dict):
    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    update_doctor(doctor_id, data)
    return {"message": "Doctor updated successfully"}


# ==============================
# DELETE
# ==============================
@router.delete("/{doctor_id}")
def delete_existing_doctor(doctor_id: str):
    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    delete_doctor(doctor_id)
    return {"message": "Doctor deleted successfully"}