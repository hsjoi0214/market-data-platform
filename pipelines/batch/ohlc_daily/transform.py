from __future__ import annotations

from typing import Any, Dict, List


def to_curated_prices_daily(raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
    Analytics output. For now it's 1:1 daily OHLC rows (already daily).
    Later you can aggregate intraday ticks into daily candles.
    """
    # In this simplified version, curated_daily is already daily OHLC.
    # We keep a separate function to preserve the "analytics layer" concept.
    return list(curated_daily)