"""Load sample LMS records into SQLite, keeping track of the last successful sync.

This is a standalone portfolio example, not an export of a production integration.
"""

import argparse
import csv
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger(__name__)
DATASETS = ("courses", "enrollments", "submissions", "users")


def connect_db(path: Path) -> sqlite3.Connection:
    """Create a local database and the tables used by the demo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS records (
            dataset TEXT NOT NULL,
            record_id TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY (dataset, record_id)
        );
        CREATE TABLE IF NOT EXISTS checkpoints (
            dataset TEXT PRIMARY KEY,
            updated_at TEXT NOT NULL
        );
    """)
    return connection


def parse_timestamp(value: str) -> datetime:
    """Require timezone-aware timestamps so comparisons are predictable."""
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return timestamp.astimezone(timezone.utc)


def read_sample_rows(path: Path, dataset: str) -> list[dict[str, str]]:
    """Read the mock export. A production connector would replace this step."""
    with (path / f"{dataset}.csv").open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        if not row.get("id") or not row.get("updated_at"):
            raise ValueError(f"Invalid row in {dataset}: id and updated_at are required")
        parse_timestamp(row["updated_at"])
    return rows


def sync_dataset(connection: sqlite3.Connection, dataset: str, rows: list[dict[str, str]]) -> int:
    """Upsert changed rows and advance the checkpoint after the batch succeeds.

    Rows sharing a checkpoint timestamp are replayed safely on the next run.
    This avoids skipping records at the exact boundary.
    """
    import json

    if dataset not in DATASETS:
        raise ValueError(f"Unknown dataset: {dataset}")

    checkpoint_row = connection.execute(
        "SELECT updated_at FROM checkpoints WHERE dataset = ?", (dataset,)
    ).fetchone()
    checkpoint = parse_timestamp(checkpoint_row[0]) if checkpoint_row else None
    changed = [row for row in rows if checkpoint is None or parse_timestamp(row["updated_at"]) >= checkpoint]
    # Process older updates first. The record guard below prevents stale overwrites.
    changed.sort(key=lambda row: parse_timestamp(row["updated_at"]))

    with connection:
        for row in changed:
            timestamp = parse_timestamp(row["updated_at"]).isoformat()
            connection.execute("""
                INSERT INTO records (dataset, record_id, updated_at, payload)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(dataset, record_id) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                WHERE excluded.updated_at >= records.updated_at
            """, (dataset, row["id"], timestamp, json.dumps(row, sort_keys=True)))

        if changed:
            latest = max(parse_timestamp(row["updated_at"]) for row in changed).isoformat()
            connection.execute("""
                INSERT INTO checkpoints (dataset, updated_at) VALUES (?, ?)
                ON CONFLICT(dataset) DO UPDATE SET updated_at = excluded.updated_at
            """, (dataset, latest))
    return len(changed)


def run(data_dir: Path, db_path: Path) -> dict[str, int]:
    """Sync the four demo datasets and report the processed row counts."""
    counts = {}
    with connect_db(db_path) as connection:
        for dataset in DATASETS:
            rows = read_sample_rows(data_dir, dataset)
            counts[dataset] = sync_dataset(connection, dataset, rows)
            LOG.info("%s: processed %d rows", dataset, counts[dataset])
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local, synthetic LMS data sync")
    parser.add_argument("--data-dir", type=Path, default=Path("sample_data"))
    parser.add_argument("--db", type=Path, default=Path("output/demo.sqlite3"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run(args.data_dir, args.db)


if __name__ == "__main__":
    main()
