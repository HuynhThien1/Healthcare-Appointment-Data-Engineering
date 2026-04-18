CREATE TABLE IF NOT EXISTS healthcare_dw.fact_notification_audit
(
    notification_key String,
    transaction_id String,
    slot_id String,
    patient_id UInt64,
    action String,
    event_type String,
    event_time DateTime64(3),
    channel String,
    send_status String,              -- PENDING / SENT / FAILED
    error_message String,
    processed_at DateTime64(3),
    sent_at Nullable(DateTime64(3))
)
ENGINE = ReplacingMergeTree(processed_at)
ORDER BY (notification_key, processed_at);