# SPDX-License-Identifier: GPL-3.0-only
import contextlib
import io
import json
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pods"))
import openroot_vector_inventory_v1 as inventory


class VectorInventoryTests(unittest.TestCase):
    def create_unified_database(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            connection.executescript(
                """
                CREATE TABLE sources (source_artifact_sha256 TEXT, source_path TEXT);
                CREATE TABLE rag_chunks (chunk_content_sha256 TEXT, chunk_text TEXT);
                CREATE TABLE embeddings (
                    chunk_content_sha256 TEXT,
                    model TEXT,
                    dimensions INTEGER,
                    embedding TEXT
                );
                """
            )

    def create_candidate_database(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            connection.execute(
                """
                CREATE TABLE embeddings (
                    chunk_content_sha256 TEXT,
                    chunk_text TEXT,
                    source_artifact_sha256 TEXT,
                    source_path TEXT,
                    model TEXT,
                    dimensions INTEGER,
                    embedding TEXT
                )
                """
            )
            connection.execute(
                "INSERT INTO embeddings VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    hashlib.sha256(b"an indexed document chunk").hexdigest(),
                    "an indexed document chunk",
                    "b" * 64,
                    "/home/jesse/openroot/docs/example.md",
                    "nomic-embed-text",
                    768,
                    json.dumps([0.0] * 768),
                ),
            )

    def test_inventory_reports_compatibility_without_modifying_databases(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            candidate = home / "pods" / "vector-index.db"
            unified = home / "recovery-evidence" / "unified.db"
            self.create_candidate_database(candidate)
            self.create_unified_database(unified)

            before = candidate.read_bytes()
            report = inventory.build_report(home, unified)

            self.assertEqual(candidate.read_bytes(), before)
            self.assertFalse(report["merge_performed"])
            self.assertEqual(len(report["candidate_databases"]), 1)
            result = report["candidate_databases"][0]
            self.assertEqual(result["integrity_check"], "ok")
            self.assertEqual(result["embedding_models"], ["nomic-embed-text"])
            self.assertEqual(result["embedding_dimensions"], [768])
            self.assertTrue(result["chunk_content_sha256_recoverable"])
            self.assertTrue(result["chunk_text_present"])
            self.assertTrue(result["source_provenance_recoverable"])
            self.assertTrue(result["compatible_with_unified_embeddings_table"])
            self.assertEqual(result["recommended_merge_strategy"], "SAFE_MERGE")
            self.assertIn("CREATE TABLE", result["tables"]["embeddings"]["create_table_sql"])

    def test_discovery_excludes_backups_and_sidecars(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            pods = home / "pods"
            pods.mkdir()
            for name in (
                "vector.db",
                "vector.db-wal",
                "vector-backup.db",
                "credentials.sqlite",
            ):
                (pods / name).touch()
            self.assertEqual(
                [path.name for path in inventory.iter_database_files(home)],
                ["vector.db"],
            )

    def test_missing_model_values_cannot_be_marked_safe(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            candidate = home / "pods" / "vector-index.db"
            unified = home / "recovery-evidence" / "unified.db"
            self.create_candidate_database(candidate)
            self.create_unified_database(unified)
            with sqlite3.connect(candidate) as connection:
                connection.execute(
                    "INSERT INTO embeddings VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        hashlib.sha256(b"another chunk").hexdigest(),
                        "another chunk",
                        "d" * 64,
                        "/home/jesse/openroot/docs/another.md",
                        None,
                        768,
                        json.dumps([0.0] * 768),
                    ),
                )

            result = inventory.build_report(home, unified)["candidate_databases"][0]
            self.assertEqual(
                result["recommended_merge_strategy"], "CONDITIONAL_MERGE"
            )

    def test_hash_that_does_not_match_chunk_text_is_not_mergeable(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            candidate = home / "pods" / "vector-index.db"
            unified = home / "recovery-evidence" / "unified.db"
            self.create_candidate_database(candidate)
            self.create_unified_database(unified)
            with sqlite3.connect(candidate) as connection:
                connection.execute(
                    "UPDATE embeddings SET chunk_content_sha256 = ?",
                    ("c" * 64,),
                )

            result = inventory.build_report(home, unified)["candidate_databases"][0]
            self.assertFalse(result["chunk_content_sha256_recoverable"])
            self.assertEqual(result["recommended_merge_strategy"], "DO_NOT_MERGE")

    def test_indirect_chunk_and_source_links_are_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            candidate = home / "pods" / "vector-index.sqlite"
            unified = home / "recovery-evidence" / "unified.db"
            candidate.parent.mkdir(parents=True)
            with sqlite3.connect(candidate) as connection:
                connection.executescript(
                    f"""
                    CREATE TABLE embeddings (
                        chunk_id INTEGER, model TEXT, dim INTEGER, vector TEXT
                    );
                    CREATE TABLE chunks (
                        id INTEGER, content_sha256 TEXT, chunk_text TEXT,
                        source_id INTEGER
                    );
                    CREATE TABLE sources (
                        id INTEGER, artifact_sha256 TEXT, source_path TEXT
                    );
                    INSERT INTO sources VALUES (
                        7, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
                        '/home/jesse/openroot/docs/source.md'
                    );
                    INSERT INTO chunks VALUES (
                        9, '{hashlib.sha256(b"recoverable text").hexdigest()}',
                        'recoverable text', 7
                    );
                    """
                )
                connection.execute(
                    "INSERT INTO embeddings VALUES (?, ?, ?, ?)",
                    (9, "nomic-embed-text", 768, json.dumps([0.0] * 768)),
                )
            self.create_unified_database(unified)

            result = inventory.build_report(home, unified)["candidate_databases"][0]
            self.assertTrue(result["source_provenance_recoverable"])
            self.assertEqual(result["vectors_with_complete_mapping"], 1)
            self.assertEqual(result["vectors_with_verified_chunk_hash"], 1)
            self.assertEqual(result["recommended_merge_strategy"], "SAFE_MERGE")

    def test_report_writer_creates_unique_timestamped_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = {"merge_performed": False, "candidate_databases": []}
            first = inventory.write_report(report, root)
            second = inventory.write_report(report, root)
            self.assertTrue(first.is_file())
            self.assertTrue(second.is_file())
            self.assertNotEqual(first.parent, second.parent)
            self.assertEqual(json.loads(first.read_text())["merge_performed"], False)

    def test_main_prints_report_path_and_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            unified = home / "recovery-evidence" / "unified.db"
            self.create_unified_database(unified)
            self.create_candidate_database(home / "pods" / "vector-index.db")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                inventory.main(home, unified, home / "recovery-evidence")

            lines = output.getvalue().splitlines()
            self.assertTrue(lines[0].startswith("Report: "))
            self.assertIn("1 candidate(s); 1 safe", lines[1])
            self.assertTrue(Path(lines[0].removeprefix("Report: ")).is_file())


if __name__ == "__main__":
    unittest.main()
