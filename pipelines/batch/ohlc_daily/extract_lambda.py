"""Compatibility wrapper for the batch extract Lambda entrypoint."""

from pipelines.batch.ohlc_daily.cloud.extract_lambda import lambda_handler

__all__ = ["lambda_handler"]
