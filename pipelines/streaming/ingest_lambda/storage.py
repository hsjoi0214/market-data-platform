from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable


def write_jsonl(path: Path, records: Iterable[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
            
            
# This was used for the local testing of the ingest lambda, but is not used in the actual lambda code, which writes to s3 instead of local disk.