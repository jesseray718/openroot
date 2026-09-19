import datetime
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ShellWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.bin_dir = self.root / "bin"
        self.fake_bin = self.root / "fake-bin"
        self.bin_dir.mkdir()
        self.fake_bin.mkdir()
        self.env = os.environ.copy()
        self.env["PATH"] = str(self.fake_bin) + os.pathsep + self.env["PATH"]

    def stage_script(self, name):
        source = (REPO_ROOT / "bin" / name).read_text()
        source = source.replace("cd /home/jesse/openroot", 'cd "${OPENROOT_TEST_ROOT:-/home/jesse/openroot}"')
        destination = self.bin_dir / name
        destination.write_text(source)
        destination.chmod(0o755)
        helper = REPO_ROOT / "bin/sqlite_params.py"
        if helper.exists():
            (self.bin_dir / helper.name).write_text(helper.read_text())
        self.env["OPENROOT_TEST_ROOT"] = str(self.root)
        return destination

    def fake_command(self, name, body):
        path = self.fake_bin / name
        path.write_text("#!/usr/bin/env bash\nset -eu\n" + body + "\n")
        path.chmod(0o755)
        return path

    def run_script(self, name, *args, timeout=20):
        script = self.stage_script(name)
        return subprocess.run(
            ["bash", str(script), *args],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def create_lessons_db(self):
        (self.root / "data").mkdir(exist_ok=True)
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            con.execute(
                "CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, lesson_ids TEXT, outcome TEXT)"
            )
            con.execute(
                "CREATE TABLE lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT, mistake TEXT, root_cause TEXT, correction TEXT, cost TEXT, source TEXT, verified INTEGER DEFAULT 0)"
            )

    def test_hype_gate_accepts_clean_copy_and_rejects_case_insensitive_banned_phrases(self):
        clean = self.root / "clean.md"
        clean.write_text("A measured result with stated uncertainty.\n")
        accepted = self.run_script("hype_gate.sh", str(clean))
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertIn("[PASS]", accepted.stdout)

        hype = self.root / "hype.md"
        hype.write_text("A REVOLUTIONARY perpetual design using zero-point energy.\n")
        rejected = self.run_script("hype_gate.sh", str(hype))
        self.assertEqual(1, rejected.returncode)
        self.assertIn("[FAIL]", rejected.stdout)
        self.assertIn("[HELD]", rejected.stdout)

        percent = self.root / "percent.md"
        percent.write_text("Efficiency exceeds 100% according to the draft.\n")
        self.assertEqual(1, self.run_script("hype_gate.sh", str(percent)).returncode)
        greater = self.root / "greater.md"
        greater.write_text("Measured x > y.\n")
        self.assertEqual(0, self.run_script("hype_gate.sh", str(greater)).returncode)

    def test_abstract_grade_sends_only_abstract_body_and_has_offline_fallback(self):
        manuscript = self.root / "paper.md"
        manuscript.write_text(
            "# Title\n\n## Abstract\nMeasured 4.0 +/- 0.2 with a calibrated meter.\n\n## 1. Introduction\nSECRET BODY\n"
        )
        captured = self.root / "captured.txt"
        self.env["CAPTURED_STDIN"] = str(captured)
        self.fake_command(
            "ollama",
            'cat > "$CAPTURED_STDIN"\nprintf "%s\\n" "VERDICT: PASS" "FIRST_FIX: none"',
        )
        result = self.run_script("abstract_grade.sh", str(manuscript))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("VERDICT: PASS", result.stdout)
        self.assertIn("Measured 4.0", captured.read_text())
        self.assertNotIn("SECRET BODY", captured.read_text())

        self.fake_command("ollama", "exit 1")
        unavailable = self.run_script("abstract_grade.sh", str(manuscript))
        self.assertEqual(0, unavailable.returncode)
        self.assertIn("VERDICT: UNAVAILABLE", unavailable.stdout)

    def test_daily_loop_records_unique_pending_task_and_links_new_lesson(self):
        self.create_lessons_db()
        recall_log = self.root / "recall.log"
        self.env["RECALL_LOG"] = str(recall_log)
        recall = self.bin_dir / "task_recall.sh"
        recall.write_text('#!/usr/bin/env bash\nprintf "%s" "$1" > "$RECALL_LOG"\n')
        recall.chmod(0o755)

        first = self.run_script("daily_loop_v1.sh", "start", "verify thermal claim")
        second = self.run_script("daily_loop_v1.sh", "start", "verify thermal claim")
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(0, second.returncode, second.stderr)
        self.assertEqual("verify thermal claim", recall_log.read_text())
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            self.assertEqual(1, con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])

        finished = self.run_script(
            "daily_loop_v1.sh", "finish", "verify thermal claim", "new_mistake", "missed calibration"
        )
        self.assertEqual(0, finished.returncode, finished.stderr)
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            task = con.execute("SELECT outcome, lesson_ids FROM tasks").fetchone()
            lesson = con.execute("SELECT domain, mistake, source FROM lessons").fetchone()
        self.assertEqual(("new_mistake", "[1]"), task)
        self.assertEqual(("new_mistake", "missed calibration", "session"), lesson)

    def test_daily_loop_binds_sql_like_task_values(self):
        self.create_lessons_db()
        recall = self.bin_dir / "task_recall.sh"
        recall.write_text("#!/usr/bin/env bash\nexit 0\n")
        recall.chmod(0o755)
        task = "test O'Brien'); DROP TABLE tasks; --"
        self.assertEqual(0, self.run_script("daily_loop_v1.sh", "start", task).returncode)
        self.assertEqual(
            0,
            self.run_script("daily_loop_v1.sh", "finish", task, "new_mistake", "it's data").returncode,
        )
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            self.assertEqual(1, con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])
            self.assertEqual("it's data", con.execute("SELECT mistake FROM lessons").fetchone()[0])

    def test_daily_loop_keeps_empty_lesson_ids_as_json_when_task_succeeds(self):
        self.create_lessons_db()
        recall = self.bin_dir / "task_recall.sh"
        recall.write_text("#!/usr/bin/env bash\nexit 0\n")
        recall.chmod(0o755)

        started = self.run_script("daily_loop_v1.sh", "start", "successful task")
        self.assertEqual(0, started.returncode, started.stderr)
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            self.assertEqual(
                ("[]", "pending"),
                con.execute("SELECT lesson_ids, outcome FROM tasks").fetchone(),
            )

        finished = self.run_script("daily_loop_v1.sh", "finish", "successful task", "ok")
        self.assertEqual(0, finished.returncode, finished.stderr)
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            self.assertEqual(
                ("[]", "ok"),
                con.execute("SELECT lesson_ids, outcome FROM tasks").fetchone(),
            )
            self.assertEqual(0, con.execute("SELECT COUNT(*) FROM lessons").fetchone()[0])

    def test_daily_loop_rejects_start_without_description(self):
        self.create_lessons_db()
        result = self.run_script("daily_loop_v1.sh", "start")
        self.assertEqual(1, result.returncode)
        self.assertIn("usage:", result.stdout)

    def test_refinement_v2_feeds_grader_fix_into_next_attempt_and_banks_pass(self):
        self.create_lessons_db()
        (self.root / "docs").mkdir()
        state = self.root / "ollama-state"
        second_input = self.root / "second-builder-input"
        self.env.update({"FAKE_STATE": str(state), "SECOND_INPUT": str(second_input)})
        self.fake_command(
            "ollama",
            'n=0; [ ! -f "$FAKE_STATE" ] || n=$(cat "$FAKE_STATE"); n=$((n+1)); echo "$n" > "$FAKE_STATE"\n'
            'case "$n" in\n'
            '  1) cat >/dev/null; echo "draft one" ;;\n'
            '  2) cat >/dev/null; printf "VERDICT: FAIL\\nFIX: add uncertainty\\n" ;;\n'
            '  3) cat > "$SECOND_INPUT"; echo "draft two with uncertainty" ;;\n'
            '  4) cat >/dev/null; printf "VERDICT: PASS\\nFIX: NONE\\n" ;;\n'
            'esac',
        )

        result = self.run_script("refinement_loop_v2.sh", "article", "include measurements", "3")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("GRADER FIX REQUIRED: add uncertainty", second_input.read_text())
        self.assertEqual("draft two with uncertainty\n", (self.root / "docs/article.md").read_text())
        with sqlite3.connect(self.root / "data/refinement.db") as con:
            rows = con.execute("SELECT attempt, accepted FROM iterations ORDER BY attempt").fetchall()
        self.assertEqual([(1, 0), (2, 1)], rows)

    def test_refinement_v2_binds_document_and_requires_exact_pass_line(self):
        self.create_lessons_db()
        (self.root / "docs").mkdir()
        self.fake_command(
            "ollama",
            'cat >/dev/null\ncase "$*" in *qwen2.5-coder*) echo draft;; *) printf "NOTE: VERDICT: PASS\\nFIX: no\\n";; esac',
        )
        doc = "O'Brien'); DROP TABLE iterations; --"
        result = self.run_script("refinement_loop_v2.sh", doc, "rubric", "1")
        self.assertEqual(1, result.returncode)
        with sqlite3.connect(self.root / "data/refinement.db") as con:
            self.assertEqual(doc, con.execute("SELECT doc_ref FROM iterations").fetchone()[0])

    def test_refinement_v3_fails_fast_when_builder_is_offline(self):
        self.create_lessons_db()
        self.fake_command("ollama", "cat >/dev/null; exit 1")
        result = self.run_script("refinement_loop_v3.sh", "article", "rubric", "2")
        self.assertEqual(1, result.returncode)
        self.assertIn("[held] 7B offline", result.stdout)
        with sqlite3.connect(self.root / "data/refinement.db") as con:
            self.assertEqual(0, con.execute("SELECT COUNT(*) FROM iterations").fetchone()[0])

    def test_refinement_v3_binds_sql_like_document_values(self):
        self.create_lessons_db()
        (self.root / "docs").mkdir()
        self.fake_command(
            "ollama",
            'case "$*" in *qwen2.5-coder*) echo draft;; *) printf "VERDICT: PASS\\nFIX: NONE\\n";; esac',
        )
        doc = "O'Brien'); DELETE FROM iterations; --"
        result = self.run_script("refinement_loop_v3.sh", doc, "rubric", "1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        with sqlite3.connect(self.root / "data/refinement.db") as con:
            self.assertEqual(
                (doc, 1, 1),
                con.execute("SELECT doc_ref, attempt, accepted FROM iterations").fetchone(),
            )

    def test_fleet_check_reports_green_when_models_ledgers_refs_and_agents_are_ready(self):
        (self.root / "data").mkdir()
        for name, schema in {
            "lessons.db": "CREATE TABLE lessons (id INTEGER)",
            "mesh.db": "CREATE TABLE mesh_tasks (status TEXT); CREATE TABLE agents (id INTEGER)",
            "team_gate.db": "CREATE TABLE gate (id INTEGER)",
            "canonical_index.db": "CREATE TABLE idx (id INTEGER)",
        }.items():
            with sqlite3.connect(self.root / "data" / name) as con:
                con.executescript(schema)
                if name == "lessons.db":
                    con.execute("INSERT INTO lessons VALUES (1)")
                if name == "mesh.db":
                    con.execute("INSERT INTO agents VALUES (1)")
                    con.execute("INSERT INTO mesh_tasks VALUES ('open')")
        for name in ("task_recall.sh", "lessons_v1.sh", "mesh_recruit_v1.sh", "mesh_publish_v2.sh", "onepass_v3.sh"):
            (self.bin_dir / name).write_text("")
        self.fake_command(
            "curl",
            'printf "%s" \'{"models":[{"name":"qwen2.5-coder:7b"},{"name":"qwen2.5:3b"},{"name":"nomic-embed-text"}]}\'',
        )
        self.fake_command(
            "git",
            'case " $* " in\n'
            '  *" rev-parse --show-toplevel "*) echo "$OPENROOT_TEST_ROOT" ;;\n'
            '  *" status --porcelain "*) exit 0 ;;\n'
            '  *" status --short "*) exit 0 ;;\n'
            '  *" rev-parse --short "*) echo abc1234 ;;\n'
            '  *" rev-parse "*) echo same-revision ;;\n'
            'esac',
        )

        result = self.run_script("fleet_check_v1.sh")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("[VERIFY PASS] fleet GREEN", result.stdout)
        self.assertNotIn("model missing", result.stdout)

    def test_fleet_check_missing_script_prevents_green_result(self):
        (self.root / "data").mkdir()
        self.fake_command("git", 'case " $* " in *" rev-parse --show-toplevel "*) echo "$OPENROOT_TEST_ROOT";; *) echo same;; esac')
        self.fake_command("curl", "exit 1")
        result = self.run_script("fleet_check_v1.sh")
        self.assertIn("bin/onepass_v3.sh missing", result.stdout)
        self.assertNotIn("[VERIFY PASS]", result.stdout)

    def test_weekly_audit_banks_metrics_report_when_model_is_offline(self):
        self.create_lessons_db()
        (self.root / "context_bridge").mkdir()
        with sqlite3.connect(self.root / "data/lessons.db") as con:
            con.execute(
                "INSERT INTO lessons (domain, mistake, correction, verified) VALUES ('test', 'mistake', 'fixed', 1)"
            )
            con.execute(
                "INSERT INTO tasks (description, outcome) VALUES ('task', 'repeat_mistake')"
            )
        self.fake_command("ollama", "cat >/dev/null; exit 1")
        self.fake_command(
            "git",
            'case " $* " in *"rev-parse --short master"*) echo abc1234;; *"diff --cached --stat"*) echo "1 file changed";; esac',
        )

        result = self.run_script("weekly_audit_v1.sh")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = self.root / "reports" / ("lesson_audit-" + datetime.date.today().strftime("%Y%m%d") + ".md")
        self.assertTrue(report.exists())
        text = report.read_text()
        self.assertIn("THEME: unavailable - 3B offline", text)
        self.assertIn("- lessons total: 1", text)
        self.assertIn("- pct_fixed: 100.0%", text)
        self.assertIn("- repeat_mistake tasks: 1", text)
        self.assertEqual(1, len(list((self.root / "context_bridge").glob("*-audit.md"))))

    def test_research_ready_is_idempotent_for_claims_and_manuscript_skeletons(self):
        (self.root / "data").mkdir()
        (self.root / "context_bridge").mkdir()
        self.fake_command(
            "git",
            'case " $* " in *"rev-parse --short master"*) echo abc1234;; *"diff --cached --stat"*) echo "files changed";; esac',
        )

        first = self.run_script("research_ready_v1.sh")
        second = self.run_script("research_ready_v1.sh")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        with sqlite3.connect(self.root / "data/research.db") as con:
            self.assertEqual(9, con.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            self.assertEqual(9, con.execute("SELECT COUNT(*) FROM manuscripts").fetchone()[0])
            self.assertEqual(
                {"asserted"}, {row[0] for row in con.execute("SELECT DISTINCT status FROM claims")}
            )
        manuscripts = list((self.root / "docs/research").glob("*.md"))
        self.assertEqual(9, len(manuscripts))
        self.assertTrue(all("measurements pending" in path.read_text() for path in manuscripts))
        self.assertIn("claims already registered (9)", second.stdout)
        self.assertIn("subsystem='thixo_gel'", (self.root / "docs/research/thixo-foam.md").read_text())

    def test_research_ready_migrates_legacy_claims_schema(self):
        (self.root / "data").mkdir()
        (self.root / "context_bridge").mkdir()
        with sqlite3.connect(self.root / "data/research.db") as con:
            con.execute("CREATE TABLE claims (id INTEGER PRIMARY KEY, subsystem TEXT, claim TEXT, status TEXT)")
        self.fake_command(
            "git",
            'case " $* " in *"rev-parse --short master"*) echo abc1234;; *"diff --cached --stat"*) echo changed;; esac',
        )
        result = self.run_script("research_ready_v1.sh")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        with sqlite3.connect(self.root / "data/research.db") as con:
            columns = {row[1] for row in con.execute("PRAGMA table_info(claims)")}
            indexes = {row[1] for row in con.execute("PRAGMA index_list(claims)")}
        self.assertTrue({"instrument", "lit_anchor", "target_metric"} <= columns)
        self.assertIn("idx_claims_identity", indexes)


if __name__ == "__main__":
    unittest.main()
