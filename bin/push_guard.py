#!/usr/bin/env python3
"""Conservative normal-push gate for openroot. No force-push support."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

REPO = Path("/home/jesse/openroot")
LIMIT = 5 * 1024 * 1024

def git(*args):
    result = subprocess.run(["git", "-C", str(REPO), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=120)
    if result.returncode:
        raise RuntimeError("git command failed: " + " ".join(args[:3]))
    return result.stdout

def forbidden(name):
    parts = Path(name).parts
    return (name.endswith((".pyc", ".log")) or ".next" in parts
            or any(part.lower().startswith("manifest") for part in parts))

def validate_changes(raw):
    records = raw.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    if len(records) % 2:
        raise RuntimeError("unexpected diff encoding")
    paths = []
    for index in range(0, len(records), 2):
        status = records[index].decode("ascii")
        name = records[index + 1].decode("utf-8")
        if status == "D":
            raise RuntimeError("tracked deletion requires separate review")
        if forbidden(name):
            raise RuntimeError("forbidden release path: " + name)
        paths.append(name)
    return paths

def selftest():
    assert forbidden("x.pyc") and forbidden("a/.next/b")
    assert forbidden("package/manifest.json")
    assert not forbidden("bin/push_guard.py")
    assert validate_changes(b"A\0bin/push_guard.py\0") == ["bin/push_guard.py"]
    for raw in [b"D\0old.txt\0", b"A\0x.log\0", b"A\0"]:
        try:
            validate_changes(raw)
        except (RuntimeError, UnicodeError):
            pass
        else:
            raise AssertionError("unsafe diff accepted")
    print("[banked] push-guard self-test=PASS")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
        return
    print("[gate] --push with PUSH=1 would fetch, verify ancestry and release objects, then normal-push main")
    if args.push and os.environ.get("PUSH") != "1":
        raise RuntimeError("--push requires PUSH=1")
    if git("branch", "--show-current").strip() != b"main":
        raise RuntimeError("release branch must be main")
    if git("diff", "--cached", "--name-only").strip():
        raise RuntimeError("index contains staged changes")
    if args.push:
        git("fetch", "--no-tags", "origin", "main")
        upstream = git("rev-parse", "FETCH_HEAD").strip().decode("ascii")
    else:
        upstream = git("rev-parse", "refs/remotes/origin/main").strip().decode("ascii")
    head = git("rev-parse", "HEAD").strip().decode("ascii")
    git("merge-base", "--is-ancestor", upstream, head)
    commits = git("rev-list", upstream + ".." + head).splitlines()
    for commit_bytes in commits:
        commit = commit_bytes.decode("ascii")
        parents = git("rev-list", "--parents", "-n", "1", commit).split()
        if len(parents) != 2:
            raise RuntimeError("non-linear release requires separate review")
        parent = parents[1].decode("ascii")
        changed = validate_changes(git("diff", "--no-renames", "--name-status",
                                       "-z", parent, commit))
        for name in changed:
            size = int(git("cat-file", "-s", commit + ":" + name))
            if size > LIMIT:
                raise RuntimeError("release path exceeds 5 MiB: " + name)
    objects = git("rev-list", "--objects", "--no-object-names",
                  upstream + ".." + head).splitlines()
    if objects:
        listing = git("cat-file", "--batch-check", "--batch-all-objects")
        wanted = set(objects)
        for line in listing.splitlines():
            oid, kind, size = line.split()
            if oid in wanted and kind == b"blob" and int(size) > LIMIT:
                raise RuntimeError("release history contains a blob exceeding 5 MiB")
    print(f"[banked] ancestry/index/history gates=PASS ahead={len(commits)}")
    if args.push:
        if head != git("rev-parse", "HEAD").strip().decode("ascii"):
            raise RuntimeError("HEAD changed during verification")
        git("push", "origin", head + ":refs/heads/main")
        print(f"[banked] normal push=PASS sha={head}")
    else:
        print("[held] dry-run only; remote freshness not verified without --push")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("[held] " + str(exc).replace("\n", " ")[:400])
        sys.exit(1)
