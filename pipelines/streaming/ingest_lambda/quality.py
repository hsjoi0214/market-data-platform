from __future__ import annotations

from typing import Any, Dict, List, Tuple
import pandas as pd
import great_expectations as gx


def validate_curated_prices(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Validate curated price events using Great Expectations.
    Returns (ok, message). If ok is False, message contains a short failure summary.
    """
    if not records:
        return False, "No records to validate"

    df = pd.DataFrame(records)

    # Build an in-memory GE context (lightweight)
    context = gx.get_context(mode="ephemeral")
    datasource = context.data_sources.add_pandas(name="pandas_src")
    asset = datasource.add_dataframe_asset(name="curated_prices_df")

    batch_def = asset.add_batch_definition_whole_dataframe("batch")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    # Expectations (your locked minimum suite)
    batch.expect_column_values_to_not_be_null("symbol")
    batch.expect_column_values_to_match_regex("symbol", r"^[A-Z.\-]{1,10}$")

    batch.expect_column_values_to_not_be_null("price")
    batch.expect_column_values_to_be_between("price", min_value=0, strict_min=True)

    batch.expect_column_values_to_not_be_null("currency")
    batch.expect_column_values_to_be_in_set("currency", ["USD"])  # start strict

    batch.expect_column_values_to_not_be_null("ts_market")
    batch.expect_column_values_to_not_be_null("ts_ingest")

    # parseable timestamps check (pandas coercion)
    ts_market_parsed = pd.to_datetime(df["ts_market"], errors="coerce", utc=True)
    ts_ingest_parsed = pd.to_datetime(df["ts_ingest"], errors="coerce", utc=True)
    if ts_market_parsed.isna().any():
        return False, "ts_market contains unparseable timestamps"
    if ts_ingest_parsed.isna().any():
        return False, "ts_ingest contains unparseable timestamps"

    result = batch.validate()
    if result.success:
        return True, "PASS"

    # Short, readable failure summary
    failed = [r for r in result.results if not r.success]
    msg = f"FAIL: {len(failed)} expectations failed"
    return False, msg