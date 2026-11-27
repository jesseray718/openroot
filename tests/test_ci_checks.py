import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


chains = load("check_tracked_chains")
secrets = load("check_tracked_secrets")


def entry(previous, seq):
    record = {"previous_hash": previous, "seq": seq}
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["hash"] = hashlib.sha256(encoded).hexdigest()
    return record


class CICheckTests(unittest.TestCase):
    def test_pathway_chain_and_tampering(self):
        first = entry(None, 1)
        second = entry(first["hash"], 2)
        self.assertIsNone(chains.check_records([first, second]))
        second["seq"] = 3
        self.assertIn("sequence mismatch", chains.check_records([first, second]))

    def test_genesis_serialization_and_missing_link(self):
        record = {"block_id": 0, "previous_hash": "GENESIS"}
        record["hash"] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        self.assertIsNone(chains.check_records([record]))
        del record["previous_hash"]
        self.assertIn("missing link", chains.check_records([record]))

    def test_token_patterns_without_exposing_values(self):
        fake_key = b"AK" + b"IA" + b"A" * 16
        fake_token = b"gh" + b"p_" + b"A" * 36
        self.assertIn("AWS access key ID", secrets.scan(fake_key))
        self.assertIn("GitHub token", secrets.scan(fake_token))
        self.assertEqual([], secrets.scan(b"ordinary text"))


if __name__ == "__main__":
    unittest.main()
