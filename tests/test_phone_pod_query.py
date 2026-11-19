import hashlib
import http.server
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class OllamaHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length))
        payload = json.dumps({"response": "Heat is stored in the masonry mass."}).encode()
        self.server.models.append(request["model"])
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


class PhonePodQueryTests(unittest.TestCase):
    def test_phone_command_verifies_snapshot_and_answers_via_loopback_ollama(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            snapshot = home / "openroot-phone-compact-test"
            for relative in (
                "bin/fts_pod_search.py",
                "bin/lumo_lib.py",
            ):
                destination = snapshot / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPO_ROOT / relative, destination)

            db_path = snapshot / "data/thermodynamics/openroot_interactive_pods.db"
            db_path.parent.mkdir(parents=True)
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "CREATE TABLE interactive_chain "
                    "(block_height INTEGER PRIMARY KEY, merkle_root TEXT)"
                )
                conn.execute(
                    "CREATE VIRTUAL TABLE pod_fts USING fts5("
                    "block_height UNINDEXED, timestamp UNINDEXED, prompt_text, "
                    "response_text, dossier_tags UNINDEXED)"
                )
                conn.execute("INSERT INTO interactive_chain VALUES (1, 'root-1')")
                conn.execute(
                    "INSERT INTO pod_fts VALUES (1, '2026-11-01', "
                    "'thermal storage', 'Store heat in masonry.', 'energy')"
                )
                for height in range(2, 5):
                    conn.execute(
                        "INSERT INTO interactive_chain VALUES (?, ?)",
                        (height, f"root-{height}"),
                    )
                    conn.execute(
                        "INSERT INTO pod_fts VALUES (?, '2026-11-01', "
                        "'thermal storage', 'Another record.', 'energy')",
                        (height,),
                    )

            manifest_files = []
            for relative in (
                "bin/fts_pod_search.py",
                "bin/lumo_lib.py",
                "data/thermodynamics/openroot_interactive_pods.db",
            ):
                path = snapshot / relative
                manifest_files.append({
                    "path": relative,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
            (snapshot / "manifest.json").write_text(json.dumps({
                "type": "test",
                "payload_bytes": sum(item["bytes"] for item in manifest_files),
                "omitted": [],
                "files": manifest_files,
            }))
            (snapshot / "verification.txt").write_text("verified")

            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), OllamaHandler)
            server.models = []
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(thread.join)
            self.addCleanup(server.shutdown)

            env = {
                **os.environ,
                "HOME": str(home),
                "OLLAMA_HOST": f"http://127.0.0.1:{server.server_port}",
            }
            result = subprocess.run(
                [
                    sys.executable, str(REPO_ROOT / "bin/openroot-phone-v1"),
                    "ask", "--json", "thermal storage",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            desktop = subprocess.run(
                [
                    sys.executable, str(REPO_ROOT / "bin/fts_pod_search.py"),
                    "ask", "--db", str(db_path), "--json", "thermal storage",
                ],
                cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False,
            )
            (snapshot / "bin/lumo_lib.py").write_text("tampered")
            tampered = subprocess.run(
                [
                    sys.executable, str(REPO_ROOT / "bin/openroot-phone-v1"),
                    "ask", "--json", "thermal storage",
                ],
                cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(0, desktop.returncode, desktop.stderr)
        answer = json.loads(result.stdout)
        desktop_answer = json.loads(desktop.stdout)
        self.assertEqual("Heat is stored in the masonry mass.", answer["answer"])
        self.assertEqual("qwen2.5:1.5b", server.models[0])
        self.assertEqual(3, len(answer["evidence_ids"]))
        self.assertEqual(answer["evidence_ids"], desktop_answer["evidence_ids"])
        self.assertEqual(answer["database_sha256"], desktop_answer["database_sha256"])
        self.assertEqual(
            f"root-{answer['evidence'][0]['block_height']}",
            answer["evidence"][0]["merkle_root"],
        )
        self.assertNotEqual(0, tampered.returncode)
        self.assertIn("FAIL: bin/lumo_lib.py", tampered.stderr)
        self.assertEqual(2, len(server.models))


if __name__ == "__main__":
    unittest.main()
