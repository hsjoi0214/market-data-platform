# Streaming Pipeline Execution Order

This file is the simplest way to follow the streaming pipeline from beginning to end.

## Folder Layout

- `pipelines/streaming/ingest_lambda/local/`: local learning runner and local-only helpers
- `pipelines/streaming/ingest_lambda/cloud/`: AWS Lambda entrypoint
- `pipelines/streaming/ingest_lambda/common/`: shared business logic

## Cloud Path (Current AWS Streaming Path)

1. **Deploy infrastructure with Terraform**
   Files:
   - `infra/terraform/lambda.tf`
   - `infra/terraform/iam.tf`
   - `infra/terraform/eventbridge.tf`
   - `infra/terraform/cloudwatch.tf`
   - `infra/terraform/quality_metrics.tf`

2. **Invoke the streaming Lambda**
   File:
   - `pipelines/streaming/ingest_lambda/cloud/lambda_handler.py`

3. **Fetch latest prices from the provider**
   File:
   - `pipelines/streaming/ingest_lambda/common/provider.py`

4. **Normalize records into curated schema**
   File:
   - `pipelines/streaming/ingest_lambda/common/transform.py`

5. **Run quality checks**
   File:
   - `pipelines/streaming/ingest_lambda/common/quality.py`

6. **Write raw and curated data**
   What happens:
   - raw JSONL lands in S3
   - passing curated records land in S3
   - passing curated records update DynamoDB
   - failing curated records land in quarantine

## Local Path (Learning Walkthrough)

1. **Run the local streaming app**
   File:
   - `pipelines/streaming/ingest_lambda/local/app.py`

2. **Fetch latest prices**
   File:
   - `pipelines/streaming/ingest_lambda/common/provider.py`

3. **Normalize records**
   File:
   - `pipelines/streaming/ingest_lambda/common/transform.py`

4. **Validate curated output**
   File:
   - `pipelines/streaming/ingest_lambda/common/quality.py`

5. **Write local files**
   File:
   - `pipelines/streaming/ingest_lambda/local/storage.py`
