CREATE TABLE IF NOT EXISTS {db}.fact_appointment (
    appointment_id Int32,
    booking_ref String,
    slot_id String,
    doctor_id String,
    patient_id Int32,
    slot_date Nullable(Date),
    slot_code String,
    booked_at Nullable(DateTime),
    appointment_count Int32,
    is_deleted UInt8,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY appointment_id;