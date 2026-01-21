from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from pipelines.streaming.ingest_lambda.provider import fetch_latest_prices
from pipelines.streaming.ingest_lambda.storage import write_jsonl
from pipelines.streaming.ingest_lambda.transform import normalize_price_event
from pipelines.streaming.ingest_lambda.quality import validate_curated_prices


def run_local(symbols: List[str] | None = None) -> None:
    symbols = symbols or ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA"]

    raw = fetch_latest_prices(symbols)
    curated = [normalize_price_event(e) for e in raw]
    #curated[0]["price"] = -1  # <-- intentional failure test to check quarantine

    ok, msg = validate_curated_prices(curated)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    raw_path = Path("data/raw/prices") / f"prices_{ts}.jsonl"
    curated_path = Path("data/curated/prices") / f"prices_{ts}.jsonl"
    quarantine_path = Path("data/quarantine/streaming") / f"prices_{ts}.jsonl"

    # RAW always lands
    write_jsonl(raw_path, raw)

    if ok:
        write_jsonl(curated_path, curated)
        print("QUALITY:", msg)
        print(f"Wrote raw: {raw_path}")
        print(f"Wrote curated: {curated_path}")
    else:
        write_jsonl(quarantine_path, curated)
        print("QUALITY:", msg)
        print(f"Wrote raw: {raw_path}")
        print(f"Wrote quarantine: {quarantine_path}")

    print("Curated sample:", curated[0])


if __name__ == "__main__":
    run_local()