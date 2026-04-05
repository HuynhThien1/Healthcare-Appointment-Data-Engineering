CREATE TABLE IF NOT EXISTS {db}.fact_slot_daily (
    slot_id String,
    doctor_id String,
    slot_date Nullable(Date),
    slot_code String,
    slot_status String,
    slot_count Int32,
    is_available Int32,
    is_booked Int32,
    is_blocked Int32,
    is_cancelled Int32,
    is_deleted UInt8,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY slot_id;