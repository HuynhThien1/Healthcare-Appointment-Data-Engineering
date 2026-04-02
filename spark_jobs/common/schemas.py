from pyspark.sql.types import (
    StructType, StructField, StringType, LongType
)

doctor_row_schema = StructType([
    StructField("doctor_id", LongType(), True),
    StructField("doctor_code", StringType(), True),
    StructField("doctor_name", StringType(), True),
    StructField("specialty", StringType(), True),
    StructField("phone_number", StringType(), True),
    StructField("email", StringType(), True),
    StructField("employment_status", StringType(), True),
    StructField("clinic_id", LongType(), True),
    StructField("start_working_date", LongType(), True),
    StructField("created_at", LongType(), True),
    StructField("updated_at", LongType(), True),
])

payload_schema = StructType([
    StructField("before", doctor_row_schema, True),
    StructField("after", doctor_row_schema, True),
    StructField("op", StringType(), True),
    StructField("ts_ms", LongType(), True),
])

debezium_doctor_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", payload_schema, True),
])