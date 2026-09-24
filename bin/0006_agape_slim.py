#!/usr/bin/env python3
"""Remove vendor archives and build artifacts. Keep only source."""
import os, shutil, subprocess
from pathlib import Path
from datetime import datetime

REPO = Path(os.environ["HOME"]) / "openroot-monorepo"

# 1. Kill the two giants
GIANTS = [
    "core/une/vendor_archive",
    "core/agape-une/openroot",
]

for g in GIANTS:
    path = REPO / g
    if path.exists():
        size_mb = round(sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1024 / 1024, 1)
        shutil.rmtree(str(path))
        print("DEL " + g + " (" + str(size_mb) + " MB)")

# 2. Kill any remaining build artifacts everywhere
ARTIFACT_DIRS = ["build", "vendor", "vendor_archive", "sync-from-kai", "cmake-build-debug", "cmake-build-release"]
removed = 0
for name in ARTIFACT_DIRS:
    for d in REPO.rglob(name):
        if d.is_dir() and ".git" not in str(d):
            sz = round(sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / 1024 / 1024, 1)
            shutil.rmtree(str(d))
            print("DEL " + str(d.relative_to(REPO)) + " (" + str(sz) + " MB)")
            removed += 1

# 3. Kill large binary files (.so, .o, .a, .gguf, .bin, .tar.gz, .gz)
BINARY_EXTS = {".so", ".o", ".a", ".gguf", ".bin", ".gz", ".tgz", ".zip", ".exe", ".dll", ".dylib"}
bin_killed = 0
for f in REPO.rglob("*"):
    if f.is_file() and f.suffix in BINARY_EXTS and ".git" not in str(f):
        sz = round(f.stat().st_size / 1024, 0)
        f.unlink()
        bin_killed += 1
print("Deleted " + str(bin_killed) + " binary files")

# 4. Add to .gitignore
gi = REPO / ".gitignore"
content = gi.read_text() if gi.exists() else ""
for line in ["vendor/", "vendor_archive/", "build/", "sync-from-kai/", "*.so", "*.o", "*.a", "*.gguf", "*.bin", "*.tar.gz", "*.tgz", "*.zip"]:
    if line not in content:
        content += line + "\n"
gi.write_text(content)

# 5. Amend commit
subprocess.run(["git", "add", "-A"], cwd=str(REPO))
subprocess.run(["git", "commit", "--amend", "-m",
    "AGAPE_ONE: debloated monorepo (removed vendor archives + binaries)\n\n"
    "Timestamp: " + datetime.now().isoformat()],
    cwd=str(REPO))

# 6. Dashboard
total = sum(1 for f in REPO.rglob("*") if f.is_file() and ".git" not in str(f))
size_kb = sum(f.stat().st_size for f in REPO.rglob("*") if f.is_file() and ".git" not in str(f))
py = sum(1 for f in REPO.rglob("*.py") if ".git" not in str(f))
md = sum(1 for f in REPO.rglob("*.md") if ".git" not in str(f))
js = sum(1 for f in REPO.rglob("*.js") if ".git" not in str(f))
json_n = sum(1 for f in REPO.rglob("*.json") if ".git" not in str(f))

print()
print("=" * 60)
print("  SLIM DASHBOARD")
print("=" * 60)
print("  Files:    " + str(total))
print("  Python:   " + str(py))
print("  Markdown: " + str(md))
print("  JSON:     " + str(json_n))
print("  JS:       " + str(js))
print("  Size:     " + str(round(size_kb / 1024, 1)) + " MB")
print()
print("  eta = useful_joules / human_joules")
print("  Serve the least among us.")
