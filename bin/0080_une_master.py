#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
UNE = HOME / "une"
TOOLS = UNE / "tools"
STATE = UNE / "state"
LEDGER = STATE / "eta_ledger.jsonl"
POSTULATES = UNE / "POSTULATES.md"
HANDOFF = UNE / "HANDOFF.md"
MESH_NOTE = UNE / "SYNCTHING_TEMPLATE.md"
ENV_EXAMPLE = UNE / ".env.example"
RUN_PHONE = UNE / "run_phone.sh"
ETA_DOC = UNE / "ETA_MODEL.md"

DOCUMENTS = Path("/storage/emulated/0/Documents")
DEFAULT_THRESHOLD = 1.0

def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def ensure_dirs():
    UNE.mkdir(parents=True, exist_ok=True)
    TOOLS.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)

def command_exists(name):
    return shutil.which(name) is not None

def git_root():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=UNE,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        return Path(out)
    except Exception:
        return None

def safe_write(path, content, apply=False):
    if path.exists():
        print(f"KEEP  {path}")
        return False
    print(f"CREATE {path}")
    if apply:
        path.write_text(content, encoding="utf-8")
        try:
            path.chmod(0o600)
        except OSError:
            pass
    return True

def eta(benefit, effort, minutes, risk):
    return benefit / ((1 + effort) * (1 + minutes) * (1 + risk))

def eta_t(benefit, persistence, leverage, effort, minutes):
    return (benefit * persistence * leverage) / ((1 + effort) * (1 + minutes))

def coordination_cost(nodes, rounds, reciprocity):
    if reciprocity >= 1.0:
        return 0.0
    return nodes * 0.001 * (1 + 0.1 * rounds) * ((1 - reciprocity) ** rounds)

def have_not_weight(haves):
    return 1.0 / (1.0 + max(0.0, haves))

def append_ledger(record):
    ensure_dirs()
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

def read_ledger():
    if not LEDGER.exists():
        return []
    records = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records

def materialize_files(apply):
    ensure_dirs()

    safe_write(RUN_PHONE, """#!/data/data/com.termux/files/usr/bin/bash
set -eu
ROOT="${UNE_ROOT:-$HOME/une}"
exec python3 "$ROOT/bin/une_master.py" "$@"
""", apply)

    safe_write(UNE / "CODEOWNERS", """* @OWNER
.github/ @OWNER
""", apply)

    safe_write(UNE / "CONTRIBUTING.md", """# Contributing

- Do not overwrite live engines.
- Do not reset Syncthing identities unless diagnosing a verified identity collision.
- Review `git diff` before committing.
- Pushing requires an explicit human `--push` flag.
- Claims about physics must distinguish measured results from local models.
""", apply)

    safe_write(UNE / "SPONSOR.md", """# Sponsor policy

Funds and material support should prioritize measured, reversible work that improves the lowest-capacity node.
""", apply)

    safe_write(ENV_EXAMPLE, """# Copy to .env only when needed. Do not commit secrets.
GITHUB_TOKEN=
SYNCTHING_DEVICE_ID=
LOCAL_LLM_URL=http://192.168.1.10:8080
""", apply)

    safe_write(ETA_DOC, """# ETA model

This is a local prioritization model, not a replacement for physical law.

eta = B / ((1 + E) * (1 + T) * (1 + K))
eta_t = (B * P * L) / ((1 + E) * (1 + T))
alpha_A ~= delta(eta_t) / delta(t)

Coordination model:
C(N,T,R) = 0 if R >= 1
C(N,T,R) = N * 0.001 * (1 + 0.1T) * (1-R)^T if R < 1

Have-not weighting:
w = 1 / (1 + haves)

Landauer's principle remains a physical lower bound for irreversible bit erasure. Measured joules are recorded as measurements; ledger values are not energy.
""", apply)

    safe_write(MESH_NOTE, """# Syncthing template

- Use one Syncthing instance per device identity.
- Pair only verified, distinct device IDs.
- Enable versioning before broad synchronization.
- Keep `/storage/emulated/0/Documents` excluded unless a specific, reviewed folder is intentionally shared.
- Never remove Syncthing state as routine maintenance.
- Use sneakernet export for immutable, reviewed handoffs when appropriate.
""", apply)

    safe_write(UNE / ".github" / "copilot-instructions.md", """# Copilot instructions

Preserve live engines. Never use `eval()`. Do not automate pushes. Treat physical-law claims as hypotheses unless supported by measurements and citations. Prefer reversible changes and reviewable diffs.
""", apply)

    safe_write(UNE / ".github" / "workflows" / "ci.yml", """name: ci
on: [push, pull_request]
jobs:
  syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 -m py_compile bin/une_master.py
""", apply)

    if apply:
        RUN_PHONE.chmod(0o700)
        print("\nMaterialization completed. No engine was overwritten.")
    else:
        print("\nDry run only. Add --apply to create missing files.")

def status():
    ensure_dirs()
    root = git_root()
    print("UNE master status")
    print(f"Root:       {UNE}")
    print(f"Documents:  {DOCUMENTS}")
    print(f"Git root:   {root if root else 'not a repository'}")
    print(f"Ledger:     {LEDGER} ({'present' if LEDGER.exists() else 'absent'})")
    print()

    for name in ["git", "python3", "syncthing", "ssh", "gh", "rish"]:
        print(f"{name:10} {'present' if command_exists(name) else 'not found'}")

    engines = list(UNE.rglob("agape_engine.py"))
    print()
    if engines:
        print("Existing engines (query only; never overwritten):")
        for engine in engines:
            print(f"  {engine}")
    else:
        print("Existing engines: none found under ~/une")

    if DOCUMENTS.exists():
        print("\nDocuments policy: present and excluded from all automatic operations.")
    else:
        print("\nDocuments policy: storage path not available in this environment.")

def postulate():
    ensure_dirs()
    content = """# Postulates

## Scope

This project uses a local coordination and prioritization model. It does not claim to repeal Amdahl's law, Landauer's principle, or any other physical result.

## Operational commitments

- Improve the lowest-capacity node first.
- Prefer measured physical quantities over modeled quantities.
- Treat ledger metrics as coordination records, not energy or currency.
- Make changes reversible whenever possible.
- Require explicit human consent before commits and pushes.
- Keep Documents out of automatic mesh and archive operations.
- Preserve living engines; query them only unless their maintainer explicitly authorizes a change.
"""
    if POSTULATES.exists():
        print(f"KEEP  {POSTULATES}")
    else:
        POSTULATES.write_text(content, encoding="utf-8")
        print(f"WROTE  {POSTULATES}")

def seed():
    ensure_dirs()
    seed_dir = UNE / "seeds"
    seed_dir.mkdir(exist_ok=True)
    path = seed_dir / f"seed_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(
        "# Seed\n\n"
        "Record a small, reversible, measurable task.\n\n"
        "- Intended beneficiary / lowest node:\n"
        "- Measurement to collect:\n"
        "- Reversal path:\n"
        "- Next action:\n",
        encoding="utf-8"
    )
    print(f"WROTE  {path}")

def decide(args):
    score = eta(args.benefit, args.effort, args.minutes, args.risk)
    score_t = eta_t(
        args.benefit,
        args.persistence,
        args.leverage,
        args.effort,
        args.minutes
    )
    weight = have_not_weight(args.haves)
    cost = coordination_cost(args.nodes, args.rounds, args.reciprocity)
    approved = score >= args.threshold and args.reversible

    record = {
        "time": now(),
        "type": "decision",
        "event": args.event,
        "domain": args.domain,
        "action": args.action,
        "benefit": args.benefit,
        "effort": args.effort,
        "minutes": args.minutes,
        "risk": args.risk,
        "persistence": args.persistence,
        "leverage": args.leverage,
        "haves": args.haves,
        "vote_weight": weight,
        "nodes": args.nodes,
        "rounds": args.rounds,
        "reciprocity": args.reciprocity,
        "coordination_cost": cost,
        "eta": score,
        "eta_t": score_t,
        "threshold": args.threshold,
        "reversible": args.reversible,
        "approved": approved
    }
    append_ledger(record)

    print(f"eta:                 {score:.6f}")
    print(f"eta_t:               {score_t:.6f}")
    print(f"have-not weight:     {weight:.6f}")
    print(f"coordination model:  {cost:.6f}")
    print(f"reversible:          {'yes' if args.reversible else 'no'}")
    print(f"decision:            {'APPROVED' if approved else 'NOT APPROVED'}")
    print(f"ledger:              {LEDGER}")

def landauer(bits):
    kb = 1.380649e-23
    temp_k = 300.0
    joules = bits * kb * temp_k * math.log(2)
    print(f"Landauer minimum at 300 K for {bits:g} irreversible bit erasures:")
    print(f"{joules:.12e} J")
    print("This is a physical lower bound for irreversible erasure, not cancelled by this ledger.")

def handoff():
    ensure_dirs()
    records = read_ledger()
    decisions = [r for r in records if r.get("type") == "decision"]
    approved = [r for r in decisions if r.get("approved")]

    content = f"""# Handoff

Generated: {now()}

## Safety state

- Documents are excluded from automatic operations.
- No live engine was overwritten by this tool.
- Syncthing identities were not reset.
- No Git push was performed by this tool.

## Ledger

- Total decisions: {len(decisions)}
- Approved reversible decisions: {len(approved)}
- Ledger path: `{LEDGER}`

## Next action

Review `git diff` before committing. Use an explicit human `--push` only after reviewing the committed change.
"""
    HANDOFF.write_text(content, encoding="utf-8")
    print(f"WROTE  {HANDOFF}")

def git_commit(message, push):
    root = git_root()
    if not root:
        print("Git commit skipped: ~/une is not inside a Git repository.", file=sys.stderr)
        return 2

    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root)
    if diff.returncode == 0:
        print("Nothing staged; no commit created.")
        return 0

    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True)
    print("Commit created.")

    if push:
        answer = input("Push this commit to its configured remote? Type YES to continue: ")
        if answer == "YES":
            subprocess.run(["git", "push"], cwd=root, check=True)
            print("Push completed.")
        else:
            print("Push cancelled.")
    return 0

def main():
    parser = argparse.ArgumentParser(
        prog="une_master.py",
        description="Safe local dispatcher and ETA ledger."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status")

    p_mat = sub.add_parser("materialize")
    p_mat.add_argument("--apply", action="store_true")
    p_mat.add_argument("--commit", action="store_true")
    p_mat.add_argument("--push", action="store_true")
    p_mat.add_argument("--message", default="chore: materialize UNE infrastructure")

    p_post = sub.add_parser("postulate")

    p_seed = sub.add_parser("seed")

    p_decide = sub.add_parser("decide")
    p_decide.add_argument("--event", required=True)
    p_decide.add_argument("--domain", required=True)
    p_decide.add_argument("--action", required=True)
    p_decide.add_argument("--benefit", type=float, required=True)
    p_decide.add_argument("--effort", type=float, required=True)
    p_decide.add_argument("--minutes", type=float, required=True)
    p_decide.add_argument("--risk", type=float, required=True)
    p_decide.add_argument("--persistence", type=float, default=1.0)
    p_decide.add_argument("--leverage", type=float, default=1.0)
    p_decide.add_argument("--haves", type=float, default=0.0)
    p_decide.add_argument("--nodes", type=float, default=1.0)
    p_decide.add_argument("--rounds", type=float, default=1.0)
    p_decide.add_argument("--reciprocity", type=float, default=1.0)
    p_decide.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    p_decide.add_argument("--reversible", action="store_true")

    p_landauer = sub.add_parser("landauer")
    p_landauer.add_argument("bits", type=float)

    p_handoff = sub.add_parser("handoff")

    args = parser.parse_args()

    if args.cmd == "status":
        status()
    elif args.cmd == "materialize":
        materialize_files(args.apply)
        if args.commit:
            if not args.apply:
                print("--commit requires --apply.", file=sys.stderr)
                return 2
            return git_commit(args.message, args.push)
        elif args.push:
            print("--push requires --commit and --apply.", file=sys.stderr)
            return 2
    elif args.cmd == "postulate":
        postulate()
    elif args.cmd == "seed":
        seed()
    elif args.cmd == "decide":
        if not 0.0 <= args.reciprocity <= 1.0:
            print("--reciprocity must be between 0 and 1.", file=sys.stderr)
            return 2
        decide(args)
    elif args.cmd == "landauer":
        if args.bits < 0:
            print("bits must be non-negative.", file=sys.stderr)
            return 2
        landauer(args.bits)
    elif args.cmd == "handoff":
        handoff()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
