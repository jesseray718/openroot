#!/usr/bin/env python3
"""Tiered, resumable populate for hash_manifest_optiplex.db (manifest table).

Targets the host-aware `manifest` table (path, sha256, size_bytes, mtime_ns,
hashed_at, host, status, error_text). Leaves the legacy `hash_manifest` table
untouched. Resumable: files whose (mtime_ns, size_bytes) already match a
status='ok' row for this host are skipped.

Examples:
  python3 bin/hash_manifest_populate_v1.py --tier repo --dry-run
  python3 bin/hash_manifest_populate_v1.py --tier data
  python3 bin/hash_manifest_populate_v1.py --tier usb
  python3 bin/hash_manifest_populate_v1.py --root /data
"""
import argparse
import hashlib
import os
import random
import sqlite3
import stat as statmod
import sys
import time
from datetime import datetime, timezone

DB = "/home/jesse/openroot/data/hash_manifest_optiplex.db"
HOST = "optiplex"
CHUNK = 1 << 20

TIERS = {
    "repo":  ("/home/jesse/openroot", {".git", "data"}),
    "data":  ("/home/jesse/openroot/data", set()),
    "trees": ("/home/jesse/podkit-unify", set()),
    "usb":   ("/mnt/sdb1", set()),
    "home":  ("/home/jesse", {".cache", "snap"}),
}
EXCLUDE_DIRS = {".ssh", "__pycache__", "node_modules", "merge_staging", "lost+found"}
SKIP_REALPATHS = {
    os.path.realpath(DB),
    os.path.realpath(DB) + "-wal",
    os.path.realpath(DB) + "-shm",
}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def iter_files(root, extra_excl, root_dev):
    for dirpath, dirnames, filenames in os.walk(root):
        keep = []
        for d in sorted(dirnames):
            if d in EXCLUDE_DIRS or d in extra_excl or d.startswith("*"):
                continue
            p = os.path.join(dirpath, d)
            try:
                if os.stat(p, follow_symlinks=False).st_dev != root_dev:
                    continue
            except OSError:
                continue
            keep.append(d)
        dirnames[:] = keep
        for name in sorted(filenames):
            if name.startswith("*"):
                continue
            path = os.path.join(dirpath, name)
            if os.path.realpath(path) in SKIP_REALPATHS:
                continue
            try:
                st = os.stat(path, follow_symlinks=False)
            except OSError as e:
                yield path, None, str(e)
                continue
            if not statmod.S_ISREG(st.st_mode):
                continue
            yield path, st, None


def main():
    ap = argparse.ArgumentParser(description="tiered resumable hash-manifest populate")
    ap.add_argument("--tier", choices=sorted(TIERS))
    ap.add_argument("--root")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--spot", type=int, default=5)
    a = ap.parse_args()

    if a.root:
        root, extra = os.path.abspath(a.root), set()
    elif a.tier:
        root, extra = TIERS[a.tier]
    else:
        ap.error("need --tier or --root")
    if not os.path.isdir(root):
        print("ROOT MISSING:", root)
        sys.exit(1)
    root_dev = os.stat(root).st_dev
    label = a.tier or root

    if a.dry_run:
        n = b = 0
        for path, st, err in iter_files(root, extra, root_dev):
            if st is not None:
                n += 1
                b += st.st_size
        print("DRY-RUN %s: files=%d bytes=%d (%.2f GB)" % (label, n, b, b / 1e9))
        if n == 0:
            print("WARNING: 0 files seen - check root path, permissions, mounts")
        return

    conn = sqlite3.connect(DB, timeout=30)
    conn.execute("PRAGMA synchronous=NORMAL")
    known = {}
    for path, mtime_ns, size in conn.execute(
        "SELECT path, mtime_ns, size_bytes FROM manifest WHERE host=? AND status='ok'",
        (HOST,),
    ):
        known[path] = (mtime_ns, size)

    rows, spot = [], []
    def stamp():
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    hashed = skipped = errors = bytes_had = 0
    t0 = time.time()

    def flush(batch):
        conn.executemany(
            "INSERT OR REPLACE INTO manifest "
            "(path, sha256, size_bytes, mtime_ns, hashed_at, host, status, error_text) "
            "VALUES (?,?,?,?,?,?,?,?)",
            batch,
        )
        conn.commit()

    for path, st, err in iter_files(root, extra, root_dev):
        if err is not None:
            rows.append((path, "", 0, 0, stamp(), HOST, "error", err))
            errors += 1
        else:
            if known.get(path) == (st.st_mtime_ns, st.st_size):
                skipped += 1
                continue
            try:
                digest = sha256_of(path)
            except OSError as e:
                rows.append((path, "", st.st_size, st.st_mtime_ns, stamp(), HOST, "error", str(e)))
                errors += 1
                continue
            rows.append((path, digest, st.st_size, st.st_mtime_ns, stamp(), HOST, "ok", None))
            spot.append((path, digest))
            hashed += 1
            bytes_had += st.st_size
        if len(rows) >= a.batch:
            flush(rows)
            rows.clear()
        total = hashed + errors
        if total and total % 1000 == 0:
            rate = bytes_had / max(time.time() - t0, 0.1) / 1e6
            print(
                "[%s] %d files, %.2f GB, %.0f MB/s, err=%d, skip=%d"
                % (label, total, bytes_had / 1e9, rate, errors, skipped),
                flush=True,
            )
    if rows:
        flush(rows)

    bad = 0
    for path, digest in random.sample(spot, min(a.spot, len(spot))):
        if sha256_of(path) != digest:
            bad += 1
            print("SPOT-FAIL:", path)

    dt = time.time() - t0
    print(
        "DONE %s: hashed=%d (%.2f GB) skipped=%d errors=%d elapsed=%.0fs spot_bad=%d"
        % (label, hashed, bytes_had / 1e9, skipped, errors, dt, bad)
    )
    if hashed + skipped + errors == 0:
        print("WARNING: 0 files seen - check root path, permissions, mounts")
    conn.close()


if __name__ == "__main__":
    main()
