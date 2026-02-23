from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, Iterable, List
import random


def _iso_z(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def fetch_daily_prices_stub(symbols: Iterable[str], days: int = 30, source: str = "stub") -> List[Dict]:
    """
    Stub "daily prices" for N days for each symbol.
    Output is provider-like, not curated yet.
    """
    if days < 2:
        raise ValueError("days must be >= 2")

    end = date.today()
    start = end - timedelta(days=days * 2)  # buffer for weekends

    rows: List[Dict] = []
    for sym in symbols:
        # start price
        px = random.uniform(80, 300)

        d = start
        while d <= end and len([r for r in rows if r["symbol"] == sym]) < days:
            # skip weekends
            if d.weekday() >= 5:
                d += timedelta(days=1)
                continue

            # random walk
            drift = random.uniform(-0.03, 0.03)
            close = max(1.0, px * (1.0 + drift))
            open_ = px
            high = max(open_, close) * (1.0 + random.uniform(0.0, 0.02))
            low = min(open_, close) * (1.0 - random.uniform(0.0, 0.02))
            volume = int(random.uniform(1_000_000, 20_000_000))

            ts_market = datetime(d.year, d.month, d.day, 21, 0, tzinfo=timezone.utc)  # market close-ish UTC
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
            d += timedelta(days=1)

    # stable ordering
    rows.sort(key=lambda r: (r["symbol"], r["date"]))
    return rows