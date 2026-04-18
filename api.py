from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.patient_route import router as patient_router
from app.routes.doctor_route import router as doctor_router
from app.routes.doctor_slot_route import router as slot_router
from app.routes.appointment_route import router as appointment_router
from app.routes.payment_route import router as payment_router
from app.routes.medical_record_route import router as record_router
from app.routes.schedule_router import router as schedule_router
from app.routes import auth_route
from app.routes import calendar_route
from app.jobs.scheduler import start_scheduler
app = FastAPI()

# ✅ ADD THIS BLOCK RIGHT HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(slot_router)
app.include_router(appointment_router)
# app.include_router(payment_router)
app.include_router(record_router)
app.include_router(auth_route.router)
app.include_router(schedule_router)
app.include_router(calendar_route.router)

@app.on_event("startup")
def startup_event():
    start_scheduler()