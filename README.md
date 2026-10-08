# LMS Data Sync — Python ETL Pipeline

This is a small portfolio project I put together to demonstrate some of the data engineering concepts I've worked with professionally.

The project is inspired by my experience building and maintaining a data integration using **Instructure's Canvas Data Access Platform (DAP) library** to synchronize data between Canvas and a target database.

This version is strictly a test project. It uses synthetic data, CSV files, and a local SQLite database to demonstrate similar ETL concepts without relying on any company systems, production data, or proprietary code.

## What it does

The project covers several common data engineering tasks:

- **Incremental data syncing:** Processes sample course, user, enrollment, and submission records without reloading everything each time.
- **Inserts and updates:** Uses upserts to handle new and modified records while avoiding duplicates.
- **Checkpoint tracking:** Keeps track of successful syncs so the pipeline knows where to pick up.
- **Data validation:** Checks incoming records and handles timestamps before loading them.
- **Logging:** Records processing activity to make it easier to troubleshoot issues.
- **Unit testing:** Includes tests for repeated runs, updated records, and invalid timestamps.

## Getting started

You'll need Python 3.10 or newer. Everything runs using Python's standard library, so there's nothing extra to install.

**Linux / macOS:**

```bash
PYTHONPATH=src python -m canvas_sync.sync
PYTHONPATH=src python -m unittest discover -s tests -v
```

**Windows PowerShell:**

```powershell
$env:PYTHONPATH = "src"
python -m canvas_sync.sync
python -m unittest discover -s tests -v
```

The pipeline creates a local SQLite database at `output/demo.sqlite3`.

You can run it multiple times without creating duplicate records. If you want to start over, just delete the database and run the script again.

## Background

The original integration I worked on used **Instructure's Canvas DAP library** to synchronize LMS data into a target database for reporting and other downstream uses.

Working on that integration gave me hands-on experience with data synchronization, handling large datasets, troubleshooting failed or lengthy syncs, and maintaining data pipelines.

I wanted a way to demonstrate some of those same skills on GitHub, so I built this simplified example from scratch.

There are a few important differences between this demo and the original integration:

- This project uses CSV files instead of connecting to Canvas through the DAP library.
- All data is fictional and was created specifically for testing.
- SQLite replaces the actual target database environment.
- The pipeline focuses on core ETL functionality rather than replicating a production integration.

This is also intentionally a simplified implementation. It doesn't handle everything a production pipeline would, such as deleted records, schema changes, API pagination, or more advanced recovery scenarios.

## Why I built this

I wanted to have something on GitHub that demonstrates my experience with Python, ETL development, database integration, and incremental data processing.

Since the work I performed for my previous employer is not mine to publish, I created this independent example using general data engineering practices.

**This repository is for demonstration and testing purposes only.** It is not the original Instructure integration, contains no employer-owned code or data, and is not intended to be used as a production Canvas Data 2 synchronization tool.
