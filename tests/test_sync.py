"""Basic checks for the incremental-load logic."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from canvas_sync.sync import connect_db, parse_timestamp, run, sync_dataset


class SyncTests(unittest.TestCase):
    def test_repeated_run_does_not_duplicate_records(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "test.sqlite3"
            samples = Path(__file__).resolve().parents[1] / "sample_data"
            run(samples, database)
            run(samples, database)
            with sqlite3.connect(database) as connection:
                count = connection.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            self.assertEqual(count, 8)

    def test_newer_update_replaces_existing_row(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect_db(Path(directory) / "test.sqlite3") as connection:
                sync_dataset(connection, "courses", [{"id": "c1", "updated_at": "2026-01-01T00:00:00Z", "name": "Old"}])
                sync_dataset(connection, "courses", [{"id": "c1", "updated_at": "2026-01-02T00:00:00Z", "name": "New"}])
                payload = connection.execute("SELECT payload FROM records").fetchone()[0]
            self.assertIn('"New"', payload)

    def test_timestamps_require_timezone(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2026-01-01T00:00:00")

    def test_bad_batch_does_not_advance_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect_db(Path(directory) / "test.sqlite3") as connection:
                with self.assertRaises(ValueError):
                    sync_dataset(connection, "courses", [{"id": "c1", "updated_at": "not-a-date"}])
                self.assertIsNone(connection.execute("SELECT updated_at FROM checkpoints").fetchone())


if __name__ == "__main__":
    unittest.main()
