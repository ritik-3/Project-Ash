from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_task_log(base_dir: Path, payload: dict[str, Any]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    log_file = base_dir / "task_log.jsonl"
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
