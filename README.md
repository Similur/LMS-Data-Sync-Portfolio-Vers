# LMS Data Sync — Incremental Pipeline Demo

A small Python portfolio project based on general learning-management-system integration patterns. It uses **fully synthetic records**, a local SQLite database, and a CSV-based mock source. No access to Canvas, Microsoft Fabric, or an employer system is required.

## What it shows

- Incremental synchronization of example courses, users, enrollments, and submissions datasets
- Repeatable upserts so rerunning a batch does not duplicate records
- Per-dataset checkpoints, with transaction-backed updates
- Basic schema checks, UTC timestamp handling, and logging
- Unit tests covering repeated loads, changed records, and invalid timestamps

## Run it

Requires Python 3.10+ and only the standard library.

```bash
PYTHONPATH=src python -m canvas_sync.sync
PYTHONPATH=src python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m canvas_sync.sync
python -m unittest discover -s tests -v
```

Results are written to `output/demo.sqlite3`. Repeated runs are safe. Deleting the database starts a fresh demo sync.

## Project context and boundaries

This is a **new illustrative implementation**, not the original code used at a previous employer. It intentionally does not use Instructure's DAP client or reproduce a production Canvas Data 2 API call, table schema, organizational architecture, configuration, or error logs. The CSV source is a placeholder for where an approved production data connector would go.

The sample dataset names reflect common LMS concepts, not an export of proprietary data. Values, IDs, dates, and records were created for this demo.

**Important:** This example models a simplified timestamp-based sync. It does not support deletes, schema evolution, pagination, provider-specific cursors, or full production recovery semantics. Real Canvas Data 2 integrations should use documented provider interfaces and their supported synchronization rules.

## Why make this public?

The repository demonstrates general-purpose Python ETL skills—validation, loading, upserts, checkpoints, and tests—without sharing any work product, student information, internal endpoints, or secrets from an employer.

## License and publication

No license is included automatically. Add a license only if you are comfortable granting those rights to others. Review your employment agreement and confidentiality obligations before publishing anything derived from work done for an employer.
