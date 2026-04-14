from fastapi import APIRouter
from app.services.payment_service import *

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/")
def get_all():
    return get_all_payments()

@router.post("/")
def create(data:dict):
    create_payment(data)
    return {"msg":"created"}