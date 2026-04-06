CREATE VIEW IF NOT EXISTS {db}.vw_fact_appointment_current AS
SELECT *
FROM (
    SELECT
        appointment_id,
        argMax(booking_ref, dw_updated_at) AS booking_ref,
        argMax(slot_id, dw_updated_at) AS slot_id,
        argMax(doctor_id, dw_updated_at) AS doctor_id,
        argMax(patient_id, dw_updated_at) AS patient_id,
        argMax(slot_date, dw_updated_at) AS slot_date,
        argMax(slot_code, dw_updated_at) AS slot_code,
        argMax(booked_at, dw_updated_at) AS booked_at,
        argMax(appointment_count, dw_updated_at) AS appointment_count,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.fact_appointment
    GROUP BY appointment_id
) t
WHERE is_deleted = 0;


CREATE VIEW IF NOT EXISTS {db}.vw_fact_slot_daily_current AS
SELECT *
FROM (
    SELECT
        slot_id,
        argMax(doctor_id, dw_updated_at) AS doctor_id,
        argMax(slot_date, dw_updated_at) AS slot_date,
        argMax(slot_code, dw_updated_at) AS slot_code,
        argMax(slot_status, dw_updated_at) AS slot_status,
        argMax(slot_count, dw_updated_at) AS slot_count,
        argMax(is_available, dw_updated_at) AS is_available,
        argMax(is_booked, dw_updated_at) AS is_booked,
        argMax(is_blocked, dw_updated_at) AS is_blocked,
        argMax(is_cancelled, dw_updated_at) AS is_cancelled,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.fact_slot_daily
    GROUP BY slot_id
) t
WHERE is_deleted = 0;


CREATE VIEW IF NOT EXISTS {db}.vw_fact_medical_record_current AS
SELECT *
FROM (
    SELECT
        record_id,
        argMax(slot_id, dw_updated_at) AS slot_id,
        argMax(doctor_id, dw_updated_at) AS doctor_id,
        argMax(patient_id, dw_updated_at) AS patient_id,
        argMax(slot_date, dw_updated_at) AS slot_date,
        argMax(slot_code, dw_updated_at) AS slot_code,
        argMax(version_number, dw_updated_at) AS version_number,
        argMax(diagnosis_note, dw_updated_at) AS diagnosis_note,
        argMax(prescription_note, dw_updated_at) AS prescription_note,
        argMax(record_count, dw_updated_at) AS record_count,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.fact_medical_record
    GROUP BY record_id
) t
WHERE is_deleted = 0;