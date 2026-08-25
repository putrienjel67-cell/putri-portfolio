from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


def _safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def build_change_log(before: pd.DataFrame, after: pd.DataFrame, key: str = "record_id") -> pd.DataFrame:
    """Return field-level changes so automated cleanup remains inspectable."""
    changes: list[dict] = []
    before_by_key = before.drop_duplicates(key, keep="first").set_index(key)
    after_by_key = after.drop_duplicates(key, keep="first").set_index(key)

    common_keys = before_by_key.index.intersection(after_by_key.index)
    common_columns = before_by_key.columns.intersection(after_by_key.columns)

    for record_id in common_keys:
        for column in common_columns:
            old_value = _safe(before_by_key.at[record_id, column])
            new_value = _safe(after_by_key.at[record_id, column])
            if str(old_value) != str(new_value):
                changes.append(
                    {
                        "record_id": record_id,
                        "field": column,
                        "before": old_value,
                        "after": new_value,
                        "changed_by": "automation",
                        "changed_at": datetime.now().isoformat(timespec="seconds"),
                    }
                )

    return pd.DataFrame(changes)
