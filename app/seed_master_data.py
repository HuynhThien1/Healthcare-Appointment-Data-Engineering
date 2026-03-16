from faker import Faker
from datetime import datetime, timedelta, date, time
import random
from db import get_app_connection

fake = Faker()

SPECIALTIES = ["Cardiology", "Dermatology", "Neurology", "Pediatrics", "Orthopedics", "ENT", "General Medicine"]
EMPLOYMENT_STATUSES = ["ACTIVE", "INACTIVE", "ON_LEAVE"]
PATIENT_STATUSES = ["ACTIVE", "INACTIVE"]
GENDERS = ["MALE", "FEMALE", "OTHER"]
SLOT_STATUSES = ["AVAILABLE", "BOOKED", "BLOCKED", "CANCELLED"]
SLOT_TYPES = ["CONSULTATION", "FOLLOW_UP", "TEST", "EMERGENCY"]
APPOINTMENT_STATUSES = ["BOOKED", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW"]
BOOKING_CHANNELS = ["WEB", "MOBILE", "PHONE", "WALK_IN"]
APPOINTMENT_TYPES = ["NEW", "FOLLOW_UP", "CHECKUP"]
PAYMENT_STATUSES = ["PENDING", "PAID", "FAILED", "REFUNDED", "PARTIALLY_PAID"]
PAYMENT_METHODS = ["CASH", "CARD", "BANK_TRANSFER", "INSURANCE"]
RECORD_STATUSES = ["DRAFT", "FINAL", "AMENDED"]

def random_timestamp(days_back=60):
    now = datetime.now()


def seed_doctors(cur, n=10):
    for i in range(1, n+1):
        cur.execute("""
            INSERT INTO doctor(doctor_id, doctor_code, doctor_name, specialty,
                phone_number, email, employment_status, clinic_id,
                start_working_date, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE, NOW(), NOW())
            ON CONFLICT (doctor_id) DO NOTHING""", (
            i, f"DOC{i:04d}", 
            f"Doctor {i}",
            random.choice(["Cardiology", "Neurology", "Pediatrics"]),
            fake.phone_number(),
            f"doctor{i}@hospital.com",
            random.choice(["ACTIVE", "INACTIVE", "ON_LEAVE"]),
            random.randint(1,  3)
            )                   
)
        

def main():
    conn = get_app_connection()
    cur = conn.cursor()

    seed_doctors(cur, 10)

    conn.commit()
    cur.close()
    conn.close()
    print("Seeded master data.")

if __name__ == "__main__":
    main()
