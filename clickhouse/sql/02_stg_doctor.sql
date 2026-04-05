CREATE TABLE IF NOT EXISTS {db}.stg_doctor (
    doctor_id String,
    doctor_name String,
    specialty String,
    start_working_date Nullable(Date),
    op String,
    is_deleted UInt8,
    cdc_ts Nullable(DateTime64(3)),
    dw_ingested_at DateTime,
    dw_batch_id UInt64
) ENGINE = ReplacingMergeTree(dw_ingested_at)
ORDER BY (doctor_id, dw_ingested_at);