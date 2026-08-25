from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROCESSED = ROOT / "data" / "processed"
REVIEW = ROOT / "data" / "review"

st.set_page_config(page_title="Operations Control Center", layout="wide")
st.title("Operations Control Center")
st.caption("A compact view of intake health, exceptions, and data quality. Fictional portfolio data only.")

report_files = sorted(REPORTS.glob("operations_report_*.json"), reverse=True)
master_files = sorted(PROCESSED.glob("master_data_*.csv"), reverse=True)
review_files = sorted(REVIEW.glob("review_queue_*.csv"), reverse=True)

if not report_files or not master_files:
    st.info("Run the pipeline first. The dashboard reads the most recent generated outputs.")
    st.stop()

report = json.loads(report_files[0].read_text(encoding="utf-8"))
data = pd.read_csv(master_files[0])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows received", report["rows_received"])
col2.metric("Rows written", report["rows_written"])
col3.metric("Average quality", f"{report['quality']['average_score']:.1f}/100")
col4.metric("Needs review", report["quality"]["review_records"])

st.subheader("Status distribution")
st.bar_chart(data["status"].fillna("missing").value_counts())

st.subheader("Quality distribution")
st.bar_chart(data["quality_score"].value_counts().sort_index())

st.subheader("Latest master data")
st.dataframe(data, use_container_width=True, hide_index=True)

st.subheader("Human review queue")
if review_files:
    review = pd.read_csv(review_files[0])
    if review.empty:
        st.success("No records require manual review in the latest run.")
    else:
        st.dataframe(review, use_container_width=True, hide_index=True)
else:
    st.write("No review queue has been generated yet.")

st.subheader("Run details")
st.json(report)
