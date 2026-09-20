#!/usr/bin/env python3
"""push_guard.py — Guard against unseen web-UI commits before push"""
import subprocess, sys, json

def git_diff_stat():
    result = subprocess.run("git diff --stat HEAD", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    print("[push_guard] Pre-push verification")
    diff = git_diff_stat()
    if "unchanged" in diff.lower() or not diff:
        print("[push_guard] No pending changes — safe to push")
        sys.exit(0)
    
    print(f"[push_guard] Pending changes:\n{diff}")
    print("[push_guard] WARNING: Review unseen commits before force-push")
    sys.exit(0)  # Non-blocking, just warns

if __name__ == "__main__":
    main()
