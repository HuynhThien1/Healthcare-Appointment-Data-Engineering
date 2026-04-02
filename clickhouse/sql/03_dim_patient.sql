CREATE TABLE IF NOT EXISTS healthcare_dw.dim_patient
(
    patient_id UInt64,
    patient_code String,
    patient_name String,
    gender String,
    patient_status String,
    is_deleted UInt8 DEFAULT 0,
    op String,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY patient_id;