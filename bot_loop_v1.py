#!/data/data/com.termux/files/usr/bin/python3
"""OPENROOT BOT LOOP v1.0 — canary [botloop-v1-ok]

Autonomous watch->sync->refine->absorb cycle.
- Watches mobile ledgers (hash change = activity)
- Re-runs unify_v2.py when changes detected
- Captures failures with sha256 into OptiPlex data/lessons.db
- PID-locked, single instance, survives shell exit via nohup
"""
import json, hashlib, time, subprocess, pathlib, os, sys
from datetime import datetime, timezone

HOME = pathlib.Path(os.path.expanduser("~"))
OPENROOT = HOME / "openroot"
BOTSTATE = OPENROOT / "data_bot_state.json"
UNIFIER = OPENROOT / "unify_v2.py"
PIDFILE = OPENROOT / "bot_loop.pid"
LOOP_INTERVAL_S = 300  # 5 min cadence
OPTIPLEX_USER = "jesse"
OPTIPLEX_HOST = "192.168.1.193"
OPTIPLEX_BASE = "/home/jesse/openroot"

WATCHED = [
    "/sdcard/openroot/thermo_ledger/eta_moves.jsonl",
    "/sdcard/openroot/parallel_analysis/ledger/ideas.jsonl",
    "/sdcard/openroot/ledger/experiments/linux_command_persistence.jsonl",
]

def fhash(path):
    p = pathlib.Path(path)
    if not p.exists():
        return "missing"
    return hashlib.sha256(p.read_bytes()).hexdigest()

def snapshot():
    return {w: fhash(w) for w in WATCHED}

def absorb_failure(stage, err_text, exit_code):
    """Hash-bind failure into OptiPlex lessons.db via SSH (The Chain)."""
    err_text = (err_text or "")[:500]
    lesson = {
        "stage": stage,
        "error": err_text,
        "exit_code": exit_code,
        "ts": time.time(),
        "sha256": hashlib.sha256(
            (stage + err_text + str(exit_code)).encode()
        ).hexdigest(),
    }
    payload = json.dumps(lesson).replace("'", "'\\''")
    cmd = (
        f"ssh -o BatchMode=yes -o ConnectTimeout=10 {OPTIPLEX_USER}@{OPTIPLEX_HOST} "
        f"'cd {OPTIPLEX_BASE} && mkdir -p data && sqlite3 data/lessons.db "
        f"\"CREATE TABLE IF NOT EXISTS lessons ("
        f"id INTEGER PRIMARY KEY, ts REAL, stage TEXT, error TEXT, "
        f"exit_code INTEGER, sha256 TEXT);\" && "
        f"sqlite3 data/lessons.db "
        f"\"INSERT INTO lessons (ts,stage,error,exit_code,sha256) VALUES("
        f"'{lesson['ts']}','{lesson['stage']}','{payload[:400]}','{lesson['exit_code']}','{lesson['sha256']}');\" && "
        f"echo ABSORBED'"
    )
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return proc.returncode == 0 and "ABSORBED" in proc.stdout
    except Exception:
        return False

def run_unifier():
    proc = subprocess.run(
        ["python", str(UNIFIER)], capture_output=True, text=True, timeout=300
    )
    return proc.returncode, proc.stdout, proc.stderr

def main():
    if PIDFILE.exists():
        old_pid = PIDFILE.read_text().strip()
        try:
            if int(old_pid) == os.getpid():
                pass  # M6 fix: pidfile holds OUR OWN pid (launcher race) — take over
            else:
                os.kill(int(old_pid), 0)
                print(f"[bot] already running pid={old_pid}, exiting")
                return
        except (ValueError, ProcessLookupError, PermissionError):
            pass  # stale pid, take over
    PIDFILE.write_text(str(os.getpid()))

    state = {}
    if BOTSTATE.exists():
        try:
            state = json.loads(BOTSTATE.read_text())
        except Exception:
            state = {}

    cycle = 0
    print(f"[bot] loop started pid={os.getpid()} interval={LOOP_INTERVAL_S}s")
    while True:
        cycle += 1
        now = datetime.now(timezone.utc).isoformat()[:19]
        snap = snapshot()
        changed = [w for w in WATCHED if state.get(w) != snap[w]]

        if changed:
            print(f"[bot:{now}] cycle={cycle} CHANGE DETECTED in {len(changed)} ledger(s)")
            rc, out, err = run_unifier()
            print(out.strip()[-500:])
            if rc != 0:
                ok = absorb_failure("unifier_run", err, rc)
                print(f"[bot] FAILURE absorbed to lessons.db: {ok}")
            else:
                print(f"[bot] unifier exit=0, refinery cycle complete")
        else:
            print(f"[bot:{now}] cycle={cycle} idle — no ledger changes")

        state["snapshots"] = snap
        state["cycles"] = cycle
        state["last_ts"] = time.time()
        BOTSTATE.write_text(json.dumps(state, indent=1))

        time.sleep(LOOP_INTERVAL_S)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[bot] stopped by operator")
        if PIDFILE.exists():
            PIDFILE.unlink()
    finally:
        if PIDFILE.exists() and PIDFILE.read_text().strip() == str(os.getpid()):
            PIDFILE.unlink()
