from __future__ import annotations

from pathlib import Path

import pandas as pd


SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}


def read_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(path)
    elif suffix in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported intake format: {path.suffix}")

    frame = frame.copy()
    frame["source_file"] = path.name
    return frame


def load_batch(folder: Path) -> tuple[pd.DataFrame, list[str]]:
    files = sorted(path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES)
    if not files:
        raise FileNotFoundError(f"No CSV or Excel intake files found in {folder}")

    frames: list[pd.DataFrame] = []
    rejected: list[str] = []
    expected_columns: set[str] | None = None

    for path in files:
        try:
            frame = read_source(path)
            current = set(frame.columns) - {"source_file"}
            if expected_columns is None:
                expected_columns = current
            elif current != expected_columns:
                rejected.append(f"{path.name}: schema mismatch")
                continue
            frames.append(frame)
        except Exception as exc:  # batch intake should continue when one source fails
            rejected.append(f"{path.name}: {exc}")

    if not frames:
        raise ValueError("All intake files failed validation")

    return pd.concat(frames, ignore_index=True), rejected
