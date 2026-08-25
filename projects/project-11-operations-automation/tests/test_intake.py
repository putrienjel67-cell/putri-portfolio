from pathlib import Path

import pandas as pd

from src.intake import load_batch


def test_load_batch_combines_matching_csv_files(tmp_path: Path) -> None:
    pd.DataFrame([{"record_id": "A1", "status": "new"}]).to_csv(tmp_path / "one.csv", index=False)
    pd.DataFrame([{"record_id": "A2", "status": "completed"}]).to_csv(tmp_path / "two.csv", index=False)

    combined, rejected = load_batch(tmp_path)

    assert len(combined) == 2
    assert set(combined["source_file"]) == {"one.csv", "two.csv"}
    assert rejected == []


def test_load_batch_rejects_schema_mismatch_without_stopping_batch(tmp_path: Path) -> None:
    pd.DataFrame([{"record_id": "A1", "status": "new"}]).to_csv(tmp_path / "good.csv", index=False)
    pd.DataFrame([{"record_id": "A2", "state": "new"}]).to_csv(tmp_path / "bad.csv", index=False)

    combined, rejected = load_batch(tmp_path)

    assert len(combined) == 1
    assert rejected == ["bad.csv: schema mismatch"]
