import contextlib
import importlib.util
import io
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "knowledge_probe_under_test", REPO_ROOT / "bin/knowledge_probe_v1.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class KnowledgeProbeTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.data = self.root / "data"
        self.data.mkdir()
        self.module.ROOT = str(self.root)
        self.module.DATA_DIR = str(self.data)
        self.module.CACHE_DB = str(self.data / "proof_cache.db")
        self.module.REPORT_PATH = str(self.root / "analysis" / "report.md")

    def test_q_escapes_sqlite_identifiers(self):
        self.assertEqual('"plain"', self.module.q("plain"))
        self.assertEqual('"odd""name"', self.module.q('odd"name'))

    def test_scan_dbs_finds_terms_without_rowid_and_skips_cache(self):
        db_path = self.data / "ledger.db"
        with sqlite3.connect(db_path) as con:
            con.execute('CREATE TABLE "odd table" ("select" TEXT PRIMARY KEY, note TEXT) WITHOUT ROWID')
            con.execute('INSERT INTO "odd table" VALUES (?, ?)', ("key", "Newton chain theorem"))
        with sqlite3.connect(self.module.CACHE_DB) as con:
            con.execute("CREATE TABLE decoy (value TEXT)")
            con.execute("INSERT INTO decoy VALUES ('Newton chain theorem')")

        hits = self.module.scan_dbs()

        matching = [hit for hit in hits if hit["term"] in {"newton chain", "newton", "theorem"}]
        self.assertTrue(matching)
        self.assertTrue(all(hit["db"] == "ledger.db" for hit in hits))
        self.assertTrue(all(hit["table"] == "odd table" for hit in hits))
        self.assertTrue(all(hit["rowid"] == "match 1" for hit in matching))
        self.assertTrue(any("Newton chain theorem" in hit["snippet"] for hit in matching))

    def test_scan_dbs_returns_empty_for_tables_without_columns(self):
        with sqlite3.connect(self.data / "empty.db"):
            pass
        self.assertEqual([], self.module.scan_dbs())

    def test_scan_files_returns_nonempty_paths_and_builds_bounded_grep(self):
        completed = subprocess.CompletedProcess([], 0, stdout="/one.md\n\n/two.py\n", stderr="")
        with mock.patch.object(self.module.subprocess, "run", return_value=completed) as run:
            self.assertEqual(["/one.md", "/two.py"], self.module.scan_files())

        cmd = run.call_args.args[0]
        self.assertEqual("grep", cmd[0])
        self.assertIn("--exclude-dir=.git", cmd)
        self.assertIn("--include=*.py", cmd)
        self.assertEqual(str(self.root), cmd[-1])
        self.assertEqual(300, run.call_args.kwargs["timeout"])

    def test_scan_files_failure_is_held(self):
        output = io.StringIO()
        with mock.patch.object(self.module.subprocess, "run", side_effect=subprocess.TimeoutExpired("grep", 300)), contextlib.redirect_stdout(output):
            self.assertEqual([], self.module.scan_files())
        self.assertIn("file sweep failed", output.getvalue())

    def test_ollama_serializes_request_and_returns_response(self):
        with mock.patch.object(
            self.module.urllib.request, "urlopen", return_value=Response({"response": "answer"})
        ) as urlopen:
            self.assertEqual("answer", self.module.ollama("prompt", "model", timeout=11))
        request = urlopen.call_args.args[0]
        self.assertEqual(self.module.OLLAMA_URL, request.full_url)
        self.assertEqual(
            {"model": "model", "prompt": "prompt", "stream": False}, json.loads(request.data)
        )
        self.assertEqual(11, urlopen.call_args.kwargs["timeout"])

    def test_prove_pass_fail_cache_and_unavailable_paths(self):
        with mock.patch.object(self.module, "ollama", side_effect=["proof", "VERDICT: PASS"]):
            passed = self.module.prove("valid")
        self.assertEqual("PROVED", passed["status"])

        with mock.patch.object(self.module, "ollama") as ollama:
            cached = self.module.prove("valid")
        ollama.assert_not_called()
        self.assertEqual("proof", cached["proof"])

        with mock.patch.object(self.module, "ollama", side_effect=["draft", "VERDICT: FAIL"]):
            failed = self.module.prove("invalid")
        self.assertEqual("FAILED", failed["status"])
        with mock.patch.object(self.module, "ollama") as ollama:
            held = self.module.prove("invalid")
        ollama.assert_not_called()
        self.assertNotIn("proof", held)

        with mock.patch.object(self.module, "ollama", side_effect=OSError("offline")):
            unavailable = self.module.prove("unknown")
        self.assertEqual("UNBANKED", unavailable["status"])

    def test_main_writes_bounded_report_with_zero_hit_sections(self):
        hit = {
            "db": "ledger.db",
            "table": "facts",
            "cluster": "newton_chain",
            "term": "newton",
            "rowid": "match 1",
            "snippet": "Newton\nchain",
        }
        file_hits = [str(self.root / ("file-%02d.md" % n)) for n in range(65)]
        with mock.patch.object(self.module, "scan_dbs", return_value=[hit]), mock.patch.object(
            self.module, "scan_files", return_value=file_hits
        ), mock.patch.object(
            self.module,
            "prove",
            side_effect=[{"status": "PROVED"}, {"status": "PROVED"}],
        ), mock.patch.object(
            self.module.glob, "glob", return_value=[str(self.data / "ledger.db")]
        ):
            self.module.main()

        report = Path(self.module.REPORT_PATH).read_text()
        self.assertIn("Sqlite ledger hits (1 total across 1 dbs)", report)
        self.assertIn("`ledger.db::facts` [newton=match 1]: Newton chain", report)
        self.assertIn("### synergetics — 0 hit(s)", report)
        self.assertIn("- **zero hits**", report)
        self.assertIn("Repo text files matching clusters (65 files)", report)
        self.assertIn("file-59.md", report)
        self.assertNotIn("file-60.md", report)
        self.assertIn("second call: PROVED", report)


if __name__ == "__main__":
    unittest.main()
