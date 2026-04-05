CREATE TABLE IF NOT EXISTS {db}.stg_doctor_slot (
    slot_id String,
    doctor_id String,
    slot_date Nullable(Date),
    slot_code String,
    slot_status String,
    op String,
    is_deleted UInt8,
    cdc_ts Nullable(DateTime64(3)),
    dw_ingested_at DateTime,
    dw_batch_id UInt64
) ENGINE = ReplacingMergeTree(dw_ingested_at)
ORDER BY (slot_id, dw_ingested_at);