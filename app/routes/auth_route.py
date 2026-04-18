from fastapi import APIRouter, HTTPException
from app.services.patient_service import get_patient_by_id
from app.services.doctor_service import get_doctor_by_id  # assuming you have this
from app.services.admin_service import get_admin_by_code

router = APIRouter(prefix="/auth", tags=["Auth"])


# 🔹 PATIENT LOGIN
@router.post("/login/patient")
def login_patient(data: dict):
    patient_id = data.get("patient_id")

    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id is required")

    patient = get_patient_by_id(patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "message": "Login successful",
        "role": "patient",
        "user": patient
    }


# 🔹 DOCTOR LOGIN
@router.post("/login/doctor")
def login_doctor(data: dict):
    doctor_id = data.get("doctor_id")

    if not doctor_id:
        raise HTTPException(status_code=400, detail="doctor_id is required")

    doctor = get_doctor_by_id(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {
        "message": "Login successful",
        "role": "doctor",
        "user": doctor
    }

@router.post("/login/admin")
def login_admin(data: dict):
    admin_code = data.get("admin_code")

    if not admin_code:
        raise HTTPException(status_code=400, detail="admin_code is required")

    admin = get_admin_by_code(admin_code)

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {
        "message": "Login successful",
        "role": "admin",
        "user": admin
    }