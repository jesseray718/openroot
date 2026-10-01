# SPDX-License-Identifier: GPL-3.0-or-later
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicContractTests(unittest.TestCase):
    def test_required_files_exist(self):
        paths = [
            ".env.example",
            ".gitattributes",
            "docs/ARCHITECTURE.md",
            "docs/OPERATIONS.md",
            "docs/ROUTING.md",
            "docs/NEWTON_CHAIN.md",
            "schemas/routing_decision.schema.json",
            "schemas/newton_chain_claim.schema.json",
            "data/examples/routing_decision.example.json",
        ]
        for relative in paths:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_routing_example(self):
        path = ROOT / "data/examples/routing_decision.example.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "candidate")
        self.assertEqual(len(record["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
