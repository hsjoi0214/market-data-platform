# Batch Pipeline – Incremental Mode

**Date:** 2026-02-24  
**Mode:** incremental  
**Symbols:** AAPL, MSFT  
**Lookback Days:** 10  

## Command

BATCH_MODE=incremental poetry run python -m pipelines.batch.ohlc_daily.app

## Output Summary

RAW rows: 20  
CURATED rows: 20  
ANALYTICS rows: 20  
QUALITY: PASS

## Notes

- 10 trading days × 2 symbols = 20 rows.
- Incremental window simulation successful.
- Great Expectations validation passed.