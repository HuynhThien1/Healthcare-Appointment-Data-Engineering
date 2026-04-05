CREATE VIEW IF NOT EXISTS {db}.vw_dim_doctor_current AS
SELECT *
FROM (
    SELECT
        doctor_id,
        argMax(doctor_name, dw_updated_at) AS doctor_name,
        argMax(specialty, dw_updated_at) AS specialty,
        argMax(start_working_date, dw_updated_at) AS start_working_date,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.dim_doctor
    GROUP BY doctor_id
)
WHERE is_deleted = 0;

CREATE VIEW IF NOT EXISTS {db}.vw_dim_patient_current AS
SELECT *
FROM (
    SELECT
        patient_id,
        argMax(patient_name, dw_updated_at) AS patient_name,
        argMax(gender, dw_updated_at) AS gender,
        argMax(date_of_birth, dw_updated_at) AS date_of_birth,
        argMax(insurance_number, dw_updated_at) AS insurance_number,
        argMax(email, dw_updated_at) AS email,
        argMax(phone_number, dw_updated_at) AS phone_number,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.dim_patient
    GROUP BY patient_id
)
WHERE is_deleted = 0;

CREATE VIEW IF NOT EXISTS {db}.vw_dim_slot_code_current AS
SELECT *
FROM (
    SELECT
        slot_code,
        argMax(start_time, dw_updated_at) AS start_time,
        argMax(end_time, dw_updated_at) AS end_time,
        argMax(display_order, dw_updated_at) AS display_order,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.dim_slot_code
    GROUP BY slot_code
)
WHERE is_deleted = 0;

CREATE VIEW IF NOT EXISTS {db}.vw_dim_doctor_slot_current AS
SELECT *
FROM (
    SELECT
        slot_id,
        argMax(doctor_id, dw_updated_at) AS doctor_id,
        argMax(slot_date, dw_updated_at) AS slot_date,
        argMax(slot_code, dw_updated_at) AS slot_code,
        argMax(slot_status, dw_updated_at) AS slot_status,
        argMax(is_deleted, dw_updated_at) AS is_deleted,
        max(dw_updated_at) AS latest_dw_updated_at
    FROM {db}.dim_doctor_slot
    GROUP BY slot_id
)
WHERE is_deleted = 0;