import pandas as pd

from src.quality import score_records


REQUIRED = ["record_id", "client_name", "email", "status", "received_at"]
ALLOWED = ["new", "in_progress", "waiting", "completed"]


def test_clean_record_scores_100():
    df = pd.DataFrame([
        {
            "record_id": "REQ-1",
            "client_name": "Example Office",
            "email": "ops@example.com",
            "status": "new",
            "received_at": pd.Timestamp("2026-08-20"),
        }
    ])

    scored, summary = score_records(df, REQUIRED, ALLOWED)

    assert scored.loc[0, "quality_score"] == 100
    assert not bool(scored.loc[0, "review_required"])
    assert summary.perfect_records == 1


def test_bad_email_and_status_are_sent_to_review():
    df = pd.DataFrame([
        {
            "record_id": "REQ-2",
            "client_name": "Example Office",
            "email": "not-an-email",
            "status": "unknown",
            "received_at": pd.Timestamp("2026-08-20"),
        }
    ])

    scored, summary = score_records(df, REQUIRED, ALLOWED)

    assert scored.loc[0, "quality_score"] < 100
    assert bool(scored.loc[0, "review_required"])
    assert summary.review_records == 1
