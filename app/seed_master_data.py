from faker import Faker
from datetime import datetime, timedelta, date, time
from psycopg2.extras import execute_values

import random
from app.db import get_app_connection

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


# this function will generate master data for doctor table
def seed_doctors(n: int = 50):
    rows = []
    now = datetime.now()

    for doctor_id in range(1, n + 1):
        rows.append(
            (doctor_id,
            f"DOC{doctor_id:04d}",
            fake.name(),
            random.choice(SPECIALTIES),
            fake.phone_number()[:20],
            f"doctor{doctor_id}@gmail.com",
            random.choice(EMPLOYMENT_STATUSES),
            random.randint(1, 3),
            fake.date_between(start_date="-5y", end_date="today"),
            now,
            now)
        )
    
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO doctor (
                    doctor_id, doctor_code, doctor_name, specialty, phone_number, email,
                    employment_status, clinic_id, start_working_date, created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (doctor_id) DO NOTHING;
                """,
                rows
            )
        conn.commit()
        print(f"Seeded doctor: {len(rows)} rows")
    finally:
        conn.close()


#Seed master patients data
def seed_patients(n: int = 50):
    rows = []
    now = datetime.now()

    for patient_id in range(1, n + 1):
        rows.append(
            (
                patient_id,
                fake.name(),
                fake.address().replace("\n", ", "),
                fake.phone_number()[:20],
                f"patient{patient_id}@example.com",
                f"INS{patient_id:06d}",
                random.choice(["Bao Viet", "PVI", "VietinBank Insurance", "None"]),
                fake.date_of_birth(minimum_age=1, maximum_age=90),
                random.choice(["Male", "Female"]),
                random.choice(PATIENT_STATUSES),
                fake.name(),
                fake.phone_number()[:20],
                now,
                now,
            )
        )
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO patient (
                    patient_id, patient_name, address, phone_number, email,
                    insurance_number, insurance_provider, date_of_birth, gender,
                    patient_status, emergency_contact_name, emergency_contact_phone,
                    created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (patient_id) DO NOTHING;
                """,
                rows,
            )
        conn.commit()
        print(f"Seeded patient: {len(rows)} rows")
    finally:
        conn.close()

#Seed doctor slot master data
def seed_doctor_slots(days: int = 5, slots_per_day: int = 5):
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT doctor_id, clinic_id FROM doctor ORDER BY doctor_id;")
            doctors = cur.fetchall()

            if not doctors:
                print("No doctors found. Please seed doctor first.")
                return

            rows = []
            slot_id = 1
            base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

            for doctor_id, clinic_id in doctors:
                for day_offset in range(days):
                    current_day = base_date + timedelta(days=day_offset)
                    for slot_index in range(slots_per_day):
                        start_time = current_day + timedelta(hours=slot_index)
                        end_time = start_time + timedelta(minutes=45)

                        rows.append(
                            (
                                slot_id,
                                doctor_id,
                                clinic_id,
                                start_time.date(),
                                start_time,
                                end_time,
                                "AVAILABLE",
                                random.choice(SLOT_TYPES),
                                1,
                                datetime.now(),
                                datetime.now(),
                            )
                        )
                        slot_id += 1

            execute_values(
                cur,
                """
                INSERT INTO doctor_slot (
                    slot_id, doctor_id, clinic_id, slot_date, start_time, end_time,
                    slot_status, slot_type, max_capacity, created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (slot_id) DO NOTHING;
                """,
                rows,
            )

        conn.commit()
        print(f"Seeded doctor_slot: {len(rows)} rows")
    finally:
        conn.close()

def seed_appointments(n: int = 20):
    # explanation: Seed bảng appointment.
    # explanation: Chỉ lấy slot AVAILABLE để tạo lịch hẹn ban đầu.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT slot_id, doctor_id, start_time
                FROM doctor_slot
                WHERE slot_status = 'AVAILABLE'
                ORDER BY slot_id
                LIMIT %s;
                """,
                (n,),
            )
            slots = cur.fetchall()

            cur.execute("SELECT patient_id FROM patient ORDER BY patient_id;")
            patients = [row[0] for row in cur.fetchall()]

            if not slots or not patients:
                print("No slots or patients found.")
                return

            appointment_rows = []
            now = datetime.now()

            for appointment_id, (slot_id, doctor_id, start_time) in enumerate(slots, start=1):
                patient_id = random.choice(patients)
                status = random.choice(["BOOKED", "CONFIRMED", "COMPLETED"])

                appointment_rows.append(
                    (
                        appointment_id,
                        f"CONF{appointment_id:06d}",
                        slot_id,
                        doctor_id,
                        patient_id,
                        status,
                        random.choice(BOOKING_CHANNELS),
                        random.choice(APPOINTMENT_TYPES),
                        fake.sentence(nb_words=6),
                        now - timedelta(hours=random.randint(1, 72)),
                        None,
                        now if status == "COMPLETED" else None,
                        None,
                        "seed_script",
                        "seed_script",
                        now,
                        now,
                    )
                )

            execute_values(
                cur,
                """
                INSERT INTO appointment (
                    appointment_id, confirmation_number, slot_id, doctor_id, patient_id,
                    status, booking_channel, appointment_type, reason_for_visit,
                    booked_at, cancelled_at, completed_at, cancel_reason,
                    created_by, updated_by, created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (appointment_id) DO NOTHING;
                """,
                appointment_rows,
            )

            # explanation: Những slot đã được dùng để tạo appointment thì chuyển sang BOOKED.
            cur.execute(
                """
                UPDATE doctor_slot
                SET slot_status = 'BOOKED',
                    updated_at = NOW()
                WHERE slot_id IN (
                    SELECT slot_id
                    FROM appointment
                );
                """
            )

        conn.commit()
        print(f"Seeded appointment: {len(appointment_rows)} rows")
    finally:
        conn.close()

def seed_appointments(n: int = 20):
    # explanation: Seed bảng appointment.
    # explanation: Chỉ lấy slot AVAILABLE để tạo lịch hẹn ban đầu.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT slot_id, doctor_id, start_time
                FROM doctor_slot
                WHERE slot_status = 'AVAILABLE'
                ORDER BY slot_id
                LIMIT %s;
                """,
                (n,),
            )
            slots = cur.fetchall()

            cur.execute("SELECT patient_id FROM patient ORDER BY patient_id;")
            patients = [row[0] for row in cur.fetchall()]

            if not slots or not patients:
                print("No slots or patients found.")
                return

            appointment_rows = []
            now = datetime.now()

            for appointment_id, (slot_id, doctor_id, start_time) in enumerate(slots, start=1):
                patient_id = random.choice(patients)
                status = random.choice(["BOOKED", "CONFIRMED", "COMPLETED"])

                appointment_rows.append(
                    (
                        appointment_id,
                        f"CONF{appointment_id:06d}",
                        slot_id,
                        doctor_id,
                        patient_id,
                        status,
                        random.choice(BOOKING_CHANNELS),
                        random.choice(APPOINTMENT_TYPES),
                        fake.sentence(nb_words=6),
                        now - timedelta(hours=random.randint(1, 72)),
                        None,
                        now if status == "COMPLETED" else None,
                        None,
                        "seed_script",
                        "seed_script",
                        now,
                        now,
                    )
                )

            execute_values(
                cur,
                """
                INSERT INTO appointment (
                    appointment_id, confirmation_number, slot_id, doctor_id, patient_id,
                    status, booking_channel, appointment_type, reason_for_visit,
                    booked_at, cancelled_at, completed_at, cancel_reason,
                    created_by, updated_by, created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (appointment_id) DO NOTHING;
                """,
                appointment_rows,
            )

            # explanation: Những slot đã được dùng để tạo appointment thì chuyển sang BOOKED.
            cur.execute(
                """
                UPDATE doctor_slot
                SET slot_status = 'BOOKED',
                    updated_at = NOW()
                WHERE slot_id IN (
                    SELECT slot_id
                    FROM appointment
                );
                """
            )

        conn.commit()
        print(f"Seeded appointment: {len(appointment_rows)} rows")
    finally:
        conn.close()

def seed_appointment_status_history():
    # explanation: Seed bảng appointment_status_history dựa trên dữ liệu appointment đã có.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT appointment_id, status, booked_at
                FROM appointment
                ORDER BY appointment_id;
                """
            )
            appointments = cur.fetchall()

            if not appointments:
                print("No appointments found for appointment_status_history.")
                return

            rows = []
            for history_id, (appointment_id, status, booked_at) in enumerate(appointments, start=1):
                rows.append(
                    (
                        history_id,
                        appointment_id,
                        None,
                        status,
                        booked_at or datetime.now(),
                        "seed_script",
                        "Initial status",
                    )
                )

            execute_values(
                cur,
                """
                INSERT INTO appointment_status_history (
                    history_id, appointment_id, old_status, new_status, changed_at,
                    changed_by, reason
                )
                VALUES %s
                ON CONFLICT (history_id) DO NOTHING;
                """,
                rows,
            )

        conn.commit()
        print(f"Seeded appointment_status_history: {len(rows)} rows")
    finally:
        conn.close()


def seed_payments():
    # explanation: Seed bảng payment theo từng appointment.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT appointment_id, status
                FROM appointment
                ORDER BY appointment_id;
                """
            )
            appointments = cur.fetchall()

            if not appointments:
                print("No appointments found for payment.")
                return

            rows = []
            now = datetime.now()

            for payment_id, (appointment_id, appointment_status) in enumerate(appointments, start=1):
                amount_total = round(random.uniform(20, 150), 2)
                amount_covered = round(random.uniform(0, amount_total * 0.7), 2)
                amount_patient = round(amount_total - amount_covered, 2)

                if appointment_status == "COMPLETED":
                    payment_status = "PAID"
                    paid_datetime = now
                else:
                    payment_status = random.choice(["PENDING", "FAILED", "PARTIALLY_PAID"])
                    paid_datetime = None

                rows.append(
                    (
                        payment_id,
                        appointment_id,
                        amount_total,
                        amount_covered,
                        amount_patient,
                        paid_datetime,
                        payment_status,
                        random.choice(["CASH", "CARD", "INSURANCE"]),
                        f"TXN{payment_id:06d}",
                        "USD",
                        now,
                        now,
                    )
                )

            execute_values(
                cur,
                """
                INSERT INTO payment (
                    payment_id, appointment_id, amount_total, amount_covered,
                    amount_patient_responsibility, paid_datetime, payment_status,
                    payment_method, transaction_reference, currency, created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (payment_id) DO NOTHING;
                """,
                rows,
            )

        conn.commit()
        print(f"Seeded payment: {len(rows)} rows")
    finally:
        conn.close()


def seed_medical_records():
    # explanation: Seed bảng medical_record.
    # explanation: Chỉ tạo medical_record cho appointment đã COMPLETED để hợp logic hơn.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT appointment_id, patient_id, doctor_id
                FROM appointment
                WHERE status = 'COMPLETED'
                ORDER BY appointment_id;
                """
            )
            appointments = cur.fetchall()

            if not appointments:
                print("No COMPLETED appointments found for medical_record.")
                return

            rows = []
            now = datetime.now()

            for record_id, (appointment_id, patient_id, doctor_id) in enumerate(appointments, start=1):
                rows.append(
                    (
                        record_id,
                        appointment_id,
                        patient_id,
                        doctor_id,
                        1,
                        fake.text(max_nb_chars=100),
                        fake.text(max_nb_chars=100),
                        fake.text(max_nb_chars=100),
                        fake.text(max_nb_chars=100),
                        random.choice(RECORD_STATUSES),
                        now,
                        now,
                    )
                )

            execute_values(
                cur,
                """
                INSERT INTO medical_record (
                    record_id, appointment_id, patient_id, doctor_id, version_number,
                    diagnosis_note, prescription_note, lab_summary,
                    follow_up_instruction, record_status, created_at, updated_at
                )
                VALUES %s
                ON CONFLICT (record_id) DO NOTHING;
                """,
                rows,
            )

        conn.commit()
        print(f"Seeded medical_record: {len(rows)} rows")
    finally:
        conn.close()


def seed_all():
    # explanation: Chạy seed theo đúng thứ tự khóa ngoại.
    # explanation: doctor + patient -> doctor_slot -> appointment -> history/payment/medical_record
    seed_doctors()
    seed_patients()
    seed_doctor_slots()
    seed_appointments()
    seed_appointment_status_history()
    seed_payments()
    seed_medical_records()


if __name__ == "__main__":
    seed_all()