CREATE TABLE IF NOT EXISTS {db}.stg_appointment (
    appointment_id Int32,
    booking_ref String,
    slot_id String,
    patient_id Int32,
    booked_at Nullable(DateTime),
    op String,
    is_deleted UInt8,
    cdc_ts Nullable(DateTime64(3)),
    dw_ingested_at DateTime,
    dw_batch_id UInt64
) ENGINE = ReplacingMergeTree(dw_ingested_at)
ORDER BY (appointment_id, dw_ingested_at);