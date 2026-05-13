"""Compatibility wrapper for the streaming Lambda entrypoint."""

from pipelines.streaming.ingest_lambda.cloud.lambda_handler import lambda_handler

__all__ = ["lambda_handler"]
