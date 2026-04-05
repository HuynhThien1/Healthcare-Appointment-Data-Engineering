CREATE TABLE IF NOT EXISTS {db}.fact_appointment_transaction (
    transaction_id String,
    slot_id String,
    doctor_id String,
    patient_id Int32,
    slot_date Nullable(Date),
    slot_code String,
    action String,
    created_at Nullable(DateTime),
    event_count Int32,
    is_booked_event Int32,
    is_confirmed_event Int32,
    is_cancelled_event Int32,
    is_completed_event Int32,
    is_no_show_event Int32,
    is_deleted UInt8,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY transaction_id;