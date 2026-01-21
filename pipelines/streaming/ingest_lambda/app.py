from datetime import datetime, timezone
from pathlib import Path

from pipelines.streaming.ingest_lambda.provider import fetch_latest_prices
from pipelines.streaming.ingest_lambda.storage import write_jsonl
from pipelines.streaming.ingest_lambda.transform import normalize_price_event


def run_local(symbols=None) -> None:
    symbols = symbols or ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA"]

    raw = fetch_latest_prices(symbols)
    curated = [normalize_price_event(e) for e in raw]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # ✅ match your folder structure
    raw_path = Path("data/raw/prices") / f"prices_{ts}.jsonl"
    curated_path = Path("data/curated/prices") / f"prices_{ts}.jsonl"

    write_jsonl(raw_path, raw)
    write_jsonl(curated_path, curated)

    print(f"Wrote raw: {raw_path}")
    print(f"Wrote curated: {curated_path}")
    print("Curated sample:", curated[0])


if __name__ == "__main__":
    run_local()