CREATE TABLE IF NOT EXISTS {db}.dim_slot_code (
    slot_code String,
    start_time String,
    end_time String,
    display_order Nullable(Int32),
    is_deleted UInt8,
    dw_updated_at DateTime
)
ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY slot_code;