import contextlib
import importlib.util
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fts_pod_search_under_test", REPO_ROOT / "bin/fts_pod_search.py"
)
fts_pod_search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fts_pod_search)


class FtsPodSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db = Path(self.temp_dir.name) / "pods.db"
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "CREATE TABLE interactive_chain "
                "(block_height INTEGER PRIMARY KEY, merkle_root TEXT)"
            )
            conn.execute(
                "CREATE VIRTUAL TABLE pod_fts USING fts5("
                "block_height UNINDEXED, timestamp UNINDEXED, prompt_text, "
                "response_text, dossier_tags UNINDEXED)"
            )
            conn.execute(
                "INSERT INTO interactive_chain VALUES (?, ?)",
                (7, "root-seven"),
            )
            conn.execute(
                "INSERT INTO pod_fts VALUES (?, ?, ?, ?, ?)",
                (7, "2026-11-01T00:00:00Z", "thermal storage",
                 "Store heat in the masonry mass.", "energy"),
            )
            conn.execute(
                "INSERT INTO pod_fts VALUES (?, ?, ?, ?, ?)",
                (8, "2026-11-02T00:00:00Z", "thermal measurement",
                 "Measure the temperature difference.", "measurement"),
            )

    def test_search_returns_stable_evidence_ids_and_seal_metadata(self):
        first = fts_pod_search.search_pods("thermal storage", self.db, limit=1)
        second = fts_pod_search.search_pods("thermal storage", self.db, limit=1)

        self.assertEqual([7], [record["block_height"] for record in first])
        self.assertEqual(first[0]["evidence_id"], second[0]["evidence_id"])
        self.assertEqual("root-seven", first[0]["merkle_root"])

    def test_search_uses_multiple_query_terms_and_limit(self):
        records = fts_pod_search.search_pods("thermal measurement", self.db, limit=1)
        self.assertEqual(1, len(records))

    def test_missing_database_is_reported(self):
        with self.assertRaises(FileNotFoundError):
            fts_pod_search.search_pods("thermal", self.db.parent / "missing.db")

    def test_empty_search_does_not_call_model(self):
        with mock.patch.object(fts_pod_search.lumo_lib, "ollama_generate_local") as generate:
            with self.assertRaises(LookupError):
                fts_pod_search.answer_pods("no matching records", self.db)
        generate.assert_not_called()

    def test_answer_is_local_and_includes_evidence_ids_in_prompt(self):
        with mock.patch.object(
            fts_pod_search.lumo_lib, "ollama_generate_local", return_value="Store heat."
        ) as generate:
            result = fts_pod_search.answer_pods(
                "How can heat be stored?", self.db, model="local-model",
            )

        self.assertEqual("Store heat.", result["answer"])
        self.assertEqual("local-model", result["model"])
        self.assertEqual(64, len(result["database_sha256"]))
        self.assertTrue(result["evidence_ids"])
        self.assertIn(result["evidence_ids"][0], generate.call_args.args[0])

    def test_remote_model_endpoint_is_rejected(self):
        with mock.patch.object(fts_pod_search.lumo_lib, "OLLAMA_HOST", "http://example.com:11434"):
            with self.assertRaisesRegex(ValueError, "loopback"):
                fts_pod_search.answer_pods("thermal", self.db)

    def test_refuses_database_with_wal(self):
        Path(str(self.db) + "-wal").write_bytes(b"pending transactions")
        with mock.patch.object(fts_pod_search.lumo_lib, "ollama_generate_local") as generate:
            with self.assertRaisesRegex(RuntimeError, "WAL"):
                fts_pod_search.answer_pods("thermal", self.db)
        generate.assert_not_called()

    def test_cli_legacy_search_and_json_ask(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = fts_pod_search.main(["thermal", "--db", str(self.db)])
        self.assertEqual(0, status)
        self.assertIn("Evidence ID:", output.getvalue())

        with mock.patch.object(
            fts_pod_search.lumo_lib, "ollama_generate_local", return_value="Store heat."
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = fts_pod_search.main([
                    "ask", "thermal", "--db", str(self.db), "--json",
                ])
        self.assertEqual(0, status)
        self.assertIn('"evidence_ids"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
