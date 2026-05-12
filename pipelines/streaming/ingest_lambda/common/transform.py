from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _iso_z_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_price_event(e: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize provider output into the curated schema contract.
    """
    symbol = str(e["symbol"]).upper().strip()
    price = float(e["price"])
    currency = str(e.get("currency", "USD")).upper().strip()

    ts_market = str(e.get("ts_market") or _iso_z_now())
    ts_ingest = str(e.get("ts_ingest") or _iso_z_now())
    source = str(e.get("source", "unknown"))

    return {
        "symbol": symbol,
        "price": price,
        "currency": currency,
        "ts_market": ts_market,
        "ts_ingest": ts_ingest,
        "source": source,
    }