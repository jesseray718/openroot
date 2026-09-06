"""Tests for the offline toolkit modules."""
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Allow import without install
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from offline.queue import OperationQueue
from offline.dedup import DedupIndex, _sha256
from offline.lifecycle import DataLifecycle
from offline.priority import PriorityScorer
from offline.thermal import ThermalRegulator


class TestPriorityScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = PriorityScorer()

    def test_basic_score(self):
        # score = urgency^2 * impact
        self.assertAlmostEqual(self.scorer.score(2.0, 3.0), 12.0)

    def test_zero_urgency(self):
        self.assertEqual(self.scorer.score(0.0, 10.0), 0.0)

    def test_negative_clamped(self):
        self.assertEqual(self.scorer.score(-5.0, 5.0), 0.0)

    def test_weights_applied(self):
        scorer = PriorityScorer(weight_urgency=2.0, weight_impact=0.5)
        # 3^2 * 4 * 2.0 * 0.5 = 9*4*1 = 36
        self.assertAlmostEqual(scorer.score(3.0, 4.0), 36.0)

    def test_rank_order(self):
        items = [
            {"urgency": 1.0, "impact": 1.0},
            {"urgency": 5.0, "impact": 2.0},
            {"urgency": 2.0, "impact": 3.0},
        ]
        ranked = self.scorer.rank(items)
        # 5^2*2=50 > 2^2*3=12 > 1^2*1=1
        self.assertEqual(ranked[0]["urgency"], 5.0)
        self.assertEqual(ranked[1]["urgency"], 2.0)

    def test_explain_keys(self):
        info = self.scorer.explain(3.0, 2.0)
        for key in ("urgency", "impact", "urgency_squared", "raw_score", "final_score", "formula"):
            self.assertIn(key, info)


class TestDedup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.idx = DedupIndex(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_first_put_not_duplicate(self):
        _, is_dup = self.idx.put({"data": "hello"})
        self.assertFalse(is_dup)

    def test_second_put_is_duplicate(self):
        self.idx.put({"data": "hello"})
        _, is_dup = self.idx.put({"data": "hello"})
        self.assertTrue(is_dup)

    def test_ref_count_increments(self):
        h, _ = self.idx.put({"x": 1})
        self.idx.put({"x": 1})
        self.assertEqual(self.idx.get(h)["ref_count"], 2)

    def test_contains(self):
        self.idx.put({"v": 42})
        self.assertTrue(self.idx.contains({"v": 42}))
        self.assertFalse(self.idx.contains({"v": 99}))

    def test_stats(self):
        self.idx.put({"a": 1})
        self.idx.put({"a": 1})
        self.idx.put({"b": 2})
        s = self.idx.stats()
        self.assertEqual(s["total_canonical"], 2)
        self.assertEqual(s["deduped_savings"], 1)

    def test_sha256_deterministic(self):
        h1 = _sha256({"key": "val"})
        h2 = _sha256({"key": "val"})
        self.assertEqual(h1, h2)

    def test_remove(self):
        h, _ = self.idx.put({"r": 1})
        removed = self.idx.remove(h)
        self.assertTrue(removed)
        self.assertIsNone(self.idx.get(h))

    def test_persistence(self):
        self.idx.put({"persist": True})
        # New instance, same file
        idx2 = DedupIndex(self.tmp.name)
        self.assertTrue(idx2.contains({"persist": True}))


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        self.tmp.close()
        self.q = OperationQueue(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_enqueue_and_pending(self):
        self.q.enqueue("save", {"v": 1})
        self.assertEqual(len(self.q.pending()), 1)

    def test_idempotency(self):
        key = self.q.enqueue("save", {"v": 1}, idem_key="abc")
        self.q.enqueue("save", {"v": 1}, idem_key="abc")
        self.assertEqual(len(self.q.all_entries()), 1)

    def test_mark_applied(self):
        key = self.q.enqueue("task", {})
        self.q.mark_applied(key)
        pending = self.q.pending()
        self.assertEqual(len(pending), 0)

    def test_mark_failed(self):
        key = self.q.enqueue("task", {})
        self.q.mark_failed(key, "network error")
        entries = self.q.all_entries()
        self.assertEqual(entries[0]["status"], "failed")

    def test_stats(self):
        self.q.enqueue("t1", {})
        self.q.enqueue("t2", {})
        key = self.q.enqueue("t3", {})
        self.q.mark_applied(key)
        s = self.q.stats()
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["by_status"].get("pending"), 2)
        self.assertEqual(s["by_status"].get("applied"), 1)


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        self.tmp.close()
        self.lc = DataLifecycle(self.tmp.name, soft_delete_retention_days=0)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_soft_delete_and_eligible(self):
        self.lc.soft_delete("rec1")
        # retention=0 means immediately eligible
        eligible = self.lc.purge_eligible()
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]["record_id"], "rec1")

    def test_restore_removes_from_eligible(self):
        self.lc.soft_delete("rec2")
        self.lc.restore("rec2")
        self.assertEqual(len(self.lc.purge_eligible()), 0)

    def test_hard_purge_requires_confirm(self):
        self.lc.soft_delete("rec3")
        result = self.lc.hard_purge("rec3", confirmed=False)
        self.assertFalse(result)
        # still eligible
        self.assertEqual(len(self.lc.purge_eligible()), 1)

    def test_hard_purge_confirmed(self):
        self.lc.soft_delete("rec4")
        result = self.lc.hard_purge("rec4", confirmed=True)
        self.assertTrue(result)
        self.assertEqual(len(self.lc.purge_eligible()), 0)

    def test_stats(self):
        self.lc.soft_delete("a")
        self.lc.soft_delete("b")
        self.lc.hard_purge("a", confirmed=True)
        s = self.lc.stats()
        self.assertEqual(s["soft_deleted"], 2)
        self.assertEqual(s["hard_purged"], 1)
        self.assertEqual(s["eligible_for_purge"], 1)


class TestThermalRegulator(unittest.TestCase):
    def test_snapshot_keys(self):
        tr = ThermalRegulator()
        snap = tr.snapshot()
        for k in ("cpu_percent", "mem_percent", "temperature_c", "sampled_at"):
            self.assertIn(k, snap)

    def test_pressure_state_low(self):
        tr = ThermalRegulator(cpu_high=80, cpu_low=40, max_concurrency=4)
        # Mock snapshot to return low CPU
        tr.snapshot = lambda: {"cpu_percent": 10.0, "mem_percent": 20.0, "temperature_c": None, "sampled_at": 0}
        tr.allowed_concurrency = lambda: 4
        self.assertEqual(tr.pressure_state(), "low")

    def test_allowed_concurrency_range(self):
        tr = ThermalRegulator(cpu_high=80, cpu_low=40, max_concurrency=4)
        c = tr.allowed_concurrency()
        self.assertGreaterEqual(c, 1)
        self.assertLessEqual(c, 4)


if __name__ == "__main__":
    unittest.main()
