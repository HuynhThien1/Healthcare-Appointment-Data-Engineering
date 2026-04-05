CREATE TABLE IF NOT EXISTS {db}.fact_medical_record (
    record_id String,
    slot_id String,
    doctor_id String,
    patient_id Int32,
    slot_date Nullable(Date),
    slot_code String,
    version_number Int32,
    diagnosis_note String,
    prescription_note String,
    record_count Int32,
    is_deleted UInt8,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY record_id;