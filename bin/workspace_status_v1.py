#!/usr/bin/env python3
"""Read-only local Git summary. Does not fetch, commit, push, or scan contents."""
import argparse
import collections
import json
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="Explicit path inside the repository")
    args = parser.parse_args()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

    def git(*flags):
        result = subprocess.run(
            ["git", "-C", args.repository, *flags],
            env=env, capture_output=True, text=True, timeout=60,
        )
        if result.returncode:
            raise SystemExit(result.stderr.strip() or "Git command failed.")
        return result.stdout.rstrip("\n")

    root = git("rev-parse", "--show-toplevel")
    branch = git(
        "status", "--short", "--branch", "--untracked-files=no"
    ).splitlines()[0]
    entries = [
        line for line in git(
            "status", "--porcelain=v1", "--untracked-files=normal"
        ).splitlines() if line
    ]
    counts = collections.Counter(line[:2] for line in entries)
    print(json.dumps({
        "repository": root,
        "branch_status": branch,
        "head": git("rev-parse", "HEAD"),
        "subject": git("log", "-1", "--format=%s"),
        "clean_including_nonignored_untracked": not entries,
        "status_entry_counts": dict(sorted(counts.items())),
        "count_basis": "Untracked directories are grouped, not expanded.",
        "remote_state": "Not refreshed; branch comparison uses local refs.",
        "network_requests": 0,
        "writes": 0,
    }, indent=2))

if __name__ == "__main__":
    main()
