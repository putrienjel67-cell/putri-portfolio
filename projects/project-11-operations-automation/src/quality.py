from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@dataclass
class QualitySummary:
    average_score: float
    perfect_records: int
    review_records: int


def _email_is_valid(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(EMAIL_PATTERN.match(str(value).strip()))


def score_records(df: pd.DataFrame, required_fields: list[str], allowed_statuses: list[str]) -> tuple[pd.DataFrame, QualitySummary]:
    scored = df.copy()
    scores: list[int] = []
    reasons: list[str] = []

    for _, row in scored.iterrows():
        score = 100
        issues: list[str] = []

        missing = [field for field in required_fields if pd.isna(row.get(field))]
        if missing:
            score -= min(50, len(missing) * 15)
            issues.append("missing:" + ",".join(missing))

        if not _email_is_valid(row.get("email")):
            score -= 20
            issues.append("invalid_email")

        status = row.get("status")
        if pd.isna(status) or status not in allowed_statuses:
            score -= 15
            issues.append("status_outside_rules")

        if pd.isna(row.get("received_at")):
            score -= 15
            issues.append("invalid_received_at")

        scores.append(max(0, score))
        reasons.append(";".join(issues) if issues else "clean")

    scored["quality_score"] = scores
    scored["quality_notes"] = reasons
    scored["review_required"] = scored["quality_score"] < 100

    summary = QualitySummary(
        average_score=round(float(scored["quality_score"].mean()), 2) if len(scored) else 0.0,
        perfect_records=int((scored["quality_score"] == 100).sum()),
        review_records=int(scored["review_required"].sum()),
    )
    return scored, summary
