#!/usr/bin/env python3
"""
rootkit — the unified dispatcher for openroot's 7-layer organism.
SPDX-License-Identifier: GPL-3.0-only

Doctrine:
  - One ID system: SHA-256 content-addressing is the spine.
  - All interfaces: hash-in, hash-out. No exceptions.
  - Exit codes: 0=banked (committed), 1=held (requires gate), 2=error (abort).
  - Delegated organs: existing bin/ scripts, absolute paths, strict contracts.

Pipeline:
  INGEST → CHUNK/SHARD → INDEX → ROUTE → COMPUTE → ATTEST → MINT → PUBLISH

Usage:
  rootkit ingest       [paths...]       # Mouth: hash-on-arrival ledger
  rootkit chunk        <shard-dir>      # Digestion: Merkle tree, fractal chunking
  rootkit index        [--rebuild]      # Memory: SQLite FTS5 + nomic semantic
  rootkit ask          <query>          # Routing: fp5s → nomic → dispatch
  rootkit task         <spec>           # Muscles: spec → 7B → gate → verify
  rootkit attest       <job_id>         # Metabolism: POPW + joules ledger
  rootkit mint         <job_id>         # Justice: Newton Chain + acre
  rootkit publish      [--tag]          # Nervous system: GitHub relay loop
  rootkit audit        [--full]         # Health check: ledger drift, chain GREEN
  rootkit organism     [--daemon]       # Circadian: heartbeat + goal ranking
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Absolute root and bin paths — no ambiguity.
ROOT = Path("/home/jesse/openroot")
BIN = ROOT / "bin"
DATA = ROOT / "data"
LOGS = ROOT / "logs"

# Canary markers (match existing doctrine).
CANARY = "[ROOTKIT]"
EXIT = {"BANKED": 0, "HELD": 1, "ERROR": 2}

# Organ scripts — absolute paths, delegated by name.
ORGANS = {
    "ingest": BIN / "lumo_ingest.py",
    "chunk": BIN / "chunker_v1.py",  # TBD: create
    "index": BIN / "a1_core_v1.py",  # scan → universal_doc_ledger
    "ask": BIN / "agape_router_v1.py",  # TBD: create
    "task": BIN / "a1_core_v1.py",  # route → spec_builder or grader
    "attest": BIN / "popw_ledger_v1.py",  # TBD: create
    "mint": BIN / "newton_chain_v1.py",  # TBD: integrate
    "publish": BIN / "relay_loop_v1.py",  # TBD: refactor
}


def now():
    """UTC ISO timestamp, seconds precision."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_op(severity, msg):
    """Structured log line to stdout."""
    print(f"{now()} {CANARY} {severity:>8s}  {msg}")


def sha256_file(p):
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s):
    """Compute SHA-256 of a string."""
    return hashlib.sha256(s.encode()).hexdigest()


def invoke(script_path, args=None, stdin_text=None):
    """
    Invoke a delegated organ script with strict contract:
      - Exit code 0 → BANKED (committed to ledger)
      - Exit code 1 → HELD (human gate required)
      - Exit code 2+ → ERROR (abort, investigate)
    
    Returns (exit_code, stdout, stderr).
    """
    if not script_path.exists():
        return EXIT["ERROR"], "", f"script not found: {script_path}"
    
    cmd = [sys.executable, str(script_path)] + (args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=stdin_text,
            timeout=3600,  # 1 hour default; override per organ
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return EXIT["ERROR"], "", f"timeout invoking {script_path}"
    except Exception as e:
        return EXIT["ERROR"], "", str(e)


def cmd_ingest(args):
    """
    INGEST (mouth): hash-on-arrival ledger.
    Contract: paths in → dedupe by SHA-256 → JSONL receipts.
    Delegates to: lumo_ingest.py (context_bridge, external files).
    """
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
    """
    CHUNK/SHARD (digestion): standardized Merkle-tree chunking.
    Contract: shard_dir in → chunk hashes + manifest.jsonl out.
    Delegates to: chunker_v1.py (TBD).
    """
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
    """
    INDEX (memory): unified SQLite FTS5 + nomic semantic index.
    Contract: scan all TEXT_EXT files → universal_doc_ledger.db + nomic embeddings.
    Delegates to: a1_core_v1.py scan (already exists).
    """
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
    """
    ASK (routing & retrieval): query → fp5s (keyword) → nomic (semantic) → dispatch.
    Contract: natural-language query in → ranked results (path, hash, rank).
    Delegates to: agape_router_v1.py (TBD).
    """
    if not args.query:
        log_op("ERROR", "ask: requires --query")
        return EXIT["ERROR"]
    
    log_op("GATE", f"ask: routing query '{args.query}'")
    
    # For now, stub: delegate to router (TBD).
    # rc, out, err = invoke(ORGANS["ask"], [args.query])
    
    log_op("HELD", "ask: router TBD (stub)")
    return EXIT["HELD"]


def cmd_task(args):
    """
    TASK (compute): atomic spec → edit → diff gate → verify → record.
    Contract: spec_json in → output_hash out (via git add -N, py_compile, grep).
    Delegates to: a1_core_v1.py route + spec_builder (TBD).
    """
    if not args.spec:
        log_op("ERROR", "task: requires --spec (JSON or path)")
        return EXIT["ERROR"]
    
    try:
        if args.spec.startswith("{"):
            spec = json.loads(args.spec)
        else:
            with open(args.spec) as f:
                spec = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log_op("ERROR", f"task: spec parse failed: {e}")
        return EXIT["ERROR"]
    
    log_op("GATE", f"task: routing spec to compute engine")
    
    # Delegate to router.
    route_args = ["route", "--task", json.dumps(spec)]
    rc, out, err = invoke(ORGANS["task"], route_args)
    
    if rc == EXIT["BANKED"]:
        log_op("BANKED", f"task complete\n{out}")
        return EXIT["BANKED"]
    elif rc == EXIT["HELD"]:
        log_op("HELD", f"task held (human gate)\n{out}")
        return EXIT["HELD"]
    else:
        log_op("ERROR", f"task failed:\n{err}")
        return EXIT["ERROR"]


def cmd_attest(args):
    """
    ATTEST (metabolism): job_id → RAPL joules → ledger record.
    Contract: job_id in → (j_human, j_useful, k_delta) out (SQLite kinetics table).
    Delegates to: popw_ledger_v1.py (TBD).
    """
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
    """
    MINT (justice layer): attested job → Newton Chain block.
    Contract: input_hash + output_hash + POPW proof → block → chain append.
    Delegates to: newton_chain_v1.py (TBD).
    """
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
    """
    PUBLISH (nervous system): local → GitHub relay loop.
    Contract: staged changes → git add -N → autobank → guarded push.
    Delegates to: relay_loop_v1.py (refactor planned).
    """
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
    """
    AUDIT (health check): drift detection + ledger equality + chain GREEN.
    Contract: full scan vs. last known state → discrepancy report.
    Delegates to: ecosystem_v2.py (exists, extended).
    """
    log_op("GATE", "audit: running health checks")
    
    audit_args = []
    if args.full:
        audit_args.append("--full")
    
    # Stub for now: would invoke ecosystem_v2.py or dedicated audit script.
    log_op("HELD", "audit: health check framework TBD")
    return EXIT["HELD"]


def cmd_organism(args):
    """
    ORGANISM (circadian): daemon that orchestrates the loop.
    Contract: goal_index → rank → next atomic task → schedule → loop.
    Delegates to: heartbeat_engine + ecosystem orchestration.
    """
    if args.daemon:
        log_op("GATE", "organism: starting daemon mode (infinite loop)")
        # Stub: would run heartbeat_engine in a loop.
        log_op("HELD", "organism daemon: TBD")
        return EXIT["HELD"]
    else:
        log_op("GATE", "organism: single cycle (goal rank + next task)")
        log_op("HELD", "organism single-cycle: TBD")
        return EXIT["HELD"]


def main():
    parser = argparse.ArgumentParser(
        description=f"{CANARY} unified dispatcher for openroot organism",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument("cmd", nargs="?", default="organism",
        choices=["ingest", "chunk", "index", "ask", "task", "attest", "mint", "publish", "audit", "organism"],
        help="organ/subcommand")
    
    # Subcommand arguments (optional, organ-specific).
    parser.add_argument("--shard-dir", default=None, help="[chunk] shard directory")
    parser.add_argument("--rebuild", action="store_true", help="[index] clear prior ledger")
    parser.add_argument("--query", default=None, help="[ask] natural-language query")
    parser.add_argument("--spec", default=None, help="[task] spec JSON or path")
    parser.add_argument("--job-id", default=None, help="[attest/mint] job UUID")
    parser.add_argument("--tag", default=None, help="[publish] git tag")
    parser.add_argument("--full", action="store_true", help="[audit] full scan vs. baseline")
    parser.add_argument("--daemon", action="store_true", help="[organism] run as daemon")
    
    args = parser.parse_args()
    
    # Ensure directories exist.
    for p in (DATA, LOGS):
        p.mkdir(parents=True, exist_ok=True)
    
    # Dispatch.
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
