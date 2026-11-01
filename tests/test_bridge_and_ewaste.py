import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "bin"))

import ewaste_manager
import node_bridge_sync


class EWasteBookingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.slots = self.root / "slots.json"
        self.ledger = self.root / "newton_chain.jsonl"
        self.slots.write_text(
            json.dumps({"2026-11-01": ["09:00", "11:00"]}),
            encoding="utf-8",
        )

    def test_booking_is_idempotent_and_seals_one_chain_receipt(self):
        self.assertTrue(ewaste_manager.book_slot(
            "2026-11-01", "09:00", self.slots, self.ledger
        ))
        self.assertTrue(ewaste_manager.book_slot(
            "2026-11-01", "09:00", self.slots, self.ledger
        ))

        self.assertEqual(
            {"2026-11-01": ["11:00"]},
            json.loads(self.slots.read_text(encoding="utf-8")),
        )
        records = ewaste_manager._read_receipts(self.ledger)
        self.assertEqual(1, len(records))
        self.assertEqual("EWASTE_PICKUP_BOOKED", records[0]["event"])

    def test_unavailable_slot_does_not_change_state(self):
        before = self.slots.read_text(encoding="utf-8")
        self.assertFalse(ewaste_manager.book_slot(
            "2026-11-01", "14:00", self.slots, self.ledger
        ))
        self.assertEqual(before, self.slots.read_text(encoding="utf-8"))
        self.assertFalse(self.ledger.exists())

    def test_invalid_date_or_time_is_rejected(self):
        with self.assertRaises(ValueError):
            ewaste_manager.book_slot("2026-02-30", "09:00", self.slots, self.ledger)
        with self.assertRaises(ValueError):
            ewaste_manager.book_slot("2026-11-01", "9:00", self.slots, self.ledger)


class NodeBridgeSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        (self.root / "data/wealth_retention").mkdir(parents=True)
        (self.root / "data/wealth_retention/manifesto.md").write_text(
            "Community wealth retention\n", encoding="utf-8"
        )
        (self.root / "bin").mkdir()
        (self.root / "bin/ewaste_manager.py").write_text("print('pipeline')\n", encoding="utf-8")

    def test_sync_defaults_to_rsync_dry_run_and_deduplicates_receipt(self):
        env = {
            "OPENROOT_HUB_HOST": "hub.example",
            "OPENROOT_HUB_USER": "operator",
            "OPENROOT_HUB_PATH": "~/openroot",
        }
        with patch.dict(os.environ, env, clear=False), patch.object(
            node_bridge_sync.subprocess, "run", return_value=type(
                "Result", (), {"stdout": ""})()
        ) as run:
            node_bridge_sync.sync(self.root)
            node_bridge_sync.sync(self.root)

        command = run.call_args.args[0]
        self.assertIn("--dry-run", command)
        self.assertIsInstance(command, list)
        self.assertFalse(run.call_args.kwargs.get("shell", False))
        receipts = (self.root / "data/bridge_receipts.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(1, len(receipts))
        self.assertEqual(
            ["bin/ewaste_manager.py", "data/wealth_retention/manifesto.md"],
            sorted(item["path"] for item in json.loads(receipts[0])["files"]),
        )

    def test_sync_rejects_shell_metacharacters_in_target_config(self):
        env = {
            "OPENROOT_HUB_HOST": "hub.example;touch",
            "OPENROOT_HUB_USER": "operator",
            "OPENROOT_HUB_PATH": "~/openroot",
        }
        with patch.dict(os.environ, env, clear=False), patch.object(
            node_bridge_sync.subprocess, "run"
        ) as run:
            with self.assertRaises(ValueError):
                node_bridge_sync.sync(self.root)
        run.assert_not_called()

    def test_sync_refuses_symlinked_blueprint_files(self):
        outside = self.root.parent / "outside-blueprint.md"
        outside.write_text("not for sync\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        link = self.root / "data/wealth_retention/external.md"
        link.symlink_to(outside)
        with self.assertRaises(ValueError):
            node_bridge_sync._file_manifest(self.root)

    def test_failed_attempt_can_be_retried_and_success_is_sealed(self):
        env = {
            "OPENROOT_HUB_HOST": "hub.example",
            "OPENROOT_HUB_USER": "operator",
            "OPENROOT_HUB_PATH": "~/openroot",
        }
        failure = node_bridge_sync.subprocess.CalledProcessError(1, ["rsync"])
        success = type("Result", (), {"stdout": ""})()
        with patch.dict(os.environ, env, clear=False), patch.object(
            node_bridge_sync.subprocess, "run", side_effect=[failure, success]
        ):
            with self.assertRaises(RuntimeError):
                node_bridge_sync.sync(self.root, apply=True)
            node_bridge_sync.sync(self.root, apply=True)

        records = node_bridge_sync._read_receipts(self.root / "data/bridge_receipts.jsonl")
        self.assertEqual(["failed", "complete"], [record["status"] for record in records])


if __name__ == "__main__":
    unittest.main()
