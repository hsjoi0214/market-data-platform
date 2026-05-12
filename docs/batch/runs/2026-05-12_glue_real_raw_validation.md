# Batch Glue Transform - Real Raw Layout Validation

**Date:** 2026-05-12
**Environment:** dev
**Region:** us-east-1
**Glue Job:** mdp-market-data-dev-batch-ohlc-daily
**Glue Job Run ID:** jr_60de712aae10f59e36b17db977468b13fac94ff00e557eb6faaeecf70c2af982
**Athena Query Execution ID:** daf36bc7-87a5-4972-aed7-58d9d9f6e1ef

## What Changed

- Updated the Glue reader to use recursive file lookup.
- This allows Glue to read nested raw objects such as:
  - `raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-12/window_days=10/symbol=AAPL.jsonl`
  - `raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-12/window_days=10/symbol=MSFT.jsonl`

## Glue Result

- Job state: `SUCCEEDED`
- Started: `2026-05-12T11:11:01.864+02:00`
- Completed: `2026-05-12T11:12:41.291+02:00`
- Execution time: `93` seconds

## Output Verification

Parquet files landed in:

- `s3://mdp-market-data-dev-us-east-1-a66798a5/curated/prices_daily/`
- `s3://mdp-market-data-dev-us-east-1-a66798a5/analytics/ohlc_daily/`

Observed output files:

- `curated/prices_daily/part-00000-579d2904-372e-4cc3-9ad1-3601927b1af5-c000.snappy.parquet`
- `curated/prices_daily/part-00001-579d2904-372e-4cc3-9ad1-3601927b1af5-c000.snappy.parquet`
- `curated/prices_daily/part-00002-579d2904-372e-4cc3-9ad1-3601927b1af5-c000.snappy.parquet`
- `curated/prices_daily/part-00003-579d2904-372e-4cc3-9ad1-3601927b1af5-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00000-7b05c5af-9af2-441d-a1a6-e88b6a8cdae7-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00001-7b05c5af-9af2-441d-a1a6-e88b6a8cdae7-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00002-7b05c5af-9af2-441d-a1a6-e88b6a8cdae7-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00003-7b05c5af-9af2-441d-a1a6-e88b6a8cdae7-c000.snappy.parquet`

## Athena Smoke Check

Query:

```sql
SELECT count(*) AS row_count FROM ohlc_daily;
```

Result:

- `row_count = 724`

## Interpretation

- The Glue job successfully reads the new nested Alpha Vantage raw layout.
- The count is `724` because Glue currently reads the full `raw/prices_daily/` history under that root, not just the newest extract slice.
- This is acceptable for the current transform validation step and highlights why partitioning and scoped batch windows are the next improvements.
