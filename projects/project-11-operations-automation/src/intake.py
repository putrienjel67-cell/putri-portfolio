from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd


SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}
CORE_OPERATION_COLUMNS = {
    "record_id",
    "client_name",
    "email",
    "request_type",
    "status",
    "received_at",
}


def read_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(path)
    elif suffix in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported intake format: {path.suffix}")

    frame = frame.copy()
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    frame["source_file"] = path.name
    return frame


def _choose_reference_schema(frames: list[tuple[Path, pd.DataFrame]]) -> frozenset[str]:
    """Choose the most plausible batch schema instead of trusting file order.

    A malformed file can sort before a valid source, so the first filename should
    never define what 'correct' means. Repeated schemas win first. Ties are broken
    by overlap with the operational fields used by this project.
    """
    schemas = [frozenset(frame.columns) - {"source_file"} for _, frame in frames]
    counts = Counter(schemas)

    return max(
        counts,
        key=lambda schema: (
            counts[schema],
            len(schema & CORE_OPERATION_COLUMNS),
            len(schema),
        ),
    )


def load_batch(folder: Path) -> tuple[pd.DataFrame, list[str]]:
    files = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not files:
        raise FileNotFoundError(f"No CSV or Excel intake files found in {folder}")

    readable: list[tuple[Path, pd.DataFrame]] = []
    rejected: list[str] = []

    for path in files:
        try:
            readable.append((path, read_source(path)))
        except Exception as exc:  # one unreadable source should not stop the batch
            rejected.append(f"{path.name}: {exc}")

    if not readable:
        raise ValueError("All intake files failed validation")

    expected_columns = _choose_reference_schema(readable)
    accepted: list[pd.DataFrame] = []

    for path, frame in readable:
        current = frozenset(frame.columns) - {"source_file"}
        if current != expected_columns:
            rejected.append(f"{path.name}: schema mismatch")
            continue
        accepted.append(frame)

    if not accepted:
        raise ValueError("All intake files failed schema validation")

    return pd.concat(accepted, ignore_index=True), rejected
