CREATE DATABASE IF NOT EXISTS healthcare_dw;

CREATE TABLE IF NOT EXISTS healthcare_dw.ods_doctor_cdc
(
    kafka_key String,
    topic String,
    partition Int32,
    offset Int64,
    kafka_timestamp DateTime,
    op String,
    event_ts_ms Int64,
    doctor_id Int32,
    doctor_code String,
    doctor_name String,
    specialty String,
    phone_number String,
    email String,
    employment_status String,
    clinic_id Int32,
    start_working_date String,
    created_at DateTime,
    updated_at DateTime,
    dw_ingested_at DateTime
)
ENGINE = MergeTree
ORDER BY (doctor_id, offset);