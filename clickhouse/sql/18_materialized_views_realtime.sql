-- =========================
-- DIMENSION TABLES
-- =========================

CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_dim_doctor
TO {db}.dim_doctor
AS
SELECT
    doctor_id,
    doctor_name,
    specialty,
    start_working_date,
    is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_doctor;


CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_dim_patient
TO {db}.dim_patient
AS
SELECT
    patient_id,
    patient_name,
    gender,
    date_of_birth,
    insurance_number,
    email,
    phone_number,
    is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_patient;


CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_dim_slot_code
TO {db}.dim_slot_code
AS
SELECT
    slot_code,
    start_time,
    end_time,
    display_order,
    is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_slot_code_template;


CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_dim_doctor_slot
TO {db}.dim_doctor_slot
AS
SELECT
    slot_id,
    doctor_id,
    slot_date,
    slot_code,
    slot_status,
    is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_doctor_slot;


-- =========================
-- FACT TABLES
-- =========================

-- appointment → JOIN slot
CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_fact_appointment
TO {db}.fact_appointment
AS
SELECT
    a.appointment_id,
    a.booking_ref,
    a.slot_id,
    s.doctor_id,
    a.patient_id,
    s.slot_date,
    s.slot_code,
    a.booked_at,
    1 AS appointment_count,
    a.is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_appointment a
LEFT JOIN {db}.stg_doctor_slot s
    ON a.slot_id = s.slot_id;


-- appointment_transaction → JOIN slot
CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_fact_appointment_transaction
TO {db}.fact_appointment_transaction
AS
SELECT
    t.transaction_id,
    t.slot_id,
    s.doctor_id,
    t.patient_id,
    s.slot_date,
    s.slot_code,
    t.action,
    t.created_at,
    1 AS event_count,
    if(t.action = 'BOOKED', 1, 0) AS is_booked_event,
    if(t.action = 'CONFIRMED', 1, 0) AS is_confirmed_event,
    if(t.action = 'CANCELLED', 1, 0) AS is_cancelled_event,
    if(t.action = 'COMPLETED', 1, 0) AS is_completed_event,
    if(t.action = 'NO_SHOW', 1, 0) AS is_no_show_event,
    t.is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_appointment_transaction t
LEFT JOIN {db}.stg_doctor_slot s
    ON t.slot_id = s.slot_id;


-- slot_daily (no join needed)
CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_fact_slot_daily
TO {db}.fact_slot_daily
AS
SELECT
    slot_id,
    doctor_id,
    slot_date,
    slot_code,
    slot_status,
    1 AS slot_count,
    if(slot_status = 'AVAILABLE', 1, 0) AS is_available,
    if(slot_status = 'BOOKED', 1, 0) AS is_booked,
    if(slot_status = 'BLOCKED', 1, 0) AS is_blocked,
    if(slot_status = 'CANCELLED', 1, 0) AS is_cancelled,
    is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_doctor_slot;


-- medical_record → JOIN slot (FIX CUỐI)
CREATE MATERIALIZED VIEW IF NOT EXISTS {db}.mv_fact_medical_record
TO {db}.fact_medical_record
AS
SELECT
    m.record_id,
    m.slot_id,
    s.doctor_id,
    m.patient_id,
    s.slot_date,
    s.slot_code,
    m.version_number,
    m.diagnosis_note,
    m.prescription_note,
    1 AS record_count,
    m.is_deleted,
    now() AS dw_updated_at
FROM {db}.stg_medical_record m
LEFT JOIN {db}.stg_doctor_slot s
    ON m.slot_id = s.slot_id;