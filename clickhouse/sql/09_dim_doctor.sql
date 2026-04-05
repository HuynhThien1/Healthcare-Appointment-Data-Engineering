CREATE TABLE IF NOT EXISTS {db}.dim_doctor (
    doctor_id String,
    doctor_name String,
    specialty String,
    start_working_date Nullable(Date),
    is_deleted UInt8,
    dw_updated_at DateTime
) ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY doctor_id;