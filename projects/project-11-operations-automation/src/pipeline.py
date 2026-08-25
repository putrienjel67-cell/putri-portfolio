from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

from audit import build_change_log
from dashboard import build_dashboard_payload, write_dashboard
from history import append_run_history
from intake import load_batch
from master_match import match_to_master
from quality import QualitySummary, score_records
from reconciliation import find_possible_duplicates


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class QAResult:
    rows_received: int
    rows_written: int
    duplicate_rows_removed: int
    missing_required_values: int
    invalid_status_rows: int


def load_config() -> dict:
    with (ROOT / "config.yaml").open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def clean_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().replace({"": pd.NA})


def normalize_records(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [column.strip().lower() for column in cleaned.columns]

    for column in config["text_fields"]:
        if column in cleaned.columns:
            cleaned[column] = clean_text(cleaned[column])

    if "email" in cleaned.columns:
        cleaned["email"] = clean_text(cleaned["email"]).str.lower()

    if "status" in cleaned.columns:
        cleaned["status"] = cleaned["status"].str.lower().str.replace(" ", "_", regex=False)

    if "received_at" in cleaned.columns:
        cleaned["received_at"] = pd.to_datetime(cleaned["received_at"], errors="coerce")

    return cleaned


def validate_records(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, QAResult]:
    required = config["required_fields"]
    missing_columns = [column for column in required if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    rows_received = len(df)
    missing_required_values = int(df[required].isna().sum().sum())
    duplicate_mask = df.duplicated(subset=["record_id"], keep="first")
    duplicate_count = int(duplicate_mask.sum())
    deduplicated = df.loc[~duplicate_mask].copy()

    invalid_status = ~deduplicated["status"].isin(config["allowed_statuses"])
    invalid_status_count = int(invalid_status.fillna(True).sum())
    deduplicated.loc[invalid_status, "qa_flag"] = "review_status"

    incomplete = deduplicated[required].isna().any(axis=1)
    deduplicated.loc[incomplete, "qa_flag"] = deduplicated.loc[incomplete, "qa_flag"].fillna("missing_required_data")
    deduplicated["qa_flag"] = deduplicated["qa_flag"].fillna("ok")

    result = QAResult(rows_received, len(deduplicated), duplicate_count, missing_required_values, invalid_status_count)
    return deduplicated, result


def _latest_master(output_dir: Path) -> pd.DataFrame:
    files = sorted(output_dir.glob("master_data_*.csv"), reverse=True)
    if not files:
        return pd.DataFrame()
    return pd.read_csv(files[0])


def write_outputs(
    df: pd.DataFrame,
    result: QAResult,
    quality: QualitySummary,
    reconciliation: pd.DataFrame,
    master_matches: pd.DataFrame,
    audit_log: pd.DataFrame,
    rejected_sources: list[str],
    config: dict,
) -> None:
    output_dir = ROOT / config["output_dir"]
    report_dir = ROOT / config["report_dir"]
    review_dir = ROOT / config.get("review_dir", "data/review")
    audit_dir = ROOT / config.get("audit_dir", "data/audit")
    dashboard_dir = ROOT / config.get("dashboard_dir", "dashboard/data")
    history_file = report_dir / "run_history.json"
    for directory in (output_dir, report_dir, review_dir, audit_dir, dashboard_dir):
        directory.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(output_dir / f"master_data_{run_id}.csv", index=False)
    df.loc[df["review_required"]].to_csv(review_dir / f"review_queue_{run_id}.csv", index=False)
    reconciliation.to_csv(review_dir / f"possible_matches_{run_id}.csv", index=False)
    master_matches.to_csv(review_dir / f"master_match_decisions_{run_id}.csv", index=False)
    audit_log.to_csv(audit_dir / f"change_log_{run_id}.csv", index=False)

    report = {
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        **asdict(result),
        "records_requiring_review": quality.review_records,
        "average_quality_score": quality.average_score,
        "quality": asdict(quality),
        "possible_entity_matches": len(reconciliation),
        "master_safe_matches": int((master_matches.get("decision") == "safe_match").sum()) if not master_matches.empty else 0,
        "master_review_matches": int((master_matches.get("decision") == "review_match").sum()) if not master_matches.empty else 0,
        "automated_field_changes": len(audit_log),
        "rejected_sources": rejected_sources,
    }
    report_path = report_dir / f"operations_report_{run_id}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    append_run_history(report, history_file)
    dashboard = build_dashboard_payload(df, report)
    write_dashboard(dashboard, dashboard_dir / "latest.json")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    config = load_config()
    intake_dir = ROOT / config.get("input_dir", "data/incoming")
    output_dir = ROOT / config["output_dir"]

    logging.info("Reading intake batch: %s", intake_dir)
    raw, rejected_sources = load_batch(intake_dir)
    for rejection in rejected_sources:
        logging.warning("Rejected source: %s", rejection)

    normalized = normalize_records(raw, config)
    validated, result = validate_records(normalized, config)
    scored, quality = score_records(validated, config["required_fields"], config["allowed_statuses"])
    possible_matches = find_possible_duplicates(scored, float(config.get("match_threshold", 0.88)))

    previous_master = _latest_master(output_dir)
    master_matches = match_to_master(scored, previous_master, float(config.get("master_match_threshold", 0.9)))

    raw_for_audit = raw.copy()
    raw_for_audit.columns = [column.strip().lower() for column in raw_for_audit.columns]
    audit_log = build_change_log(raw_for_audit, scored)
    write_outputs(scored, result, quality, possible_matches, master_matches, audit_log, rejected_sources, config)

    logging.info(
        "Finished: %s received | %s written | %s review | quality %.2f/100",
        result.rows_received,
        result.rows_written,
        quality.review_records,
        quality.average_score,
    )


if __name__ == "__main__":
    main()
