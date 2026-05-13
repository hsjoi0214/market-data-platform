"""
Batch Glue transform job.

Learning Surface:
- Cloud
Execution Step:
- 2 of 4 in the cloud batch walkthrough
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, to_date


def get_arg(args, name, default=None):
    """Read one named Glue job argument from `sys.argv`, returning a default when absent."""
    if name in args:
        return args[args.index(name) + 1]
    return default


def main():
    """
    Run the cloud batch transform from raw JSONL in S3 to curated and analytics Parquet.

    Glue intentionally stays transform-only in this project: extraction happens upstream
    in the batch extract Lambda, and querying happens downstream in Glue Catalog/Athena.
    The analytics output is partitioned by symbol/year/month so Athena scans stay more
    targeted than a single flat directory of Parquet files.
    """
    import sys

    raw_input_path = get_arg(sys.argv, "--RAW_INPUT_PATH")
    curated_output_path = get_arg(sys.argv, "--CURATED_OUTPUT_PATH")
    analytics_output_path = get_arg(sys.argv, "--ANALYTICS_OUTPUT_PATH")

    if not raw_input_path or not curated_output_path or not analytics_output_path:
        raise ValueError("Missing one or more required Glue job args")

    spark = SparkSession.builder.appName("batch-ohlc-daily").getOrCreate()

    # Read raw JSONL recursively so Glue can consume nested raw batch runs
    # such as source=alphavantage/mode=incremental/as_of=.../window_days=.../*.jsonl
    df_raw = spark.read.option("recursiveFileLookup", "true").json(raw_input_path)

    # Standardize schema/types
    df_curated = (
        df_raw
        .select(
            col("symbol").cast("string"),
            col("date").cast("string"),
            col("open").cast("double"),
            col("high").cast("double"),
            col("low").cast("double"),
            col("close").cast("double"),
            col("volume").cast("bigint"),
            col("currency").cast("string"),
            col("ts_market").cast("string"),
            col("ts_ingest").cast("string"),
            col("source").cast("string"),
        )
    )

    # Curated output (Parquet)
    (
        df_curated
        .write
        .mode("overwrite")
        .parquet(curated_output_path)
    )

    # Derive partition columns from the daily trading date for OLAP-friendly analytics layout.
    df_analytics = (
        df_curated
        .withColumn("trading_date", to_date(col("date"), "yyyy-MM-dd"))
        .withColumn("year", date_format(col("trading_date"), "yyyy"))
        .withColumn("month", date_format(col("trading_date"), "MM"))
        .drop("trading_date")
    )

    # Analytics output is partitioned by symbol/year/month.
    (
        df_analytics
        .write
        .mode("overwrite")
        .partitionBy("symbol", "year", "month")
        .parquet(analytics_output_path)
    )

    spark.stop()


if __name__ == "__main__":
    main()
