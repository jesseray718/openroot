#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
rootkit - unified dispatcher for the openroot organism.

Doctrine:
  - SHA-256 content addressing is the spine; organs talk by hash.
  - Exit codes: 0=BANKED (work really ran), 1=HELD (human gate / not built),
    2=ERROR (abort).
  - Never report BANKED for work that did not run.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
BIN = ROOT / "bin"
DATA = ROOT / "data"
LOGS = ROOT / "logs"

CANARY = "[ROOTKIT]"
EXIT = {"BANKED": 0, "HELD": 1, "ERROR": 2}

# Organs that exist today and are really wired.
WIRED = {
    "ingest": BIN / "lumo_ingest.py",
    "index": BIN / "a1_core_v1.py",
    "route": BIN / "a1_core_v1.py",
    "bom": BIN / "bom_from_source_v1.py",
    "migrate": BIN / "rootkit_migrate_v1.py",
}

# Organs that are planned but not built yet. Calls return HELD.
PLANNED = {
    "chunk": BIN / "chunker_v1.py",
    "ask": BIN / "agape_router_v1.py",
    "attest": BIN / "popw_ledger_v1.py",
    "mint": BIN / "newton_chain_v1.py",
    "publish": BIN / "relay_loop_v1.py",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_op(severity, msg):
    print(f"{now()} {CANARY} {severity:>6s}  {msg}")


def sha256_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def invoke(script_path, args=None, timeout=3600):
    if not script_path.exists():
        return EXIT["ERROR"], "", f"script not found: {script_path}"
    cmd = [sys.executable, str(script_path)] + list(args or [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return EXIT["ERROR"], "", f"timeout invoking {script_path}"
    except Exception as e:
        return EXIT["ERROR"], "", str(e)


def finish(name, rc, out, err):
    """Map a delegate's exit code to a rootkit exit code and log it."""
    if rc == 0:
        log_op("BANKED", f"{name} complete")
        if out.strip():
            print(out.rstrip())
        return EXIT["BANKED"]
    if rc == 1:
        log_op("HELD", f"{name} held (human gate)")
        if out.strip():
            print(out.rstrip())
        return EXIT["HELD"]
    log_op("ERROR", f"{name} failed rc={rc}")
    if out.strip():
        print(out.rstrip())
    if err.strip():
        print(err.rstrip(), file=sys.stderr)
    return EXIT["ERROR"]


def planned_stub(name):
    log_op("HELD", f"{name}: organ not built yet ({PLANNED[name].name})")
    return EXIT["HELD"]


def cmd_ingest(args):
    log_op("GATE", "ingest: lumo_ingest.py")
    return finish("ingest", *invoke(WIRED["ingest"]))


def cmd_index(args):
    log_op("GATE", "index: a1_core_v1.py scan")
    return finish("index", *invoke(WIRED["index"], ["scan"]))


def cmd_chunk(args):
    return planned_stub("chunk")


def cmd_ask(args):
    if not args.query:
        log_op("ERROR", "ask: requires --query")
        return EXIT["ERROR"]
    # Routing hint only; no retrieval is performed yet.
    rc, out, err = invoke(WIRED["route"], ["route", "--task", args.query])
    log_op("HELD", "ask: retrieval not built; routing hint only")
    if out.strip():
        print(out.rstrip())
    return EXIT["HELD"]


def load_spec(raw):
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    with open(raw) as f:
        return json.load(f)


def cmd_task(args):
    if not args.spec:
        log_op("ERROR", "task: requires --spec (JSON or path)")
        return EXIT["ERROR"]
    try:
        spec = load_spec(args.spec)
    except (json.JSONDecodeError, OSError) as e:
        log_op("ERROR", f"task: spec parse failed: {e}")
        return EXIT["ERROR"]

    spec_sha = sha256_text(json.dumps(spec, sort_keys=True))
    ttype = spec.get("type")
    log_op("GATE", f"task: spec_sha256={spec_sha[:12]} type={ttype}")

    if ttype == "bom":
        if not spec.get("source"):
            log_op("ERROR", "task[bom]: spec.source required")
            return EXIT["ERROR"]
        return finish("task[bom]", *invoke(WIRED["bom"], ["--source", spec["source"]]))

    # No executor: never report BANKED for work that did not run.
    rc, out, err = invoke(WIRED["route"], ["route", "--task", json.dumps(spec)])
    log_op("HELD", f"task: no executor for type={ttype!r}; routing hint only")
    if out.strip():
        print(out.rstrip())
    return EXIT["HELD"]


def cmd_attest(args):
    return planned_stub("attest")


def cmd_mint(args):
    return planned_stub("mint")


def cmd_publish(args):
    return planned_stub("publish")


def cmd_audit(args):
    log_op("HELD", "audit: not built yet")
    return EXIT["HELD"]


def cmd_organism(args):
    log_op("HELD", "organism: loop not built yet")
    return EXIT["HELD"]


def cmd_doctor(args):
    print(f"{CANARY} doctor: preflight")
    wired_missing = []
    print(" wired:")
    for name, path in sorted(WIRED.items()):
        ok = path.exists()
        if not ok:
            wired_missing.append(name)
        print(f"  {name:8s} {path.name:28s} {'OK' if ok else 'MISSING'}")
    planned_missing = []
    print(" planned:")
    for name, path in sorted(PLANNED.items()):
        ok = path.exists()
        if not ok:
            planned_missing.append(name)
        print(f"  {name:8s} {path.name:28s} {'present' if ok else 'not built'}")
    if wired_missing:
        log_op("ERROR", f"wired organs missing: {', '.join(wired_missing)}")
        return EXIT["ERROR"]
    if planned_missing:
        log_op("HELD", f"wired OK; not built: {', '.join(planned_missing)}")
        return EXIT["HELD"]
    log_op("BANKED", "all organs present")
    return EXIT["BANKED"]


def main():
    handlers = {
        "ingest": cmd_ingest, "chunk": cmd_chunk, "index": cmd_index,
        "ask": cmd_ask, "task": cmd_task, "attest": cmd_attest,
        "mint": cmd_mint, "publish": cmd_publish, "audit": cmd_audit,
        "doctor": cmd_doctor, "organism": cmd_organism,
    }
    p = argparse.ArgumentParser(description=f"{CANARY} openroot dispatcher")
    p.add_argument("cmd", nargs="?", default="doctor", choices=sorted(handlers))
    p.add_argument("--query", default=None)
    p.add_argument("--spec", default=None)
    p.add_argument("--job-id", default=None)
    p.add_argument("--tag", default=None)
    args = p.parse_args()

    for d in (DATA, LOGS):
        d.mkdir(parents=True, exist_ok=True)
    sys.exit(handlers[args.cmd](args))


if __name__ == "__main__":
    main()
