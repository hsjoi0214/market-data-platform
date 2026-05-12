# Batch Pipeline Execution Order

This file is the simplest way to follow the batch pipeline from beginning to end.

## Folder Layout

- `pipelines/batch/ohlc_daily/local/`: local learning runner and local-only helpers
- `pipelines/batch/ohlc_daily/cloud/`: AWS entrypoints
- `pipelines/batch/ohlc_daily/common/`: shared business logic and reserved shared modules

## Cloud Path (Current AWS Batch Path)

1. **Deploy infrastructure with Terraform**
   Files:
   - `infra/terraform/batch_extract_lambda.tf`
   - `infra/terraform/glue_job.tf`
   - `infra/terraform/glue_catalog.tf`
   - `infra/terraform/batch_s3_prefixes.tf`
   - `infra/terraform/athena.tf`

   What happens:
   - creates the batch extract Lambda
   - creates the Glue job
   - creates S3 batch prefixes
   - creates Glue Catalog metadata
   - creates Athena workgroup

2. **Invoke the batch extract Lambda**
   File:
   - `pipelines/batch/ohlc_daily/cloud/extract_lambda.py`

   What happens:
   - reads runtime mode like `incremental` or `backfill`
   - calls the provider layer
   - writes raw historical JSONL to `raw/prices_daily/`

3. **Fetch historical data from the provider**
   File:
   - `pipelines/batch/ohlc_daily/common/provider.py`

   What happens:
   - loads Alpha Vantage API key from Secrets Manager
   - calls Alpha Vantage historical daily endpoint
   - returns raw records for downstream processing

4. **Run the Glue transform job**
   File:
   - `pipelines/batch/ohlc_daily/cloud/glue_job.py`

   What happens:
   - reads raw JSONL from S3
   - standardizes schema and data types
   - writes curated Parquet to `curated/prices_daily/`
   - writes analytics Parquet to `analytics/ohlc_daily/`

5. **Read metadata through Glue Catalog**
   File:
   - `infra/terraform/glue_catalog.tf`

   What happens:
   - registers the `ohlc_daily` table
   - points Athena to analytics Parquet in S3

6. **Query analytics through Athena**
   File:
   - `infra/terraform/athena.tf`

   What happens:
   - Athena queries the `mdp_market_data_dev.ohlc_daily` table
   - this is the OLAP consumption layer

## Local Learning Path

1. **Run the local batch pipeline**
   File:
   - `pipelines/batch/ohlc_daily/local/app.py`

2. **Generate or fetch raw rows**
   File:
   - `pipelines/batch/ohlc_daily/common/provider.py`

3. **Normalize records**
   File:
   - `pipelines/batch/ohlc_daily/common/transform.py`

4. **Validate analytics output**
   File:
   - `pipelines/batch/ohlc_daily/common/quality.py`

5. **Write local JSONL outputs**
   File:
   - `pipelines/batch/ohlc_daily/local/storage.py`

## Important Note

There is **no EventBridge trigger for the batch path yet**.

Right now the cloud batch flow is:

- Terraform deploys the resources
- you invoke the batch extract Lambda manually
- you run the Glue job manually
- you validate results in S3 and Athena

If we later schedule batch execution, EventBridge would be inserted between step 1 and step 2 in the cloud path.
