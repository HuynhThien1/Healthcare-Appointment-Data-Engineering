from fastapi import APIRouter, HTTPException
from app.services.medical_record_service import *

router = APIRouter(prefix="/records", tags=["Medical Records"])


# ==============================
# GET ALL
# ==============================
@router.get("/")
def get_all():
    return get_all_records()


# ==============================
# GET LATEST RECORD
# ==============================
@router.get("/{slot_id}/{patient_id}")
def get_latest(slot_id: str, patient_id: int):
    record = get_latest_record(slot_id, patient_id)

    if not record:
        raise HTTPException(404, "Record not found")

    return record


# ==============================
# CREATE (NEW VERSION)
# ==============================
@router.post("/")
def create(data: dict):
    return create_record(data)