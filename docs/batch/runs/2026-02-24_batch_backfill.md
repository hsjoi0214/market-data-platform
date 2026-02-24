# Batch Pipeline – Backfill Mode

**Date:** 2026-02-24  
**Mode:** backfill  
**Symbols:** AAPL, MSFT  
**Backfill Days:** 252  

## Command

poetry run python -m pipelines.batch.ohlc_daily.app

## Output Summary

RAW rows: 504  
CURATED rows: 504  
ANALYTICS rows: 504  
QUALITY: PASS

## Notes

- 252 trading days × 2 symbols = 504 rows.
- Great Expectations validation passed.
- Files written to:
  - data/raw/prices_daily/
  - data/curated/prices_daily/
  - data/analytics/ohlc_daily/