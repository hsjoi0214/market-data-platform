# Terraform Learning Order

This guide is the easiest way to read the Terraform in a student-friendly order.

The intended path is:

1. `Orientation`
2. `Foundation` for shared infrastructure
3. `Streaming` using the 9-category checklist
4. `Batch` using the 9-category checklist

## Orientation

- `infra/terraform/main.tf`

## Foundation

- `infra/terraform/provider.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/s3.tf`
- `infra/terraform/ecr.tf`
- `infra/terraform/outputs.tf`

These files are shared by both pipelines, so they come before the streaming and batch tracks.

## Streaming Track

### 1. Networking

- No dedicated VPC or subnet Terraform exists yet for streaming in this repo.

### 2. Security

- `infra/terraform/s3.tf`

### 3. Compute / Processing

- `infra/terraform/ecr.tf`
- `infra/terraform/lambda.tf`
- `infra/terraform/eventbridge.tf`

### 4. Persistence / Data Stores

- `infra/terraform/s3.tf`
- `infra/terraform/dynamodb.tf`

### 5. Permissions / IAM

- `infra/terraform/iam.tf`

### 6. Configuration / Secrets

- `infra/terraform/variables.tf`
- `infra/terraform/iam.tf`
- `infra/terraform/lambda.tf`

### 7. Observability / Operations

- `infra/terraform/eventbridge.tf`
- `infra/terraform/cloudwatch.tf`
- `infra/terraform/quality_metrics.tf`

### 8. Reliability / Production Readiness

- `infra/terraform/quality_metrics.tf`

### 9. Environment / Delivery

- `infra/terraform/provider.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/ecr.tf`
- `infra/terraform/outputs.tf`

## Batch Track

### 1. Networking

- No dedicated VPC or subnet Terraform exists yet for batch in this repo.

### 2. Security

- `infra/terraform/s3.tf`

### 3. Compute / Processing

- `infra/terraform/ecr.tf`
- `infra/terraform/batch_extract_lambda.tf`
- `infra/terraform/glue_job.tf`
- `infra/terraform/athena.tf`

### 4. Persistence / Data Stores

- `infra/terraform/s3.tf`
- `infra/terraform/batch_s3_prefixes.tf`
- `infra/terraform/glue_catalog.tf`
- `infra/terraform/athena.tf`

### 5. Permissions / IAM

- `infra/terraform/batch_extract_lambda.tf`
- `infra/terraform/glue_job.tf`

### 6. Configuration / Secrets

- `infra/terraform/variables.tf`
- `infra/terraform/batch_extract_lambda.tf`
- `infra/terraform/glue_catalog.tf`

### 7. Observability / Operations

- `infra/terraform/athena.tf`

### 8. Reliability / Production Readiness

- No dedicated batch-specific reliability Terraform exists yet in this repo.

### 9. Environment / Delivery

- `infra/terraform/provider.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/ecr.tf`
- `infra/terraform/outputs.tf`
