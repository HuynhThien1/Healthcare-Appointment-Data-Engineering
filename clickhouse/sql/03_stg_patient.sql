CREATE TABLE IF NOT EXISTS {db}.stg_patient (
    patient_id Int32,
    patient_name String,
    address String,
    phone_number String,
    insurance_number String,
    date_of_birth Nullable(Date32),
    gender String,
    email String,
    created_at Nullable(DateTime),
    updated_at Nullable(DateTime),
    op String,
    is_deleted UInt8,
    cdc_ts Nullable(DateTime64(3)),
    dw_ingested_at DateTime,
    dw_batch_id UInt64
) ENGINE = ReplacingMergeTree(dw_ingested_at)
ORDER BY (patient_id, dw_ingested_at);