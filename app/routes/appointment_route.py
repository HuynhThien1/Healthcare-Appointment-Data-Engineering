from fastapi import APIRouter, HTTPException
from app.services.appointment_service import *

router = APIRouter(prefix="/appointments", tags=["Appointments"])


# ==============================
# GET ALL
# ==============================
@router.get("/")
def get_all():
    return get_all_appointments()


# ==============================
# GET BY ID
# ==============================
@router.get("/{id}")
def get_one(id: int):
    appt = get_appointment_by_id(id)
    if not appt:
        raise HTTPException(404, "Not found")
    return appt

@router.get("/appointments/patient/{patient_id}")
def get_patient_appointments_api(patient_id: int):
    return get_patient_appointments(patient_id)

@router.get("/appointments/doctor/{doctor_id}")
def get_doctor_appointments_api(doctor_id: str):
    return get_doctor_appointments(doctor_id)

# ==============================
# BOOK SLOT
# ==============================
@router.post("/")
def create(data: dict):
    return create_appointment(data)


# ==============================
# CANCEL
# ==============================
@router.post("/cancel")
def cancel(data: dict):
    return cancel_appointment(
        data["slot_id"],   # str
        data["patient_id"] # int
    )


# ==============================
# DELETE (optional)
# ==============================
@router.delete("/{id}")
def delete(id: int):
    delete_appointment(id)
    return {"msg": "deleted"}