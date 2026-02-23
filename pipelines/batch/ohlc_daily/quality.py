from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd
import great_expectations as gx


def validate_ohlc_daily(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    if not records:
        return False, "No records to validate"

    df = pd.DataFrame(records)

    # minimal parse checks
    date_parsed = pd.to_datetime(df.get("date"), errors="coerce", utc=True)
    if date_parsed.isna().any():
        return False, "date contains unparseable values"

    context = gx.get_context(mode="ephemeral")
    datasource = context.data_sources.add_pandas(name="pandas_src")
    asset = datasource.add_dataframe_asset(name="ohlc_daily")
    batch_def = asset.add_batch_definition_whole_dataframe("batch")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})
    validator = context.get_validator(batch=batch)

    # Expectations
    validator.expect_column_values_to_not_be_null("symbol")
    validator.expect_column_values_to_match_regex("symbol", r"^[A-Z.\-]{1,10}$")

    validator.expect_column_values_to_not_be_null("date")

    for col in ["open", "high", "low", "close"]:
        validator.expect_column_values_to_not_be_null(col)
        validator.expect_column_values_to_be_between(col, min_value=0, strict_min=True)

    # OHLC sanity: high >= low, open/close within [low, high]
    validator.expect_column_pair_values_a_to_be_greater_than_b("high", "low", or_equal=True)
    validator.expect_column_pair_values_a_to_be_greater_than_b("open", "low", or_equal=True)
    validator.expect_column_pair_values_a_to_be_less_than_b("open", "high", or_equal=True)
    validator.expect_column_pair_values_a_to_be_greater_than_b("close", "low", or_equal=True)
    validator.expect_column_pair_values_a_to_be_less_than_b("close", "high", or_equal=True)

    validator.expect_column_values_to_be_in_set("currency", ["USD"])

    result = validator.validate()
    if result.success:
        return True, "PASS"

    failed = [r for r in result.results if not r.success]
    return False, f"FAIL: {len(failed)} expectations failed"