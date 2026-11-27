import hashlib
import os
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "agape_ledger.sh"


class AgapeLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "audit.log"
        self.env = {**os.environ, "AGAPE_LEDGER_FILE": str(self.path)}

    def run_ledger(self, *args):
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_pipe_message_and_tampering(self):
        self.assertEqual(0, self.run_ledger("log", "TEST", "one|two").returncode)
        self.assertEqual(0, self.run_ledger("log", "TEST", "second").returncode)
        self.assertEqual(0, self.run_ledger("verify").returncode)
        data = self.path.read_text().replace("one|two", "one|changed")
        self.path.write_text(data)
        self.assertNotEqual(0, self.run_ledger("verify").returncode)
        self.assertNotEqual(0, self.run_ledger("log", "TEST", "third").returncode)
        self.assertEqual(data, self.path.read_text())

    def test_missing_empty_and_truncated_chain_fail(self):
        self.assertNotEqual(0, self.run_ledger("verify").returncode)
        self.path.touch()
        self.assertNotEqual(0, self.run_ledger("verify").returncode)
        self.assertEqual(0, self.run_ledger("log", "TEST", "first").returncode)
        self.path.write_bytes(self.path.read_bytes().rstrip(b"\n"))
        self.assertNotEqual(0, self.run_ledger("verify").returncode)

    def test_existing_format_is_preserved_when_appending(self):
        prefix = "2026-01-01T000000Z|TEST|legacy"
        digest = hashlib.sha256(f"{prefix}|{'0' * 64}".encode()).hexdigest()
        original = f"{prefix}|{digest}\n"
        self.path.write_text(original)
        self.assertEqual(0, self.run_ledger("verify").returncode)
        self.assertEqual(0, self.run_ledger("log", "TEST", "new").returncode)
        self.assertTrue(self.path.read_text().startswith(original))
        self.assertEqual(0, self.run_ledger("verify").returncode)

    def test_concurrent_writers_preserve_chain(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: self.run_ledger("log", "TEST", str(i)), range(16)))
        self.assertTrue(all(result.returncode == 0 for result in results))
        self.assertEqual(16, len(self.path.read_text().splitlines()))
        self.assertEqual(0, self.run_ledger("verify").returncode)

    def test_multiline_input_is_rejected(self):
        self.assertNotEqual(0, self.run_ledger("log", "TEST", "first\nsecond").returncode)
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
