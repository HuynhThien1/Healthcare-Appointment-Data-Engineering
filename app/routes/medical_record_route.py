from fastapi import APIRouter, HTTPException
from app.services import medical_record_service
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
@router.get("/detail/{slot_id}")
def get_latest(slot_id: str):
    record = get_latest_record(slot_id)
    if not record:
        raise HTTPException(404, "Record not found")
    return record


@router.get("/doctor/{doctor_id}")
async def read_doctor_records(doctor_id: str):
    records = medical_record_service.get_records_by_doctor(doctor_id)
    return {"status": "success", "data": records}

@router.post("/create-version")
async def add_record(data: dict):
    try:
        version = medical_record_service.create_new_version(data)
        return {"message": "Record created", "version": version}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/slot/{slot_id}")
def get_slot_history(slot_id: str):
    try:
        data = get_records_by_slot(slot_id)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.get("/patient-insurance/{insurance_code}")
async def read_patient_records(insurance_code: str):
    try:
        records = medical_record_service.get_records_by_patient_insurance(insurance_code)
        return {"status": "success", "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# CREATE (NEW VERSION)
# ==============================
@router.post("/")
def create(data: dict):
    return create_record(data)