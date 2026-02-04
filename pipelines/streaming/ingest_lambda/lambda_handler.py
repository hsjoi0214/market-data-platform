from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import PurePosixPath
from typing import Any, Dict, List

import boto3

from pipelines.streaming.ingest_lambda.provider import fetch_latest_prices
from pipelines.streaming.ingest_lambda.quality import validate_curated_prices
from pipelines.streaming.ingest_lambda.transform import normalize_price_event


def _ddb_safe(obj: Any) -> Any:
    """
    Convert Python types to DynamoDB-safe types.
    DynamoDB does not accept float; use Decimal.
    """
    if isinstance(obj, float):
        # Convert via string to preserve the value users expect
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _ddb_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_ddb_safe(v) for v in obj]
    return obj


def _jsonl(records: List[Dict[str, Any]]) -> bytes:
    return ("\n".join(json.dumps(r) for r in records) + "\n").encode("utf-8")


def _key(prefix: str, ts: str) -> str:
    return str(PurePosixPath(prefix) / f"prices_{ts}.jsonl")


def _put_metric(namespace: str, metric_name: str, value: float = 1.0) -> None:
    """
    Publish a lightweight custom metric to CloudWatch.
    This is more reliable than log-based metric filters (especially for container Lambdas).
    """
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


def lambda_handler(event, context):
    bucket = os.environ["S3_BUCKET_NAME"]
    table_name = os.environ["DDB_TABLE_LATEST_PRICES"]

    symbols = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA"]  # stub list for now

    raw = fetch_latest_prices(symbols)
    curated = [normalize_price_event(e) for e in raw]

    ok, msg = validate_curated_prices(curated)
    print(f"QUALITY={'PASS' if ok else 'FAIL'}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    s3 = boto3.client("s3")

    # RAW write (always)
    raw_key = _key("raw/prices", ts)
    s3.put_object(Bucket=bucket, Key=raw_key, Body=_jsonl(raw))

    # Storage liveness metric: "did raw land?"
    _put_metric(namespace="MDP/Storage", metric_name="StorageRawWriteCount", value=1)

    if ok:
        # CURATED write (only on PASS)
        curated_key = _key("curated/prices", ts)
        s3.put_object(Bucket=bucket, Key=curated_key, Body=_jsonl(curated))

        # Serve latest prices to DynamoDB
        ddb = boto3.resource("dynamodb")
        table = ddb.Table(table_name)
        for item in curated:
            table.put_item(Item=_ddb_safe(item))

        return {
            "quality": "PASS",
            "message": msg,
            "s3_raw_key": raw_key,
            "s3_curated_key": curated_key,
            "items_written": len(curated),
        }

    # FAIL → quarantine
    quarantine_key = _key("quarantine/streaming", ts)
    s3.put_object(Bucket=bucket, Key=quarantine_key, Body=_jsonl(curated))

    # Quality metric: "how often do we fail GE?"
    _put_metric(namespace="MDP/Quality", metric_name="QualityFailCount", value=1)

    return {
        "quality": "FAIL",
        "message": msg,
        "s3_raw_key": raw_key,
        "s3_quarantine_key": quarantine_key,
        "items_quarantined": len(curated),
    }