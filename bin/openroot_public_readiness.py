#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
openroot_public_readiness.py

SSH only. Live tree: /home/jesse/openroot
Repo: jesseray718/openroot
Default: dry-run. Nothing hits GitHub until --apply.

Why this exists:
  The first draft died on three defects:
  1. gh --body "multiline with quotes" — shell eats the body
  2. labels that do not exist on the repo — gh issue create exits nonzero
  3. CONTRIBUTING.md and SECURITY.md already exist — >> would append a second copy

Usage on OptiPlex:
  python3 /home/jesse/openroot/bin/openroot_public_readiness.py
  python3 /home/jesse/openroot/bin/openroot_public_readiness.py --apply
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

REPO = "jesseray718/openroot"
BASE_DIR = "/home/jesse/openroot"
MILESTONE_TITLE = "v2.9 Cascade Grid Sweep"
KNOWN_LABELS = {
    "bug",
    "build-partner",
    "collaboration",
    "dev",
    "documentation",
    "duplicate",
    "enhancement",
    "experiment",
    "good first issue",
    "good first task",
    "help wanted",
    "instrumentation",
    "invalid",
    "materials",
    "pinned",
    "PoPW",
    "question",
    "replication",
    "research",
    "thermo",
    "validation",
    "wontfix",
}
ENSURE_LABELS = {
    "presentation": "0x6f42c1",
    "high-priority": "0xb60205",
    "medium-priority": "0xfbca04",
    "low-priority": "0xc2e0c6",
    "web": "0x1d76db",
    "maintenance": "0x5319e7",
    "audit": "0x006b75",
    "community": "0xd4c5f9",
    "ci-cd": "0x0e8a16",
    "infrastructure": "0x0052cc",
    "templates": "0xc5def5",
    "architecture": "0xbfd4f2",
    "science": "0x006b75",
    "security": "0xee0701",
    "governance": "0x5319e7",
    "communication": "0xfbca04",
    "legal": "0xb60205",
    "compliance": "0xd93f0b",
    "metrics": "0x1d76db",
    "release": "0x0e8a16",
    "automation": "0x0e8a16",
}


def canary() -> str:
    return "PUB_READY_V2_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("[cmd]", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run_cmd(["gh", *args], check=check)


def ensure_auth() -> None:
    p = gh("auth", "status", check=False)
    blob = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0 or "Logged in" not in blob:
        print("[error] gh is not authenticated on this pane.")
        print("fix: gh auth login")
        sys.exit(1)
    print("[held] gh auth ok")


def ensure_labels(apply: bool) -> None:
    existing = set(KNOWN_LABELS)
    listed = gh("label", "list", "--repo", REPO, "--limit", "200", "--json", "name", check=False)
    if listed.returncode == 0 and listed.stdout.strip():
        try:
            existing = {row["name"] for row in json.loads(listed.stdout)}
        except json.JSONDecodeError:
            pass
    missing = [name for name in ENSURE_LABELS if name not in existing]
    if not missing:
        print("[held] all custom labels exist")
        return
    print("[pending] labels to create:", ", ".join(missing))
    if not apply:
        return
    for name in missing:
        color = ENSURE_LABELS[name].removeprefix("0x")
        created = gh(
            "label",
            "create",
            name,
            "--repo",
            REPO,
            "--color",
            color,
            "--force",
            check=False,
        )
        if created.returncode == 0:
            print("[banked] label", name)
        else:
            print("[error] label create failed", name, created.stderr.strip())


def issues() -> list[dict]:
    return [
        {
            "title": "[PRIORITY-HIGH] Update README.md to showcase OpenRoot strengths and achievements",
            "labels": ["documentation", "presentation", "high-priority"],
            "body": """## Objective
Rewrite README.md so a stranger understands the project in 30 seconds.

## Do not invent numbers
Keep N14 locked. 1.34 stays MODEL until H-003 pad data exists.
Do not write eta_solar > 100 percent. Do not restore protein-foam yard mix.

## Required sections
- [ ] Vision, 1-2 paragraphs
- [ ] Core thesis: permaculture + Agape + local AI
- [ ] Capabilities with measured metrics only
- [ ] Proof of Physical Work with citations to hangs, not slogans
- [ ] Stack: Ollama, Qwen 7B/3B, SQLite FTS5, Nomic Embed
- [ ] Hardware: OptiPlex 3060, Samsung A15/Termux, Orange Pi targets
- [ ] Contributor entry points (CONTRIBUTING.md already exists — link it)
- [ ] Badges that resolve: CI, license GPL-3.0, docs CC-BY-SA-4.0

## Success
New visitor knows what to clone, what not to claim, and where to open a first issue.
""",
        },
        {
            "title": "Create OpenRoot landing page on GitHub Pages",
            "labels": ["web", "presentation", "medium-priority", "enhancement"],
            "body": """## Objective
Static landing page as public entry. Repo currently has_pages=false.

## Constraints
- No backend.
- Purple/gold is fine. Do not paste dummy paths.
- Do not republish handbook ghosts that were never on GitHub.

## Sections
- Hero + tagline
- Problem: centralization, extraction, entropy
- Solution: mesh, local AI, passive energy
- Project grid: OpenCell, Aerocement, Thermal Labyrinth, Stirling
- Metrics placeholder that links ledgers, not invented dashboards
- CTA + GitHub + docs

## Deliverables
- docs/ or site/ index that Pages can serve
- .github/workflows/pages.yml
- No custom domain until CNAME is a real name you own
""",
        },
        {
            "title": "[AUDIT] Repository hygiene: branches, tags, untracked files",
            "labels": ["maintenance", "audit", "low-priority"],
            "body": """## Live facts as of 2026-09-21
- default branch: main
- extra branch: master (still present)
- latest main: 125e685 [FIX][CASCADE] refine_next cleanup
- latest release tag on the releases page is mixed: v0.4.0 latest, also v1.0.0 / v1.1.0
- milestone v2.9 Cascade Grid Sweep is #11 and exists

## Checklist
- [ ] List stale branches >6 months
- [ ] Decide master vs main. Do not delete master until every local pane tracks main
- [ ] Confirm .gitignore covers *.db, venv, __pycache__, logs
- [ ] Do not git-add seed_master.log autoupdate.log context_bridge rotating json
- [ ] Tag only after a human reads git status --porcelain

## Commands
```
git -C /home/jesse/openroot branch -a --sort=-committerdate | head -20
git -C /home/jesse/openroot status --porcelain | wc -l
find /home/jesse/openroot -name '*.db' ! -path '/home/jesse/openroot/.git/*' -type f
```
""",
        },
        {
            "title": "[CRITICAL] Set up CI/CD pipeline for automated testing",
            "labels": ["ci-cd", "infrastructure", "high-priority"],
            "body": """## Required workflows
1. Python lint: flake8, black --check, isort --check
2. ShellCheck on *.sh
3. pytest with an honest coverage number. Do not claim 60 percent until tests exist
4. py_compile + bash -n
5. bandit + secret scan

## Files
- .github/workflows/ci.yml
- tests/
- pyproject.toml

Do not block merge on coverage that has never been measured.
""",
        },
        {
            "title": "Implement GitHub Issue templates",
            "labels": ["templates", "documentation", "low-priority"],
            "body": """Create .github/ISSUE_TEMPLATE/
- bug_report.yaml
- feature_request.yaml
- documentation_improvement.yaml

Reuse existing labels. Do not invent severity labels until they exist.
""",
        },
        {
            "title": "[DOC] Create ARCHITECTURE.md documenting system design",
            "labels": ["documentation", "architecture", "high-priority"],
            "body": """Document what already runs, not a future organism.

## Must include
- Two-pane law: A15 vs OptiPlex
- Data flow: ledgers, SQLite FTS5, session seeds
- Model routing: local 7B/3B
- Verification: stack_gate, push_guard, human commit
- What this repo is not: Solana, token mint, 100 percent efficient stove
""",
        },
        {
            "title": "[DOC] Document thermal/energy projects for peer review readiness",
            "labels": ["documentation", "science", "high-priority", "thermo", "PoPW"],
            "body": """Projects: OpenCell, Thermal Labyrinth, Aerocement panels, Stirling, geodesic.

Each project needs problem, specs, measurement method, comparison, BOM, limits.

N14: service from (sun-on-face + outdoor air + ground + sky + RMH) can exceed sun-on-face.
Locked model number is 1.34 until H-003.
Forbidden: 134 percent efficient sunlight, 2197 W by summing heat+cold+work.
""",
        },
        {
            "title": "[LEGAL] Verify licenses, SPDX headers, and compliance",
            "labels": ["legal", "compliance", "high-priority"],
            "body": """- LICENSE GPL-3.0 for code already on the repo
- Docs CC-BY-SA-4.0
- SPDX on new source files
- Third-party attribution
- No patents. Ever.
""",
        },
        {
            "title": "Create public dashboard for project metrics",
            "labels": ["metrics", "infrastructure", "medium-priority"],
            "body": """Track commits, PRs, joules if a hang exists, stars, forks.

Do not publish eta from a model row as a pad measurement.
Link raw ledger hashes. No Grafana until a host actually runs it.
""",
        },
        {
            "title": "Implement changelog with automated release notes",
            "labels": ["release", "automation", "low-priority"],
            "body": """CHANGELOG.md Keep a Changelog format.
Do not tag v2.9.0 until the grid sweep has a result file.
Current public latest release label is v0.4.0. Version story is already confused. Fix the story before adding another tag.
""",
        },
    ]


def create_one(item: dict, apply: bool) -> dict:
    if not apply:
        print("[dry-run]", item["title"])
        return {"title": item["title"], "num": None, "dry_run": True}
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(item["body"])
        body_path = fh.name
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        REPO,
        "--title",
        item["title"],
        "--body-file",
        body_path,
        "--milestone",
        MILESTONE_TITLE,
    ]
    if item["labels"]:
        cmd.extend(["--label", ",".join(item["labels"])])
    try:
        p = run_cmd(cmd, check=False)
    finally:
        os.unlink(body_path)
    if p.returncode != 0:
        print("[error]", item["title"])
        print(p.stderr)
        return {"title": item["title"], "num": None, "error": p.stderr.strip()}
    url = p.stdout.strip()
    num = url.rsplit("/", 1)[-1] if url else None
    print("[banked]", url)
    return {"title": item["title"], "num": num, "url": url}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="actually create labels and issues")
    args = parser.parse_args()
    stamp = canary()
    print("=== [stage:init]", stamp, "===")
    print("pane: SSH")
    print("tree:", BASE_DIR)
    print("repo:", REPO)
    print("mode:", "APPLY" if args.apply else "DRY-RUN")
    if os.getcwd() != BASE_DIR:
        if os.path.isdir(BASE_DIR):
            os.chdir(BASE_DIR)
        else:
            print("[error] missing", BASE_DIR, "— wrong pane or tree not mounted")
            return 1
    ensure_auth()
    ensure_labels(args.apply)
    created = [create_one(item, args.apply) for item in issues()]
    out_dir = os.path.join(BASE_DIR, "context_bridge")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pub_ready_issues_" + stamp + ".json")
    payload = {
        "canary": stamp,
        "apply": args.apply,
        "repo": REPO,
        "milestone": MILESTONE_TITLE,
        "issues": created,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print("[banked]", out_path)
    print("created_or_planned:", len(created))
    print("[exit=0]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
