"""
Batch extract Lambda entrypoint.

Learning Surface:
- Cloud
Execution Step:
- 1 of 4 in the cloud batch walkthrough
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import PurePosixPath
from typing import Any, Dict, Iterable, List

import boto3

from pipelines.batch.ohlc_daily.common.provider import DailyPricesRequest, fetch_daily_prices


def _parse_symbols(value: str | Iterable[str] | None) -> List[str]:
    """Normalize symbol input from event or environment variables into a clean list."""
    if value is None:
        return ["AAPL", "MSFT"]

    if isinstance(value, str):
        items = [part.strip().upper() for part in value.split(",")]
    else:
        items = [str(part).strip().upper() for part in value]

    out = [item for item in items if item]
    if not out:
        raise ValueError("At least one symbol is required")
    return out


def _parse_as_of(value: str | None) -> date | None:
    """Parse an optional ISO date override used to make batch windows reproducible."""
    if not value:
        return None
    return date.fromisoformat(value)


def _jsonl(records: List[Dict[str, Any]]) -> bytes:
    """Serialize records to newline-delimited JSON bytes for S3 object writes."""
    return ("\n".join(json.dumps(r) for r in records) + "\n").encode("utf-8")


def _put_metric(namespace: str, metric_name: str, value: float) -> None:
    """Publish a lightweight CloudWatch custom metric for batch observability."""
    cw = boto3.client("cloudwatch")
    cw.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value,
                "Unit": "Count",
            }
        ],
    )


def _group_by_symbol(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group extracted raw rows by symbol so each symbol lands in its own raw object."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["symbol"]), []).append(row)
    return grouped


def _s3_key(mode: str, as_of: date, window_days: int, symbol: str) -> str:
    """Build a deterministic raw S3 object key for one batch extract slice."""
    prefix = PurePosixPath(
        "raw",
        "prices_daily",
        "source=alphavantage",
        f"mode={mode}",
        f"as_of={as_of.isoformat()}",
        f"window_days={window_days}",
    )
    return str(prefix / f"symbol={symbol}.jsonl")


def _resolve_request(event: Dict[str, Any]) -> DailyPricesRequest:
    """Merge Lambda event overrides and environment defaults into one extract request."""
    mode = str(event.get("mode") or os.getenv("BATCH_MODE", "incremental")).strip().lower()
    if mode not in {"backfill", "incremental"}:
        raise ValueError("mode must be 'backfill' or 'incremental'")

    symbols = _parse_symbols(event.get("symbols") or os.getenv("BATCH_SYMBOLS", "AAPL,MSFT"))
    backfill_days = int(event.get("backfill_days") or os.getenv("BATCH_BACKFILL_DAYS", "90"))
    lookback_days = int(event.get("lookback_days") or os.getenv("BATCH_LOOKBACK_DAYS", "10"))
    as_of = _parse_as_of(str(event.get("as_of") or os.getenv("BATCH_AS_OF", "")).strip() or None)

    return DailyPricesRequest(
        mode=mode,
        symbols=symbols,
        source="alphavantage",
        backfill_days=backfill_days,
        lookback_days=lookback_days,
        as_of=as_of,
    )


def lambda_handler(event, context):
    """
    Execute one cloud batch extract run and land raw historical JSONL into S3.

    This is the first runtime step in the current cloud batch path after Terraform
    has provisioned the Lambda and its IAM permissions.
    """
    event = event or {}

    bucket = os.environ["S3_BUCKET_NAME"]
    req = _resolve_request(event)

    rows = fetch_daily_prices(req)
    if not rows:
        raise RuntimeError("Batch extract fetched zero rows")

    window_days = req.backfill_days if req.mode == "backfill" else req.lookback_days
    as_of = req.as_of or date.today()

    s3 = boto3.client("s3")
    grouped = _group_by_symbol(rows)
    written_keys: List[str] = []

    for symbol, symbol_rows in grouped.items():
        key = _s3_key(req.mode, as_of, window_days, symbol)
        s3.put_object(Bucket=bucket, Key=key, Body=_jsonl(symbol_rows))
        written_keys.append(key)

    _put_metric(namespace="MDP/Storage", metric_name="StorageRawWriteCount", value=1)

    return {
        "mode": req.mode,
        "symbols": req.symbols,
        "as_of": as_of.isoformat(),
        "window_days": window_days,
        "rows_written": len(rows),
        "objects_written": len(written_keys),
        "s3_keys": written_keys,
    }
