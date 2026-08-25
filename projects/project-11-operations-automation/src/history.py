from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def append_run_history(report: dict, history_file: Path) -> None:
    history_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "run_id": report["run_id"],
        "generated_at": report["generated_at"],
        "rows_received": report["rows_received"],
        "rows_written": report["rows_written"],
        "review_records": report["quality"]["review_records"],
        "average_quality_score": report["quality"]["average_score"],
        "possible_entity_matches": report["possible_entity_matches"],
        "automated_field_changes": report["automated_field_changes"],
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
    }

    history: list[dict] = []
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            history = []

    history.append(entry)
    history_file.write_text(json.dumps(history[-100:], indent=2), encoding="utf-8")
