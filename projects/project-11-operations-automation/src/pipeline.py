from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml


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

    result = QAResult(
        rows_received=rows_received,
        rows_written=len(deduplicated),
        duplicate_rows_removed=duplicate_count,
        missing_required_values=missing_required_values,
        invalid_status_rows=invalid_status_count,
    )
    return deduplicated, result


def write_outputs(df: pd.DataFrame, result: QAResult, config: dict) -> None:
    output_dir = ROOT / config["output_dir"]
    report_dir = ROOT / config["report_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(output_dir / f"clean_operations_{run_id}.csv", index=False)

    report = {
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        **asdict(result),
        "records_requiring_review": int((df["qa_flag"] != "ok").sum()),
    }
    with (report_dir / f"qa_report_{run_id}.json").open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    config = load_config()
    source = ROOT / config["input_file"]

    logging.info("Reading intake file: %s", source)
    raw = pd.read_csv(source)
    cleaned = normalize_records(raw, config)
    validated, result = validate_records(cleaned, config)
    write_outputs(validated, result, config)

    logging.info(
        "Finished: %s rows received, %s written, %s duplicates removed.",
        result.rows_received,
        result.rows_written,
        result.duplicate_rows_removed,
    )


if __name__ == "__main__":
    main()
