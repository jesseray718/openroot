import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "master_mesh_sync_loop.sh"


class MeshSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = self.root / SCRIPT.name
        self.script.write_bytes(SCRIPT.read_bytes())
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name, body in {
            "sleep": "exit 77\n",
            "scp": 'printf "%s\\n" "$@" > "$ARGS_FILE"\nexit "${SCP_EXIT:-0}"\n',
        }.items():
            path = self.bin / name
            path.write_text("#!/usr/bin/env bash\n" + body)
            path.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
            "OPTIPLEX_TAILSCALE_IP": "example.invalid",
            "MESH_SSH_USER": "example",
            "MESH_REMOTE_DIR": "/destination",
            "ARGS_FILE": str(self.root / "scp-args"),
            "MESH_PAYLOAD_KEEP": "2",
        }

    def run_loop(self, env=None):
        return subprocess.run(
            ["bash", str(self.script)],
            env=env or self.env,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_missing_destination_fails_before_creating_payload(self):
        env = self.env.copy()
        del env["OPTIPLEX_TAILSCALE_IP"]
        result = self.run_loop(env)
        self.assertNotEqual(0, result.returncode)
        self.assertFalse((self.root / "workareas").exists())

    def test_success_excludes_logs_and_retains_latest_payloads(self):
        export = self.root / "workareas" / "mesh_export_redacted"
        export.mkdir(parents=True)
        (export / "item.txt").write_text("item")
        logs = self.root / "workareas" / "compost_logs"
        logs.mkdir()
        (logs / "private.txt").write_text("private")
        releases = self.root / "workareas" / "release"
        releases.mkdir()
        for year in ("20000101", "20010101"):
            (releases / f"mesh_sync_payload_{year}T000000Z_old.tar.gz").write_text("old")

        result = self.run_loop()
        self.assertEqual(77, result.returncode)
        self.assertIn("[ok] transmitted", result.stdout)
        self.assertIn("BatchMode=yes", (self.root / "scp-args").read_text())
        payloads = sorted(releases.glob("mesh_sync_payload_*.tar.gz"))
        self.assertEqual(2, len(payloads))
        with tarfile.open(payloads[-1]) as archive:
            names = archive.getnames()
        self.assertIn("workareas/mesh_export_redacted/item.txt", names)
        self.assertFalse(any("compost_logs" in name for name in names))

    def test_failed_transfer_is_not_reported_as_transmitted(self):
        (self.root / "workareas" / "mesh_export_redacted").mkdir(parents=True)
        self.env["SCP_EXIT"] = "1"
        result = self.run_loop()
        self.assertEqual(77, result.returncode)
        self.assertNotIn("transmitted", result.stdout)
        self.assertIn("transfer failed", result.stderr)

    def test_failed_archive_is_not_sent(self):
        (self.root / "workareas" / "mesh_export_redacted").mkdir(parents=True)
        fake_tar = self.bin / "tar"
        fake_tar.write_text("#!/usr/bin/env bash\nexit 1\n")
        fake_tar.chmod(0o755)
        result = self.run_loop()
        self.assertIn("payload creation failed", result.stderr)
        self.assertFalse((self.root / "scp-args").exists())
        self.assertEqual([], list((self.root / "workareas" / "release").glob("*.tar.gz")))


if __name__ == "__main__":
    unittest.main()
