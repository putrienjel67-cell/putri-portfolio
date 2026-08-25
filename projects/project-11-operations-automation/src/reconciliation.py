from __future__ import annotations

from difflib import SequenceMatcher

import pandas as pd


def similarity(left: object, right: object) -> float:
    if pd.isna(left) or pd.isna(right):
        return 0.0
    return SequenceMatcher(None, str(left).lower().strip(), str(right).lower().strip()).ratio()


def find_possible_duplicates(df: pd.DataFrame, threshold: float = 0.88) -> pd.DataFrame:
    """Find records that are not exact ID duplicates but may describe the same entity."""
    candidates: list[dict] = []
    records = df.reset_index(drop=True)

    for left_index in range(len(records)):
        for right_index in range(left_index + 1, len(records)):
            left = records.iloc[left_index]
            right = records.iloc[right_index]

            name_score = similarity(left.get("client_name"), right.get("client_name"))
            email_score = similarity(left.get("email"), right.get("email"))
            combined = round((name_score * 0.6) + (email_score * 0.4), 3)

            if combined >= threshold and left.get("record_id") != right.get("record_id"):
                candidates.append(
                    {
                        "left_record_id": left.get("record_id"),
                        "right_record_id": right.get("record_id"),
                        "client_name_left": left.get("client_name"),
                        "client_name_right": right.get("client_name"),
                        "match_score": combined,
                        "decision": "human_review",
                    }
                )

    return pd.DataFrame(candidates)
