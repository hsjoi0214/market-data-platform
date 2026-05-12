# Batch Extract Lambda - Real Data Validation

**Date:** 2026-05-12
**Environment:** dev
**Region:** us-east-1
**Lambda:** mdp-market-data-dev-batch-extract
**Image Tag:** v6
**Data Source:** Alpha Vantage via AWS Secrets Manager
**Bucket:** mdp-market-data-dev-us-east-1-a66798a5

## What Was Added

- Dedicated batch extract Lambda for historical daily data
- Dedicated IAM role and policy for:
  - `s3:PutObject` to `raw/prices_daily/*`
  - `secretsmanager:GetSecretValue`
  - CloudWatch logs and custom metrics
- Real Alpha Vantage historical daily extraction path
- Retry/backoff handling for Alpha Vantage free-tier `1 request per second` burst limit

## Invocation

Manual invocation command:

```bash
aws lambda invoke \
  --function-name mdp-market-data-dev-batch-extract \
  --cli-binary-format raw-in-base64-out \
  --payload '{}' \
  /private/tmp/batch_extract_response.json \
  --profile mdp-dev \
  --region us-east-1
```

Default Lambda runtime configuration used:

- `mode = incremental`
- `symbols = AAPL,MSFT`
- `lookback_days = 10`

## Lambda Response

```json
{
  "mode": "incremental",
  "symbols": ["AAPL", "MSFT"],
  "as_of": "2026-05-12",
  "window_days": 10,
  "rows_written": 20,
  "objects_written": 2,
  "s3_keys": [
    "raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-12/window_days=10/symbol=AAPL.jsonl",
    "raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-12/window_days=10/symbol=MSFT.jsonl"
  ]
}
```

## S3 Verification

Observed objects:

- `raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-12/window_days=10/symbol=AAPL.jsonl`
- `raw/prices_daily/source=alphavantage/mode=incremental/as_of=2026-05-12/window_days=10/symbol=MSFT.jsonl`

Observed sizes:

- `AAPL` object: `2516` bytes
- `MSFT` object: `2510` bytes

## Outcome

This validates the first real-data batch ingestion step end to end:

- real Alpha Vantage historical daily data fetched successfully
- secret loaded from AWS Secrets Manager
- batch extract Lambda executed successfully
- raw historical JSONL landed in S3 under `raw/prices_daily/`
- both symbols were written using deterministic, rerunnable object keys
