#!/usr/bin/env python3
"""Probe OptiPlex from A15. Never run the A15 key path on the box as a requirement."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_lib  # noqa: E402

TARGET = "jesse@192.168.1.193"
KEY = "/data/data/com.termux/files/home/.ssh/id_ed25519_optiplex"
ALIAS_HINT = "Host optiplex  HostName 192.168.1.193  User jesse"


def run(cmd, timeout=12):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        ms = int((time.time() - t0) * 1000)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip(), ms
    except subprocess.TimeoutExpired:
        return 124, "", "timeout", int((time.time() - t0) * 1000)
    except FileNotFoundError:
        return 127, "", "ssh binary missing", 0


def main() -> int:
    pane = kit_lib.detect_pane()
    report = {
        "pane": pane,
        "target": TARGET,
        "ssh_bin": shutil.which("ssh"),
        "key_exists": Path(KEY).exists() if pane == "A15" else None,
        "alias_hint": ALIAS_HINT,
    }
    if pane == "SSH":
        report["note"] = "already on the box; probe is A15-to-box. hostname local only."
        rc, out, err, ms = run(["hostname"])
        report["hostname"] = out or err
        report["ok"] = rc == 0
        print(json.dumps(report, indent=2))
        return 0 if rc == 0 else 1
    if pane != "A15":
        report["ok"] = False
        report["note"] = "unknown pane; will not guess IPs"
        print(json.dumps(report, indent=2))
        return 2
    if not Path(KEY).exists():
        report["ok"] = False
        report["note"] = "key missing; do not generate a second key until you list authorized_keys on the box"
        print(json.dumps(report, indent=2))
        return 3
    cmd = [
        "ssh",
        "-i",
        KEY,
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=8",
        "-o",
        "StrictHostKeyChecking=accept-new",
        TARGET,
        "hostname; uname -s; test -d /home/jesse/models; echo MODELS:$?; test -d /home/jesse/openroot; echo OPENROOT:$?",
    ]
    rc, out, err, ms = run(cmd)
    report["rc"] = rc
    report["latency_ms"] = ms
    report["out"] = out
    report["err"] = err
    report["ok"] = rc == 0
    try:
        con = kit_lib.connect()
        con.execute(
            "INSERT INTO ssh_session(t,target,key_path,rc,latency_ms,note) VALUES(?,?,?,?,?,?)",
            (
                time.strftime("%Y-%m-%dT%H:%M:%S"),
                TARGET,
                KEY,
                rc,
                ms,
                out[:200] if out else err[:200],
            ),
        )
        con.commit()
        report["logged"] = True
    except Exception as e:
        report["logged"] = False
        report["log_err"] = str(e)
    print(json.dumps(report, indent=2))
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
