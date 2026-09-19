import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "bin/sqlite_params.py"


class SqliteParamsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database = Path(self.temp_dir.name) / "test.db"
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "CREATE TABLE records (id INTEGER PRIMARY KEY, value TEXT, note TEXT)"
            )

    def run_helper(self, sql, *values):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.database), sql, *values],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_write_binds_values_literally_and_commits_them(self):
        value = "O'Brien'); DROP TABLE records; --"

        result = self.run_helper(
            "INSERT INTO records (value, note) VALUES (?, ?)", value, "saved"
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                [(value, "saved")],
                connection.execute("SELECT value, note FROM records").fetchall(),
            )

    def test_query_prints_rows_with_null_as_an_empty_field(self):
        with sqlite3.connect(self.database) as connection:
            connection.executemany(
                "INSERT INTO records (value, note) VALUES (?, ?)",
                [("alpha", None), ("beta", "two")],
            )

        result = self.run_helper(
            "SELECT value, note FROM records WHERE value IN (?, ?) ORDER BY id",
            "alpha",
            "beta",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("alpha|\nbeta|two\n", result.stdout)

    def test_missing_database_and_sql_reports_usage(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("usage: sqlite_params.py <database> <sql> [value ...]", result.stderr)


if __name__ == "__main__":
    unittest.main()
