# Batch Partitioned Analytics Validation

**Date:** 2026-05-13  
**Environment:** dev  
**Region:** us-east-1

## What Was Validated

- Glue analytics output is now partitioned by:
  - `symbol`
  - `year`
  - `month`
- Glue Catalog table was updated with matching partition keys
- Athena was repaired and queried successfully against the partitioned layout

## Manual Batch Run

### Batch Extract Lambda

- Lambda: `mdp-market-data-dev-batch-extract`
- Response:
  - `mode = incremental`
  - `symbols = [AAPL, MSFT]`
  - `as_of = 2026-05-13`
  - `rows_written = 20`
  - `objects_written = 2`

Raw objects written:

- `raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-13/window_days=10/symbol=AAPL.jsonl`
- `raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-13/window_days=10/symbol=MSFT.jsonl`

### Glue Job

- Job: `mdp-market-data-dev-batch-ohlc-daily`
- JobRunId: `jr_e80b1f9de6d3187b20a1734de4fb0696d953a45647180eecf5bb34d8db84d274`
- Result: `SUCCEEDED`
- Execution time: `57` seconds

## S3 Partition Verification

Observed output paths under `analytics/ohlc_daily/`:

- `symbol=AAPL/year=2025/month=03/`
- `symbol=AAPL/year=2026/month=05/`
- `symbol=MSFT/year=2025/month=03/`

This confirms that the analytics dataset is landing in partitioned layout rather than a flat folder.

## Athena Validation

### Partition Repair

- QueryExecutionId: `9456a670-14a1-40a8-abf4-0c72d7197afa`
- Query:

```sql
MSCK REPAIR TABLE ohlc_daily;
```

### Count Query

- QueryExecutionId: `7ca5e555-76b4-4ff4-a30e-629896cad440`
- Result:
  - `row_count = 744`

### Limit Query

- QueryExecutionId: `08b856e8-7b2b-4250-9751-9827159d7c36`
- Sample rows returned successfully from:
  - `symbol = AAPL`
  - `year = 2026`
  - `month = 05`

### Filter Query

- QueryExecutionId: `3dd06c74-b9f2-4f3d-9eae-d5b447754b29`
- Result:
  - `aapl_rows = 372`

### Aggregation Query

- QueryExecutionId: `c34cbecf-c343-4d9d-a6b6-2b132abf3951`
- Query grouped by:
  - `symbol`
  - `year`
  - `month`
- Result: successful monthly averages returned

## Conclusion

`B3` and `B4` are now complete for the batch analytics path:

- partitioned analytics output is implemented
- partition-aware Glue Catalog metadata is in place
- Athena reads the partitioned dataset successfully

The next batch phase is `B5`: cloud data quality and observability hardening.
