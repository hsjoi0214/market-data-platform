from __future__ import annotations

from datetime import datetime, timezone

from pipelines.batch.ohlc_daily.provider import fetch_daily_prices_stub
from pipelines.batch.ohlc_daily.storage import write_jsonl
from pipelines.batch.ohlc_daily.transform import to_curated_prices_daily, to_ohlc_daily
from pipelines.batch.ohlc_daily.quality import validate_ohlc_daily


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_local() -> None:
    symbols = ["AAPL", "MSFT"]
    days = 30

    ts = _ts()

    # 1) Extract (stub)
    raw_rows = fetch_daily_prices_stub(symbols=symbols, days=days)

    # 2) Land RAW
    raw_path = f"data/raw/prices_daily/prices_daily_{ts}.jsonl"
    write_jsonl(raw_path, raw_rows)
    print(f"Wrote RAW: {raw_path} rows={len(raw_rows)}")

    # 3) Curate
    curated_rows = to_curated_prices_daily(raw_rows)
    curated_path = f"data/curated/prices_daily/prices_daily_{ts}.jsonl"
    write_jsonl(curated_path, curated_rows)
    print(f"Wrote CURATED: {curated_path} rows={len(curated_rows)}")

    # 4) Analytics output (OHLC)
    ohlc_rows = to_ohlc_daily(curated_rows)
    analytics_path = f"data/analytics/ohlc_daily/ohlc_daily_{ts}.jsonl"
    write_jsonl(analytics_path, ohlc_rows)
    print(f"Wrote ANALYTICS: {analytics_path} rows={len(ohlc_rows)}")

    # 5) Quality gate (GE)
    ok, msg = validate_ohlc_daily(ohlc_rows)
    print(f"QUALITY: {'PASS' if ok else 'FAIL'} - {msg}")

    if not ok:
        quarantine_path = f"data/quarantine/batch/ohlc_daily/ohlc_daily_{ts}.jsonl"
        write_jsonl(quarantine_path, ohlc_rows)
        print(f"Wrote QUARANTINE: {quarantine_path} rows={len(ohlc_rows)}")


if __name__ == "__main__":
    run_local()