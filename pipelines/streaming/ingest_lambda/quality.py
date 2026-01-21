from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd
import great_expectations as gx


def validate_curated_prices(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Great Expectations 1.11-compatible validation for curated price events.
    Returns (ok, message).
    """
    if not records:
        return False, "No records to validate"

    df = pd.DataFrame(records)

    # Extra guard: timestamp parseability (GE doesn't automatically parse strings)
    ts_market_parsed = pd.to_datetime(df.get("ts_market"), errors="coerce", utc=True)
    ts_ingest_parsed = pd.to_datetime(df.get("ts_ingest"), errors="coerce", utc=True)
    if ts_market_parsed.isna().any():
        return False, "ts_market contains unparseable timestamps"
    if ts_ingest_parsed.isna().any():
        return False, "ts_ingest contains unparseable timestamps"

    # Create an ephemeral GE context and a pandas datasource/asset
    context = gx.get_context(mode="ephemeral")

    datasource = context.data_sources.add_pandas(name="pandas_src")
    asset = datasource.add_dataframe_asset(name="curated_prices")

    # Create a batch for this dataframe
    batch_def = asset.add_batch_definition_whole_dataframe("batch")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    # Create a validator (this is where expect_* lives)
    validator = context.get_validator(batch=batch)

    # ---- Locked minimum expectations ----
    validator.expect_column_values_to_not_be_null("symbol")
    validator.expect_column_values_to_match_regex("symbol", r"^[A-Z.\-]{1,10}$")

    validator.expect_column_values_to_not_be_null("price")
    validator.expect_column_values_to_be_between("price", min_value=0, strict_min=True)

    validator.expect_column_values_to_not_be_null("currency")
    validator.expect_column_values_to_be_in_set("currency", ["USD"])  # strict for now

    validator.expect_column_values_to_not_be_null("ts_market")
    validator.expect_column_values_to_not_be_null("ts_ingest")

    result = validator.validate()

    if result.success:
        return True, "PASS"

    failed = [r for r in result.results if not r.success]
    return False, f"FAIL: {len(failed)} expectations failed"