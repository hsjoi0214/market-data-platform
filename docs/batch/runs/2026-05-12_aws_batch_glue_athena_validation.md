# Batch Pipeline - AWS Glue and Athena Validation

**Date:** 2026-05-12
**Environment:** dev
**Region:** us-east-1
**Bucket:** mdp-market-data-dev-us-east-1-a66798a5
**Glue Job:** mdp-market-data-dev-batch-ohlc-daily
**Glue Job Run ID:** jr_0628e1bf2b1d5b4b0723a2fde5ca02335b35d0445b20bacc93faa8f1cab58881
**Athena Workgroup:** mdp-market-data-dev-athena
**Athena Query Execution ID:** a1fc59f7-424b-44a2-9040-3f11ccc4fdc6

## Infrastructure Validation

- Ran `terraform fmt`.
- Ran `terraform plan` and `terraform apply` for the batch infrastructure.
- Confirmed the live Glue role S3 policy allows object access across the entire project bucket:
  - `arn:aws:s3:::mdp-market-data-dev-us-east-1-a66798a5/*`
- Applied Glue Catalog table metadata update from JSON to Parquet.

## Glue Job Result

- Job state: `SUCCEEDED`
- Started: `2026-05-12T10:10:44.371+02:00`
- Completed: `2026-05-12T10:12:09.397+02:00`
- Execution time: `76` seconds

## S3 Output Verification

Parquet files landed in:

- `s3://mdp-market-data-dev-us-east-1-a66798a5/curated/prices_daily/`
- `s3://mdp-market-data-dev-us-east-1-a66798a5/analytics/ohlc_daily/`

Observed files:

- `curated/prices_daily/part-00000-ccbed305-5090-43a7-bf12-ec64c0e2b4a2-c000.snappy.parquet`
- `curated/prices_daily/part-00001-ccbed305-5090-43a7-bf12-ec64c0e2b4a2-c000.snappy.parquet`
- `curated/prices_daily/part-00002-ccbed305-5090-43a7-bf12-ec64c0e2b4a2-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00000-576ec881-6c9b-4718-b250-75c56c70ab22-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00001-576ec881-6c9b-4718-b250-75c56c70ab22-c000.snappy.parquet`
- `analytics/ohlc_daily/part-00002-576ec881-6c9b-4718-b250-75c56c70ab22-c000.snappy.parquet`

## Athena Validation

Query:

```sql
SELECT count(*) AS row_count FROM ohlc_daily;
```

Result:

- `row_count = 704`

## Outcome

The AWS batch pipeline is now validated end to end:

- Glue job runs successfully
- Curated and analytics Parquet outputs land in S3
- Glue Catalog points to Parquet
- Athena reads the table successfully
