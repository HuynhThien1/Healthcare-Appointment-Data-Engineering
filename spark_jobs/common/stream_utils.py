from pyspark.sql.functions import (
    col,
    from_json,
    coalesce,
    current_timestamp,
    lit,
    when,
    to_timestamp,
    from_unixtime,
    expr,
    date_add,
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
        base_col = coalesce(
            col(f"json_data.payload.after.{column_name}"),
            col(f"json_data.payload.before.{column_name}")
        )

        # PostgreSQL DATE via Debezium -> days since epoch
        if column_name in ["date_of_birth", "slot_date", "start_working_date"]:
            select_exprs.append(
                date_add(expr("DATE '1970-01-01'"), base_col.cast("int")).alias(column_name)
            )

        # PostgreSQL TIMESTAMP via Debezium -> microseconds since epoch
        elif column_name in ["created_at", "updated_at", "booked_at"]:
            select_exprs.append(
                to_timestamp(from_unixtime(base_col.cast("double") / lit(1000000))).alias(column_name)
            )

        else:
            select_exprs.append(base_col.alias(column_name))

    select_exprs.extend([
        col("json_data.payload.op").alias("op"),
        when(col("json_data.payload.op") == lit("d"), lit(1)).otherwise(lit(0)).alias("is_deleted"),

        # Debezium envelope ts_ms is milliseconds
        to_timestamp(from_unixtime(col("json_data.payload.ts_ms").cast("double") / lit(1000))).alias("cdc_ts"),

        current_timestamp().alias("dw_ingested_at"),
    ])

    return parsed_df.select(*select_exprs)


