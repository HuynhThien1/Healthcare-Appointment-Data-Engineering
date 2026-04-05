CREATE TABLE IF NOT EXISTS {db}.stg_slot_code_template (
    slot_code String,
    start_time String,
    end_time String,
    display_order Nullable(Int32),
    op String,
    is_deleted UInt8,
    cdc_ts Nullable(DateTime64(3)),
    dw_ingested_at DateTime,
    dw_batch_id UInt64
) ENGINE = ReplacingMergeTree(dw_ingested_at)
ORDER BY (slot_code, dw_ingested_at);