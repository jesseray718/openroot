import sqlite3
import hashlib
import time
import sys
import os
from pathlib import Path
from multiprocessing import Pool

DB = "data/file_ledger.db"

# Import DOMAINS from the canonical ledger script to avoid drift
ns = {}
exec(open("bin/file_ledger_v2.py").read().split("def ")[0], ns)
DOMAINS = ns["DOMAINS"]

def hash_one(args):
    domain, relpath = args
    # Use DOMAINS map for correct root path per domain
    root = DOMAINS.get(domain)
    if not root:
        return (domain, relpath, "-domain-unknown-")
    fpath = os.path.join(root, relpath)
    h = hashlib.sha256()
    try:
        with open(fpath, "rb") as f:
            while chunk := f.read(1 << 20):
                h.update(chunk)
        return (domain, relpath, h.hexdigest())
    except OSError:
        return (domain, relpath, "-unreadable-")

def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    
    con = sqlite3.connect(DB, timeout=120)
    con.execute("PRAGMA busy_timeout=120000")
    con.execute("PRAGMA journal_mode = WAL;")
    con.execute("PRAGMA synchronous = NORMAL;")
    con.execute("PRAGMA cache_size = -65536;")
    con.execute("PRAGMA temp_store = MEMORY;")

    def flush(rows):
        for attempt in range(5):
            try:
                con.executemany("UPDATE files SET sha256=?, hashed_ts=? WHERE domain=? AND relpath=?",
                                [(h, time.time(), d, r) for d, r, h in rows])
                con.commit()
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < 4:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise

    rows = con.execute("SELECT domain, relpath FROM files WHERE sha256 IS NULL ORDER BY domain, relpath").fetchall()
    total = len(rows)
    if total == 0:
        print("[banked] nothing to do"); return

    print(f"[gate] parallel hash queue: {total:,} files, {workers} workers (WAL + optimized cache)")
    
    done = 0; t0 = time.time(); buf = []
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(hash_one, rows, chunksize=64):
            buf.append(rec)
            done += 1
            if len(buf) >= 2000:
                flush(buf); buf = []
            if done % 5000 == 0:
                now = time.time()
                print(f"  {done:,}/{total:,} ({100*done/total:.0f}%) "
                      f"{now-t0:.0f}s elapsed, {done/(now-t0):.0f} files/s", flush=True)
        if buf:
            flush(buf)
            
    un = con.execute("SELECT COUNT(*) FROM files WHERE sha256 IS NULL").fetchone()[0]
    print(f"[banked] parallel pass complete: {done:,} files in {time.time()-t0:.0f}s, "
          f"remaining NULL={un:,}")

if __name__ == "__main__":
    main()
