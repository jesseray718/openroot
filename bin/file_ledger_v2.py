#!/usr/bin/env python3
# file_ledger_v2.py — cross-device hash ledger. v2: blocks column, core-file exclusion, hash mode.
# Usage: file_ledger_v2.py index | hash | dedupe-report
# SPDX-License-Identifier: GPL-3.0-only
# v2: migrate v1 db (add blocks), skip sparse-core pathology, hash queue smallest-first.
import os, sys, sqlite3, time, hashlib, stat

DB = "/home/jesse/openroot/data/file_ledger.db"
DOMAINS = {
    "optiplex-home": "/home/jesse",
    "optiplex-sd":   "/mnt/sdb1",
    # "optiplex-usb": "/media/jesse/USB",   # enable after mounting sdc1
}
EXCLUDE_DIRS = {".git","venv","__pycache__","node_modules",".cache",
                ".cargo",".rustup",".mozilla","lost+found"}
EXCLUDE_PREFIX = ("/home/jesse/.ollama/models",)
# v2: pathological artifacts — excluded from ledger entirely
EXCLUDE_PATHS = {
    ("optiplex-home",
     "openroot/consolidation-backups/untracked_collision_20260919-072429/"
     "data/usb128-import-20260913/core"),
}
HASH_BATCH = 2000

def migrate(con):
    cols = {r[1] for r in con.execute("PRAGMA table_info(files)")}
    if "blocks" not in cols:
        con.execute("ALTER TABLE files ADD COLUMN blocks INT")
        con.commit()
    con.execute("""DELETE FROM files WHERE domain='optiplex-home'
        AND relpath LIKE '%/usb128-import-20260913/core'""")
    con.commit()

def index():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS files(
        domain TEXT, relpath TEXT, size INT, mtime REAL, blocks INT,
        sha256 TEXT, seen_ts REAL, hashed_ts REAL,
        PRIMARY KEY(domain, relpath))""")
    migrate(con)
    for domain, root in DOMAINS.items():
        if not os.path.isdir(root):
            print(f"[held] {domain}: root absent"); continue
        n = 0; t0 = time.time()
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            if dirpath.startswith(EXCLUDE_PREFIX): dirnames[:] = []; continue
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                try: st = os.lstat(p)
                except OSError: continue
                if not stat.S_ISREG(st.st_mode): continue
                rel = os.path.relpath(p, root)
                if (domain, rel) in EXCLUDE_PATHS: continue
                con.execute("""INSERT INTO files(domain,relpath,size,mtime,blocks,seen_ts)
                    VALUES(?,?,?,?,?,?) ON CONFLICT(domain,relpath)
                    DO UPDATE SET size=excluded.size, mtime=excluded.mtime, sha256=CASE WHEN files.sha256 IS NOT NULL AND (files.size<>excluded.size OR files.mtime<>excluded.mtime) THEN NULL ELSE files.sha256 END,
                                  blocks=excluded.blocks, seen_ts=excluded.seen_ts""",
                    (domain, rel, st.st_size, st.st_mtime,
                     st.st_blocks, time.time()))
                n += 1
        con.commit()
        print(f"[banked] {domain}: {n} files re-indexed in {time.time()-t0:.0f}s")
    # honest size by ALLOCATED bytes now
    for row in con.execute("""SELECT domain, COUNT(*),
            printf('%.1f GiB', COALESCE(SUM(blocks),SUM(size))*512/1073741824.0)
            FROM files GROUP BY domain ORDER BY 3 DESC"""):
        print(f"  {row[0]:16s} {row[1]:>9,} files  {row[2]} (allocated)")
    con.close()

def hash_pass():
    con = sqlite3.connect(DB)
    todo = con.execute("""SELECT domain, relpath, size FROM files
        WHERE sha256 IS NULL ORDER BY size ASC""").fetchall()
    total = len(todo)
    print(f"[gate] hash queue: {total:,} files, "
          f"{sum(r[2] for r in todo)/1073741824.0:.1f} GiB")
    roots = {d: DOMAINS[d] for d in DOMAINS}
    done = 0; t0 = time.time(); last = t0
    for domain, rel, size in todo:
        p = os.path.join(roots[domain], rel)
        h = hashlib.sha256()
        try:
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1<<20), b""): h.update(chunk)
            con.execute("UPDATE files SET sha256=?, hashed_ts=? WHERE domain=? AND relpath=?",
                        (h.hexdigest(), time.time(), domain, rel))
        except OSError:
            con.execute("UPDATE files SET sha256='-unreadable-' WHERE domain=? AND relpath=?",
                        (domain, rel))
        done += 1
        if done % HASH_BATCH == 0:
            con.commit()
            now = time.time()
            print(f"  {done:,}/{total:,} ({100*done/total:.0f}%) "
                  f"{now-t0:.0f}s elapsed, {done/(now-t0):.0f} files/s", flush=True)
            last = now
    con.commit()
    print(f"[banked] hash pass complete: {done:,} files in {time.time()-t0:.0f}s")
    un = con.execute("SELECT COUNT(*) FROM files WHERE sha256 IS NULL").fetchone()[0]
    print(f"[gate] remaining unhashed: {un:,}")
    con.close()

def dedupe_report():
    con = sqlite3.connect(DB)
    print("[gate] top 30 duplicate groups by wasted bytes (within+across domains):")
    for sha, n, tot in con.execute("""
        SELECT sha256, COUNT(*), SUM(size) FROM files
        WHERE sha256 IS NOT NULL AND sha256 != '-unreadable-'
        GROUP BY sha256 HAVING COUNT(*) > 1
        ORDER BY SUM(size)*(COUNT(*)-1)/COUNT(*) DESC LIMIT 30"""):
        dups = con.execute("""SELECT domain, relpath FROM files
            WHERE sha256=? ORDER BY size DESC""", (sha,)).fetchall()
        waste = tot * (n-1) / n
        print(f"\n{waste/1073741824.0:8.2f} GiB wasted  ({n} copies, {tot/1073741824.0:.2f} GiB each-set)")
        for d, rp in dups[:5]:
            print(f"   {d}: {rp}")
        if n > 5: print(f"   ... +{n-5} more")
    con.close()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "index"
    {"index": index, "hash": hash_pass,
     "dedupe-report": dedupe_report}.get(mode, lambda: print(f"[held] unknown {mode}"))()
