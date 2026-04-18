from fastapi import APIRouter
from app.services.schedule_service import *

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.get("/preview/{doctor_id}/{year}/{month}")
def preview(doctor_id: str, year: int, month: int):
    return generate_preview(doctor_id, year, month)


@router.get("/status/{doctor_id}/{year}/{month}")
def status(doctor_id: str, year: int, month: int):
    return get_month_status(doctor_id, year, month)


@router.post("/confirm")
def confirm(data: dict):
    return confirm_generate(
        data["doctor_id"],
        data["year"],
        data["month"],
        data["slots"]
    )