from fastapi import APIRouter, HTTPException
from app.services.doctor_slot_service import (
    get_doctor_slots,
    get_patient_by_slot,
    get_slot_id,
    upsert_doctor_slot,
    delete_slot
)

router = APIRouter(prefix="/slots", tags=["Slots"])


# ==============================
# GET ALL SLOTS FOR DOCTOR (UI)
# ==============================
@router.get("/doctor/slots/{doctor_id}/{date}")
def get_slots(doctor_id: str, date: str):
    return get_doctor_slots(doctor_id, date)


# ==============================
# GET PATIENT IN SLOT
# ==============================
@router.get("/doctor/{doctor_id}/{date}/{slot_code}/patient")
def get_patient(doctor_id: str, date: str, slot_code: str):
    result = get_patient_by_slot(doctor_id, date, slot_code)

    if not result:
        return {"patient_id": None}

    return result


# ==============================
# GET SLOT ID
# ==============================
@router.get("/doctor/slot/{doctor_id}/{date}/{slot_code}")
def get_slot_id_route(doctor_id: str, date: str, slot_code: str):
    result = get_slot_id(doctor_id, date, slot_code)

    if not result:
        raise HTTPException(404, "Slot not found")

    return result


# ==============================
# UPSERT SLOT (MAIN API)
# ==============================
@router.put("/doctor/slot/{doctor_id}/{date}/{slot_code}/{status}")
def update_slot_status(
    doctor_id: str,
    date: str,
    slot_code: str,
    status: str
):
    return upsert_doctor_slot(doctor_id, date, slot_code, status)


# ==============================
# DELETE SLOT
# ==============================
@router.delete("/{slot_id}")
def delete(slot_id: str):
    delete_slot(slot_id)
    return {"msg": "deleted"}