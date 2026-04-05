from pyspark.sql.functions import (
    col,
    from_json,
    coalesce,
    current_timestamp,
    lit,
    when,
)


def build_cdc_dataframe(raw_df, debezium_schema, columns):
    parsed_df = (
        raw_df
        .selectExpr("CAST(value AS STRING) AS kafka_value")
        .filter(col("kafka_value").isNotNull())
        .withColumn("json_data", from_json(col("kafka_value"), debezium_schema))
        .filter(col("json_data").isNotNull())
        .filter(col("json_data.payload").isNotNull())
    )

    select_exprs = []

    for column_name in columns:
        select_exprs.append(
            coalesce(
                col(f"json_data.payload.after.{column_name}"),
                col(f"json_data.payload.before.{column_name}")
            ).alias(column_name)
        )

    select_exprs.extend([
        col("json_data.payload.op").alias("op"),
        when(col("json_data.payload.op") == lit("d"), lit(1)).otherwise(lit(0)).alias("is_deleted"),
        current_timestamp().alias("dw_ingested_at"),
    ])

    return parsed_df.select(*select_exprs)