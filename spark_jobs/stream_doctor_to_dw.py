from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, coalesce, current_timestamp, lit, when

from spark_jobs.common.schemas import debezium_doctor_schema
from spark_jobs.common.clickhouse_writer import write_to_clickhouse

KAFKA_BOOTSTRAP = "broker:29092"
TOPIC = "postgres.public.doctor"

CLICKHOUSE_JDBC_URL = "jdbc:clickhouse://clickhouse:8123/healthcare_dw"
CLICKHOUSE_PROPERTIES = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "app_user",
    "password": "clickhousepassword",
}

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

    parsed_df = raw_df.selectExpr("CAST(value AS STRING) AS kafka_value") \
        .withColumn("json_data", from_json(col("kafka_value"), debezium_doctor_schema))

    transformed_df = parsed_df.select(
        coalesce(col("json_data.after.doctor_id"), col("json_data.before.doctor_id")).alias("doctor_id"),
        coalesce(col("json_data.after.doctor_code"), col("json_data.before.doctor_code")).alias("doctor_code"),
        coalesce(col("json_data.after.doctor_name"), col("json_data.before.doctor_name")).alias("doctor_name"),
        coalesce(col("json_data.after.specialty"), col("json_data.before.specialty")).alias("specialty"),
        coalesce(col("json_data.after.employment_status"), col("json_data.before.employment_status")).alias("employment_status"),
        when(col("json_data.op") == lit("d"), lit(1)).otherwise(lit(0)).alias("is_deleted"),
        col("json_data.op").alias("op"),
        current_timestamp().alias("dw_updated_at"),
    )

    query = (
        transformed_df.writeStream
        .outputMode("append")
        .foreachBatch(
            lambda batch_df, batch_id: write_to_clickhouse(
                batch_df=batch_df,
                batch_id=batch_id,
                table_name="dim_doctor",
                jdbc_url=CLICKHOUSE_JDBC_URL,
                properties=CLICKHOUSE_PROPERTIES,
            )
        )
        .option("checkpointLocation", "/tmp/checkpoints/stream_doctor_to_dw")
        .start()
    )

    query.awaitTermination()

if __name__ == "__main__":
    main()