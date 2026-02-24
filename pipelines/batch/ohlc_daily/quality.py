from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd
import great_expectations as gx


def validate_ohlc_daily(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    GE 1.11-compatible validation for OHLC daily analytics output.
    Returns (ok, message).
    """
    if not records:
        return False, "No records to validate"

    df = pd.DataFrame(records)

    # ---- Pandas guards for OHLC invariants (more reliable than hunting GE expectation names) ----
    required_cols = ["symbol", "date", "open", "high", "low", "close"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        return False, f"Missing columns: {missing}"

    # numeric coercion + NaN check
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df[["open", "high", "low", "close"]].isna().any().any():
        return False, "OHLC contains non-numeric values"

    # OHLC relationships:
    # low <= open/close <= high, and low <= high
    bad = df[
        (df["low"] > df["high"])
        | (df["open"] < df["low"]) | (df["open"] > df["high"])
        | (df["close"] < df["low"]) | (df["close"] > df["high"])
    ]
    if not bad.empty:
        return False, f"OHLC invariant failed for {len(bad)} rows"

    # Date parseability
    parsed = pd.to_datetime(df["date"], errors="coerce", utc=True)
    if parsed.isna().any():
        return False, "date contains unparseable timestamps"

    # ---- GE checks (schema + simple constraints) ----
    context = gx.get_context(mode="ephemeral")

    datasource = context.data_sources.add_pandas(name="pandas_src_batch")
    asset = datasource.add_dataframe_asset(name="ohlc_daily")

    batch_def = asset.add_batch_definition_whole_dataframe("batch")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    validator = context.get_validator(batch=batch)

    validator.expect_column_values_to_not_be_null("symbol")
    validator.expect_column_values_to_match_regex("symbol", r"^[A-Z.\-]{1,10}$")

    validator.expect_column_values_to_not_be_null("date")

    for c in ["open", "high", "low", "close"]:
        validator.expect_column_values_to_not_be_null(c)
        validator.expect_column_values_to_be_between(c, min_value=0, strict_min=True)

    result = validator.validate()
    if result.success:
        return True, "PASS"

    failed = [r for r in result.results if not r.success]
    return False, f"FAIL: {len(failed)} expectations failed"