import pandas as pd

from src.master_match import match_to_master


def test_exact_email_is_safe_match():
    incoming = pd.DataFrame([
        {"record_id": "NEW-1", "client_name": "Northwind Studio", "email": "hello@northwind.example", "request_type": "contact update"}
    ])
    master = pd.DataFrame([
        {"record_id": "MASTER-9", "client_name": "Northwind Studio", "email": "hello@northwind.example", "request_type": "contact update"}
    ])

    result = match_to_master(incoming, master)

    assert result.loc[0, "decision"] == "safe_match"
    assert result.loc[0, "master_record_id"] == "MASTER-9"
    assert result.loc[0, "match_score"] == 1.0


def test_close_name_requires_review_not_auto_merge():
    incoming = pd.DataFrame([
        {"record_id": "NEW-2", "client_name": "Blue Harbor Company", "email": "new@blueharbor.example", "request_type": "crm enrichment"}
    ])
    master = pd.DataFrame([
        {"record_id": "MASTER-10", "client_name": "Blue Harbor Co", "email": "admin@blueharbor.example", "request_type": "crm enrichment"}
    ])

    result = match_to_master(incoming, master, threshold=0.85)

    assert result.loc[0, "decision"] == "review_match"
    assert result.loc[0, "master_record_id"] == "MASTER-10"
