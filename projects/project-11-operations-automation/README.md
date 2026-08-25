# Operations Control Desk — Multi-Source Data Operations Automation

Most data-entry problems do not begin with typing. They begin when several people, exports, spreadsheets, and systems describe the same business information differently.

This project is a Python-based operations system built around that messier reality. It accepts multiple CSV and Excel sources, tags each record with its origin, validates and standardizes the data, scores quality, separates uncertain records for review, checks for possible duplicate entities, compares records with prior master data, records automated changes, and produces clean operational outputs plus dashboard-ready metrics.

> Portfolio project using fictional sample data. No client or production data is included.

## The business problem

A real operations queue can receive a CRM export, a vendor spreadsheet, a form download, and a manually maintained tracker in the same week. Each source can be individually reasonable while still creating conflicts when the records are combined.

The hard part is not copying one row into another file. It is deciding which differences are harmless formatting issues, which records are duplicates, which values can be standardized safely, and which cases need a person to look at them.

That is the problem this project models.

## Design principle

**Automate repeatable checks. Keep uncertain business decisions visible.**

The system can safely trim whitespace, normalize email casing, standardize known status labels, parse dates, reject unusable schemas, remove exact duplicate IDs, and calculate operational QA metrics. It can also suggest likely entity matches.

It does not silently merge fuzzy matches or discard incomplete records just because they are inconvenient.

## End-to-end flow

```text
CSV / Excel sources
        |
        v
Batch intake + source tagging
        |
        v
Schema checks + normalization
        |
        v
Exact duplicate handling
        |
        v
Record-level quality scoring
        |
        +--------------------> Human review queue
        |
        v
Cross-record reconciliation
        |
        +--------------------> Possible-match review
        |
        v
Previous-master comparison
        |
        +----> exact email = safe match
        +----> close fuzzy match = review match
        +----> no match = new record
        |
        v
Master data output
        |
        +----> field-level audit log
        +----> JSON operations report
        +----> dashboard payload
        +----> run history
```

A more detailed architecture note is available in `docs/architecture.md`.

## What happens during a run

The intake layer scans the incoming folder for supported CSV and Excel files. A broken or unsupported source is recorded as a rejection instead of stopping the entire batch. Valid files are combined and each record keeps a `source_file` field so its origin remains traceable.

The processing layer then normalizes common text fields, email casing, status labels, and dates. Required fields are validated and exact duplicate request IDs are handled deterministically.

Every remaining record receives a quality score from 0–100. Missing required values, malformed email addresses, unsupported statuses, and invalid dates reduce the score. A score below 100 routes the record into the human-review queue rather than deleting it.

The reconciliation layer looks for records that may refer to the same entity even when names differ slightly. Separately, the master-match layer compares the current batch with the previous master output. Exact email matches can be marked safe, while fuzzy matches are exported as review decisions rather than merged automatically.

Finally, the system writes a master dataset, review queues, reconciliation candidates, master-match decisions, a field-level audit log, an operations report, dashboard data, and rolling run history.

## Interactive dashboard

The Streamlit dashboard in `dashboard/app.py` turns generated outputs into a compact operations control center. It includes:

- rows received and written
- average quality score
- current review workload
- possible entity matches
- safe master matches
- rejected-source count
- status distribution
- quality distribution
- latest master dataset
- latest human-review queue
- historical quality and review trends across runs

Run it locally with:

```bash
streamlit run dashboard/app.py
```

## Scheduled automation

Project 11 includes a separate GitHub Actions workflow for unattended weekday processing. The workflow can also be started manually. It installs the project, runs the operations pipeline, and uploads generated processed data, review queues, audit logs, and reports as a workflow artifact.

The schedule demonstrates how the same local pipeline can become a recurring operational job without rewriting the core logic.

## Repository structure

```text
project-11-operations-automation/
├── config.yaml
├── requirements.txt
├── run_daily.py
├── data/
│   ├── incoming/
│   │   ├── operations_intake.csv
│   │   ├── crm_export.csv
│   │   └── vendor_requests.csv
│   ├── processed/
│   ├── review/
│   └── audit/
├── dashboard/
│   ├── app.py
│   └── data/
├── docs/
│   └── architecture.md
├── reports/
├── src/
│   ├── pipeline.py
│   ├── intake.py
│   ├── quality.py
│   ├── reconciliation.py
│   ├── master_match.py
│   ├── audit.py
│   ├── dashboard.py
│   └── history.py
└── tests/
    ├── test_quality.py
    ├── test_intake.py
    └── test_master_match.py
```

## Why the sample sources overlap

The fictional sources intentionally contain a mix of exact matches, near matches, inconsistent capitalization, unsupported statuses, missing values, and different request wording.

For example, `Blue Harbor Co` and `Blue Harbor Company` are deliberately close enough to test reconciliation behavior. The system should notice the similarity, but it should not pretend that similarity alone proves they are the same business record.

That distinction is one of the main reasons this project exists.

## Configuration instead of buried rules

Required fields, accepted statuses, source locations, output locations, and matching thresholds live in `config.yaml` rather than being scattered throughout the Python modules. Operational rules tend to change more often than file-processing mechanics, so separating them makes the system easier to inspect and maintain.

## Auditability

Cleaning data without recording what changed makes troubleshooting difficult. The audit module records field-level before/after values so the automation does not leave only the final answer behind.

Run-level history is also retained, which makes it possible to see whether average data quality improves, exception volume rises, or review workload changes over time.

## Automated checks

The CI workflow runs pytest and then executes the sample pipeline whenever Project 11 changes. Tests cover quality scoring, multi-source intake, and the distinction between safe master matches and fuzzy matches that require review.

This gives the project two QA layers: the system checks business data, while CI checks the system itself.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/pipeline.py
pytest -q
streamlit run dashboard/app.py
```

On macOS/Linux use `source .venv/bin/activate`.

## What this demonstrates

Project 11 combines data entry and data operations rather than treating them as separate worlds: multi-source ingestion, spreadsheet/CSV handling, schema validation, normalization, data-quality scoring, duplicate management, master-data reconciliation, exception routing, human review, audit trails, batch history, reporting, dashboarding, automated tests, CI, and scheduled automation.

The goal is not to make automation look magical. The goal is to show where automation is useful, where evidence should be preserved, and where a human decision still matters.
