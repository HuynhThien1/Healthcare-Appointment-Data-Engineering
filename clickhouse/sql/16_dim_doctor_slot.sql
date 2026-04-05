CREATE TABLE IF NOT EXISTS {db}.dim_doctor_slot (
    slot_id String,
    doctor_id String,
    slot_date Nullable(Date),
    slot_code String,
    slot_status String,
    is_deleted UInt8,
    dw_updated_at DateTime
) ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY slot_id;