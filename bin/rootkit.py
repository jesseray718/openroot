#!/usr/bin/env python3
"""
rootkit — the unified dispatcher for openroot's 7-layer organism.
SPDX-License-Identifier: GPL-3.0-only

Doctrine:
  - One ID system: SHA-256 content-addressing is the spine.
  - All interfaces: hash-in, hash-out. No exceptions.
  - Exit codes: 0=banked (committed), 1=held (requires gate), 2=error (abort).
"""

import argparse
import hashlib
import json
import os
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

ORGANS = {
    "ingest": BIN / "lumo_ingest.py",
    "chunk": BIN / "chunker_v1.py",
    "index": BIN / "a1_core_v1.py",
    "ask": BIN / "agape_router_v1.py",
    "task": BIN / "a1_core_v1.py",
    "attest": BIN / "popw_ledger_v1.py",
    "mint": BIN / "newton_chain_v1.py",
    "publish": BIN / "relay_loop_v1.py",
}

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def log_op(severity, msg):
    print(f"{now()} {CANARY} {severity:>8s}  {msg}")

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def invoke(script_path, args=None, stdin_text=None):
    if not script_path.exists():
        return EXIT["ERROR"], "", f"script not found: {script_path}"

    cmd = [sys.executable, str(script_path)] + (args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, input=stdin_text, timeout=3600)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return EXIT["ERROR"], "", f"timeout invoking {script_path}"
    except Exception as e:
        return EXIT["ERROR"], "", str(e)

def cmd_ingest(args):
    log_op("GATE", "ingest: delegating to lumo_ingest.py")
    rc, out, err = invoke(ORGANS["ingest"])
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"ingest complete\n{out}")
        return EXIT["BANKED"]
    elif rc == EXIT["HELD"]:
        log_op("HELD", f"ingest requires human gate\n{out}")
        return EXIT["HELD"]
    else:
        log_op("ERROR", f"ingest failed:\n{err}")
        return EXIT["ERROR"]

def cmd_chunk(args):
    if not args.shard_dir:
        log_op("ERROR", "chunk: requires --shard-dir")
        return EXIT["ERROR"]
    shard_path = Path(args.shard_dir)
    if not shard_path.exists():
        log_op("ERROR", f"chunk: shard directory absent: {shard_path}")
        return EXIT["ERROR"]
    log_op("GATE", f"chunk: processing shard {shard_path}")
    rc, out, err = invoke(ORGANS["chunk"], [str(shard_path)])
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"chunk complete\n{out}")
        return EXIT["BANKED"]
    else:
        log_op("ERROR", f"chunk failed:\n{err}")
        return EXIT["ERROR"]

def cmd_index(args):
    log_op("GATE", "index: scanning filesystem for text assets")
    cmd_args = ["scan"]
    if args.rebuild:
        log_op("HELD", "index: --rebuild flag set; clearing prior ledger (human gate)")
        cmd_args.append("--rebuild")
    rc, out, err = invoke(ORGANS["index"], cmd_args)
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"index complete\n{out}")
        return EXIT["BANKED"]
    elif rc == EXIT["HELD"]:
        log_op("HELD", f"index held\n{out}")
        return EXIT["HELD"]
    else:
        log_op("ERROR", f"index failed:\n{err}")
        return EXIT["ERROR"]

def cmd_ask(args):
    if not args.query:
        log_op("ERROR", "ask: requires --query")
        return EXIT["ERROR"]
    log_op("GATE", f"ask: routing query '{args.query}'")
    log_op("HELD", "ask: router TBD (stub)")
    return EXIT["HELD"]

def cmd_task(args):
    if not args.spec:
        log_op("ERROR", "task: requires --spec (JSON or path)")
        return EXIT["ERROR"]
    try:
        if args.spec.lstrip().startswith("{"):
            spec = json.loads(args.spec)
        else:
            with open(args.spec) as f:
                spec = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log_op("ERROR", f"task: spec parse failed: {e}")
        return EXIT["ERROR"]

    spec_sha = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    log_op("GATE", f"task: spec_sha256={spec_sha[:12]} type={spec.get('type')}")

    executors = {"bom": BIN / "bom_from_source_v1.py"}
    ttype = spec.get("type")
    if ttype == "bom":
        if not spec.get("source"):
            log_op("ERROR", "task[bom]: spec.source required")
            return EXIT["ERROR"]
        rc, out, err = invoke(executors["bom"], ["--source", spec["source"]])
        if rc == 0:
            log_op("BANKED", f"task[bom] complete
{out}")
            return EXIT["BANKED"]
        log_op("ERROR" if rc >= 2 else "HELD", f"task[bom] rc={rc}
{out}{err}")
        return EXIT["ERROR"] if rc >= 2 else EXIT["HELD"]

    # No executor: never report BANKED for work that did not run.
    rc, out, err = invoke(ORGANS["task"], ["route", "--task", json.dumps(spec)])
    log_op("HELD", f"task: no executor for type={ttype!r}; routing hint only
{out}")
    return EXIT["HELD"]


def cmd_attest(args):
    if not args.job_id:
        log_op("ERROR", "attest: requires --job-id")
        return EXIT["ERROR"]
    log_op("GATE", f"attest: recording energy metabolism for {args.job_id}")
    rc, out, err = invoke(ORGANS["attest"], [args.job_id])
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"attest complete\n{out}")
        return EXIT["BANKED"]
    else:
        log_op("ERROR", f"attest failed:\n{err}")
        return EXIT["ERROR"]

def cmd_mint(args):
    if not args.job_id:
        log_op("ERROR", "mint: requires --job-id")
        return EXIT["ERROR"]
    log_op("GATE", f"mint: recording block to Newton Chain for {args.job_id}")
    rc, out, err = invoke(ORGANS["mint"], [args.job_id])
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"mint complete\n{out}")
        return EXIT["BANKED"]
    else:
        log_op("ERROR", f"mint failed:\n{err}")
        return EXIT["ERROR"]

def cmd_publish(args):
    log_op("GATE", "publish: initiating relay loop to GitHub")
    push_args = []
    if args.tag:
        push_args.extend(["--tag", args.tag])
    rc, out, err = invoke(ORGANS["publish"], push_args)
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"publish complete\n{out}")
        return EXIT["BANKED"]
    elif rc == EXIT["HELD"]:
        log_op("HELD", f"publish held (human gate)\n{out}")
        return EXIT["HELD"]
    else:
        log_op("ERROR", f"publish failed:\n{err}")
        return EXIT["ERROR"]

def cmd_audit(args):
    log_op("GATE", "audit: running health checks")
    log_op("HELD", "audit: health check framework TBD")
    return EXIT["HELD"]

def cmd_organism(args):
    if args.daemon:
        log_op("GATE", "organism: starting daemon mode (infinite loop)")
        log_op("HELD", "organism daemon: TBD")
        return EXIT["HELD"]
    else:
        log_op("GATE", "organism: single cycle (goal rank + next task)")
        log_op("HELD", "organism single-cycle: TBD")
        return EXIT["HELD"]

def main():
    parser = argparse.ArgumentParser(description=f"{CANARY} unified dispatcher for openroot organism")
    parser.add_argument("cmd", nargs="?", default="organism",
        choices=["ingest", "chunk", "index", "ask", "task", "attest", "mint", "publish", "audit", "organism"])
    parser.add_argument("--shard-dir", default=None, help="[chunk] shard directory")
    parser.add_argument("--rebuild", action="store_true", help="[index] clear prior ledger")
    parser.add_argument("--query", default=None, help="[ask] natural-language query")
    parser.add_argument("--spec", default=None, help="[task] spec JSON or path")
    parser.add_argument("--job-id", default=None, help="[attest/mint] job UUID")
    parser.add_argument("--tag", default=None, help="[publish] git tag")
    parser.add_argument("--full", action="store_true", help="[audit] full scan vs. baseline")
    parser.add_argument("--daemon", action="store_true", help="[organism] run as daemon")
    args = parser.parse_args()

    for p in (DATA, LOGS):
        p.mkdir(parents=True, exist_ok=True)

    handlers = {
        "ingest": cmd_ingest,
        "chunk": cmd_chunk,
        "index": cmd_index,
        "ask": cmd_ask,
        "task": cmd_task,
        "attest": cmd_attest,
        "mint": cmd_mint,
        "publish": cmd_publish,
        "audit": cmd_audit,
        "organism": cmd_organism,
    }

    rc = handlers[args.cmd](args)
    sys.exit(rc)

if __name__ == "__main__":
    main()
