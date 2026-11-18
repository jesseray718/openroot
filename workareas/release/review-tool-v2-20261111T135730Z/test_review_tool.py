import copy
import json
import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import review_tool as r

def worker(root, index):
    return r.Store(root).append("test", {"index": index}, str(index))

class Tests(unittest.TestCase):
    def task(self):
        return {
            "name": "fixture", "base_eta": 80,
            "observation_days": 14, "feedback": True,
            "involves_compute": True, "compute_joules": 1200
        }

    def test_clean_task(self):
        out = r.evaluate(self.task())
        self.assertEqual(out["heuristic_score"], 80)
        self.assertTrue(out["threshold_passed"])
        self.assertEqual(len(out["rule_trace"]), 3)
        self.assertTrue(all(x["passed"] for x in out["rule_trace"]))

    def test_penalties(self):
        t = self.task()
        t.update(base_eta=55, observation_days=0, feedback=False,
                 compute_joules=0)
        self.assertEqual(r.evaluate(t)["heuristic_score"], 35)

    def test_invalid_inputs(self):
        for key, value in [
            ("base_eta", float("nan")), ("base_eta", 101),
            ("feedback", "true"), ("compute_joules", -1)
        ]:
            t = self.task()
            t[key] = value
            with self.assertRaises(ValueError):
                r.evaluate(t)

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            r.parse('{"x":1,"x":2}')

    def test_idempotent_append(self):
        with tempfile.TemporaryDirectory() as d:
            s = r.Store(d)
            first = s.append("test", {"x": 1}, "same")
            second = s.append("test", {"x": 1}, "same")
            self.assertEqual(first["entry"]["hash"], second["entry"]["hash"])
            self.assertEqual(s.verify()["entries"], 1)

    def test_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            s = r.Store(d)
            s.append("test", {"x": 1}, "one")
            row = r.read_chain(s.ledger)[0]
            row["payload"]["x"] = 99
            s.ledger.write_bytes(r.encode(row) + b"\n")
            with self.assertRaises(ValueError):
                s.verify()
            with self.assertRaises(ValueError):
                s.append("test", {}, "two")

    def test_old_double_hash_detected(self):
        entry = {"payload": {}, "previous_hash": "genesis"}
        entry["hash"] = r.digest(entry)
        entry["hash"] = r.digest(entry)
        with self.assertRaises(ValueError):
            r.verify_rows([entry])

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "real").write_text("{}")
            (p / "link").symlink_to(p / "real")
            with self.assertRaises(ValueError):
                r.read_bytes(p / "link")

    def test_missing_ledger_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                r.Store(d).verify()

    def test_full_hash_required(self):
        with self.assertRaises(ValueError):
            r.exact_entry([], "abc")

    def test_concurrent_append(self):
        with tempfile.TemporaryDirectory() as d:
            with ProcessPoolExecutor(max_workers=4) as pool:
                list(pool.map(worker, [d] * 12, range(12)))
            self.assertEqual(r.Store(d).verify()["entries"], 12)

if __name__ == "__main__":
    unittest.main(verbosity=2)
