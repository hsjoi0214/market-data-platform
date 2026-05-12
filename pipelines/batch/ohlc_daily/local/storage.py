"""
Batch local storage helpers.

Learning Surface:
- Local
Execution Step:
- Used by steps 2, 3, 4, and 5 of 5 in the local batch walkthrough
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    """Write records to a local JSONL file, creating parent folders when needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
