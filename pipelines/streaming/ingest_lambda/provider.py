from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Dict
import random


def fetch_latest_prices(symbols: Iterable[str], source: str = "stub") -> List[Dict]:
    """
    Local stub: returns fake prices so we can build the pipeline without API keys.
    Replace later with a real provider call.
    """
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    out = []
    for s in symbols:
        price = round(random.uniform(50, 500), 2)
        out.append(
            {
                "symbol": s,
                "price": price,
                "currency": "USD",
                "ts_market": now,
                "ts_ingest": now,
                "source": source,
            }
        )
    return out