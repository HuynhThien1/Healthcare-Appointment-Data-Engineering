from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

from spark_jobs.common.clickhouse_writer import write_to_clickhouse
from spark_jobs.common.stream_table_configs import TABLE_CONFIGS
from spark_jobs.common.stream_utils import build_cdc_dataframe

KAFKA_BOOTSTRAP = "broker:29092"

CLICKHOUSE_JDBC_URL = "jdbc:clickhouse://clickhouse:8123/healthcare_dw"
CLICKHOUSE_PROPERTIES = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "app_user",
    "password": "clickhousepassword",
}


def make_batch_writer(table_name: str, pk: str):
    def debug_and_write(batch_df, batch_id):
        total_rows = batch_df.count()
        print(f"[table={table_name}][batch_id={batch_id}] total rows before write = {total_rows}")

        if total_rows == 0:
            print(f"[table={table_name}][batch_id={batch_id}] empty batch, skip write")
            return

        print(f"[table={table_name}][batch_id={batch_id}] preview batch data:")
        batch_df.show(truncate=False)

        null_pk_df = batch_df.filter(col(pk).isNull())
        null_pk_count = null_pk_df.count()
        print(f"[table={table_name}][batch_id={batch_id}] rows with null {pk} = {null_pk_count}")

        if null_pk_count > 0:
            print(f"[table={table_name}][batch_id={batch_id}] preview rows with null {pk}:")
            null_pk_df.show(truncate=False)

        clean_df = batch_df.filter(col(pk).isNotNull())
        clean_count = clean_df.count()
        print(f"[table={table_name}][batch_id={batch_id}] rows after filtering {pk} not null = {clean_count}")

        if clean_count == 0:
            print(f"[table={table_name}][batch_id={batch_id}] no valid rows to write, skip ClickHouse")
            return

        final_df = clean_df.withColumn("dw_batch_id", lit(int(batch_id)))

        write_to_clickhouse(
            batch_df=final_df,
            batch_id=batch_id,
            table_name=table_name,
            jdbc_url=CLICKHOUSE_JDBC_URL,
            properties=CLICKHOUSE_PROPERTIES,
        )

        print(f"[table={table_name}][batch_id={batch_id}] write to ClickHouse completed")

    return debug_and_write


def create_stream_query(spark: SparkSession, config: dict):
    raw_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", config["topic"])
        .option("startingOffsets", "earliest")
        .load()
    )

    transformed_df = build_cdc_dataframe(
        raw_df=raw_df,
        debezium_schema=config["schema"],
        columns=config["columns"],
    ).filter(col(config["pk"]).isNotNull())

    query = (
        transformed_df.writeStream
        .outputMode("append")
        .foreachBatch(make_batch_writer(config["target_table"], config["pk"]))
        .option("checkpointLocation", config["checkpoint"])
        .start()
    )

    return query


def main():
    spark = (
        SparkSession.builder
        .appName("stream_all_cdc_to_staging")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    queries = []
    for config in TABLE_CONFIGS:
        print(f"Starting stream for topic={config['topic']} -> table={config['target_table']}")
        query = create_stream_query(spark, config)
        queries.append(query)

    for query in queries:
        query.awaitTermination()


if __name__ == "__main__":
    main()