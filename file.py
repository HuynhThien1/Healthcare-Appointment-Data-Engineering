import random
import time
from datetime import datetime
import psycopg2
from faker import Faker

fake = Faker()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "healthcare_booking_realtime",
    "user": "postgres",
    "password": "your_password"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_random_patient_id(cur):
    cur.execute("SELECT patient_id FROM patient ORDER BY random() LIMIT 1;")
    row = cur.fetchone()
    return row[0] if row else None


def get_random_available_slot(cur):
    cur.execute("""
        SELECT slot_id, doctor_id
        FROM doctor_slot
        WHERE slot_status = 'AVAILABLE'
        ORDER BY random()
        LIMIT 1;
    """)
    return cur.fetchone()


def create_appointment(cur):
    slot = get_random_available_slot(cur)
    patient_id = get_random_patient_id(cur)

    if not slot or not patient_id:
        print("No available slot or patient found.")
        return

    slot_id, doctor_id = slot
    status = random.choice(["BOOKED", "CONFIRMED"])
    booking_channel = random.choice(["WEB", "MOBILE", "PHONE", "WALK_IN"])
    appointment_type = random.choice(["NEW", "FOLLOW_UP", "CHECKUP"])
    confirmation_number = f"APT{int(time.time() * 1000)}"

    cur.execute("""
        INSERT INTO appointment (
            confirmation_number,
            slot_id,
            doctor_id,
            patient_id,
            status,
            booking_channel,
            appointment_type,
            reason_for_visit,
            booked_at,
            created_by,
            updated_by,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, NOW(), NOW())
        RETURNING appointment_id;
    """, (
        confirmation_number,
        slot_id,
        doctor_id,
        patient_id,
        status,
        booking_channel,
        appointment_type,
        fake.sentence(nb_words=6),
        "python_generator",
        "python_generator"
    ))

    appointment_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO appointment_status_history (
            appointment_id,
            old_status,
            new_status,
            changed_at,
            changed_by,
            reason
        )
        VALUES (%s, %s, %s, NOW(), %s, %s);
    """, (
        appointment_id,
        None,
        status,
        "python_generator",
        "Initial generated status"
    ))

    cur.execute("""
        UPDATE doctor_slot
        SET slot_status = 'BOOKED',
            updated_at = NOW()
        WHERE slot_id = %s;
    """, (slot_id,))

    print(f"[INSERT] appointment_id={appointment_id}, status={status}")


def get_random_active_appointment(cur):
    cur.execute("""
        SELECT appointment_id, patient_id, doctor_id, status, slot_id
        FROM appointment
        WHERE status IN ('BOOKED', 'CONFIRMED')
        ORDER BY random()
        LIMIT 1;
    """)
    return cur.fetchone()


def progress_appointment(cur):
    row = get_random_active_appointment(cur)
    if not row:
        print("No active appointment to update.")
        return

    appointment_id, patient_id, doctor_id, old_status, slot_id = row

    if old_status == "BOOKED":
        new_status = random.choice(["CONFIRMED", "CANCELLED"])
    else:
        new_status = random.choice(["COMPLETED", "NO_SHOW", "CANCELLED"])

    cur.execute("""
        UPDATE appointment
        SET status = %s,
            cancelled_at = CASE WHEN %s = 'CANCELLED' THEN NOW() ELSE cancelled_at END,
            completed_at = CASE WHEN %s = 'COMPLETED' THEN NOW() ELSE completed_at END,
            cancel_reason = CASE WHEN %s = 'CANCELLED' THEN %s ELSE cancel_reason END,
            updated_by = %s,
            updated_at = NOW()
        WHERE appointment_id = %s;
    """, (
        new_status,
        new_status,
        new_status,
        new_status,
        "Auto generated cancel reason",
        "python_generator",
        appointment_id
    ))

    cur.execute("""
        INSERT INTO appointment_status_history (
            appointment_id,
            old_status,
            new_status,
            changed_at,
            changed_by,
            reason
        )
        VALUES (%s, %s, %s, NOW(), %s, %s);
    """, (
        appointment_id,
        old_status,
        new_status,
        "python_generator",
        "Auto status progression"
    ))

    if new_status == "COMPLETED":
        cur.execute("""
            SELECT 1 FROM payment WHERE appointment_id = %s;
        """, (appointment_id,))
        exists_payment = cur.fetchone()

        if not exists_payment:
            amount_total = round(random.uniform(50, 300), 2)
            amount_covered = round(random.uniform(0, amount_total), 2)
            amount_patient = round(amount_total - amount_covered, 2)

            cur.execute("""
                INSERT INTO payment (
                    appointment_id,
                    amount_total,
                    amount_covered,
                    amount_patient_responsibility,
                    paid_datetime,
                    payment_status,
                    payment_method,
                    transaction_reference,
                    currency,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s, NOW(), NOW());
            """, (
                appointment_id,
                amount_total,
                amount_covered,
                amount_patient,
                "PAID",
                random.choice(["CASH", "CARD", "BANK_TRANSFER", "INSURANCE"]),
                f"TXN{int(time.time() * 1000)}",
                "USD"
            ))

        cur.execute("""
            SELECT 1 FROM medical_record WHERE appointment_id = %s;
        """, (appointment_id,))
        exists_record = cur.fetchone()

        if not exists_record:
            cur.execute("""
                INSERT INTO medical_record (
                    appointment_id,
                    patient_id,
                    doctor_id,
                    version_number,
                    diagnosis_note,
                    prescription_note,
                    lab_summary,
                    follow_up_instruction,
                    record_status,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, 1, %s, %s, %s, %s, %s, NOW(), NOW());
            """, (
                appointment_id,
                patient_id,
                doctor_id,
                fake.sentence(nb_words=8),
                fake.sentence(nb_words=10),
                fake.sentence(nb_words=7),
                "Follow up after 2 weeks",
                random.choice(["DRAFT", "FINAL", "AMENDED"])
            ))

        cur.execute("""
            UPDATE doctor_slot
            SET slot_status = 'BOOKED',
                updated_at = NOW()
            WHERE slot_id = %s;
        """, (slot_id,))

    elif new_status == "CANCELLED":
        cur.execute("""
            UPDATE doctor_slot
            SET slot_status = 'AVAILABLE',
                updated_at = NOW()
            WHERE slot_id = %s;
        """, (slot_id,))

    print(f"[UPDATE] appointment_id={appointment_id}, {old_status} -> {new_status}")


def main():
    while True:
        conn = None
        try:
            conn = get_connection()
            conn.autocommit = False
            cur = conn.cursor()

            action = random.choice(["insert", "update", "insert", "update", "insert"])

            if action == "insert":
                create_appointment(cur)
            else:
                progress_appointment(cur)

            conn.commit()
            cur.close()

        except Exception as e:
            if conn:
                conn.rollback()
            print("Error:", e)

        finally:
            if conn:
                conn.close()

        time.sleep(random.randint(2, 5))


if __name__ == "__main__":
    main()