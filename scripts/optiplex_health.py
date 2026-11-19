#!/usr/bin/env python3
import os
import subprocess
import sqlite3
import json
from pathlib import Path

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def check_optiplex_health():
    report = {}
    ollama_ok, _ = run_cmd("pgrep -x ollama || pgrep -x llama-server")
    report["local_inference_engine"] = "Active" if ollama_ok else "Inactive"
    
    ts_ok, ts_out = run_cmd("tailscale status --json")
    if ts_ok:
        ts_data = json.loads(ts_out)
        report["tailscale_mesh"] = {
            "status": "Connected",
            "self": ts_data.get("Self", {}).get("HostName", "Unknown")
        }
    else:
        report["tailscale_mesh"] = {"status": "Disconnected"}

    git_ok, git_out = run_cmd("git worktree list")
    report["git_worktrees"] = git_out.splitlines() if git_ok else "No active worktrees"

    db_path = Path.expanduser(Path("~/openroot/db/canonical.db"))
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            integrity = cursor.fetchone()[0]
            conn.close()
            report["canonical_sqlite_db"] = f"Healthy ({integrity})"
        except Exception as e:
            report["canonical_sqlite_db"] = f"Error: {e}"
    else:
        report["canonical_sqlite_db"] = "Path not initialized"

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    check_optiplex_health()
