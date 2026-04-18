import json
import smtplib
from email.mime.text import MIMEText

import psycopg2
from kafka import KafkaConsumer
from clickhouse_driver import Client
from app.db import get_app_connection

from datetime import datetime

from app.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    APP_DB_CONFIG,
    CLICKHOUSE_HOST,
    CLICKHOUSE_NATIVE_PORT,
    CLICKHOUSE_DB,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
    TOPIC_NOTIFICATION_BOOKING_EVENT,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    SMTP_FROM,
)



def get_clickhouse_client():
    return Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_NATIVE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB,
    )



def already_sent(ch_client, notification_key: str) -> bool:
    query = """
        SELECT count()
        FROM fact_notification_audit
        WHERE notification_key = %(notification_key)s
          AND send_status = 'SENT'
    """
    result = ch_client.execute(query, {"notification_key": notification_key})
    return result[0][0] > 0

def parse_event_time(event_time_value):
    if isinstance(event_time_value, datetime):
        return event_time_value

    if event_time_value is None:
        raise ValueError("event_time is None")

    s = str(event_time_value).strip()

    # hỗ trợ ISO có T và Z
    s = s.replace("T", " ").replace("Z", "")

    # thử nhiều format
    fmts = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    # fallback cho fromisoformat
    return datetime.fromisoformat(s)

def write_audit(ch_client, event: dict, send_status: str, error_message: str = "", mark_sent: bool = False):
    insert_sql = """
        INSERT INTO fact_notification_audit
        (
            notification_key,
            transaction_id,
            slot_id,
            patient_id,
            action,
            event_type,
            event_time,
            channel,
            send_status,
            error_message,
            processed_at,
            sent_at
        )
        VALUES
    """

    event_time_dt = parse_event_time(event.get("event_time"))
    processed_at_dt = datetime.now()
    sent_at_dt = datetime.now() if mark_sent else None

    rows = [(
        event["notification_key"],
        event["transaction_id"],
        event["slot_id"],
        int(event["patient_id"]),
        event["action"],
        event["event_type"],
        event_time_dt,
        event["channel"],
        send_status,
        error_message,
        processed_at_dt,
        sent_at_dt,
    )]

    print("AUDIT DEBUG:", event.get("event_time"), type(event.get("event_time")), event_time_dt, type(event_time_dt))

    ch_client.execute(insert_sql, rows)

def fetch_booking_details(pg_conn, patient_id, slot_id):
    sql = """
        SELECT
            p.patient_name,
            p.email,
            ds.slot_date,
            ds.slot_code,
            d.doctor_name,
            d.specialty
        FROM patient p
        JOIN doctor_slot ds
          ON ds.slot_id = %s
        JOIN doctor d
          ON d.doctor_id = ds.doctor_id
        WHERE p.patient_id = %s
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql, (slot_id, patient_id))
        return cur.fetchone()


def build_subject(event_type: str) -> str:
    if event_type == "BOOKING_CONFIRMATION":
        return "Booking Confirmation"
    if event_type == "BOOKING_CANCELLATION":
        return "Booking Cancellation"
    return "Appointment Notification"

def build_body(event_type, patient_name, slot_date, slot_code, doctor_name, specialty):
    if event_type == "BOOKING_CONFIRMATION":
        return f"""Dear {patient_name},

Your appointment has been booked successfully.

Doctor: {doctor_name}
Specialty: {specialty}
Date: {slot_date}
Slot: {slot_code}

Thank you.
"""
    return f"""Dear {patient_name},

Your appointment has been cancelled.

Doctor: {doctor_name}
Specialty: {specialty}
Date: {slot_date}
Slot: {slot_code}

Thank you.
"""


def send_email(to_email: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("Missing SMTP_USER / SMTP_PASS in .env")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, [to_email], msg.as_string())


def main():
    consumer = KafkaConsumer(
        TOPIC_NOTIFICATION_BOOKING_EVENT,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="notification-service-group",
    )

    ch_client = get_clickhouse_client()

    for message in consumer:
        event = message.value
        notification_key = event["notification_key"]

        try:
            if already_sent(ch_client, notification_key):
                print(f"SKIP duplicate notification: {notification_key}")
                continue

            pg_conn = get_app_connection()
            try:
                booking = fetch_booking_details(
                    pg_conn,
                    patient_id=event["patient_id"],
                    slot_id=event["slot_id"],
                )
            finally:
                pg_conn.close()

            if not booking:
                raise RuntimeError("Cannot find booking details for notification")

            patient_name, email, slot_date, slot_code, doctor_name, specialty = booking

            if not email:
                raise RuntimeError("Patient email is null")

            subject = build_subject(event["event_type"])
            body = build_body(
                event["event_type"],
                patient_name,
                slot_date,
                slot_code,
                doctor_name,
                specialty,
            )

            write_audit(ch_client, event, send_status="PENDING", error_message="", mark_sent=False)
            send_email(email, subject, body)
            write_audit(ch_client, event, send_status="SENT", error_message="", mark_sent=True)

            print(f"SENT notification: {notification_key}")

        except Exception as exc:
            write_audit(ch_client, event, send_status="FAILED", error_message=str(exc), mark_sent=False)
            print(f"FAILED notification: {notification_key} - {exc}")


if __name__ == "__main__":
    main()