import random
import time
from datetime import datetime

from app.db import get_app_connection


def _get_next_id(cur, table_name: str, id_column: str) -> int:
    # explanation: Vì schema dùng INT PRIMARY KEY thủ công,
    # explanation: nên mỗi lần insert phải tự lấy id kế tiếp.
    cur.execute(f"SELECT COALESCE(MAX({id_column}), 0) + 1 FROM {table_name};")
    return cur.fetchone()[0]


def book_random_appointment():
    # explanation: Tạo một appointment mới từ một slot còn AVAILABLE.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT patient_id FROM patient ORDER BY random() LIMIT 1;")
            patient = cur.fetchone()

            cur.execute(
                """
                SELECT slot_id, doctor_id, start_time
                FROM doctor_slot
                WHERE slot_status = 'AVAILABLE'
                ORDER BY random()
                LIMIT 1;
                """
            )
            slot = cur.fetchone()

            if not patient or not slot:
                print("No patient or available slot found.")
                return

            appointment_id = _get_next_id(cur, "appointment", "appointment_id")
            history_id = _get_next_id(cur, "appointment_status_history", "history_id")

            patient_id = patient[0]
            slot_id, doctor_id, start_time = slot
            now = datetime.now()

            cur.execute(
                """
                INSERT INTO appointment (
                    appointment_id, confirmation_number, slot_id, doctor_id, patient_id,
                    status, booking_channel, appointment_type, reason_for_visit,
                    booked_at, cancelled_at, completed_at, cancel_reason,
                    created_by, updated_by, created_at, updated_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    'BOOKED', %s, %s, %s,
                    %s, NULL, NULL, NULL,
                    'stream_generator', 'stream_generator', %s, %s
                );
                """,
                (
                    appointment_id,
                    f"CONF{appointment_id:06d}",
                    slot_id,
                    doctor_id,
                    patient_id,
                    random.choice(["WEB", "MOBILE", "PHONE", "WALK_IN"]),
                    random.choice(["NEW", "FOLLOW_UP", "CHECKUP"]),
                    f"Generated booking at {now.isoformat()}",
                    now,
                    now,
                    now,
                ),
            )

            cur.execute(
                """
                INSERT INTO appointment_status_history (
                    history_id, appointment_id, old_status, new_status, changed_at,
                    changed_by, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    history_id,
                    appointment_id,
                    None,
                    "BOOKED",
                    now,
                    "stream_generator",
                    "Auto booking event",
                ),
            )

            cur.execute(
                """
                UPDATE doctor_slot
                SET slot_status = 'BOOKED',
                    updated_at = %s
                WHERE slot_id = %s;
                """,
                (now, slot_id),
            )

        conn.commit()
        print(f"Booked appointment_id={appointment_id}, slot_id={slot_id}")
    except Exception as e:
        conn.rollback()
        print(f"book_random_appointment error: {e}")
    finally:
        conn.close()


def confirm_random_appointment():
    # explanation: Đổi trạng thái từ BOOKED sang CONFIRMED.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT appointment_id, status
                FROM appointment
                WHERE status = 'BOOKED'
                ORDER BY random()
                LIMIT 1;
                """
            )
            row = cur.fetchone()

            if not row:
                print("No BOOKED appointment found.")
                return

            appointment_id, old_status = row
            history_id = _get_next_id(cur, "appointment_status_history", "history_id")
            now = datetime.now()

            cur.execute(
                """
                UPDATE appointment
                SET status = 'CONFIRMED',
                    updated_by = 'stream_generator',
                    updated_at = %s
                WHERE appointment_id = %s;
                """,
                (now, appointment_id),
            )

            cur.execute(
                """
                INSERT INTO appointment_status_history (
                    history_id, appointment_id, old_status, new_status, changed_at,
                    changed_by, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    history_id,
                    appointment_id,
                    old_status,
                    "CONFIRMED",
                    now,
                    "stream_generator",
                    "Auto confirm event",
                ),
            )

        conn.commit()
        print(f"Confirmed appointment_id={appointment_id}")
    except Exception as e:
        conn.rollback()
        print(f"confirm_random_appointment error: {e}")
    finally:
        conn.close()


def cancel_random_appointment():
    # explanation: Hủy appointment đang BOOKED hoặc CONFIRMED
    # explanation: và trả slot về AVAILABLE.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT appointment_id, slot_id, status
                FROM appointment
                WHERE status IN ('BOOKED', 'CONFIRMED')
                ORDER BY random()
                LIMIT 1;
                """
            )
            row = cur.fetchone()

            if not row:
                print("No BOOKED/CONFIRMED appointment found.")
                return

            appointment_id, slot_id, old_status = row
            history_id = _get_next_id(cur, "appointment_status_history", "history_id")
            now = datetime.now()

            cur.execute(
                """
                UPDATE appointment
                SET status = 'CANCELLED',
                    cancelled_at = %s,
                    cancel_reason = %s,
                    updated_by = 'stream_generator',
                    updated_at = %s
                WHERE appointment_id = %s;
                """,
                (
                    now,
                    "Auto cancelled by stream generator",
                    now,
                    appointment_id,
                ),
            )

            cur.execute(
                """
                INSERT INTO appointment_status_history (
                    history_id, appointment_id, old_status, new_status, changed_at,
                    changed_by, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    history_id,
                    appointment_id,
                    old_status,
                    "CANCELLED",
                    now,
                    "stream_generator",
                    "Auto cancel event",
                ),
            )

            cur.execute(
                """
                UPDATE doctor_slot
                SET slot_status = 'AVAILABLE',
                    updated_at = %s
                WHERE slot_id = %s;
                """,
                (now, slot_id),
            )

        conn.commit()
        print(f"Cancelled appointment_id={appointment_id}")
    except Exception as e:
        conn.rollback()
        print(f"cancel_random_appointment error: {e}")
    finally:
        conn.close()


def complete_random_appointment():
    # explanation: Hoàn tất một appointment đang CONFIRMED.
    # explanation: Đồng thời tạo payment nếu chưa có và medical_record nếu chưa có.
    conn = get_app_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT appointment_id, patient_id, doctor_id, status
                FROM appointment
                WHERE status = 'CONFIRMED'
                ORDER BY random()
                LIMIT 1;
                """
            )
            row = cur.fetchone()

            if not row:
                print("No CONFIRMED appointment found.")
                return

            appointment_id, patient_id, doctor_id, old_status = row
            history_id = _get_next_id(cur, "appointment_status_history", "history_id")
            now = datetime.now()

            cur.execute(
                """
                UPDATE appointment
                SET status = 'COMPLETED',
                    completed_at = %s,
                    updated_by = 'stream_generator',
                    updated_at = %s
                WHERE appointment_id = %s;
                """,
                (now, now, appointment_id),
            )

            cur.execute(
                """
                INSERT INTO appointment_status_history (
                    history_id, appointment_id, old_status, new_status, changed_at,
                    changed_by, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    history_id,
                    appointment_id,
                    old_status,
                    "COMPLETED",
                    now,
                    "stream_generator",
                    "Auto complete event",
                ),
            )

            cur.execute(
                """
                SELECT 1
                FROM payment
                WHERE appointment_id = %s;
                """,
                (appointment_id,),
            )
            payment_exists = cur.fetchone()

            if not payment_exists:
                payment_id = _get_next_id(cur, "payment", "payment_id")
                amount_total = round(random.uniform(20, 150), 2)
                amount_covered = round(random.uniform(0, amount_total * 0.7), 2)
                amount_patient = round(amount_total - amount_covered, 2)

                cur.execute(
                    """
                    INSERT INTO payment (
                        payment_id, appointment_id, amount_total, amount_covered,
                        amount_patient_responsibility, paid_datetime, payment_status,
                        payment_method, transaction_reference, currency, created_at, updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s
                    );
                    """,
                    (
                        payment_id,
                        appointment_id,
                        amount_total,
                        amount_covered,
                        amount_patient,
                        now,
                        "PAID",
                        random.choice(["CASH", "CARD", "INSURANCE"]),
                        f"TXN{payment_id:06d}",
                        "USD",
                        now,
                        now,
                    ),
                )

            cur.execute(
                """
                SELECT 1
                FROM medical_record
                WHERE appointment_id = %s;
                """,
                (appointment_id,),
            )
            record_exists = cur.fetchone()

            if not record_exists:
                record_id = _get_next_id(cur, "medical_record", "record_id")

                cur.execute(
                    """
                    INSERT INTO medical_record (
                        record_id, appointment_id, patient_id, doctor_id, version_number,
                        diagnosis_note, prescription_note, lab_summary,
                        follow_up_instruction, record_status, created_at, updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s
                    );
                    """,
                    (
                        record_id,
                        appointment_id,
                        patient_id,
                        doctor_id,
                        1,
                        "Generated diagnosis note",
                        "Generated prescription note",
                        "Generated lab summary",
                        "Generated follow-up instruction",
                        "FINAL",
                        now,
                        now,
                    ),
                )

        conn.commit()
        print(f"Completed appointment_id={appointment_id}")
    except Exception as e:
        conn.rollback()
        print(f"complete_random_appointment error: {e}")
    finally:
        conn.close()


def run_stream(interval_seconds: int = 5):
    # explanation: Chạy vòng lặp vô hạn để liên tục tạo CDC events trong database.
    actions = [
        book_random_appointment,
        confirm_random_appointment,
        cancel_random_appointment,
        complete_random_appointment,
    ]

    print("Starting stream generator...")
    while True:
        action = random.choice(actions)
        action()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_stream()