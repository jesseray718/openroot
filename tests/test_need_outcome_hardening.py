# SPDX-License-Identifier: Apache-2.0
"""Permanent regression coverage for refinement-suite findings."""
import copy
import runpy
import unittest
from pathlib import Path

from openloom.need_outcome import VERSION, evaluate, plan_chain

fixture = runpy.run_path(
    str(Path(__file__).with_name("test_need_outcome.py"))
)["fixture"]


class HardeningTests(unittest.TestCase):
    def test_oversized_integer_has_controlled_error(self):
        value = fixture()
        value["pathways"][0]["measures"]["cost"]["value"] = 10 ** 400
        with self.assertRaisesRegex(ValueError, "numeric range"):
            evaluate(value)

    def test_blank_request_identifiers_rejected(self):
        blanks = (
            "",
            "   ",
            chr(9),
            chr(10),
            " " + chr(9) + chr(10),
        )
        for name in ("need_id", "context_id", "policy_id", "access_scope"):
            for blank in blanks:
                with self.subTest(field=name, value=repr(blank)):
                    self.assertEqual(blank.strip(), "")
                    value = fixture()
                    value[name] = blank
                    with self.assertRaises(ValueError):
                        evaluate(value)

    def test_invalid_freshness_labels_rejected(self):
        examples = [
            {},
            {"corpus_generation": ""},
            {"corpus_generation": "   "},
            {" ": "generation-1"},
            {"corpus_generation": None},
            {"corpus_generation": 0},
            {"corpus_generation": False},
            {"corpus_generation": {}},
        ]
        for freshness in examples:
            with self.subTest(freshness=freshness):
                value = fixture()
                value["freshness"] = freshness
                with self.assertRaises(ValueError):
                    evaluate(value)

    def test_multiple_generation_labels_accepted(self):
        value = fixture()
        value["freshness"] = {
            "corpus_generation": "corpus-2",
            "policy_generation": "policy-3",
        }
        original = copy.deepcopy(value)
        self.assertEqual(evaluate(value)["frontier"], ["A"])
        self.assertEqual(value, original)

    def test_chain_output_identifies_engine(self):
        output = plan_chain([{"id": "A", "worker": "fixture-worker"}])
        self.assertEqual(output["engine"], VERSION)
        self.assertFalse(output["executed"])


if __name__ == "__main__":
    unittest.main()
