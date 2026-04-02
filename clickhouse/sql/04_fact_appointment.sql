CREATE TABLE IF NOT EXISTS healthcare_dw.fact_appointment
(
    appointment_id UInt64,
    patient_id UInt64,
    doctor_id UInt64,
    slot_id UInt64,
    confirmation_number String,
    status String,
    booking_channel String,
    appointment_type String,
    appointment_date Date,
    booked_at DateTime,
    cancelled_at Nullable(DateTime),
    completed_at Nullable(DateTime),
    is_cancelled UInt8,
    is_completed UInt8,
    is_no_show UInt8,
    op String,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY appointment_id;