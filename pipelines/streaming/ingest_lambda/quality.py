from __future__ import annotations

from typing import Dict, List, Tuple
import pandas as pd


def validate_prices(records: List[Dict]) -> Tuple[bool, str]:
    """
    Minimal quality gate (GE-like rules) using simple checks.
    We'll switch this to Great Expectations objects next, once the flow is working.
    """
    df = pd.DataFrame(records)

    required = ["symbol", "price", "currency", "ts_market", "ts_ingest", "source"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        return False, f"Missing columns: {missing_cols}"

    if df["symbol"].isna().any():
        return False, "Null symbol detected"

    if (df["price"] <= 0).any():
        return False, "Non-positive price detected"

    if df["currency"].isna().any():
        return False, "Null currency detected"

    return True, "PASS"