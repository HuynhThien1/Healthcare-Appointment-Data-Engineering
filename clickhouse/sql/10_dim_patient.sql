CREATE TABLE IF NOT EXISTS {db}.dim_patient (
    patient_id Int32,
    patient_name String,
    gender String,
    date_of_birth Nullable(Date32),
    insurance_number String,
    email String,
    phone_number String,
    is_deleted UInt8,
    dw_updated_at DateTime
) ENGINE = ReplacingMergeTree(dw_updated_at)
ORDER BY patient_id;