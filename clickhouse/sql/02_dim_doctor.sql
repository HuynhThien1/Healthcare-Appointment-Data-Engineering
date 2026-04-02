CREATE TABLE IF NOT EXISTS healthcare_dw.dim_doctor
(
    doctor_id UInt64,
    doctor_code String,
    doctor_name String,
    specialty String,
    employment_status String,
    is_deleted UInt8 DEFAULT 0,
    op String,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY doctor_id;