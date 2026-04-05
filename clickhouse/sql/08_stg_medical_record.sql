CREATE TABLE IF NOT EXISTS {db}.stg_medical_record (
    record_id String,
    slot_id String,
    patient_id Int32,
    version_number Int32,
    diagnosis_note String,
    prescription_note String,
    created_at Nullable(DateTime),
    updated_at Nullable(DateTime),
    op String,
    is_deleted UInt8,
    cdc_ts Nullable(DateTime64(3)),
    dw_ingested_at DateTime,
    dw_batch_id UInt64
) ENGINE = ReplacingMergeTree(dw_ingested_at)
ORDER BY (record_id, dw_ingested_at);