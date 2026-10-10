#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
rootkit - unified dispatcher for the openroot organism.

Doctrine:
  - SHA-256 content addressing is the spine.
  - Never report BANKED for work that did not run.
  - Exit codes: 0 BANKED, 1 HELD, 2 ERROR.
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

WIRED = {
    "ingest": BIN / "lumo_ingest.py",
    "index": BIN / "a1_core_v1.py",
    "route": BIN / "a1_core_v1.py",
    "chunk": BIN / "chunker_v1.py",
    "ask": BIN / "ask_router_v1.py",
    "bom": BIN / "bom_from_source_v1.py",
    "migrate": BIN / "rootkit_migrate_v1.py",
    "popw": BIN / "popw_ledger_v1.py",
    "chain": BIN / "newton_chain_v1.py",
    "publish": BIN / "relay_loop_v1.py",
}

PLANNED = {
    "organism": BIN / "heartbeat_engine.py",   # placeholder
    "mint": BIN / "mint_acre_v1.py",           # placeholder
    "audit": BIN / "ecosystem_v2.py",          # placeholder
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

def load_spec(raw):
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    with open(raw) as f:
        return json.load(f)

def parse_bom_output(stdout_text):
    src_hash = None
    out_hashes = None
    for ln in stdout_text.splitlines():
        if ln.startswith("[banked] source_sha256="):
            src_hash = ln.split("=", 1)[1].strip()
        if ln.startswith("[banked] output_hashes="):
            out_hashes = json.loads(ln.split("=", 1)[1].strip())
    return src_hash, out_hashes

def cmd_ingest(args):
    log_op("GATE", "ingest: lumo_ingest.py")
    return finish("ingest", *invoke(WIRED["ingest"]))

def cmd_index(args):
    log_op("GATE", "index: a1_core_v1.py scan")
    return finish("index", *invoke(WIRED["index"], ["scan"]))

def cmd_chunk(args):
    target = args.target or str(ROOT)
    log_op("GATE", f"chunk: {target}")
    return finish("chunk", *invoke(WIRED["chunk"], [target, "--chunk-size", str(args.chunk_size)]))

def cmd_ask(args):
    if not args.query:
        log_op("ERROR", "ask: requires --query")
        return EXIT["ERROR"]
    log_op("GATE", "ask: ask_router_v1.py")
    return finish("ask", *invoke(WIRED["ask"], ["--query", args.query, "--limit", str(args.limit)]))

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

        rc, out, err = invoke(WIRED["bom"], ["--source", spec["source"]])
        if rc != 0:
            return finish("task[bom]", rc, out, err)

        src_hash, out_hashes = parse_bom_output(out)
        if not src_hash or not out_hashes or "bom.json" not in out_hashes:
            log_op("ERROR", "task[bom]: failed to parse source/output hashes from bom renderer output")
            if out.strip():
                print(out.rstrip())
            return EXIT["ERROR"]

        output_hash = out_hashes["bom.json"]
        job_id = f"job-bom-{src_hash[:12]}-{output_hash[:8]}"

        # 1) POPW record (estimate unless measured values supplied elsewhere)
        popw_args = [
            "record",
            "--job-id", job_id,
            "--input-hash", src_hash,
            "--output-hash", output_hash,
            "--meter-kind", "estimate",
            "--joules-human", "0.0",
            "--joules-useful", "0.0",
            "--k-delta", "0.0",
            "--note", "bom render estimate"
        ]
        prc, pout, perr = invoke(WIRED["popw"], popw_args)
        if prc != 0:
            log_op("ERROR", "task[bom]: POPW record failed")
            if perr.strip():
                print(perr.rstrip(), file=sys.stderr)
            return EXIT["ERROR"]

        # 2) Attestation hash for chain linkage
        att_payload = {
            "job_id": job_id,
            "input_sha256": src_hash,
            "output_sha256": output_hash,
            "meter_kind": "estimate",
            "joules_human": 0.0,
            "joules_useful": 0.0,
            "k_delta": 0.0,
            "verifier": "rootkit_popw_v1",
        }
        att_hash = sha256_text(json.dumps(att_payload, sort_keys=True))

        # 3) Chain append
        crc, cout, cerr = invoke(WIRED["chain"], [
            "append",
            "--job-id", job_id,
            "--input-hash", src_hash,
            "--output-hash", output_hash,
            "--attestation-hash", att_hash,
            "--note", "bom render"
        ])
        if crc != 0:
            log_op("ERROR", "task[bom]: chain append failed")
            if cerr.strip():
                print(cerr.rstrip(), file=sys.stderr)
            return EXIT["ERROR"]

        # Emit underlying outputs for traceability
        if out.strip():
            print(out.rstrip())
        if pout.strip():
            print(pout.rstrip())
        if cout.strip():
            print(cout.rstrip())

        log_op("BANKED", f"task[bom] job={job_id} popw+chain recorded")
        return EXIT["BANKED"]

    # Unknown task type: route hint only, never BANKED
    rrc, rout, rerr = invoke(WIRED["route"], ["route", "--task", json.dumps(spec)])
    log_op("HELD", f"task: no executor for type={ttype!r}; routing hint only")
    if rout.strip():
        print(rout.rstrip())
    return EXIT["HELD"]

def cmd_popw(args):
    if not args.command:
        log_op("ERROR", "popw: requires --command")
        return EXIT["ERROR"]

    if args.command == "record":
        if not args.job_id:
            log_op("ERROR", "popw record: --job-id required")
            return EXIT["ERROR"]
        argv = [
            "record",
            "--job-id", args.job_id,
            "--meter-kind", args.meter_kind,
            "--joules-human", str(args.joules_human),
            "--joules-useful", str(args.joules_useful),
            "--k-delta", str(args.k_delta),
            "--note", args.note or "",
        ]
        if args.input_hash:
            argv += ["--input-hash", args.input_hash]
        if args.output_hash:
            argv += ["--output-hash", args.output_hash]
        if args.spec_hash:
            argv += ["--spec-hash", args.spec_hash]
        return finish("popw record", *invoke(WIRED["popw"], argv))

    if args.command == "stats":
        return finish("popw stats", *invoke(WIRED["popw"], ["stats"]))

    if args.command == "list":
        argv = ["list"]
        if args.job_id:
            argv += ["--job-id", args.job_id]
        return finish("popw list", *invoke(WIRED["popw"], argv))

    if args.command == "hash":
        if not args.path:
            log_op("ERROR", "popw hash: --path required")
            return EXIT["ERROR"]
        return finish("popw hash", *invoke(WIRED["popw"], ["hash", "--path", args.path]))

    log_op("ERROR", f"unknown popw command: {args.command}")
    return EXIT["ERROR"]

def cmd_chain(args):
    if not args.command:
        log_op("ERROR", "chain: requires --command")
        return EXIT["ERROR"]

    if args.command == "append":
        required = [args.job_id, args.input_hash, args.output_hash, args.attestation_hash]
        if not all(required):
            log_op("ERROR", "chain append requires --job-id --input-hash --output-hash --attestation-hash")
            return EXIT["ERROR"]
        argv = [
            "append",
            "--job-id", args.job_id,
            "--input-hash", args.input_hash,
            "--output-hash", args.output_hash,
            "--attestation-hash", args.attestation_hash,
            "--note", args.note or "",
        ]
        return finish("chain append", *invoke(WIRED["chain"], argv))

    if args.command == "verify":
        return finish("chain verify", *invoke(WIRED["chain"], ["verify"]))

    if args.command == "show":
        return finish("chain show", *invoke(WIRED["chain"], ["show"]))

    log_op("ERROR", f"unknown chain command: {args.command}")
    return EXIT["ERROR"]

def cmd_publish(args):
    if not args.job_id:
        log_op("ERROR", "publish: --job-id required")
        return EXIT["ERROR"]

    argv = ["--job-id", args.job_id]
    if args.commit:
        argv += ["--commit", "--message", args.message]
    if args.tag:
        argv += ["--tag", args.tag]
    if args.push:
        argv += ["--push"]
    if args.allow_dirty:
        argv += ["--allow-dirty"]

    log_op("GATE", "publish: relay_loop_v1.py")
    return finish("publish", *invoke(WIRED["publish"], argv, timeout=7200))

def cmd_migrate(args):
    log_op("GATE", "migrate: rootkit_migrate_v1.py")
    return finish("migrate", *invoke(WIRED["migrate"]))

def cmd_organism(args):
    return planned_stub("organism")

def cmd_mint(args):
    return planned_stub("mint")

def cmd_audit(args):
    return planned_stub("audit")

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
        "ingest": cmd_ingest,
        "index": cmd_index,
        "chunk": cmd_chunk,
        "ask": cmd_ask,
        "task": cmd_task,
        "popw": cmd_popw,
        "chain": cmd_chain,
        "publish": cmd_publish,
        "migrate": cmd_migrate,
        "doctor": cmd_doctor,
        "organism": cmd_organism,
        "mint": cmd_mint,
        "audit": cmd_audit,
    }

    p = argparse.ArgumentParser(description=f"{CANARY} openroot dispatcher")
    p.add_argument("cmd", nargs="?", default="doctor", choices=sorted(handlers))

    # common
    p.add_argument("--query", default=None)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--spec", default=None)
    p.add_argument("--target", default=str(ROOT))
    p.add_argument("--chunk-size", type=int, default=1024 * 1024)
    p.add_argument("--path", default=None)

    # shared id/hash args
    p.add_argument("--job-id", default=None)
    p.add_argument("--input-hash", default=None)
    p.add_argument("--output-hash", default=None)
    p.add_argument("--spec-hash", default=None)
    p.add_argument("--attestation-hash", default=None)

    # popw/chain subcommand selector
    p.add_argument("--command", default=None, help="for popw/chain: record|stats|list|hash OR append|verify|show")

    # popw metrics
    p.add_argument("--meter-kind", default="estimate", choices=["estimate", "measured"])
    p.add_argument("--joules-human", type=float, default=0.0)
    p.add_argument("--joules-useful", type=float, default=0.0)
    p.add_argument("--k-delta", type=float, default=0.0)
    p.add_argument("--note", default="")

    # publish controls
    p.add_argument("--commit", action="store_true")
    p.add_argument("--message", default="relay: guarded publish")
    p.add_argument("--tag", default=None)
    p.add_argument("--push", action="store_true")
    p.add_argument("--allow-dirty", action="store_true")

    args = p.parse_args()

    for d in (DATA, LOGS):
        d.mkdir(parents=True, exist_ok=True)

    rc = handlers[args.cmd](args)
    sys.exit(rc)

if __name__ == "__main__":
    main()
