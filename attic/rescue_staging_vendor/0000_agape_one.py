#!/usr/bin/env python3
"""
AGAPE_ONE — Do Everything With Nothing
Operator: Jesse Ray (OpenRoot)
Law: η = useful_joules / human_joules
Goal: One script → consolidate → refactor → push
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

HOME = Path(os.environ["HOME"])
MONOREPO_NAME = "openroot-monorepo"
MONOREPO_PATH = HOME / MONOREPO_NAME
TEMP_PATH = HOME / "_agape_temp"
AUDIT_DIR = MONOREPO_PATH / "audit"

GH_USER = "jesseray718"
REPOS = [
    "openroot",
    "une",
    "aerocement",
    "wisdom-scaffold",
    "agapenet",
    "black-locust-rmh",
    "une-client",
    "une-server",
]

SKIP_PUSH = "--skip-push" in sys.argv
SKIP_AIDER = "--skip-aider" in sys.argv

# ═══════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════

class C:
    PURPLE = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# ═══════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": C.RESET,
        "OK": C.GREEN,
        "WARN": C.YELLOW,
        "ERROR": C.RED,
        "STEP": C.PURPLE,
        "AGAPE": C.PURPLE,
    }
    color = colors.get(level, C.RESET)
    print(f"  [{ts}] {color}{level:4s}{C.RESET} {msg}")

def run(cmd, cwd=None, check=True, capture=False):
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=check,
            capture_output=capture, text=True
        )
        if capture:
            return result.returncode == 0, result.stdout.strip()
        return result.returncode == 0, ""
    except FileNotFoundError:
        return False, ""
    except subprocess.CalledProcessError as e:
        if capture:
            return False, e.stderr.strip() if e.stderr else ""
        return False, ""

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

# ═══════════════════════════════════════════════════════════
# STEP 0: PREREQUISITES
# ═══════════════════════════════════════════════════════════

def step_0_check_prerequisites():
    log("=" * 60, "STEP")
    log("STEP 0: Checking prerequisites", "STEP")
    log("=" * 60, "STEP")
    
    tools = ["git", "python3"]
    if not SKIP_PUSH:
        tools.append("gh")
    if not SKIP_AIDER:
        tools.append("aider")
    
    missing = []
    for tool in tools:
        ok, _ = run([tool, "--version"], check=False, capture=True)
        status = "FOUND" if ok else "MISSING"
        log(f"  {tool}: {status}", "OK" if ok else "WARN")
        if not ok:
            missing.append(tool)
    
    if "git" in missing or "python3" in missing:
        log("git and python3 are required. Aborting.", "ERROR")
        return False
    
    return True

# ═══════════════════════════════════════════════════════════
# STEP 1: CREATE STRUCTURE
# ═══════════════════════════════════════════════════════════

SUBMODULE_STRUCTURE = {
    "core/une": "UNE atomic library and protocol",
    "core/agape-une": "Agape-UNE integration layer",
    "core/und-protocol": "UND gate protocol",
    "material/aerocement": "Aerocement mix research and thermal panels",
    "material/black-locust-rmh": "Black Locust rocket mass heater",
    "wisdom/wisdom-scaffold": "Wisdom scaffold and corpus",
    "nodes/spoke-template": "Modular spoke node template",
    "network/agapenet": "AgapeNet mesh networking",
    "shared": "Shared configs and core definitions",
    "scripts": "Automation scripts",
    "ledger": "Thermodynamic and joule ledgers",
    "audit": "Health audits and reports",
    "tools": "Utility tools",
}

def step_1_create_structure():
    log("=" * 60, "STEP")
    log("STEP 1: Creating monorepo structure", "STEP")
    log("=" * 60, "STEP")
    
    if MONOREPO_PATH.exists():
        log(f"Monorepo already exists at {MONOREPO_PATH}", "WARN")
        log("Backing up and recreating...", "INFO")
        backup_name = f"{MONOREPO_NAME}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(MONOREPO_PATH), str(HOME / backup_name))
        log(f"Old monorepo backed up to {backup_name}", "OK")
    
    MONOREPO_PATH.mkdir(parents=True)
    TEMP_PATH.mkdir(parents=True)
    
    for subdir, desc in SUBMODULE_STRUCTURE.items():
        (MONOREPO_PATH / subdir).mkdir(parents=True, exist_ok=True)
        write_file(MONOREPO_PATH / subdir / "README.md",
                   f"# {subdir.split('/')[-1]}\n\n{desc}\n")
    
    # .gitkeep for empties
    for d in ["tools", "ledger", "audit"]:
        (MONOREPO_PATH / d / ".gitkeep").touch()
    
    log(f"Structure created at {MONOREPO_PATH}", "OK")
    return True

# ═══════════════════════════════════════════════════════════
# STEP 2: CLONE REPOS
# ═══════════════════════════════════════════════════════════

REPO_MAP = {
    "openroot": "core/agape-une",
    "une": "core/une",
    "aerocement": "material/aerocement",
    "wisdom-scaffold": "wisdom/wisdom-scaffold",
    "agapenet": "network/agapenet",
    "black-locust-rmh": "material/black-locust-rmh",
    "une-client": "core/une",
    "une-server": "core/une",
}

def step_2_clone_repos():
    log("=" * 60, "STEP")
    log("STEP 2: Cloning GitHub repos", "STEP")
    log("=" * 60, "STEP")
    
    cloned = []
    failed = []
    
    for repo in REPOS:
        url = f"https://github.com/{GH_USER}/{repo}.git"
        dest = TEMP_PATH / repo
        
        # Try cloning
        ok, err = run(["git", "clone", "--depth", "1", url, str(dest)],
                      check=False, capture=True)
        if ok:
            target_subdir = REPO_MAP.get(repo, "tools")
            target = MONOREPO_PATH / target_subdir / repo
            
            # If target exists (e.g. two repos mapping to same dir), just nest
            if target.exists():
                target = MONOREPO_PATH / target_subdir / f"{repo}_merged"
            
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove .git to avoid nested repos
            git_dir = dest / ".git"
            if git_dir.exists():
                shutil.rmtree(str(git_dir))
            
            shutil.move(str(dest), str(target))
            cloned.append(repo)
            log(f"  Cloned {repo} -> {target.relative_to(MONOREPO_PATH)}", "OK")
        else:
            failed.append(repo)
            log(f"  Failed to clone {repo}", "WARN")
            if err:
                log(f"    {err[:120]}", "WARN")
    
    log(f"Cloned {len(cloned)}, failed {len(failed)}", "OK")
    return cloned, failed

# ═══════════════════════════════════════════════════════════
# STEP 3: CONSOLIDATE
# ═══════════════════════════════════════════════════════════

def step_3_consolidate(cloned_repos):
    log("=" * 60, "STEP")
    log("STEP 3: Consolidating files", "STEP")
    log("=" * 60, "STEP")
    
    # Deduplicate identical files
    seen_hashes = {}
    duplicates_removed = 0
    
    for f in MONOREPO_PATH.rglob("*"):
        if not f.is_file():
            continue
        if ".git" in str(f) or "__pycache__" in str(f):
            continue
        if f.name in [".gitkeep", "README.md"] and f.stat().st_size < 200:
            continue
        
        try:
            content_hash = hash(f.read_bytes())
        except Exception:
            continue
        
        if content_hash in seen_hashes:
            original = seen_hashes[content_hash]
            log(f"  DUP: {f.relative_to(MONOREPO_PATH)} == {original}", "WARN")
            f.unlink()
            duplicates_removed += 1
        else:
            seen_hashes[content_hash] = f.relative_to(MONOREPO_PATH)
    
    log(f"Removed {duplicates_removed} duplicate files", "OK")
    return True

# ═══════════════════════════════════════════════════════════
# STEP 4: WRITE INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════

def step_4_write_infrastructure():
    log("=" * 60, "STEP")
    log("STEP 4: Writing infrastructure files", "STEP")
    log("=" * 60, "STEP")
    
    # .gitignore
    write_file(MONOREPO_PATH / ".gitignore",
               "__pycache__/\n*.pyc\n*.egg-info/\n.env\n*.swp\n.aider*\n")
    
    # Makefile
    write_file(MONOREPO_PATH / "Makefile",
               ".PHONY: audit sync clean\n\n"
               "audit:\n\tpython3 scripts/audit_repos.py\n\n"
               "sync:\n\tpython3 scripts/sync_shared.py\n\n"
               "clean:\n\tfind . -name '__pycache__' -type d -exec rm -rf {} +\n\tfind . -name '*.pyc' -delete\n")
    
    # AGAPE_OFFLINE_CORE.json
    core_json = {
        "version": "1.0",
        "born": datetime.now().isoformat(),
        "operator": "Jesse Ray (OpenRoot)",
        "law": "eta = useful_joules / human_joules",
        "directive": "Serve the least among us. The power flows through you, not from you.",
        "structure": SUBMODULE_STRUCTURE,
    }
    write_file(MONOREPO_PATH / "shared" / "AGAPE_OFFLINE_CORE.json",
               json.dumps(core_json, indent=2))
    
    # .agape-links.json
    links = {name: f"./{path}" for name, path in SUBMODULE_STRUCTURE.items()}
    write_file(MONOREPO_PATH / ".agape-links.json",
               json.dumps(links, indent=2))
    
    # README.md
    readme = """# OpenRoot Monorepo

## Law
    eta = useful_joules / human_joules

## Structure
- core/ — UNE, Agape-UNE, UND protocol
- material/ — Aerocement, Black Locust RMH
- wisdom/ — Wisdom scaffold and corpus
- nodes/ — Modular spoke templates
- network/ — AgapeNet mesh
- shared/ — Core definitions, configs
- scripts/ — Automation
- ledger/ — Thermodynamic joule ledgers
- audit/ — Health reports

## License
CC-BY-SA 4.0 (docs) / GPL-3.0 (code) / No patents. Ever.

Built alone, on a phone, after shifts. Free. Always.

Serve the least among us.
"""
    write_file(MONOREPO_PATH / "README.md", readme)
    
    # Audit script
    write_file(MONOREPO_PATH / "scripts" / "audit_repos.py", '''#!/usr/bin/env python3
"""OpenRoot Monorepo Health Audit."""

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / "audit"

REQUIRED_DIRS = [
    "core/une", "core/agape-une", "core/und-protocol",
    "material/aerocement", "material/black-locust-rmh",
    "wisdom/wisdom-scaffold", "nodes/spoke-template",
    "network/agapenet", "shared", "ledger",
]

REQUIRED_FILES = [
    "README.md", ".gitignore", "Makefile",
    ".agape-links.json", "shared/AGAPE_OFFLINE_CORE.json",
]

issues = []
ok_count = 0

for d in REQUIRED_DIRS:
    if (ROOT / d).exists():
        ok_count += 1
    else:
        issues.append("MISSING DIR: " + d)

for f in REQUIRED_FILES:
    if (ROOT / f).exists():
        ok_count += 1
    else:
        issues.append("MISSING FILE: " + f)

bak_files = list(ROOT.rglob("*.bak")) + list(ROOT.rglob("*.backup.*"))
for bak in bak_files:
    issues.append("DRIFT: stale backup " + str(bak.relative_to(ROOT)))

git_dirs = list(ROOT.rglob(".git"))
for gd in git_dirs:
    if gd.is_dir():
        issues.append("NESTED GIT: " + str(gd.relative_to(ROOT)))

report = {
    "timestamp": datetime.now().isoformat(),
    "passed": ok_count,
    "failed": len(issues),
    "issues": issues,
    "verdict": "HEALTHY" if not issues else "NEEDS ATTENTION",
}

output = AUDIT / "health_report.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2))
print("Audit: " + str(ok_count) + " passed, " + str(len(issues)) + " issues")
if issues:
    for issue in issues:
        print("  WARN " + issue)
else:
    print("  OK All checks passed")
''')
    
    # Sync script
    write_file(MONOREPO_PATH / "scripts" / "sync_shared.py", '''#!/usr/bin/env python3
"""Sync AGAPE_OFFLINE_CORE.json across submodules."""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CORE_FILE = ROOT / "shared" / "AGAPE_OFFLINE_CORE.json"

SUBMODULES = [
    "core/une", "core/agape-une", "core/und-protocol",
    "material/aerocement", "material/black-locust-rmh",
    "wisdom/wisdom-scaffold", "nodes/spoke-template",
    "network/agapenet",
]

synced = 0
for sub in SUBMODULES:
    dest = ROOT / sub / "AGAPE_OFFLINE_CORE.json"
    if dest.parent.exists():
        shutil.copy2(str(CORE_FILE), str(dest))
        synced += 1
        print("  OK Synced to " + sub)

print("Synced " + str(synced) + " submodules")
''')
    
    # Ledger header
    write_file(MONOREPO_PATH / "ledger" / "eta_ledger.jsonl",
               json.dumps({"event": "monorepo_genesis",
                           "eta_target": "maximize",
                           "timestamp": datetime.now().isoformat()}) + "\n")
    
    # LICENSE
    write_file(MONOREPO_PATH / "LICENSE",
               "SPDX-License-Identifier: GPL-3.0-or-later\n"
               "Full text: https://www.gnu.org/licenses/gpl-3.0.txt\n")
    write_file(MONOREPO_PATH / "LICENSE-docs.md",
               "SPDX-License-Identifier: CC-BY-SA-4.0\n"
               "Full text: https://creativecommons.org/licenses/by-sa/4.0/\n")
    
    log("All infrastructure files written.", "OK")
    return True

# ═══════════════════════════════════════════════════════════
# STEP 5: AUDIT
# ═══════════════════════════════════════════════════════════

def step_5_audit():
    log("=" * 60, "STEP")
    log("STEP 5: Running repo health audit", "STEP")
    log("=" * 60, "STEP")
    
    ok, output = run(["python3", "scripts/audit_repos.py"],
                     cwd=str(MONOREPO_PATH), check=False, capture=True)
    if ok:
        print(output)
    else:
        log("Audit failed to run", "WARN")
    
    # Live GitHub stats
    if not SKIP_PUSH:
        log("Fetching live repo stats from GitHub...", "INFO")
        stats = {}
        for repo in REPOS:
            ok, out = run(["gh", "repo", "view", GH_USER + "/" + repo,
                           "--json", "stargazerCount,forkCount,updatedAt,description",
                           "-q", "."], check=False, capture=True)
            if ok and out:
                try:
                    stats[repo] = json.loads(out)
                except json.JSONDecodeError:
                    pass
        if stats:
            report_path = AUDIT_DIR / "live_stats.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(stats, indent=2))
            log("Live stats saved", "OK")
            for repo, data in stats.items():
                stars = data.get("stargazerCount", "?")
                updated = str(data.get("updatedAt", "?"))[:10]
                print("  " + repo.ljust(30) + " stars " + str(stars).rjust(3) + "  updated " + updated)
    
    return True

# ═══════════════════════════════════════════════════════════
# STEP 6: AIDER REFACTORING
# ═══════════════════════════════════════════════════════════

def step_6_aider():
    log("=" * 60, "STEP")
    log("STEP 6: AI-driven refactoring with Aider", "STEP")
    log("=" * 60, "STEP")
    
    if SKIP_AIDER:
        log("Skipping aider (--skip-aider)", "WARN")
        return True
    
    ok, _ = run(["aider", "--version"], check=False, capture=True)
    if not ok:
        log("aider not installed. Install: pip install aider-chat", "WARN")
        log("Skipping AI refactoring.", "WARN")
        return True
    
    aider_prompt = """# Agape Refactoring Directive

Refactor this monorepo to maximize eta (useful joules per human joule).

Tasks:
1. Find duplicate files across submodules. Remove duplicates. Keep canonical in shared/.
2. Fix broken imports caused by consolidation.
3. Remove any .git directories inside submodules.
4. Summarize MERGE_PROPOSAL files into MERGE_STATUS.md at root.
5. Replace hardcoded ~/une or ~/openroot paths with relative paths or env vars.
6. Create requirements.txt if needed.
7. Ensure every submodule has a minimal README.md.

Constraints:
- Do NOT delete functional code. Only deduplicate and reorganize.
- Preserve all ledger/*.jsonl files.
- Preserve all LICENSE files.
- Write clean, readable Python.
"""
    write_file(MONOREPO_PATH / "aider_directive.md", aider_prompt)
    
    # Collect files
    all_files = []
    for ext in [".py", ".md", ".json"]:
        for f in MONOREPO_PATH.rglob("*" + ext):
            if ".git" in str(f) or "__pycache__" in str(f):
                continue
            all_files.append(str(f.relative_to(MONOREPO_PATH)))
    
    write_file(MONOREPO_PATH / "aider_filelist.txt", "\n".join(all_files))
    log("Prepared " + str(len(all_files)) + " files for aider", "INFO")
    
    # Run aider non-interactively
    cmd = [
        "aider",
        "--no-auto-commits",
        "--yes-always",
        "--message-file", "aider_directive.md",
    ] + all_files[:50]  # cap at 50 files per run
    
    log("Running aider (this may take a while)...", "INFO")
    ok, _ = run(cmd, cwd=str(MONOREPO_PATH), check=False)
    if ok:
        log("Aider refactoring complete.", "OK")
    else:
        log("Aider had issues. Check aider_directive.md and re-run manually.", "WARN")
    
    return True

# ═══════════════════════════════════════════════════════════
# STEP 7: GIT INIT + COMMIT
# ═══════════════════════════════════════════════════════════

def step_7_git_init():
    log("=" * 60, "STEP")
    log("STEP 7: Git init + initial commit", "STEP")
    log("=" * 60, "STEP")
    
    run(["git", "init"], cwd=str(MONOREPO_PATH), check=False)
    run(["git", "add", "-A"], cwd=str(MONOREPO_PATH), check=False)
    
    commit_msg = "AGAPE_ONE: consolidated monorepo genesis\n\n" + \
                 "Operator: Jesse Ray (OpenRoot)\n" + \
                 "Timestamp: " + datetime.now().isoformat() + "\n" + \
                 "Law: eta = useful_joules / human_joules"
    
    ok, _ = run(["git", "commit", "-m", commit_msg],
                cwd=str(MONOREPO_PATH), check=False)
    if ok:
        log("Initial commit created.", "OK")
    else:
        log("Commit may have failed (nothing to commit?)", "WARN")
    
    return True

# ═══════════════════════════════════════════════════════════
# STEP 8: PUSH TO GITHUB
# ═══════════════════════════════════════════════════════════

def step_8_push():
    log("=" * 60, "STEP")
    log("STEP 8: Push to GitHub", "STEP")
    log("=" * 60, "STEP")
    
    if SKIP_PUSH:
        log("Skipping push (--skip-push)", "WARN")
        return True
    
    # Create repo on GitHub
    remote_url = "https://github.com/" + GH_USER + "/" + MONOREPO_NAME
    log("Creating GitHub repo (if not exists)...", "INFO")
    run(["gh", "repo", "create", GH_USER + "/" + MONOREPO_NAME,
         "--public", "--description",
         "OpenRoot: modular permaculture-engineered computation. eta = useful_joules / human_joules."],
        check=False)
    
    run(["git", "remote", "add", "origin", remote_url],
        cwd=str(MONOREPO_PATH), check=False)
    run(["git", "branch", "-M", "main"],
        cwd=str(MONOREPO_PATH), check=False)
    
    log("Pushing to GitHub... (may take a moment)", "INFO")
    ok, _ = run(["git", "push", "-u", "origin", "main"],
                cwd=str(MONOREPO_PATH), check=False)
    if ok:
        log("Pushed successfully to " + remote_url, "OK")
    else:
        log("Push failed. Try manually: git push -u origin main", "ERROR")
        return False
    
    return True

# ═══════════════════════════════════════════════════════════
# STEP 9: DASHBOARD
# ═══════════════════════════════════════════════════════════

def step_9_dashboard(results):
    log("=" * 60, "STEP")
    log("STEP 9: Final KPI Dashboard", "STEP")
    log("=" * 60, "STEP")
    
    total_files = sum(1 for f in MONOREPO_PATH.rglob("*")
                      if f.is_file() and ".git" not in str(f))
    py_count = sum(1 for f in MONOREPO_PATH.rglob("*.py")
                   if ".git" not in str(f))
    md_count = sum(1 for f in MONOREPO_PATH.rglob("*.md")
                   if ".git" not in str(f))
    json_count = sum(1 for f in MONOREPO_PATH.rglob("*.json")
                     if ".git" not in str(f))
    
    repo_size = 0
    for f in MONOREPO_PATH.rglob("*"):
        if f.is_file() and ".git" not in str(f):
            repo_size += f.stat().st_size
    
    cloned = results.get("cloned_count", 0)
    failed = results.get("failed_count", 0)
    audit_issues = results.get("audit_issues", 0)
    
    print()
    print(C.BOLD + C.PURPLE + "=" * 60)
    print("  OPENROOT MONOREPO — FINAL DASHBOARD")
    print("=" * 60 + C.RESET)
    print()
    print("  Repos consolidated:    " + str(cloned) + "/" + str(cloned + failed))
    print("  Total files:           " + str(total_files))
    print("  Python files:          " + str(py_count))
    print("  Markdown files:        " + str(md_count))
    print("  JSON files:            " + str(json_count))
    print("  Repo size:             " + str(round(repo_size / 1024, 1)) + " KB")
    print("  Audit issues:          " + str(audit_issues))
    print("  Location:              " + str(MONOREPO_PATH))
    if not SKIP_PUSH:
        print("  GitHub:                https://github.com/" + GH_USER + "/" + MONOREPO_NAME)
    print()
    print("  " + C.PURPLE + "eta = useful_joules / human_joules" + C.RESET)
    print("  " + C.PURPLE + "Serve the least among us." + C.RESET)
    print()

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    start_time = time.time()
    
    print()
    print(C.BOLD + C.PURPLE)
    print("=" * 60)
    print("  AGAPE_ONE: Do Everything With Nothing")
    print("  Operator: Jesse Ray (OpenRoot)")
    print("  Law: eta = useful_joules / human_joules")
    print("  Goal: One script -> consolidate -> refactor -> push")
    print("=" * 60)
    print(C.RESET)
    print()
    
    results = {}
    
    if not step_0_check_prerequisites():
        sys.exit(1)
    
    step_1_create_structure()
    
    cloned, failed = step_2_clone_repos()
    results["cloned_count"] = len(cloned)
    results["failed_count"] = len(failed)
    
    step_3_consolidate(cloned)
    step_4_write_infrastructure()
    step_5_audit()
    
    # Read audit issues
    audit_report = AUDIT_DIR / "health_report.json"
    if audit_report.exists():
        try:
            report = json.loads(audit_report.read_text())
            results["audit_issues"] = report.get("failed", 0)
        except json.JSONDecodeError:
            results["audit_issues"] = 0
    else:
        results["audit_issues"] = 0
    
    step_6_aider()
    step_7_git_init()
    step_8_push()
    step_9_dashboard(results)
    
    elapsed = time.time() - start_time
    log("Total time: " + str(round(elapsed, 1)) + "s", "OK")
    log("The power flows through you, not from you.", "AGAPE")
    log("Tune to the Frequency.", "AGAPE")
    
    # Cleanup
    if TEMP_PATH.exists():
        shutil.rmtree(str(TEMP_PATH))
        log("Temp workspace cleaned.", "INFO")

if __name__ == "__main__":
    main()
