from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def build_dashboard_payload(master_data: pd.DataFrame, report: dict) -> dict:
    status_counts = (
        master_data["status"].fillna("missing").value_counts(dropna=False).to_dict()
        if "status" in master_data.columns
        else {}
    )
    quality_bands = {}
    if "quality_score" in master_data.columns:
        bands = pd.cut(
            master_data["quality_score"],
            bins=[-1, 69, 89, 99, 100],
            labels=["critical", "needs_review", "good", "perfect"],
        )
        quality_bands = bands.value_counts().to_dict()

    return {
        "run_id": report.get("run_id"),
        "kpis": {
            "rows_received": report.get("rows_received", 0),
            "rows_written": report.get("rows_written", 0),
            "records_requiring_review": report.get("records_requiring_review", 0),
            "average_quality_score": report.get("average_quality_score", 0),
        },
        "status_distribution": {str(k): int(v) for k, v in status_counts.items()},
        "quality_distribution": {str(k): int(v) for k, v in quality_bands.items()},
    }


def write_dashboard(payload: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
