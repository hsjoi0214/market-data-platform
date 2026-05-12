# Streaming Ingest Structure

This package is intentionally split for teaching:

- `common/`: shared business logic
- `local/`: the local streaming walkthrough
- `cloud/`: the AWS Lambda entrypoint

Read it in this order:

1. `local/app.py` for the end-to-end local flow
2. `common/provider.py`, `common/transform.py`, and `common/quality.py` for shared logic
3. `cloud/lambda_handler.py` for the AWS runtime entrypoint

Important teaching boundary:

- deleting `local/` should not break the cloud streaming deployment
- `cloud/` may import from `common/`
- `common/` must not import from `local/` or `cloud/`
