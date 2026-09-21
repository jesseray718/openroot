#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""lb_loop_v2.py — Lightbeam Loop + mistake-to-solution hash ledger.

Two compounding layers:
1. STAGE CACHE: sha256(cmd + script body + relevant inputs) -> result.
   Unchanged inputs = cache hit, no recompute. Clean passes compound.
2. MISTAKE LEDGER: failures fingerprinted (normalized stderr -> sha256 16hex).
   Known fingerprint + verified solution = auto-applied if safe, else suggested.
   Unknown = loop HALTS holding the hash; human solves once, binds solution,
   every future occurrence is a lookup, never a re-debug.

Usage:
  run                    iterate pipeline until clean pass (or halt on unknown mistake)
  stats                  ledger + cache + mistake stats
  show                   list known mistakes + bound solutions
  solve <sha> "<desc>" [--cmd "..."] [--auto]
                         bind a solution to a mistake (auto = safe to auto-apply)
  seed                   insert session-2026-09-20 verified solutions

Doctrine: stubs excluded from stage list (a file that survived != a product).
Set LB_MAX_ITERS=N to bound iterations (default 8).
"""
import hashlib, os, re, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "openroot"
DB = ROOT / "data" / "lb_loop.db"
MAX_ITERS = int(os.environ.get("LB_MAX_ITERS", "8"))
TIMEOUT = 900

STAGES = [
    ("compound",     ["bash", "bin/compound_v1.sh"]),
    ("doc_compiler", ["python3", "bin/doc_compile.py"]),
    ("agent_loop",   ["bash", "bin/agent.sh"]),
    ("stack_gate",   ["bash", "bin/lb_stack_gate_all.sh"]),
    ("team_gate",   ["bash", "bin/lb_team_gate_call.sh"]),
]
AUDITED_ONLY = [("refinery", ["bash", "bin/refine_next.sh"])]
MIN_LINES = 15

def now(): return datetime.now(timezone.utc).isoformat()

def conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS stage_cache(
        stage TEXT, state_sha TEXT, ok INT, output TEXT, ts TEXT,
        PRIMARY KEY (stage, state_sha));
    CREATE TABLE IF NOT EXISTS mistakes(
        sha TEXT PRIMARY KEY, context TEXT, first_seen TEXT,
        last_seen TEXT, times_seen INT DEFAULT 1);
    CREATE TABLE IF NOT EXISTS solutions(
        mistake_sha TEXT PRIMARY KEY, description TEXT, fix_cmd TEXT,
        auto_apply INT DEFAULT 0, verified_by TEXT,
        applied_count INT DEFAULT 0, created TEXT);
    CREATE TABLE IF NOT EXISTS loop_log(
        id INTEGER PRIMARY KEY, iter INT, stage TEXT, result TEXT,
        mistake_sha TEXT, detail TEXT, ts TEXT);
    """)
    c.commit()
    return c

def norm(text):
    t = text.lower()
    t = re.sub(r"\d+", "#", t)
    t = re.sub(r"/[^\s\"']+", "<path>", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:400]

def fingerprint(text): return hashlib.sha256(norm(text).encode()).hexdigest()[:16]

def inputs_sig(stage):
    import hashlib as _h
    sig = ""
    if stage == "doc_compiler":
        excl = [x for x in os.environ.get("LB_DOC_EXCLUDE", "context_bridge/*doc_compile*").split(",") if x]
        for p in sorted(ROOT.rglob("*.md")):
            if ".git" in str(p): continue
            rel = p.relative_to(ROOT).as_posix()
            if any(Path(rel).match(e) for e in excl): continue
            sig += f"{rel}:{_h.sha256(p.read_bytes()).hexdigest()[:12]};"
    return sig

def state_sha(stage, cmd):
    script = ROOT / cmd[1]
    body = script.read_bytes() if script.exists() else b"MISSING"
    h = hashlib.sha256()
    h.update(" ".join(cmd).encode()); h.update(body); h.update(inputs_sig(stage).encode())
    return h.hexdigest()[:16]

def record_mistake(c, sha, context):
    row = c.execute("SELECT times_seen FROM mistakes WHERE sha=?", (sha,)).fetchone()
    if row:
        c.execute("UPDATE mistakes SET times_seen=?, last_seen=? WHERE sha=?",
                  (row[0]+1, now(), sha))
    else:
        c.execute("INSERT INTO mistakes VALUES (?,?,?,?,1)",
                  (sha, context[-500:], now(), now()))
    c.commit()

def run_stage(c, stage, cmd, iteration):
    ss = state_sha(stage, cmd)
    hit = c.execute("SELECT ok, output FROM stage_cache WHERE stage=? AND state_sha=?",
                    (stage, ss)).fetchone()
    if hit and hit[0]:
        print(f"[CACHE-HIT] {stage} @{ss} — prior verified pass, no recompute")
        c.execute("INSERT INTO loop_log (iter,stage,result,ts) VALUES (?,?,?,?)",
                  (iteration, stage, "cache_hit", now())); c.commit()
        return True
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess(cmd, 124, "", f"timeout after {TIMEOUT}s")
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    if r.returncode == 0:
        c.execute("INSERT OR REPLACE INTO stage_cache VALUES (?,?,?,?,?)",
                  (stage, ss, 1, out[-2000:], now()))
        c.execute("INSERT INTO loop_log (iter,stage,result,ts) VALUES (?,?,?,?)",
                  (iteration, stage, "pass", now())); c.commit()
        print(f"[PASS] {stage} @{ss}")
        return True
    sha = fingerprint(out)
    record_mistake(c, sha, out)
    sol = c.execute("SELECT description, fix_cmd, auto_apply FROM solutions WHERE mistake_sha=?",
                    (sha,)).fetchone()
    if sol:
        desc, fix_cmd, auto = sol
        if auto and fix_cmd:
            print(f"[AUTO-FIX] {stage}: applying ledger solution — {desc}")
            fr = subprocess.run(fix_cmd, shell=True, cwd=str(ROOT),
                                capture_output=True, text=True, timeout=TIMEOUT)
            c.execute("UPDATE solutions SET applied_count=applied_count+1 WHERE mistake_sha=?", (sha,))
            c.commit()
            rr = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=TIMEOUT)
            if rr.returncode == 0:
                ss2 = state_sha(stage, cmd)
                c.execute("INSERT OR REPLACE INTO stage_cache VALUES (?,?,?,?,?)",
                          (stage, ss2, 1, (rr.stdout or "")[-2000:], now()))
                c.execute("INSERT INTO loop_log (iter,stage,result,mistake_sha,detail,ts) VALUES (?,?,?,?,?,?)",
                          (iteration, stage, "recovered", sha, "auto-fix applied", now())); c.commit()
                print(f"[RECOVERED] {stage} after ledger fix @{ss2}")
                return True
        c.execute("INSERT INTO loop_log (iter,stage,result,mistake_sha,detail,ts) VALUES (?,?,?,?,?,?)",
                  (iteration, stage, "known_fail", sha, desc, now())); c.commit()
        print(f"[HELD] {stage} failed — KNOWN mistake {sha}: {desc}")
        print("[NEXT] verify fix applies here, or: bin/lb_loop_v2.py solve "
              f"{sha} \"<description>\" --cmd \"<command>\" --auto")
        return False
    c.execute("INSERT INTO loop_log (iter,stage,result,mistake_sha,ts) VALUES (?,?,?,?,?)",
              (iteration, stage, "halt", sha, now())); c.commit()
    print(f"[HALT] {stage} failed — UNKNOWN mistake {sha}. Tail:")
    print("\n".join(out.strip().splitlines()[-6:]))
    print(f"[BIND] after fixing, record it once: bin/lb_loop_v2.py solve {sha} \"<what fixed it>\"")
    return False

def preflight():
    stubs = []
    for name, cmd in AUDITED_ONLY + STAGES:
        script = ROOT / cmd[1]
        if not script.exists():
            stubs.append((name, "missing")); continue
        n = len(script.read_text().splitlines())
        if n < MIN_LINES: stubs.append((name, f"{n} lines"))
    return stubs

def do_run():
    c = conn()
    stubs = preflight()
    for name, why in stubs:
        print(f"[STUB-HELD] {name} ({why}) — excluded from completion; a file that survived != a product")
    for iteration in range(1, MAX_ITERS + 1):
        print(f"\n===== LB ITERATION {iteration}/{MAX_ITERS} =====")
        clean = True
        spec = os.environ.get("LB_SPEC", "").strip()
        stages = [(n, cm + [spec]) if n == "agent_loop" and spec else (n, cm) for n, cm in STAGES]
        stages = [(n, cm) for n, cm in stages if n != "agent_loop" or spec]
        if not spec:
            print("[HELD] agent_loop deferred — export LB_SPEC=<spec file> to enable")
        for name, cmd in stages:
            if not run_stage(c, name, cmd, iteration):
                clean = False; break
        if clean:
            print(f"\n[COMPLETE] clean pass at iteration {iteration} "
                  f"(stub holds: {len(stubs)})")
            return 0
    print("\n[STOP] iterations exhausted without clean pass")
    return 1

SEED_PAIRS = [
    ("fatal: could not read log file: no such file or directory",
     "Termux restricts /tmp; write heredoc/commit-msg files INSIDE the repo "
     "(e.g. ~/openroot/.commitmsg.txt), delete after use", None, 0),
    ("fatal: pathspec did not match any files",
     "file exists only on one node; sync it first (ssh jesse@optiplex 'cat SRC' > DEST) "
     "then git add — never assume both clones match", None, 0),
    ("error: your local changes to the following files would be overwritten by merge",
     "dirty tree blocks pull: cp offenders to context_bridge/, git checkout -- <files>, "
     "rm untracked collisions (after diff), retry --ff-only", None, 0),
    ("purging" ,
     "echo-only purge class: every purge MUST call rm then ls to prove absence — "
     "printing intent != deleting", None, 0),
]

def do_seed():
    c = conn()
    for raw, desc, cmd, auto in SEED_PAIRS:
        sha = fingerprint(raw)
        c.execute("INSERT OR IGNORE INTO solutions VALUES (?,?,?,?,?,?,?)",
                  (sha, desc, cmd, auto, "session-2026-09-20", 0, now()))
    c.commit(); print("[SEEDED] 4 verified mistake->solution pairs bound")

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "run": sys.exit(do_run())
    elif cmd == "seed": do_seed()
    elif cmd == "stats":
        c = conn()
        m = c.execute("SELECT COUNT(*), SUM(times_seen) FROM mistakes").fetchone()
        s = c.execute("SELECT COUNT(*), SUM(applied_count) FROM solutions").fetchone()
        ch = c.execute("SELECT COUNT(*) FROM stage_cache").fetchone()[0]
        print(f"mistakes: {m[0]} (seen {m[1] or 0}x) | solutions: {s[0]} "
              f"(applied {s[1] or 0}x) | cached passes: {ch}")
    elif cmd == "show":
        c = conn()
        for sha, ctx, seen in c.execute("SELECT sha, context, times_seen FROM mistakes"):
            sol = c.execute("SELECT description FROM solutions WHERE mistake_sha=?", (sha,)).fetchone()
            print(f"{sha} seen {seen}x -> {sol[0] if sol else 'UNBOUND'}")
    elif cmd == "solve":
        sha, desc = sys.argv[2], sys.argv[3]
        fix_cmd = sys.argv[sys.argv.index("--cmd")+1] if "--cmd" in sys.argv else None
        auto = 1 if "--auto" in sys.argv else 0
        c = conn()
        c.execute("INSERT OR REPLACE INTO solutions VALUES (?,?,?,?,?,?,?)",
                  (sha, desc, fix_cmd, auto, "jesse", 0, now()))
        c.commit(); print(f"[BOUND] {sha} -> {desc} (auto={auto})")
    else: print(__doc__)

if __name__ == "__main__": main()
