import contextlib
import hashlib
import importlib.util
import io
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "unified_workflow_under_test", REPO_ROOT / "bin/unified_workflow_v1.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UnifiedWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.module.WORKSPACE = self.root
        self.module.DATA_DIR = self.root / "data"
        self.module.DOCS_DIR = self.root / "docs"
        self.module.CTX_BRIDGE = self.root / "context_bridge"
        self.module.SEED_FILE = self.module.CTX_BRIDGE / "session-fixed-unified.md"

    def test_sha256_file_streams_binary_content(self):
        path = self.root / "payload.bin"
        content = bytes(range(256)) * 100
        path.write_bytes(content)
        self.assertEqual(hashlib.sha256(content).hexdigest(), self.module.sha256_file(path))

    def test_init_dbs_creates_expected_schema_and_is_idempotent(self):
        self.module.init_dbs()
        self.module.init_dbs()
        with sqlite3.connect(self.module.DATA_DIR / "research.db") as con:
            claims = {row[1] for row in con.execute("PRAGMA table_info(claims)")}
            manuscripts = {row[1] for row in con.execute("PRAGMA table_info(manuscripts)")}
        with sqlite3.connect(self.module.DATA_DIR / "lessons.db") as con:
            lessons = {row[1] for row in con.execute("PRAGMA table_info(lessons)")}
            tasks = {row[1] for row in con.execute("PRAGMA table_info(tasks)")}
        self.assertTrue({"subsystem", "claim", "status", "instrument", "lit_anchor", "target_metric"} <= claims)
        self.assertTrue({"subsystem", "path", "stage"} <= manuscripts)
        self.assertTrue({"domain", "mistake", "root_cause", "correction", "cost", "source", "verified"} <= lessons)
        self.assertTrue({"description", "lesson_ids", "outcome"} <= tasks)

    def test_init_dbs_migrates_existing_ledgers_and_enforces_claim_identity(self):
        self.module.DATA_DIR.mkdir()
        with sqlite3.connect(self.module.DATA_DIR / "research.db") as con:
            con.execute("CREATE TABLE claims (id INTEGER PRIMARY KEY, subsystem TEXT, claim TEXT, status TEXT)")
            con.execute("INSERT INTO claims (subsystem, claim) VALUES ('same', 'claim')")
            con.execute("INSERT INTO claims (subsystem, claim) VALUES ('same', 'claim')")
        with sqlite3.connect(self.module.DATA_DIR / "lessons.db") as con:
            con.execute("CREATE TABLE lessons (id INTEGER PRIMARY KEY, domain TEXT, mistake TEXT)")
        self.module.init_dbs()
        with sqlite3.connect(self.module.DATA_DIR / "research.db") as con:
            self.assertEqual(1, con.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            con.execute("INSERT OR IGNORE INTO claims (subsystem, claim) VALUES ('same', 'claim')")
            self.assertEqual(1, con.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
        with sqlite3.connect(self.module.DATA_DIR / "lessons.db") as con:
            columns = {row[1] for row in con.execute("PRAGMA table_info(lessons)")}
            self.assertIn("verified", columns)
            self.assertTrue(con.execute("SELECT name FROM sqlite_master WHERE name='tasks'").fetchone())

    def test_hype_gate_accepts_clean_text_and_reports_every_banned_match(self):
        clean = self.root / "clean.md"
        clean.write_text("Measured performance remains pending.")
        self.assertTrue(self.module.hype_gate(clean))

        hype = self.root / "hype.md"
        hype.write_text("A Revolutionary miracle.\nFree energy from zero point physics.\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertFalse(self.module.hype_gate(hype))
        rendered = output.getvalue().lower()
        self.assertIn("line 1: revolutionary", rendered)
        self.assertIn("line 1: miracle", rendered)
        self.assertIn("line 2: free energy", rendered)
        self.assertIn("line 2: zero point", rendered)

    def test_run_returns_trimmed_stdout_and_normalizes_process_errors(self):
        completed = subprocess.CompletedProcess(["cmd"], 7, stdout=" value \n", stderr="ignored")
        with mock.patch.object(self.module.subprocess, "run", return_value=completed) as run:
            self.assertEqual((7, "value"), self.module.run(["cmd"], input_text="in", timeout=3))
        run.assert_called_once_with(
            ["cmd"], input="in", capture_output=True, text=True, timeout=3
        )
        with mock.patch.object(self.module.subprocess, "run", side_effect=OSError("missing")):
            self.assertEqual((1, ""), self.module.run(["missing"]))

    def test_ollama_run_requires_successful_nonempty_output(self):
        success = subprocess.CompletedProcess([], 0, stdout=" answer \n", stderr="")
        with mock.patch.object(self.module.subprocess, "run", return_value=success) as run:
            self.assertEqual("answer", self.module.ollama_run("model", "prompt", "input", 4))
        run.assert_called_once_with(
            ["ollama", "run", "model", "prompt"],
            input="input",
            capture_output=True,
            text=True,
            timeout=4,
        )
        for completed in (
            subprocess.CompletedProcess([], 1, stdout="error", stderr=""),
            subprocess.CompletedProcess([], 0, stdout=" \n", stderr=""),
        ):
            with self.subTest(returncode=completed.returncode, stdout=completed.stdout), mock.patch.object(
                self.module.subprocess, "run", return_value=completed
            ):
                self.assertEqual("UNAVAILABLE (model offline)", self.module.ollama_run("m", "p"))

    def test_main_creates_ledgers_manuscripts_hero_and_verifiable_seed(self):
        run_results = [
            (0, '{"login":"tester"}'),
            (0, '{"visibility":"public"}'),
            (0, '{"visibility":"private"}'),
            (1, ""),
            (0, '{"visibility":"internal"}'),
            (0, '{"visibility":"public"}'),
            (0, "abc1234"),
        ]
        with mock.patch.object(
            self.module, "ollama_run", side_effect=["Three measured sentences.", "VERDICT: PASS"]
        ) as ollama, mock.patch.object(self.module, "run", side_effect=run_results) as run:
            self.module.main()

        self.assertEqual(2, ollama.call_count)
        self.assertEqual(7, run.call_count)
        with sqlite3.connect(self.module.DATA_DIR / "research.db") as con:
            self.assertEqual(len(self.module.CLAIMS), con.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            self.assertEqual(
                len(self.module.MANUSCRIPTS),
                con.execute("SELECT COUNT(*) FROM manuscripts").fetchone()[0],
            )
        with sqlite3.connect(self.module.DATA_DIR / "lessons.db") as con:
            lesson = con.execute("SELECT domain, mistake FROM lessons").fetchone()
        self.assertEqual(("workflow", "large paste truncated over ssh"), lesson)
        self.assertEqual("Three measured sentences.\n", (self.root / "drafts/hero_draft.md").read_text())
        for title, subsystem, slug in self.module.MANUSCRIPTS:
            text = (self.module.DOCS_DIR / "research" / (slug + ".md")).read_text()
            self.assertIn(title, text)
            self.assertIn("subsystem='%s'" % subsystem, text)
        seed = self.module.SEED_FILE.read_text()
        self.assertIn("- claims: 9 registered", seed)
        self.assertIn("- HEAD: abc1234", seed)
        digest, filename = (self.root / "seed_master.log").read_text().split()
        self.assertEqual(hashlib.sha256(self.module.SEED_FILE.read_bytes()).hexdigest(), digest)
        self.assertEqual(self.module.SEED_FILE.name, filename)

    def test_existing_manuscript_is_registered_and_hype_failure_stops_session(self):
        path = self.module.DOCS_DIR / "research/thixo-foam.md"
        path.parent.mkdir(parents=True)
        path.write_text("A revolutionary claim")
        with mock.patch.object(self.module, "ollama_run") as ollama, mock.patch.object(
            self.module, "run"
        ) as run:
            self.assertEqual(1, self.module.main())
        ollama.assert_not_called()
        run.assert_not_called()
        with sqlite3.connect(self.module.DATA_DIR / "research.db") as con:
            row = con.execute(
                "SELECT subsystem FROM manuscripts WHERE path=?", (str(path),)
            ).fetchone()
        self.assertEqual(("thixo_gel",), row)
        self.assertFalse(self.module.SEED_FILE.exists())


if __name__ == "__main__":
    unittest.main()
