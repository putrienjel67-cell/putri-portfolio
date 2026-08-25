from __future__ import annotations

from difflib import SequenceMatcher

import pandas as pd


def _similarity(left: object, right: object) -> float:
    if pd.isna(left) or pd.isna(right):
        return 0.0
    return SequenceMatcher(None, str(left).lower().strip(), str(right).lower().strip()).ratio()


def match_to_master(incoming: pd.DataFrame, master: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
    """Match incoming rows to an existing master without auto-merging uncertain candidates."""
    if master.empty or incoming.empty:
        return pd.DataFrame(columns=["record_id", "master_record_id", "match_score", "match_method", "decision"])

    matches: list[dict] = []
    for _, row in incoming.iterrows():
        email = str(row.get("email", "")).lower().strip()
        exact = master.loc[master["email"].astype("string").str.lower().str.strip() == email] if email else master.iloc[0:0]
        if not exact.empty:
            candidate = exact.iloc[0]
            matches.append({
                "record_id": row.get("record_id"),
                "master_record_id": candidate.get("record_id"),
                "match_score": 1.0,
                "match_method": "exact_email",
                "decision": "safe_match",
            })
            continue

        best_score = 0.0
        best_id = None
        for _, candidate in master.iterrows():
            name_score = _similarity(row.get("client_name"), candidate.get("client_name"))
            request_score = _similarity(row.get("request_type"), candidate.get("request_type"))
            score = round((name_score * 0.8) + (request_score * 0.2), 4)
            if score > best_score:
                best_score = score
                best_id = candidate.get("record_id")

        if best_score >= threshold:
            decision = "review_match"
        else:
            decision = "new_record"
            best_id = None

        matches.append({
            "record_id": row.get("record_id"),
            "master_record_id": best_id,
            "match_score": best_score,
            "match_method": "fuzzy_name_request" if best_id else "none",
            "decision": decision,
        })

    return pd.DataFrame(matches)
