#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
a1_core_v1.py -- [A1COREV1]
Universal doc ledger (SHA-256 dedup, non-recompute), A1 mirror hub, smart router
+ git proxy, eta/kinematics engine, permaculture decision layer, red-words tables.
Doctrine: falsifiable claims only. Never claim >100% thermodynamic efficiency.
The human is the only commit gate.
Usage: python3 bin/a1_core_v1.py {all,scan,map,route,git,decide,record,analyze,check-bin,goals}
"""
import argparse, hashlib, json, os, sqlite3, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

CANARY = "[A1COREV1]"
HOST = os.environ.get("A1_HOST", "optiplex")
OR = Path("/home/jesse/openroot")
A1 = Path("/home/jesse/A1")
DATA = OR / "data"
DB = DATA / "universal_doc_ledger.db"
CONFIG = DATA / "a1_config.json"

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "consolidation-backups",
    "archive",
    "local_archive",
    "recovery",
    "quarantine",
    "quarantine-docs",
    "logs",
    "runtime",
    "tmp",
    "cache",
    "state",
    "workareas",
}
TEXT_EXT = {".md", ".txt", ".json", ".jsonl", ".py", ".sh", ".csv", ".yaml", ".yml"}

DEFAULT_CONFIG = {
    "hosts": {"optiplex": ["/home/jesse/openroot", "/home/jesse/src/openroot"],
              "a15": ["/sdcard/openroot", "/data/data/com.termux/files/home"]},
    "eta_floor": 1.0, "share_factor": 0.5
}

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

def ensure():
    for p in (DATA, A1, A1 / "red_words", OR / "context_bridge"):
        p.mkdir(parents=True, exist_ok=True)

def cfg():
    if not CONFIG.exists():
        CONFIG.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n")
    return json.loads(CONFIG.read_text())

def connect():
    con = sqlite3.connect(str(DB))
    con.executescript("""
    CREATE TABLE IF NOT EXISTS docs(
      sha256 TEXT, host TEXT, path TEXT, size INTEGER, mtime REAL,
      first_seen TEXT, last_seen TEXT, kind TEXT,
      PRIMARY KEY (sha256, host, path));
    CREATE TABLE IF NOT EXISTS kinetics(
      ts TEXT, j_human REAL, j_useful REAL, k_delta REAL, shared REAL, note TEXT);
    CREATE TABLE IF NOT EXISTS red_words(
      ref TEXT PRIMARY KEY, text TEXT, expression TEXT, translation TEXT, imported_at TEXT);
    """)
    return con

def sha256_file(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(buf), b""):
            h.update(chunk)
    return h.hexdigest()

def scan(con, host=HOST):
    roots = cfg()["hosts"].get(host, [])
    stats = {
        "seen": 0,
        "hashed": 0,
        "cache_hits": 0,
        "new_unique": 0,
        "skipped_unreadable": 0,
        "skipped_nonregular": 0,
    }
    for root in roots:
        rp = Path(root)
        if not rp.exists():
            print(f"[held] root absent on host '{host}': {root}")
            continue
        for dp, dns, fns in os.walk(rp):
            dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
            for fn in fns:
                fp = Path(dp) / fn
                if fp.suffix.lower() not in TEXT_EXT or fp == DB:
                    continue
                try:
                    st = fp.stat()
                    if fp.is_symlink() or not fp.is_file():
                        stats["skipped_nonregular"] += 1
                        continue
                except OSError as exc:
                    stats["skipped_unreadable"] += 1
                    print(f"[banked] scan skip stat path={fp} reason={exc.__class__.__name__}")
                    continue

                stats["seen"] += 1
                old = con.execute(
                    "SELECT sha256, size, mtime, first_seen FROM docs WHERE host=? AND path=?",
                    (host, str(fp)),
                ).fetchone()

                if old and old[1] == st.st_size and abs(old[2] - st.st_mtime) < 1:
                    digest, first = old[0], old[3]
                    stats["cache_hits"] += 1
                else:
                    try:
                        digest = sha256_file(fp)
                    except OSError as exc:
                        stats["skipped_unreadable"] += 1
                        print(f"[banked] scan skip read path={fp} reason={exc.__class__.__name__}")
                        continue
                    first = old[3] if old else now()
                    stats["hashed"] += 1

                if not con.execute("SELECT 1 FROM docs WHERE sha256=?", (digest,)).fetchone():
                    stats["new_unique"] += 1

                con.execute(
                    "INSERT OR REPLACE INTO docs VALUES(?,?,?,?,?,?,?,?)",
                    (
                        digest,
                        host,
                        str(fp),
                        st.st_size,
                        st.st_mtime,
                        first,
                        now(),
                        fp.suffix.lower(),
                    ),
                )

    con.commit()
    print(
        f"[banked] scan {host}: {stats['seen']} files | hashed {stats['hashed']} "
        f"| cache-hit {stats['cache_hits']} | new-unique {stats['new_unique']} "
        f"| skipped-unreadable {stats['skipped_unreadable']} "
        f"| skipped-nonregular {stats['skipped_nonregular']}"
    )
    return stats

ROUTES = [
    ("gitops", ["commit", "push", "branch", "merge", "pr ", "release", "milestone", "issue"]),
    ("fts5_search", ["where", "what is", "which", "find", "search", "index", "list"]),
    ("spec_builder_7b", ["implement", "spec", "author", "write script", "edit", "patch"]),
    ("grader_3b", ["verify", "grade", "test", "check", "rubric", "validate"]),
    ("lumo_human_judgment", ["judge", "opinion", "design", "strategy", "tradeoff", "deep dive"]),
]
MODEL_OF = {"gitops": "git+gh cli", "fts5_search": "sqlite FTS5",
            "spec_builder_7b": "qwen2.5-coder:7b", "grader_3b": "qwen2.5:3b",
            "lumo_human_judgment": "Lumo (external, human-expert class)"}

def route(task):
    t = task.lower()
    for bucket, kws in ROUTES:
        if any(k in t for k in kws):
            return bucket
    return "fts5_search"

def check_bin():
    r = subprocess.run(["git", "-C", str(OR), "ls-files", "bin/"],
                       capture_output=True, text=True)
    tracked = [x for x in r.stdout.splitlines() if x.strip()]
    if tracked:
        print(f"[banked] bin/ tracked in git: {len(tracked)} files")
    else:
        subprocess.run(["git", "-C", str(OR), "add", "-N", "bin/"], check=False)
        print("[held] bin/ was UNTRACKED -> git add -N applied; commit awaits HUMAN GATE")

def record_kinetics(con, jh, ju, kd, shared, note=""):
    con.execute("INSERT INTO kinetics VALUES(?,?,?,?,?,?)", (now(), jh, ju, kd, shared, note))
    con.commit()
    print("[banked] kinetics row recorded")

def main():
    ap = argparse.ArgumentParser(description=CANARY + " A1 core")
    ap.add_argument("cmd", nargs="?", default="all",
                    choices=["all", "scan", "map", "route", "git", "decide",
                             "record", "analyze", "check-bin", "goals"])
    ap.add_argument("--task", default="")
    ap.add_argument("--jh", type=float, default=1.0)
    ap.add_argument("--ju", type=float, default=1.0)
    ap.add_argument("--kd", type=float, default=1.0)
    ap.add_argument("--shared", type=float, default=0.0)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    ensure()
    con = connect()
    if a.cmd == "all":
        scan(con); check_bin()
    elif a.cmd == "scan":
        scan(con)
    elif a.cmd == "route":
        b = route(a.task)
        print(f"[route] bucket={b} -> delegate to {MODEL_OF[b]}")
    elif a.cmd == "check-bin":
        check_bin()
    elif a.cmd == "record":
        record_kinetics(con, a.jh, a.ju, a.kd, a.shared, a.note)
    else:
        print(f"[held] cmd '{a.cmd}' scaffold present, expansion deferred (compost backlog)")

if __name__ == "__main__":
    main()
