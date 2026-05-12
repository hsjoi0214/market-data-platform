# Batch OHLC Daily Structure

This package is intentionally split for teaching:

- `common/`: shared business logic and reserved shared modules
- `local/`: the local batch walkthrough
- `cloud/`: AWS-specific entrypoints

Read it in this order:

1. `local/app.py` for the end-to-end local flow
2. `common/provider.py`, `common/transform.py`, and `common/quality.py` for shared logic
3. `cloud/extract_lambda.py` for cloud extraction
4. `cloud/glue_job.py` for cloud transformation

Important teaching boundary:

- deleting `local/` should not break the cloud batch deployment
- `cloud/` may import from `common/`
- `common/` must not import from `local/` or `cloud/`

One practical exception exists for Glue:

- `cloud/glue_job.py` stays self-contained so the deployed Glue script does not depend on packaging extra Python modules
