from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

import boto3
import requests

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


def _iso_z_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_api_key() -> str:
    """
    Load Alpha Vantage API key.
    Priority:
      1) AWS Secrets Manager (PROVIDER_SECRET_ID)
      2) Local env var (ALPHAVANTAGE_API_KEY)
    """
    secret_id = os.getenv("PROVIDER_SECRET_ID", "").strip()
    if secret_id:
        region = os.getenv("AWS_REGION", "us-east-1")
        sm = boto3.client("secretsmanager", region_name=region)
        resp = sm.get_secret_value(SecretId=secret_id)
        payload = resp.get("SecretString") or "{}"
        data = json.loads(payload)
        key = data.get("ALPHAVANTAGE_API_KEY", "").strip()
        if not key:
            raise RuntimeError("Secret loaded but ALPHAVANTAGE_API_KEY missing in secret JSON")
        return key

    key = os.getenv("ALPHAVANTAGE_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "No API key found. Set PROVIDER_SECRET_ID (AWS) or ALPHAVANTAGE_API_KEY (local)."
        )
    return key


def _fetch_global_quote(symbol: str, api_key: str) -> Optional[Dict]:
    """
    Calls Alpha Vantage GLOBAL_QUOTE endpoint and returns parsed JSON or None.
    """
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}
    r = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    # Common Alpha Vantage errors / throttling messages
    if "Note" in data:
        raise RuntimeError(f"Alpha Vantage throttled: {data['Note']}")
    if "Error Message" in data:
        raise RuntimeError(f"Alpha Vantage error: {data['Error Message']}")

    return data.get("Global Quote")


def fetch_latest_prices(symbols: Iterable[str], source: str = "alphavantage") -> List[Dict]:
    """
    Fetch latest prices from Alpha Vantage.
    Returns a list of events compatible with normalize_price_event().
    """
    api_key = _get_api_key()
    ts_ingest = _iso_z_now()

    out: List[Dict] = []
    for s in symbols:
        symbol = str(s).upper().strip()
        quote = _fetch_global_quote(symbol, api_key)

        # If the quote is empty, skip (do not poison the pipeline)
        if not quote:
            continue

        # Alpha Vantage uses strings for everything
        price_str = quote.get("05. price") or quote.get("05. price".strip())
        latest_trading_day = quote.get("07. latest trading day")  # YYYY-MM-DD typically

        if not price_str:
            continue

        price = float(price_str)

        # We don't get an exact market timestamp; use trading day + ingest time.
        # Keep ts_market as ingest time for now (good enough for portfolio).
        ts_market = ts_ingest
        if latest_trading_day:
            # still keep ISO format and Z; we won't fabricate a time-of-day
            ts_market = f"{latest_trading_day}T00:00:00Z"

        out.append(
            {
                "symbol": symbol,
                "price": price,
                "currency": "USD",
                "ts_market": ts_market,
                "ts_ingest": ts_ingest,
                "source": source,
            }
        )

    return out