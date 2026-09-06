#!/usr/bin/env python3
"""Append-only Proof-of-Physical-Work ledger. Stdlib only.

python3 popw_ledger.py help
python3 popw_ledger.py init
python3 popw_ledger.py add "claim" --kind yield --joules 12.5
python3 popw_ledger.py tip
python3 popw_ledger.py verify
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

HELP = """
POPW ledger — one jsonl chain. Not a second git.

python3 popw_ledger.py init
python3 popw_ledger.py add CLAIM [--kind yield|work|hang] [--joules N]
python3 popw_ledger.py tip
python3 popw_ledger.py verify
"""


def pane() -> str:
    cwd = str(Path.cwd())
    if cwd.startswith("/home/jesse") or "optiplex" in os.uname().nodename.lower():
        return "SSH"
    if cwd.startswith("/data/data/com.termux"):
        return "A15"
    return "UNKNOWN"


def path() -> Path:
    env = os.environ.get("POPW_LEDGER")
    if env:
        return Path(env)
    if pane() == "SSH":
        p = Path("/home/jesse/openroot/data/popw_ledger.jsonl")
    elif pane() == "A15":
        p = Path("/data/data/com.termux/files/home/code/openroot/data/popw_ledger.jsonl")
    else:
        p = Path("popw_ledger.jsonl")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def rows() -> list[dict]:
    fp = path()
    if not fp.exists():
        return []
    out = []
    for line in fp.read_text(errors="replace").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def cmd_init() -> int:
    fp = path()
    if fp.exists() and fp.stat().st_size:
        print(json.dumps({"ok": True, "exists": str(fp), "n": len(rows())}))
        return 0
    genesis = {
        "n": 0,
        "t": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kind": "genesis",
        "claim": "openroot popw genesis",
        "joules": 0.0,
        "prev": "0" * 64,
    }
    genesis["hash"] = sha(json.dumps(genesis, sort_keys=True))
    fp.write_text(json.dumps(genesis) + "\n")
    print(json.dumps({"ok": True, "path": str(fp), "hash": genesis["hash"]}))
    return 0


def cmd_add(claim: str, kind: str, joules: float) -> int:
    cmd_init()
    prev_rows = rows()
    prev = prev_rows[-1]["hash"]
    rec = {
        "n": len(prev_rows),
        "t": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kind": kind,
        "claim": claim[:300],
        "joules": joules,
        "prev": prev,
        "pane": pane(),
    }
    rec["hash"] = sha(json.dumps(rec, sort_keys=True))
    with path().open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({"ok": True, "n": rec["n"], "hash": rec["hash"], "prev": prev}))
    return 0


def cmd_tip() -> int:
    r = rows()
    if not r:
        print(json.dumps({"ok": False, "err": "empty"}))
        return 2
    print(json.dumps(r[-1], indent=2))
    return 0


def cmd_verify() -> int:
    r = rows()
    if not r:
        print(json.dumps({"ok": False, "err": "empty"}))
        return 2
    bad = []
    for i, rec in enumerate(r):
        h = rec.get("hash")
        body = {k: v for k, v in rec.items() if k != "hash"}
        expect = sha(json.dumps(body, sort_keys=True))
        if h != expect:
            bad.append(("hash", i))
        if i and rec.get("prev") != r[i - 1].get("hash"):
            bad.append(("link", i))
    print(json.dumps({"ok": not bad, "n": len(r), "bad": bad, "path": str(path())}))
    return 0 if not bad else 3


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"help", "-h"}:
        print(HELP)
        return 0
    c = argv[1]
    if c == "init":
        return cmd_init()
    if c == "tip":
        return cmd_tip()
    if c == "verify":
        return cmd_verify()
    if c == "add":
        claim = " ".join(a for a in argv[2:] if not a.startswith("--")) or "untitled"
        kind = "yield"
        joules = 0.0
        args = argv[2:]
        if "--kind" in args:
            kind = args[args.index("--kind") + 1]
        if "--joules" in args:
            joules = float(args[args.index("--joules") + 1])
        return cmd_add(claim, kind, joules)
    print(HELP)
    return 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
