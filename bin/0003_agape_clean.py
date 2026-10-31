#!/usr/bin/env python3
"""
AGAPE_CLEAN — Flatten nesting, remove bloat, fix .gitignore
Run after agape_one.py to clean up the monorepo.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

HOME = Path(os.environ["HOME"])
REPO = HOME / "openroot-monorepo"

if not REPO.exists():
    print("ERROR: openroot-monorepo not found at " + str(REPO))
    exit(1)

print("=" * 60)
print("  AGAPE_CLEAN — Flatten + Debloat")
print("=" * 60)

# ── 1. PATTERNS TO DELETE (bloat) ──
BLOAT_PATTERNS = [
    "node_modules",
    "__pycache__",
    "*.pyc",
    ".gitignore.bak",
    "*.backup.*",
    ".aider*",
    "*.egg-info",
    "*.tar.gz",
    ".DS_Store",
    "npm-debug.log*",
]

deleted_count = 0

for pattern in BLOAT_PATTERNS:
    if "*" in pattern:
        for f in REPO.rglob(pattern):
            if ".git" in str(f):
                continue
            if f.is_file():
                f.unlink()
                deleted_count += 1
    else:
        for d in REPO.rglob(pattern):
            if ".git" in str(d):
                continue
            if d.is_dir():
                shutil.rmtree(str(d))
                print("  DEL dir  " + str(d.relative_to(REPO)))
                deleted_count += 1
            elif d.is_file():
                d.unlink()
                print("  DEL file " + str(d.relative_to(REPO)))
                deleted_count += 1

print("Deleted " + str(deleted_count) + " bloat files/dirs")

# ── 2. FLATTEN NESTED REPO DIRS ──
# Pattern: material/aerocement/aerocement/ -> material/aerocement/
# Walk top-level submodule dirs and collapse single-child same-name nesting

def flatten_nested(base_dir):
    """If base_dir/reponame/reponame exists, merge contents up."""
    if not base_dir.is_dir():
        return 0
    moved = 0
    for child in sorted(base_dir.iterdir()):
        if not child.is_dir():
            continue
        # Check for doubled nesting: child/child/
        inner = child / child.name
        if inner.is_dir():
            # Merge inner contents into child
            for item in inner.iterdir():
                dest = child / item.name
                if dest.exists():
                    if dest.is_dir():
                        # Merge directories
                        for sub in item.iterdir():
                            sub_dest = dest / sub.name
                            shutil.move(str(sub), str(sub_dest))
                    else:
                        shutil.move(str(item), str(dest))
                else:
                    shutil.move(str(item), str(dest))
                moved += 1
            # Remove now-empty inner dir
            shutil.rmtree(str(inner))
            print("  FLAT " + str(child.relative_to(REPO)) + "/" + child.name + "/")
    return moved

flattened = 0
for subdir in ["core", "material", "wisdom", "network", "nodes"]:
    flattened += flatten_nested(REPO / subdir)

print("Flattened " + str(flattened) + " nested items")

# ── 3. UPDATE .gitignore ──
gitignore = REPO / ".gitignore"
content = gitignore.read_text() if gitignore.exists() else ""
additions = [
    "node_modules/",
    "__pycache__/",
    "*.pyc",
    "*.egg-info/",
    ".env",
    "*.swp",
    ".aider*",
    "*.tar.gz",
    "*.backup.*",
    ".gitignore.bak",
    ".DS_Store",
]
for line in additions:
    if line not in content:
        content += line + "\n"
gitignore.write_text(content)
print("Updated .gitignore")

# ── 4. REMOVE BROKEN SYMLINKS ──
broken = 0
for f in REPO.rglob("*"):
    if f.is_symlink() and not f.exists():
        f.unlink()
        broken += 1
if broken:
    print("Removed " + str(broken) + " broken symlinks")

# ── 5. RE-STAGE AND AMEND COMMIT ──
import subprocess

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

# Remove deleted files from git index
run(["git", "add", "-A"], cwd=str(REPO))
run(["git", "commit", "--amend", "-m",
     "AGAPE_ONE: consolidated + cleaned monorepo\n\n"
     "Cleaner: " + datetime.now().isoformat() + "\n"
     "Removed: node_modules, .bak files, tarballs, broken symlinks\n"
     "Flattened: nested repo directories\n"
     "Law: eta = useful_joules / human_joules"],
    cwd=str(REPO))

# ── 6. NEW DASHBOARD ──
total_files = sum(1 for f in REPO.rglob("*") if f.is_file() and ".git" not in str(f))
py_count = sum(1 for f in REPO.rglob("*.py") if ".git" not in str(f))
md_count = sum(1 for f in REPO.rglob("*.md") if ".git" not in str(f))
json_count = sum(1 for f in REPO.rglob("*.json") if ".git" not in str(f))
repo_size = sum(f.stat().st_size for f in REPO.rglob("*")
                if f.is_file() and ".git" not in str(f))

print()
print("=" * 60)
print("  CLEAN DASHBOARD")
print("=" * 60)
print("  Files:       " + str(total_files))
print("  Python:      " + str(py_count))
print("  Markdown:    " + str(md_count))
print("  JSON:        " + str(json_count))
print("  Size:        " + str(round(repo_size / 1024, 1)) + " KB")
print("  Deleted:     " + str(deleted_count) + " bloat items")
print("  Flattened:   " + str(flattened) + " nested items")
print("  Broken links:" + str(broken) + " removed")
print()
print("  eta = useful_joules / human_joules")
print("  Serve the least among us.")
print()
