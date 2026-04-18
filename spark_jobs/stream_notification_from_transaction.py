from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, to_json, struct, to_timestamp
import os

from spark_jobs.common.schemas import debezium_appointment_transaction_schema
from spark_jobs.common.stream_utils import build_cdc_dataframe
from spark_jobs.common.notification_utils import map_notification_event_type

KAFKA_BOOTSTRAP_SERVERS = "broker:29092"
SOURCE_TOPIC = "healthcare.public.appointment_transaction"
TARGET_TOPIC = "notification.booking_event"


def build_spark():
    spark = (
        SparkSession.builder
        .appName("stream_notification_from_transaction")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    spark = build_spark()

    system_start_time = os.getenv("SYSTEM_START_TIME")
    if system_start_time is None:
        raise RuntimeError("SYSTEM_START_TIME is not set")

    print("SYSTEM_START_TIME =", system_start_time)

    raw_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", SOURCE_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    tx_df = build_cdc_dataframe(
        raw_df=raw_df,
        debezium_schema=debezium_appointment_transaction_schema,
        columns=[
            "transaction_id",
            "slot_id",
            "patient_id",
            "action",
            "created_at"
        ]
    )

    notification_df = (
        tx_df
        .filter(col("is_deleted") == 0)
        .filter(col("action").isin("BOOKED", "CANCELLED"))
        .filter(col("created_at") >= to_timestamp(lit(system_start_time)))
        .withColumn("event_type", map_notification_event_type(col("action")))
        .filter(col("event_type").isNotNull())
        .withColumn("notification_key", col("transaction_id"))
        .withColumn("channel", lit("EMAIL"))
        .withWatermark("cdc_ts", "10 minutes")
        .dropDuplicates(["notification_key"])
    )

    kafka_out_df = (
        notification_df.select(
            col("notification_key").alias("key"),
            to_json(
                struct(
                    "notification_key",
                    "transaction_id",
                    "slot_id",
                    "patient_id",
                    "action",
                    "event_type",
                    col("created_at").alias("event_time"),
                    "channel"
                )
            ).alias("value")
        )
    )

    query = (
        kafka_out_df.writeStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("topic", TARGET_TOPIC)
        .option("checkpointLocation", "/tmp/checkpoints/notification_booking_event")
        .outputMode("append")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()