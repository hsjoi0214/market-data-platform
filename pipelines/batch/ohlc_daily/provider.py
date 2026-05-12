from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Iterable, List, Literal, Optional

import boto3
import requests

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


BatchMode = Literal["backfill", "incremental"]


def _iso_z(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


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


def _is_weekday(d: date) -> bool:
    return d.weekday() < 5


def _trading_days_between(start: date, end: date) -> List[date]:
    """Inclusive range of weekdays only."""
    out: List[date] = []
    d = start
    while d <= end:
        if _is_weekday(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def _last_n_trading_days(end: date, n: int) -> List[date]:
    """Return last n weekdays ending at `end` (inclusive if weekday)."""
    if n < 1:
        raise ValueError("n must be >= 1")

    out: List[date] = []
    d = end
    while len(out) < n:
        if _is_weekday(d):
            out.append(d)
        d -= timedelta(days=1)

    out.reverse()
    return out


@dataclass(frozen=True)
class DailyPricesRequest:
    mode: BatchMode
    symbols: List[str]
    source: str = "stub"

    # backfill config
    backfill_days: int = 252  # ~1 trading year; bump to ~500 for ~2 years

    # incremental config
    lookback_days: int = 10  # sliding window refresh size

    # optional override for deterministic tests
    as_of: Optional[date] = None


def fetch_daily_prices(req: DailyPricesRequest) -> List[Dict]:
    """
    Unified provider interface.

    backfill:
      - generates `backfill_days` trading days (weekday-only) up to as_of (or today)

    incremental:
      - generates last `lookback_days` trading days up to as_of (or today)
      - intended for overwrite/merge refresh of recent partitions

    Supports:
      - stub generation for local development
      - Alpha Vantage historical daily extraction for cloud batch runs
    """
    source = req.source.strip().lower()

    if source == "stub":
        end = req.as_of or date.today()

        if req.mode == "backfill":
            return fetch_daily_prices_stub(
                symbols=req.symbols,
                days=req.backfill_days,
                source=req.source,
                end=end,
            )

        if req.mode == "incremental":
            return fetch_daily_prices_stub(
                symbols=req.symbols,
                days=req.lookback_days,
                source=req.source,
                end=end,
            )

        raise ValueError(f"Unsupported mode: {req.mode}")

    if source in {"alphavantage", "alpha_vantage"}:
        return fetch_daily_prices_alphavantage(req)

    raise ValueError(f"Unsupported source: {req.source!r}")


def _fetch_daily_series(symbol: str, api_key: str, outputsize: str) -> Dict[str, Dict[str, str]]:
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": api_key,
    }

    for attempt in range(3):
        resp = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        throttle_msg = str(data.get("Note") or data.get("Information") or "").strip()
        if throttle_msg:
            lower_msg = throttle_msg.lower()
            if outputsize == "full" and "premium" in lower_msg:
                raise RuntimeError(
                    "Alpha Vantage full daily history requires premium access. "
                    "Use backfill_days <= 100 or a premium key."
                )

            if "1 request per second" in lower_msg and attempt < 2:
                time.sleep(1.2)
                continue

            raise RuntimeError(f"Alpha Vantage throttled or unavailable: {throttle_msg}")

        if "Error Message" in data:
            raise RuntimeError(f"Alpha Vantage error for {symbol}: {data['Error Message']}")

        series = data.get("Time Series (Daily)")
        if series:
            return series

        raise RuntimeError(
            f"Alpha Vantage response for {symbol} did not include 'Time Series (Daily)'"
        )

    raise RuntimeError(f"Alpha Vantage request retries exhausted for {symbol}")


def fetch_daily_prices_alphavantage(req: DailyPricesRequest) -> List[Dict]:
    end = req.as_of or date.today()
    window_days = req.backfill_days if req.mode == "backfill" else req.lookback_days
    outputsize = "full" if window_days > 100 else "compact"

    api_key = _get_api_key()
    ts_ingest = _iso_z(datetime.now(timezone.utc))
    rows: List[Dict] = []

    for symbol in req.symbols:
        normalized_symbol = str(symbol).upper().strip()
        series = _fetch_daily_series(normalized_symbol, api_key, outputsize=outputsize)

        available_days = sorted(d for d in series.keys() if date.fromisoformat(d) <= end)
        selected_days = available_days[-window_days:]

        if not selected_days:
            raise RuntimeError(
                f"No Alpha Vantage rows available for {normalized_symbol} up to {end.isoformat()}"
            )

        for day_str in selected_days:
            bar = series[day_str]
            rows.append(
                {
                    "symbol": normalized_symbol,
                    "date": day_str,
                    "open": float(bar["1. open"]),
                    "high": float(bar["2. high"]),
                    "low": float(bar["3. low"]),
                    "close": float(bar["4. close"]),
                    "volume": int(float(bar["5. volume"])),
                    "currency": "USD",
                    "ts_market": f"{day_str}T00:00:00Z",
                    "ts_ingest": ts_ingest,
                    "source": "alphavantage",
                }
            )

    rows.sort(key=lambda r: (r["symbol"], r["date"]))
    return rows


def fetch_daily_prices_stub(
    symbols: Iterable[str],
    days: int = 30,
    source: str = "stub",
    end: Optional[date] = None,
) -> List[Dict]:
    """
    Stub "daily prices" for N trading days for each symbol.
    Output is provider-like, not curated yet.

    - days = number of TRADING days (weekdays) to emit per symbol
    - end = last date to consider (defaults to today)
    """
    if days < 2:
        raise ValueError("days must be >= 2")

    end_date = end or date.today()

    # We build the exact list of trading days we want, then generate rows for those days.
    trading_days = _last_n_trading_days(end_date, days)

    rows: List[Dict] = []
    for sym in symbols:
        px = random.uniform(80, 300)  # start price

        for d in trading_days:
            # random walk
            drift = random.uniform(-0.03, 0.03)
            close = max(1.0, px * (1.0 + drift))
            open_ = px
            high = max(open_, close) * (1.0 + random.uniform(0.0, 0.02))
            low = min(open_, close) * (1.0 - random.uniform(0.0, 0.02))
            volume = int(random.uniform(1_000_000, 20_000_000))

            ts_market = datetime(
                d.year, d.month, d.day, 21, 0, tzinfo=timezone.utc
            )  # close-ish UTC
            ts_ingest = datetime.now(timezone.utc)

            rows.append(
                {
                    "symbol": sym,
                    "date": d.isoformat(),  # YYYY-MM-DD
                    "open": round(open_, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": volume,
                    "currency": "USD",
                    "ts_market": _iso_z(ts_market),
                    "ts_ingest": _iso_z(ts_ingest),
                    "source": source,
                }
            )

            px = close

    # stable ordering
    rows.sort(key=lambda r: (r["symbol"], r["date"]))
    return rows
