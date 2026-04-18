from fastapi import APIRouter
from app.services.calendar_service import *

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/")
def get_calendar(start: str, end: str):
    return get_calendar_range(start, end)


@router.put("/update")
def update_calendar(data: dict):
    update_calendar_status(data["date"], data["status"])
    return {"message": "Updated"}