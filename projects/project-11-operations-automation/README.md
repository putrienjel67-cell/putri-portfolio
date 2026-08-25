# Operations Control Desk — Data Intake, QA & Reconciliation

Most data-entry problems do not begin with typing. They begin when several people, files, and systems describe the same business information differently.

This project is a local Python operations system built around that messier reality. It takes an incoming operational dataset, standardizes it, checks data quality, separates uncertain records for review, looks for possible duplicate entities, records automated changes, and produces a clean master dataset plus an operations report.

> Portfolio project using fictional sample data. It is designed to demonstrate workflow thinking and technical implementation without presenting simulated work as client work.

## Why I built it

My earlier portfolio work covers individual operations tasks such as spreadsheet cleanup, research, list building, database updates, file organization, reporting, and administrative support. Here I wanted to connect those ideas into one controlled workflow rather than another isolated spreadsheet exercise.

The main design question was: **what should a machine safely decide, and what should it hand back to a person?**

Exact duplicate IDs can be handled automatically. A suspiciously similar company name cannot always be. Missing information should not disappear. A cleaned value should still be traceable to what arrived originally.

Those decisions shaped the system.

## Processing flow

```text
Incoming CSV
    |
    v
Schema check + normalization
    |
    v
Exact duplicate handling
    |
    v
Record-level quality scoring
    |---------------------> Review queue
    |
    v
Possible entity reconciliation
    |---------------------> Human match review
    |
    v
Clean master dataset
    |
    +----> Field-level audit log
    +----> JSON operations report
```

## What happens during a run

- Required columns are checked before processing continues.
- Text, email casing, status labels, and dates are normalized.
- Exact duplicate request IDs are removed deterministically.
- Every remaining record receives a quality score from 0–100.
- Missing required values, malformed email addresses, unsupported statuses, and invalid dates reduce that score.
- Records below 100 are routed to a separate review queue.
- A fuzzy reconciliation pass looks for different IDs that may refer to the same entity.
- Possible matches are never merged automatically; they are exported with a match score for human review.
- Field-level changes are written to an audit file with before/after values.
- The run finishes with a machine-readable JSON summary for reporting or a future dashboard.

## Repository structure

```text
project-11-operations-automation/
├── config.yaml
├── requirements.txt
├── data/
│   ├── incoming/
│   │   └── operations_intake.csv
│   ├── processed/       # generated master datasets
│   ├── review/          # exception queues and possible matches
│   └── audit/           # generated field-change logs
├── reports/             # generated run summaries
├── src/
│   ├── pipeline.py
│   ├── quality.py
│   ├── reconciliation.py
│   └── audit.py
└── tests/
    └── test_quality.py
```

## Configuration instead of hard-coded business rules

`config.yaml` controls required fields, accepted statuses, output locations, and the fuzzy-match threshold. I separated those rules from the Python modules because operational requirements change more often than the mechanics of reading and writing data.

## Quality scoring

A perfect record starts at 100. The score is reduced when required information is missing or when important fields fail validation. The score is not intended to pretend that data quality is mathematically objective. Its purpose is prioritization: clean records can continue, while questionable records become visible in the review queue.

## Reconciliation

Exact duplicates and possible duplicates are deliberately treated differently.

An identical `record_id` is deterministic enough to remove from the working dataset. Two records with similar company names or emails may represent the same entity, but automatically merging them risks destroying valid information. The reconciliation module therefore creates candidate pairs and leaves the final decision to a person.

That human-in-the-loop boundary is intentional.

## Auditability

Cleaning data without recording what changed makes troubleshooting difficult. The audit module compares the incoming record with the normalized record and records field-level before/after values. This creates a lightweight trace of what the automation changed rather than leaving only the final output.

## Automated checks

The repository includes pytest coverage for core quality-scoring behavior. A GitHub Actions workflow installs the project, runs the tests, and executes the sample pipeline whenever Project 11 changes in a push or pull request.

That gives the project two layers of QA: the system checks business data, while CI checks the system itself.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/pipeline.py
pytest -q
```

On macOS/Linux use `source .venv/bin/activate`.

## Outputs

A successful run can produce four kinds of evidence:

1. **Master dataset** — normalized records with QA fields and quality scores.
2. **Review queue** — records that still require judgment or missing-data follow-up.
3. **Reconciliation candidates** — possible cross-record matches with similarity scores.
4. **Audit + operations report** — traceable changes and run-level metrics.

## What this project demonstrates

This is not intended as a claim that every data-entry task should be automated. It demonstrates how repetitive data operations can be made more controlled: Python/pandas processing, schema validation, data normalization, QA rules, record scoring, duplicate management, fuzzy reconciliation, exception routing, human review, audit trails, configuration management, automated testing, CI, and operational reporting.

## Next build stage

The current architecture is deliberately file-based so every input and output can be inspected. The next stage is to add multi-source Excel/CSV intake, batch manifests, reconciliation against a separate master-data source, a small operations dashboard, and scheduled processing. Those additions will sit on top of the same review and audit principles rather than replacing them.
