#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from permaculture_router import build_report, load_context


class PermacultureRouterTests(unittest.TestCase):
    def write_context(self, payload):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "context.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return directory, path

    def base_payload(self):
        return {
            "schema_version": 1,
            "name": "Test context",
            "description": "A router test context.",
            "evidence_level": 1,
            "risk_level": 0,
            "uncertainty": 0.1,
            "missing_measurements": False,
            "system_map_exists": True,
            "feedback_exists": True,
            "metric_out_of_bounds": False,
            "stop_conditions_defined": True,
            "surplus_flow": 0,
            "storage_capacity": 0,
            "expected_yield": 1,
            "minimum_yield": 1,
            "renewable_option_viable": False,
            "lifecycle_benefit": 0,
            "waste_stream_detected": False,
            "reuse_path_exists": False,
            "compatible_nodes": 0,
            "connection_value": 0,
            "connection_cost": 1,
            "intervention_scale": 1,
            "reversibility": 1.0,
            "concentration_risk": 0.1,
            "edge_opportunity_score": 0.1,
            "change_detected": False,
            "adaptation_option_exists": False,
            "safety_review_complete": True,
            "claimed_outputs": [],
            "evidence_artifacts": [],
            "tags": []
        }

    def test_safe_context_prepares_plan(self):
        directory, path = self.write_context(self.base_payload())
        self.addCleanup(directory.cleanup)

        ctx = load_context(path)
        report = build_report(ctx, path)

        self.assertEqual(report["decision"], "PREPARE_HUMAN_REVIEWABLE_PLAN")
        self.assertTrue(report["governance"]["human_approval_required"])
        self.assertFalse(report["governance"]["automatic_execution_permitted"])

    def test_risk_above_evidence_holds(self):
        payload = self.base_payload()
        payload["risk_level"] = 3
        payload["evidence_level"] = 1
        payload["safety_review_complete"] = False
        payload["stop_conditions_defined"] = False
        payload["intervention_scale"] = 3
        payload["missing_measurements"] = True
        payload["uncertainty"] = 0.9

        directory, path = self.write_context(payload)
        self.addCleanup(directory.cleanup)

        ctx = load_context(path)
        report = build_report(ctx, path)

        self.assertEqual(report["decision"], "HOLD_FOR_HUMAN_REVIEW")
        self.assertTrue(any(item["severity"] == "block" for item in report["gates"]))
        self.assertTrue(report["active_principles"]["P01"]["active"])
        self.assertTrue(report["active_principles"]["P09"]["active"])

    def test_waste_and_integration_route(self):
        payload = self.base_payload()
        payload["surplus_flow"] = 2.0
        payload["storage_capacity"] = 1.0
        payload["waste_stream_detected"] = True
        payload["reuse_path_exists"] = True
        payload["compatible_nodes"] = 2
        payload["connection_value"] = 2.0
        payload["connection_cost"] = 1.0

        directory, path = self.write_context(payload)
        self.addCleanup(directory.cleanup)

        ctx = load_context(path)
        report = build_report(ctx, path)

        self.assertTrue(report["active_principles"]["P02"]["active"])
        self.assertTrue(report["active_principles"]["P06"]["active"])
        self.assertTrue(report["active_principles"]["P08"]["active"])
        action_text = " ".join(item["action"] for item in report["recommended_actions"])
        self.assertIn("surplus or waste stream", action_text)


if __name__ == "__main__":
    unittest.main()
