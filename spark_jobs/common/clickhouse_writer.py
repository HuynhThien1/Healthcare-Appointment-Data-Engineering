def write_to_clickhouse(batch_df, batch_id, table_name, jdbc_url, properties):
    if batch_df.rdd.isEmpty():
        print(f"[batch_id={batch_id}] empty batch, skip write")
        return

    batch_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", table_name) \
        .options(**properties) \
        .mode("append") \
        .save()

    print(f"[batch_id={batch_id}] wrote data to {table_name}")