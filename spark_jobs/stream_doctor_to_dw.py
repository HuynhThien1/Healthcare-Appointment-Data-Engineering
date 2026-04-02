from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, coalesce, current_timestamp, lit, when

from spark_jobs.common.schemas import debezium_doctor_schema
from spark_jobs.common.clickhouse_writer import write_to_clickhouse

KAFKA_BOOTSTRAP = "broker:29092"
TOPIC = "healthcare.public.doctor"

CLICKHOUSE_JDBC_URL = "jdbc:clickhouse://clickhouse:8123/healthcare_dw"
CLICKHOUSE_PROPERTIES = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "app_user",
    "password": "clickhousepassword",
}

def debug_and_write(batch_df, batch_id):
    total_rows = batch_df.count()
    print(f"[batch_id={batch_id}] total rows before write = {total_rows}")

    if total_rows == 0:
        print(f"[batch_id={batch_id}] empty batch, skip write")
        return

    print(f"[batch_id={batch_id}] preview batch data:")
    batch_df.show(truncate=False)

    null_doctor_df = batch_df.filter(col("doctor_id").isNull())
    null_doctor_count = null_doctor_df.count()
    print(f"[batch_id={batch_id}] rows with null doctor_id = {null_doctor_count}")

    if null_doctor_count > 0:
        print(f"[batch_id={batch_id}] preview rows with null doctor_id:")
        null_doctor_df.show(truncate=False)

    clean_df = batch_df.filter(col("doctor_id").isNotNull())
    clean_count = clean_df.count()
    print(f"[batch_id={batch_id}] rows after filtering doctor_id not null = {clean_count}")

    if clean_count == 0:
        print(f"[batch_id={batch_id}] no valid rows to write, skip ClickHouse")
        return

    write_to_clickhouse(
        batch_df=clean_df,
        batch_id=batch_id,
        table_name="dim_doctor",
        jdbc_url=CLICKHOUSE_JDBC_URL,
        properties=CLICKHOUSE_PROPERTIES,
    )

    print(f"[batch_id={batch_id}] write to ClickHouse completed")


def main():
    spark = (
        SparkSession.builder
        .appName("stream_doctor_to_dw")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    raw_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .load()
    )

    parsed_df = (
        raw_df
        .selectExpr("CAST(value AS STRING) AS kafka_value")
        .filter(col("kafka_value").isNotNull())
        .withColumn("json_data", from_json(col("kafka_value"), debezium_doctor_schema))
        .filter(col("json_data").isNotNull())
        .filter(col("json_data.payload").isNotNull())
    )

    transformed_df = (
        parsed_df
        .select(
            coalesce(
                col("json_data.payload.after.doctor_id"),
                col("json_data.payload.before.doctor_id")
            ).alias("doctor_id"),
            coalesce(
                col("json_data.payload.after.doctor_code"),
                col("json_data.payload.before.doctor_code")
            ).alias("doctor_code"),
            coalesce(
                col("json_data.payload.after.doctor_name"),
                col("json_data.payload.before.doctor_name")
            ).alias("doctor_name"),
            coalesce(
                col("json_data.payload.after.specialty"),
                col("json_data.payload.before.specialty")
            ).alias("specialty"),
            coalesce(
                col("json_data.payload.after.employment_status"),
                col("json_data.payload.before.employment_status")
            ).alias("employment_status"),
            when(col("json_data.payload.op") == lit("d"), lit(1)).otherwise(lit(0)).alias("is_deleted"),
            col("json_data.payload.op").alias("op"),
            current_timestamp().alias("dw_updated_at"),
        )
        .filter(col("doctor_id").isNotNull())
    )

    query = (
        transformed_df.writeStream
        .outputMode("append")
        .foreachBatch(debug_and_write)
        .option("checkpointLocation", "/tmp/checkpoints/stream_doctor_to_dw")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()