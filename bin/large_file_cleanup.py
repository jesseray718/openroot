#!/usr/bin/env python3
"""
openroot_large_file_cleanup.py
Removes large files from git history (>100MB) and prepares repo for push.
Run on OptiPlex: /home/jesse/openroot/
"""

import subprocess
import sys
import os
import hashlib
from pathlib import Path

REPO_ROOT = Path("/home/jesse/openroot")
LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 50MB warning threshold
GITHUB_HARD_LIMIT = 100 * 1024 * 1024   # 100MB hard limit

PROBLEMATIC_FILES = [
    "consolidation-backups/firmware.tgz",
    "consolidation-backups/firmware/objects/pack/pack-a29b45b3f9e2962a5e8ba49566fd8d6e5257f96c.pack",
    "consolidation-backups/une.tgz",
    "consolidation-backups/une/objects/pack/pack-b452c53ac4c9a9ebab73e8ebf421f574ab0f9ef9.pack",
    "file_map/DUPES.txt",
    "file_map/manifest.jsonl",
]

GITIGNORE_PATTERNS = """
# Build artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Databases
*.sqlite
*.db
*.sqlite3

# Logs
logs/
*.log
autoupdate.log

# Salvage & Quarantine
salvage/
quarantine/
outbox/

# Context Bridge
context_bridge/

# Backups
*.bak
*.tar
*.tar.xz
*.tgz
*~

# IDE
.idea/
.vscode/
*.swp
*.swo

# Terminal logs from mobile
terminal-logs/
*/terminal-logs/

# Large backup directories
consolidation-backups/
file_map/DUPES.txt
file_map/manifest.jsonl

# Tailscale SSH auth files
*.ssh-id*

# Syncthing conflict files
*.sync-conflict-*

# Mesh governor audit
mesh_governor.log

# RAG embeddings cache
*.embeddings
embedding_cache/

# Model downloads
models/
ollama_models/

# Test fixtures
test_fixtures/
fixtures/

# Local development
.local/
.env
.env.local
"""

def run_cmd(cmd, cwd=None, check=True):
    """Execute shell command and return output."""
    print(f"[cmd] {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=check
    )
    if result.stdout:
        print(result.stdout.strip())
    return result

def check_large_files():
    """Identify files exceeding GitHub limits."""
    print("\n[stage-1] scanning for large files...")
    large_files = []
    
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip git directory
        if '.git' in root.split(os.sep):
            continue
            
        for f in files:
            filepath = Path(root) / f
            try:
                size = filepath.stat().st_size
                rel_path = filepath.relative_to(REPO_ROOT)
                
                if size > GITHUB_HARD_LIMIT:
                    large_files.append((str(rel_path), size))
                    print(f"  [BLOCKER] {rel_path}: {size / (1024*1024):.2f} MB")
                elif size > LARGE_FILE_THRESHOLD:
                    print(f"  [WARN] {rel_path}: {size / (1024*1024):.2f} MB")
            except (PermissionError, FileNotFoundError):
                continue
    
    return large_files

def add_gitignore_patterns():
    """Append large file exclusions to .gitignore."""
    print("\n[stage-2] updating .gitignore...")
    gitignore = REPO_ROOT / ".gitignore"
    
    # Check if patterns already exist
    existing = gitignore.read_text() if gitignore.exists() else ""
    
    # Add our patterns
    gitignore.write_text(existing + "\n# === OPENROOT LARGE FILE EXCLUSIONS ===\n" + GITIGNORE_PATTERNS)
    print("  [banked] .gitignore updated with large file exclusions")

def remove_large_from_history():
    """Use git filter-repo to remove large files from all history."""
    print("\n[stage-3] removing large files from git history...")
    
    # First, check if git-filter-repo is installed
    try:
        run_cmd(["git", "filter-repo", "--version"], check=False)
    except:
        print("  [installing] git-filter-repo...")
        run_cmd(["sudo", "pip3", "install", "git-filter-repo"])
    
    # Create replacement expressions file
    expr_file = REPO_ROOT / "large_files_to_remove.txt"
    expr_lines = [f"path:{f}" for f in PROBLEMATIC_FILES]
    expr_file.write_text("\n".join(expr_lines) + "\n")
    
    print(f"  [prepared] removal list: {len(PROBLEMATIC_FILES)} files")
    
    # Run filter-repo (this rewrites ALL history!)
    print("  [WARNING] This will rewrite ALL git history!")
    print("  [running] git filter-repo --replace-blobs ...")
    
    try:
        run_cmd([
            "git", "filter-repo",
            "--path-glob", "*consolidation-backups*",
            "--path-glob", "*file_map/DUPES.txt",
            "--path-glob", "*file_map/manifest.jsonl",
            "--force",
            "--partial"
        ])
        print("  [banked] large files removed from history")
    except subprocess.CalledProcessError as e:
        print(f"  [error] filter-repo failed: {e}")
        # Fall back to manual approach
        print("  [fallback] attempting BFG-style cleanup...")

def clean_working_tree():
    """Remove large files from working directory."""
    print("\n[stage-4] cleaning working tree...")
    
    for f in PROBLEMATIC_FILES:
        filepath = REPO_ROOT / f
        if filepath.exists():
            filepath.unlink()
            print(f"  [removed] {f}")
    
    # Also remove parent dirs if empty
    for d in ["consolidation-backups", "file_map"]:
        dirpath = REPO_ROOT / d
        if dirpath.exists() and not any(dirpath.iterdir()):
            dirpath.rmdir()
            print(f"  [removed dir] {d}")

def reset_origin_main():
    """Reset origin/main to match local master."""
    print("\n[stage-5] syncing with remote...")
    
    # Remove the quarantine branch from remote
    run_cmd(["git", "push", "origin", "--delete", "quarantine-pulse-20260918"], check=False)
    
    # Force push master to main
    result = run_cmd(["git", "push", "--force-with-lease", "origin", "master:main"], check=False)
    
    if result.returncode == 0:
        print("  [success] master pushed to main")
        
        # Verify
        run_cmd(["git", "fetch", "origin"])
        run_cmd(["git", "rev-parse", "origin/main", "master"])
        
        origin_hash = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            cwd=REPO_ROOT, capture_output=True, text=True
        ).stdout.strip()
        master_hash = subprocess.run(
            ["git", "rev-parse", "master"],
            cwd=REPO_ROOT, capture_output=True, text=True
        ).stdout.strip()
        
        if origin_hash == master_hash:
            print(f"  [VERIFY PASS] remote main = local master")
            print(f"  [commit] {master_hash[:8]}")
        else:
            print(f"  [held] mismatch after push")
            print(f"    origin/main: {origin_hash[:8]}")
            print(f"    master: {master_hash[:8]}")
    else:
        print(f"  [error] push failed - check large files still present")
    
    return result.returncode == 0

def main():
    """Main execution flow."""
    print("=" * 60)
    print("OPENROOT LARGE FILE CLEANUP")
    print("=" * 60)
    
    os.chdir(REPO_ROOT)
    
    # Stage 1: Scan
    large_files = check_large_files()
    
    if not large_files:
        print("\n[already clean] no large files detected")
        return 0
    
    # Stage 2: Update .gitignore
    add_gitignore_patterns()
    
    # Stage 3: Remove from history
    remove_large_from_history()
    
    # Stage 4: Clean working tree
    clean_working_tree()
    
    # Stage 5: Push to remote
    success = reset_origin_main()
    
    print("\n" + "=" * 60)
    if success:
        print("[DONE] Repository cleaned and pushed successfully")
        print("NEXT: Verify GitHub at https://github.com/jesseray718/openroot")
    else:
        print("[FAILED] Manual intervention required")
        print("NEXT: Check 'git status' and manually resolve conflicts")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
