# Operations Intake & QA Automation

A small Python workflow for a very ordinary operations problem: incoming records are rarely as tidy as the spreadsheet template says they should be.

I built this project to automate the repetitive first pass I would normally do by hand: clean the intake file, standardize common fields, catch duplicate IDs, flag incomplete records, and leave a simple QA report for review.

> Portfolio project using fictional sample data. No client or production data is included.

## The problem

An operations inbox or shared spreadsheet can collect requests from different people throughout the day. Names have extra spaces, email casing is inconsistent, statuses are typed differently, records get submitted twice, and required information is sometimes missing.

None of those problems is difficult on its own. The problem is having to check the same things every time a new batch arrives.

## What the workflow does

1. Reads a CSV intake file.
2. Normalizes column names and text values.
3. Standardizes email addresses and status values.
4. Parses received dates instead of trusting the source format.
5. Checks that required columns exist.
6. Counts missing required values.
7. Removes duplicate `record_id` entries while keeping the first record.
8. Flags statuses outside the approved list.
9. Flags rows that still need a human review.
10. Exports a timestamped clean CSV and JSON QA report.

The intention is not to automate judgment. It automates the boring checks and makes exceptions visible so a person can deal with them quickly.

## Project structure

```text
project-11-operations-automation/
├── config.yaml
├── requirements.txt
├── data/
│   └── incoming/
│       └── operations_intake.csv
├── reports/                 # generated QA reports
└── src/
    └── pipeline.py
```

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/pipeline.py
```

On macOS/Linux, activate the environment with `source .venv/bin/activate` instead.

## Why the rules live in config

I kept required fields and allowed statuses in `config.yaml` rather than burying them inside the Python file. In an actual admin workflow those rules change more often than the processing logic. Keeping them separate makes the workflow easier to maintain without rewriting the pipeline.

## QA approach

A record is not silently discarded just because something looks wrong. Duplicate IDs are removed because they are objectively duplicate submissions. Other exceptions are retained and marked with `qa_flag`, so the output still provides an audit trail for manual review.

That distinction matters in operations work: automation should reduce repetitive checking without hiding uncertain data.

## Example issues intentionally included

The fictional sample contains a duplicate request, a missing email address, mixed status formatting, uppercase email text, and one status that is outside the allowed list. They are deliberate test cases, not accidental dirty data.

## Skills demonstrated

Python, pandas, CSV processing, configurable validation rules, data cleaning, duplicate detection, exception handling, QA reporting, logging, file-based automation, and operational documentation.

## Possible next iteration

The current version is deliberately local and easy to inspect. A useful next step would be a watched intake folder or scheduled job, plus an exception queue that only sends records requiring review to a human.
