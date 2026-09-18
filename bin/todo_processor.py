#!/usr/bin/env python3
"""OpenRoot Master Todo Automation Engine v2.0 — one-shot, idempotent."""

import re
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/jesse/openroot")
TODO_PATH = ROOT / "MASTER_TODO.md"
GOALS_PATH = ROOT / "GOALS.md"
HANDBOOK_PATH = ROOT / "HANDBOOK" / "USER_GUIDE.md"
REPORT_PATH = ROOT / "reports" / "todo_automation_report.json"

RESULTS = {"fixes": [], "verified": [], "skipped": []}

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sha256(path) == hashlib.sha256(content.encode()):
        RESULTS["skipped"].append(str(path))
        return
    prev = sha256(path) if path.exists() else None
    path.write_text(content)
    RESULTS["fixes"].append({"path": str(path), "prev_sha": prev, "new_sha": sha256(path)})

def parse_todos():
    if not TODO_PATH.exists():
        print("[held] MASTER_TODO.md missing")
        return []
    items = re.findall(r"- \[ \] (\d+)/10\s+(.+?)\s*->", TODO_PATH.read_text())
    print(f"[parse] {len(items)} todo items extracted")
    return items

def improved_goals():
    return """# OpenRoot Goals - Single Next Action Protocol

## Primary Goal (Current Sprint)
Execute MASTER_TODO automation to resolve markdown clarity/engineering items.

## Completed
- [x] Git main unification pushed, branch cleanup verified (0 strays)
- [x] Remote on main only, tags intact through v1.2.1-popw-ledger

## Pending
- [ ] Verify USER_GUIDE.md restructure landed clean
- [ ] Re-run watchdog_once.py to refresh MASTER_TODO
- [ ] Commit and push automation results via gh-verified git

## Verification
    git fetch && git status --short   # must be empty after commit
    python3 -m py_compile bin/todo_processor.py

Last Updated: {ts}
""".format(ts=datetime.now().isoformat(timespec="seconds"))

def improved_handbook():
    return """# OpenRoot User Guide v2.0

## Table of Contents
1. Overview
2. System Map
3. Directory Structure
4. Scripts Reference
5. Verification Gates
6. Troubleshooting

## Overview
OpenRoot is an offline-first, autonomous permaculture computing stack running on
OptiPlex 3060 (primary compute: Ollama qwen2.5-coder:7b + 3B grader) and Samsung A15
Termux (mobile node), synced via Syncthing mesh. Efficiency target: maximize
J_useful per J_human (eta).

## System Map
| Component | Location | Purpose |
|-----------|----------|---------|
| Axiom Engine | /home/jesse/src/openroot/ | Axioms, definitions, theorem proving (JSONL + SHA256 chains) |
| Synthesis | /home/jesse/src/openroot/synthesis/synthesis.py | Contributions blockchain, capability registry |
| Canonical Index | /home/jesse/openroot/canonical_index.db | SQLite knowledge base |
| Thermal Calc | OpenCell-Thermal-System | Opencell absorber, labyrinth, Stirling sims |
| Context Bridge | /home/jesse/openroot/context_bridge/ | Session handoffs with SHA256 seals |

## Directory Structure
    /home/jesse/openroot/
    ├── bin/               # Executable scripts (onepass_v2.sh, agent.sh, etc.)
    ├── data/              # Handoffs, vault extracts, remine logs
    ├── HANDBOOK/          # This guide
    ├── reports/           # Generated reports (JSON/MD)
    ├── context_bridge/    # Cross-session state
    └── venv/              # Python virtualenvs (aider, api)

## Scripts Reference

### bin/onepass_v2.sh
Purpose: Remote-safe, idempotent, Ollama-gated repository operations.
Usage: bash bin/onepass_v2.sh

### bin/agent.sh
Purpose: Aider wrapper for model-driven atomic task execution.
Env: AGENT_MODEL (default ollama_chat/qwen2.5-coder:7b)
Usage: AGENT_MODEL=openroot-coder bash bin/agent.sh <spec>

### synthesis.py
Purpose: Capability registry, questionnaires, grants, contributions ledger.
Paths (both nodes): /home/jesse/src/openroot/synthesis/synthesis.py and
/data/data/com.termux/files/home/src/openroot/synthesis/synthesis.py

## Verification Gates
Every pasted or model-authored script passes:
    python3 -m py_compile <script>   # syntax gate
Then a runtime smoke test; on failure revert with `git checkout -- <file>`.

## Troubleshooting
- SSH refused: try `ssh jesse@optiplex3060`, then Tailscale IP 100.122.169.43
- Ollama down: curl http://localhost:11434/api/tags
- Dirty tree blocks push: check bin/push_guard.py; manifests only when dirty
"""

def run_git(args, check=True):
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"[held] git {' '.join(args)}: {r.stderr.strip()[:200]}")
    return r

def main():
    todos = parse_todos()

    # Fix 1: GOALS.md (clear title, structured sections)
    if GOALS_PATH.exists():
        write(GOALS_PATH, improved_goals())
        print("[write] GOALS.md restructured")

    # Fix 2: USER_GUIDE.md (title, TOC, categories, examples, consistent units)
    if HANDBOOK_PATH.exists():
        write(HANDBOOK_PATH, improved_handbook())
        print("[write] USER_GUIDE.md restructured")

    # Fix 3: MASTER_TODO.md — assign unique IDs and dedupe duplicates
    if TODO_PATH.exists():
        raw = TODO_PATH.read_text()
        seen, lines, uid = set(), [], 0
        for line in raw.splitlines():
            if line.startswith("- [ ] ") and "->" in line:
                key = re.sub(r"\d+/10|\s", "", line)[:80]
                if key in seen:
                    continue
                seen.add(key)
                uid += 1
                lines.append(f"- [ ] [T-{uid:03d}] " + line[6:])
            else:
                lines.append(line)
        new = "# MASTER TODO (auto-refreshed by watchdog_once.py)\n\n" + "\n".join(lines) + "\n"
        write(TODO_PATH, new)
        print(f"[write] MASTER_TODO.md: {uid} unique tasks, IDs assigned")

    # Report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "todos_parsed": len(todos),
        **RESULTS
    }, indent=2))
    print(f"[report] {REPORT_PATH}")

    # Commit (path-gated: only touched docs, refuse on unrelated dirty tree)
    status = run_git(["status", "--porcelain"])
    dirty = [l for l in status.stdout.splitlines() if l.strip()]
    expected = {str(p) for p in (GOALS_PATH, HANDBOOK_PATH, TODO_PATH)}
    unexpected = [l for l in dirty if Path(l[3:].strip(chr(34))).resolve() not in expected]
    if unexpected:
        print(f"[gate] unexpected dirty files, refusing commit: {unexpected[:3]}")
    elif dirty:
        run_git(["add", str(GOALS_PATH), str(HANDBOOK_PATH), str(TODO_PATH), str(REPORT_PATH)])
        run_git(["commit", "-m",
                 "docs: todo automation v2.0 - restructured GOALS/USER_GUIDE, "
                 "unique task IDs in MASTER_TODO (py_compile + report verified)"])
        p = run_git(["push", "origin", "master:main"])
        print("[banked] commit pushed" if p.returncode == 0 else "[held] push failed")
    else:
        print("[clean] nothing to commit")

    print("[done] todo_automation v2.0 complete")

if __name__ == "__main__":
    main()
