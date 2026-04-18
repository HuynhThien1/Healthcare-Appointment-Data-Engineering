from fastapi import APIRouter, HTTPException
from app.services.patient_service import *

router = APIRouter(prefix="/patients", tags=["Patients"])


# ==============================
# GET ALL
# ==============================
@router.get("/")
def get_patients():
    return get_all_patients()


# ==============================
# GET BY ID
# ==============================
@router.get("/{patient_id}")
def get_patient(patient_id: int):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# ==============================
# GET ALL INSURANCE NUMBERS
# ==============================
@router.get("/insurance-numbers/all")
def get_insurance_numbers():
    return get_all_insurance_numbers()


@router.get("/by-insurance/{insurance}")
def get_patient_by_insurance(insurance: str):
    patient = fetch_one("""
        SELECT patient_id
        FROM patient
        WHERE insurance_number = %s
    """, (insurance,))

    if not patient:
        raise HTTPException(404, "Not found")

    return patient

# ==============================
# CREATE
# ==============================
@router.post("/")
def create(data: dict):
    patient_id = create_patient(data)
    return {
        "patient_id": patient_id
    }


# ==============================
# UPDATE
# ==============================
@router.put("/{patient_id}")
def update_existing_patient(patient_id: int, data: dict):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_patient(patient_id, data)
    return {"message": "Patient updated successfully"}


# ==============================
# DELETE
# ==============================
@router.delete("/{patient_id}")
def delete_existing_patient(patient_id: int):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    delete_patient(patient_id)
    return {"message": "Patient deleted successfully"}