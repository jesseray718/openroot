# SPDX-License-Identifier: Apache-2.0
import copy
import tempfile
import unittest
from pathlib import Path
from openloom.need_outcome import cached_evaluate, evaluate, plan_chain


def fixture():
    return {
        "need_id": "fixture-need",
        "context_id": "fixture-context",
        "policy_id": "fixture-policy-v1",
        "access_scope": "fixture-local",
        "freshness": {"corpus_generation": "fixture-1"},
        "policy": {
            "required_gates": ["consent", "safety"],
            "criteria": {"benefit": "max", "cost": "min"},
        },
        "pathways": [
            {
                "id": "A",
                "gates": {"consent": True, "safety": True},
                "measures": {
                    "benefit": {
                        "value": 5, "comparison_basis": "fixture-benefit-v1",
                        "evidence_refs": ["fixture:E1"],
                    },
                    "cost": {
                        "value": 2, "comparison_basis": "fixture-cost-v1",
                        "evidence_refs": ["fixture:E2"],
                    },
                },
            }
        ],
    }


class EngineTests(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(evaluate(fixture())["frontier"], ["A"])

    def test_missing_gate_holds(self):
        value = fixture()
        del value["pathways"][0]["gates"]["consent"]
        self.assertEqual(evaluate(value)["assessments"][0]["state"], "HOLD")

    def test_failed_gate_cannot_be_offset(self):
        value = fixture()
        value["pathways"][0]["gates"]["safety"] = False
        value["pathways"][0]["measures"]["benefit"]["value"] = 1e9
        self.assertEqual(evaluate(value)["assessments"][0]["state"], "EXCLUDE")

    def test_missing_evidence_holds(self):
        value = fixture()
        value["pathways"][0]["measures"]["cost"]["evidence_refs"] = []
        self.assertEqual(evaluate(value)["assessments"][0]["state"], "HOLD")

    def test_nan_holds(self):
        value = fixture()
        value["pathways"][0]["measures"]["benefit"]["value"] = float("nan")
        with self.assertRaises(ValueError):
            evaluate(value)

    def test_dominated_option(self):
        value = fixture()
        other = copy.deepcopy(value["pathways"][0])
        other["id"] = "B"
        other["measures"]["cost"]["value"] = 3
        value["pathways"].append(other)
        self.assertEqual(evaluate(value)["frontier"], ["A"])

    def test_incomparable_bases_hold(self):
        value = fixture()
        other = copy.deepcopy(value["pathways"][0])
        other["id"] = "B"
        other["measures"]["cost"]["comparison_basis"] = "different-currency"
        value["pathways"].append(other)
        self.assertEqual(evaluate(value)["comparison_state"], "HOLD")

    def test_exact_cache_and_changed_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "cache.sqlite"
            value = fixture()
            self.assertFalse(cached_evaluate(db, value)["receipt"]["cache_hit"])
            self.assertTrue(cached_evaluate(db, value)["receipt"]["cache_hit"])
            value["freshness"]["corpus_generation"] = "fixture-2"
            self.assertFalse(cached_evaluate(db, value)["receipt"]["cache_hit"])

    def test_failed_evaluation_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            value = fixture()
            del value["policy"]
            with self.assertRaises(ValueError):
                cached_evaluate(Path(directory) / "cache.sqlite", value)

    def test_chain_propagates_intervention(self):
        output = plan_chain([
            {"id": "A", "worker": "review", "approval_required": True},
            {"id": "B", "worker": "build", "depends_on": ["A"]},
        ])
        self.assertEqual(output["plan"][1]["route"], "blocked-by-intervention")
        self.assertFalse(output["executed"])

    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):
            plan_chain([
                {"id": "A", "worker": "x", "depends_on": ["B"]},
                {"id": "B", "worker": "y", "depends_on": ["A"]},
            ])


if __name__ == "__main__":
    unittest.main()
