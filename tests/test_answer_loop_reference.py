import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


MODULE = Path(__file__).resolve().parents[1] / "examples/answer-loop/reference.py"
spec = importlib.util.spec_from_file_location("answer_loop_reference", MODULE)
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)


class AnswerLoopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.pod = root / "synthetic.sqlite"
        self.chain = root / "pathways.jsonl"
        self.corrections = root / "corrections.jsonl"
        self.chain.write_bytes(b"")
        self.corrections.write_bytes(b"")
        self.con = sqlite3.connect(self.pod)
        self.con.executescript("""
            CREATE TABLE cell (tid TEXT PRIMARY KEY, sha256 TEXT, bytes INTEGER, payload_ref TEXT);
            CREATE VIRTUAL TABLE cell_fts USING fts5(tid UNINDEXED, body);
        """)
        self.add_cell("a", "filler " * 70 + " thermal storage token=secret", "file1")
        self.add_cell("b", "thermal insulation storage details", "file2")
        self.con.commit()
        self.con.close()
        self.model = ref.StubModel()

    def add_cell(self, tid, body, source):
        self.con.execute("INSERT INTO cell VALUES (?, ?, ?, ?)",
                         (tid, ref.digest(body.encode()), len(body.encode()), source))
        self.con.execute("INSERT INTO cell_fts VALUES (?, ?)", (tid, body))

    def ask(self, **kwargs):
        return ref.ask(self.pod, self.chain, self.corrections,
                       "thermal storage", self.model, **kwargs)

    def correct(self, kind, target):
        rows, _ = ref.read_chain(self.corrections)
        row = {"version": "answer-loop/1", "kind": kind, "target": target,
               "prev": rows[-1][0]["hash"] if rows else None}
        row["hash"] = ref.chain_hash(row, "v1")
        with self.corrections.open("ab") as stream:
            stream.write(ref.canonical(row) + b"\n")

    def test_read_only_selection_prompt_and_replay(self):
        before = ref.pod_hash(self.pod)
        con = ref.open_pod(self.pod)
        with self.assertRaises(sqlite3.OperationalError):
            con.execute("DELETE FROM cell")
        route = ref.retrieve(con, "thermal storage", budget=400, per_file=1)
        self.assertLessEqual(sum(len(x["snippet"]) for x in route), 400)
        self.assertEqual(route, ref.retrieve(con, "thermal storage", budget=400, per_file=1))
        self.assertEqual(ref.prompt_for("thermal storage", route),
                         ref.prompt_for("thermal storage", route))
        self.assertTrue(any("thermal" in x["snippet"] and x["tid"] == "a" for x in route))
        self.assertNotIn("secret", json.dumps(route))
        con.close()
        generated = self.ask()
        self.assertEqual(generated["mode"], "generated")
        self.assertEqual(ref.read_chain(self.chain)[0][0][0]["model_requests"], 1)
        replay = self.ask(expected_tip=generated["tip"])
        self.assertEqual(replay["mode"], "replay")
        self.assertEqual(replay["answer"], generated["answer"])
        self.assertEqual(self.model.requests, 1)
        self.assertEqual(before, ref.pod_hash(self.pod))

    def test_block_and_supersession_invalidate(self):
        first = self.ask()
        self.correct("BLOCK", first["tip"])
        second = self.ask(expected_tip=first["tip"])
        self.assertEqual(second["mode"], "generated")
        self.assertTrue(second["invalidated"])
        self.correct("SUPERSEDE", "a")
        third = self.ask(expected_tip=second["tip"])
        self.assertEqual(third["mode"], "generated")
        row = ref.read_chain(self.chain)[0][-1][0]
        self.assertNotIn("a", [item["tid"] for item in row["route"]])
        self.assertEqual(self.model.requests, 3)

    def test_changed_evidence_regenerates(self):
        first = self.ask()
        con = sqlite3.connect(self.pod)
        body = "thermal storage updated"
        con.execute("UPDATE cell SET sha256=?, bytes=? WHERE tid='a'",
                    (ref.digest(body.encode()), len(body.encode())))
        con.execute("UPDATE cell_fts SET body=? WHERE tid='a'", (body,))
        con.commit()
        con.close()
        self.assertEqual(self.ask(expected_tip=first["tip"])["mode"], "generated")
        self.assertEqual(self.model.requests, 2)

    def test_missing_evidence_and_bad_correction_chain(self):
        first = self.ask()
        con = sqlite3.connect(self.pod)
        con.execute("DELETE FROM cell WHERE tid='a'")
        con.execute("DELETE FROM cell_fts WHERE tid='a'")
        con.commit()
        con.close()
        result = self.ask(expected_tip=first["tip"])
        self.assertEqual(result["mode"], "generated")
        route = ref.read_chain(self.chain)[0][-1][0]["route"]
        self.assertNotIn("a", [item["tid"] for item in route])
        self.corrections.write_bytes(b'{"broken":true}\n')
        original = self.chain.read_bytes()
        with self.assertRaises(ref.Held):
            self.ask()
        self.assertEqual(self.chain.read_bytes(), original)
        self.assertEqual(self.model.requests, 2)

    def test_corruption_and_truncation_hold_without_append(self):
        first = self.ask()
        self.correct("BLOCK", first["tip"])
        second = self.ask(expected_tip=first["tip"])
        original = self.chain.read_bytes()
        self.chain.write_bytes(original.splitlines(keepends=True)[0])
        with self.assertRaisesRegex(ref.Held, "tip mismatch"):
            self.ask(expected_tip=second["tip"])
        self.chain.write_bytes(original + b'{"bad":1}\n')
        corrupt = self.chain.read_bytes()
        with self.assertRaises(ref.Held):
            self.ask()
        self.assertEqual(self.chain.read_bytes(), corrupt)
        self.assertEqual(self.model.requests, 2)

    def test_invalid_prior_record_holds_even_for_a_different_question(self):
        self.ask()
        row = json.loads(self.chain.read_text())
        row["answer_sha256"] = "invalid"
        row["hash"] = ref.chain_hash(row, "v1")
        self.chain.write_bytes(ref.canonical(row) + b"\n")
        original = self.chain.read_bytes()
        with self.assertRaisesRegex(ref.Held, "answer or prompt mismatch"):
            ref.ask(self.pod, self.chain, self.corrections, "insulation", self.model)
        self.assertEqual(self.chain.read_bytes(), original)
        self.assertEqual(self.model.requests, 1)

    def test_source_cap_and_duplicate_snippet(self):
        con = sqlite3.connect(self.pod)
        self.con = con
        self.add_cell("c", "thermal storage alternate", "file1")
        self.add_cell("d", "thermal insulation storage details", "file3")
        con.commit()
        con.close()
        con = ref.open_pod(self.pod)
        route = ref.retrieve(con, "thermal storage", per_file=1)
        con.close()
        tids = {item["tid"] for item in route}
        self.assertLessEqual(len(tids & {"a", "c"}), 1)
        self.assertLessEqual(len(tids & {"b", "d"}), 1)

    def test_changed_corrections_during_generation_hold_without_append(self):
        test = self

        class ChangingStub(ref.StubModel):
            def generate(self, prompt):
                result = super().generate(prompt)
                test.correct("SUPERSEDE", "a")
                return result

        with self.assertRaisesRegex(ref.Held, "state changed"):
            ref.ask(self.pod, self.chain, self.corrections,
                    "thermal storage", ChangingStub())
        self.assertEqual(self.chain.read_bytes(), b"")

    def test_legacy_serializations_and_malformed_rows(self):
        previous = None
        data = b""
        for recipe in ("legacy-sorted", "legacy-compact"):
            row = {"prev": previous, "value": "legacy"}
            row["ph"] = ref.chain_hash(row, recipe)
            data += ref.canonical(row) + b"\n"
            previous = row["ph"]
        self.chain.write_bytes(data)
        rows, _ = ref.read_chain(self.chain, previous)
        self.assertEqual([r[1] for r in rows], ["legacy-sorted", "legacy-compact"])
        self.chain.write_bytes(data + b'null\n')
        with self.assertRaises(ref.Held):
            ref.read_chain(self.chain)

    def test_schema_mismatch_and_active_journal_hold(self):
        empty = self.pod.parent / "empty.sqlite"
        sqlite3.connect(empty).close()
        with self.assertRaisesRegex(ref.Held, "schema"):
            ref.ask(empty, self.chain, self.corrections, "thermal", self.model)
        Path(str(self.pod) + "-wal").touch()
        with self.assertRaisesRegex(ref.Held, "journal"):
            self.ask()
        self.assertEqual(self.model.requests, 0)

    def test_drift_warns_without_generation(self):
        first = self.ask()
        con = sqlite3.connect(self.pod)
        self.con = con
        self.add_cell("c", "thermal storage additional context", "file3")
        con.commit()
        con.close()
        replay = self.ask(expected_tip=first["tip"], check_drift=True)
        self.assertEqual(replay["mode"], "replay")
        self.assertTrue(replay["drift_warning"])
        self.assertEqual(self.model.requests, 1)

    def test_no_hits_no_generation(self):
        result = ref.ask(self.pod, self.chain, self.corrections,
                         "nonexistentword", self.model)
        self.assertEqual(result["mode"], "insufficient")
        self.assertEqual(self.model.requests, 0)
        self.assertEqual(self.chain.read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
