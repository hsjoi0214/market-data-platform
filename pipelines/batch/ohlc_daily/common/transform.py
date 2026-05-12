"""
Batch transform helpers.

Learning Surface:
- Common shared logic, mainly used by the local batch walkthrough
"""

from __future__ import annotations

from typing import Any, Dict, List


def to_curated_prices_daily(raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize raw provider records into the project's canonical curated daily schema."""
    curated: List[Dict[str, Any]] = []
    for r in raw_rows:
        curated.append(
            {
                "symbol": str(r["symbol"]).upper().strip(),
                "date": str(r["date"]),  # YYYY-MM-DD
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": int(r["volume"]),
                "currency": str(r.get("currency", "USD")).upper().strip(),
                "ts_market": str(r["ts_market"]),
                "ts_ingest": str(r["ts_ingest"]),
                "source": str(r.get("source", "unknown")),
            }
        )
    return curated


def to_ohlc_daily(curated_daily: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Produce analytics-ready OHLC daily rows from curated daily price records.

    For now this is a 1:1 mapping because the input is already daily OHLC data.
    Later this function can evolve into a true aggregation step.
    """
    # In this simplified version, curated_daily is already daily OHLC.
    # We keep a separate function to preserve the "analytics layer" concept.
    return list(curated_daily)
