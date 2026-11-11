import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_newton_chain.py"


class NewtonChainValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "docs" / "newton_chain", self.root / "docs" / "newton_chain")

    def validate(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_example_passes(self):
        code, report = self.validate()
        self.assertEqual(0, code)
        self.assertEqual("passed", report["status"])

    def test_missing_proof_steps_are_rejected(self):
        example = self.root / "docs" / "newton_chain" / "EXAMPLES" / "thermal_energy_bound.yaml"
        example.write_text(
            example.read_text(encoding="utf-8").replace("proof_steps:", "missing_steps:"),
            encoding="utf-8",
        )
        code, report = self.validate()
        self.assertEqual(1, code)
        self.assertTrue(any("proof_steps" in failure for failure in report["failures"]))

    def test_unknown_status_is_rejected(self):
        example = self.root / "docs" / "newton_chain" / "EXAMPLES" / "thermal_energy_bound.yaml"
        example.write_text(
            example.read_text(encoding="utf-8").replace('status: "draft"', 'status: "unknown"', 1),
            encoding="utf-8",
        )
        code, report = self.validate()
        self.assertEqual(1, code)
        self.assertTrue(any("unsupported proof_object.status" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main()
