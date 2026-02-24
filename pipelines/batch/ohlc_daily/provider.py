from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Iterable, List, Literal, Optional
import random


BatchMode = Literal["backfill", "incremental"]


def _iso_z(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


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

    For now this uses the stub generator; later you’ll switch internals to Alpha Vantage.
    """
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

            ts_market = datetime(d.year, d.month, d.day, 21, 0, tzinfo=timezone.utc)  # close-ish UTC
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