#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# sys_ledger_v1.py — system-wide file SHA256 ledger, sharded, resumable, auditable.
# Commands:
#   plan [--roots a,b]  walk filesystem, insert new, flag changed (clear hash), mark vanished
#   run [W]             plan + spawn W workers (each owns shards shard %% W == its index)
#   work IDX W          worker: hash all pending rows in my shards
#   sweep               same as plan with default roots (for cron)
#   stats               coverage: ok/pending/perm/vanished/drift + total bytes
#   sample [N]          re-hash N random 'ok' rows, compare, flag drift (honesty audit)
#   smoke FIXTURE       plan+work on fixture dir, print hashes (test harness only)
import os, sys, sqlite3, hashlib, time, random, subprocess

ROOT = "/home/jesse/openroot"
DB = os.path.join(ROOT, "data", "sys_file_ledger.db")
LOG = os.path.join(ROOT, "logs", "sys_ledger.log")
BUF = 1024 * 1024
DEFAULT_ROOTS = ["/"]
EXCLUDE_PREFIX = ("/proc", "/sys", "/dev", "/run", "/mnt", "/media", "/var/lib/docker", "/snap")
# /mnt+/media excluded: external mounts keep their own device ledgers (A15 SD et al.)

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def log(msg):
    line = f"[sys_ledger v1 {now()}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def db():
    conn = sqlite3.connect(DB, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.execute("""CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY, size INTEGER, mtime REAL,
        sha256 TEXT, shard INTEGER, status TEXT,
        plan_ts TEXT, hash_ts TEXT)""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_shard_status ON files(shard, status)")
    return conn

def is_regular(p, st=None):
    import stat as s
    try:
        st = st or os.lstat(p)
        return s.S_ISREG(st.st_mode), st
    except OSError:
        return False, None

def walk_files(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None, followlinks=False):
            dirnames[:] = [d for d in dirnames
                           if not os.path.join(dirpath, d).startswith(EXCLUDE_PREFIX)]
            for name in filenames:
                yield os.path.join(dirpath, name)

def cmd_plan(roots):
    conn = db(); ts = now()
    seen = set(); n_new = n_changed = 0
    for p in walk_files(roots):
        ok, st = is_regular(p)
        if not ok:
            continue
        seen.add(p)
        row = conn.execute("SELECT size, mtime, sha256 FROM files WHERE path=?", (p,)).fetchone()
        shard = hash(p) % 64
        if row is None:
            conn.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?,NULL)",
                         (p, st.st_size, st.st_mtime, None, shard, "pending", ts))
            n_new += 1
        elif row[0] != st.st_size or abs(row[1] - st.st_mtime) > 1e-6:
            conn.execute("""UPDATE files SET size=?, mtime=?, sha256=NULL,
                            status='pending', plan_ts=? WHERE path=?""",
                         (st.st_size, st.st_mtime, ts, p))
            n_changed += 1
        if (n_new + n_changed) % 5000 == 0:
            conn.commit()
    for (p,) in conn.execute("SELECT path FROM files WHERE status!='vanished'"):
        if p not in seen and not p.startswith(tuple("/tmp/sys_ledger_smoke")):
            conn.execute("UPDATE files SET status='vanished' WHERE path=?", (p,))
    conn.commit(); conn.close()
    log(f"plan roots={roots} new={n_new} changed={n_changed}")
    return n_new + n_changed

def hash_one(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(BUF), b""):
            h.update(chunk)
    return h.hexdigest()

def cmd_work(idx, w):
    # v1.1: SELECT/hash WITHOUT holding a write txn; then BEGIN IMMEDIATE + backoff-retry.
    # Fixes F-SQLITE-BUSY-DEADLOCK: deferred read->write upgrade returns immediate BUSY.
    conn = db(); ts = now(); n_ok = n_err = 0
    my_shards = [s for s in range(64) if s % w == idx]
    q = ",".join("?" * len(my_shards))
    while True:
        rows = conn.execute(
            f"SELECT path, size FROM files WHERE status='pending' AND shard IN ({q}) "
            "ORDER BY path LIMIT 250", my_shards).fetchall()
        if not rows:
            break
        results = []
        for p, size in rows:
            try:
                results.append((p, "ok", hash_one(p)))
            except (OSError, PermissionError):
                results.append((p, "perm", None))
        backoff = 1.0
        while True:
            try:
                conn.execute("BEGIN IMMEDIATE")
                for p, st, s in results:
                    if st == "ok":
                        conn.execute("UPDATE files SET sha256=?, status='ok', hash_ts=? WHERE path=?",
                                     (s, now(), p))
                    else:
                        conn.execute("UPDATE files SET status='perm' WHERE path=?", (p,))
                conn.execute("COMMIT")
                break
            except sqlite3.OperationalError as e:
                try:
                    conn.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                print(f"[sys_ledger v1.1] lock retry in {backoff:.0f}s: {e}", flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
        n_ok += sum(1 for _, st, _ in results if st == "ok")
        n_err += sum(1 for _, st, _ in results if st == "perm")
        log(f"work w{idx}/{w} ok={n_ok} perm={n_err} (batch {len(rows)})")
    conn.commit(); conn.close()
    log(f"work w{idx}/{w} DONE ok={n_ok} perm={n_err}")

def cmd_run(w=2):
    cmd_plan(DEFAULT_ROOTS)
    log(f"run spawning {w} workers")
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), "work", str(i), str(w)])
             for i in range(w)]
    for pr in procs:
        pr.wait()
    bad = [pr.pid for pr in procs if pr.returncode != 0]
    log(f"run finished rc_nonzero={bad if bad else 'none'}")
    return 1 if bad else 0

def cmd_stats():
    conn = db()
    for status, c in conn.execute("SELECT status, COUNT(*) FROM files GROUP BY status"):
        print(f"  {status:10s} {c:>8d}")
    tot = conn.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE status!='vanished'").fetchone()
    conn.close()
    print(f"  total      {tot[0]:>8d}  ({tot[1]/(1<<30):.1f} GiB declared)")

def cmd_sample(n=50):
    conn = db(); random.seed()
    rows = conn.execute(
        "SELECT path, sha256 FROM files WHERE status='ok' ORDER BY RANDOM() LIMIT ?", (n,)).fetchall()
    drift = 0; gone = 0; checked = 0
    for p, expect in rows:
        ok, _ = is_regular(p)
        if not ok:
            conn.execute("UPDATE files SET status='vanished' WHERE path=?", (p,)); gone += 1
            continue
        try:
            got = hash_one(p); checked += 1
        except (OSError, PermissionError):
            conn.execute("UPDATE files SET status='perm' WHERE path=?", (p,)); gone += 1
            continue
        if got != expect:
            drift += 1
            conn.execute("UPDATE files SET sha256=NULL, status='drift' WHERE path=?", (p,))
            log(f"SAMPLE DRIFT {p} expected={expect[:12]} got={got[:12]}")
    conn.commit(); conn.close()
    log(f"sample checked={checked} drift={drift} gone={gone}/{len(rows)}")
    return 1 if drift else 0

def main(argv):
    if len(argv) < 2:
        print("usage: sys_ledger_v1.py plan|run|work|sweep|stats|sample|smoke"); return 2
    cmd, args = argv[1], argv[2:]
    if cmd == "plan":
        roots = args[0].split(",") if args and args[0] != "--" else DEFAULT_ROOTS
        if args and args[0] == "--roots":
            roots = args[1].split(",")
        cmd_plan(roots)
    elif cmd == "run":
        return cmd_run(int(args[0]) if args else 2)
    elif cmd == "work":
        cmd_work(int(args[0]), int(args[1]))
    elif cmd == "sweep":
        cmd_plan(DEFAULT_ROOTS)
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "sample":
        return cmd_sample(int(args[0]) if args else 50)
    elif cmd == "smoke":
        fx = args[0]; cmd_plan([fx])
        conn = db()
        rows = conn.execute("SELECT path, sha256 FROM files WHERE path LIKE ? AND sha256 IS NOT NULL",
                            (fx + "%",)).fetchall()
        conn.close()
        for p, s in rows:
            print(f"{s}  {p}")
    else:
        print(f"unknown: {cmd}"); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
