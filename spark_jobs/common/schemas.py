from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, IntegerType, TimestampType
)

doctor_after_schema = StructType([
    StructField("doctor_id", LongType(), True),
    StructField("doctor_code", StringType(), True),
    StructField("doctor_name", StringType(), True),
    StructField("specialty", StringType(), True),
    StructField("employment_status", StringType(), True),
])

debezium_doctor_schema = StructType([
    StructField("before", doctor_after_schema, True),
    StructField("after", doctor_after_schema, True),
    StructField("op", StringType(), True),
    StructField("ts_ms", LongType(), True),
])