#!/data/data/com.termux/files/usr/bin/python3
"""Aggressive content-hash dedup across phone / SD / USB.
Keeps newest mtime (or largest if tied). Hardlinks when same FS, else deletes dupe.
Produces No Waste. Absolute paths only.
"""
import os, sys, hashlib, json, time, collections
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---- CONFIG (edit once) ----
ROOTS = [
    "/sdcard",                          # primary + SD mount points under here
    "/storage/emulated/0",
    "/mnt/media_rw",                    # typical USB/OTG
    "/storage",                         # catch-all
]
EXCLUDE_DIRS = {
    "/sdcard/Android", "/sdcard/DCIM/.thumbnails",
    "/data", "/proc", "/sys", "/dev", "/acct",
    "lost+found", ".Trash", ".thumbnails", "cache", "Cache"
}
MIN_SIZE = 4096          # skip tiny files
HASH_ALGO = "xxh3"       # falls back to blake2b then sha256
WORKERS = 4              # Helio G99 safe
DRY_RUN = False          # set True first pass
KEEP_POLICY = "newest"   # newest | largest | first
LEDGER = "/sdcard/openroot/dedup/dedup_ledger.jsonl"
REPORT = "/sdcard/openroot/dedup/last_run_report.json"
# ----------------------------

def get_hasher():
    try:
        import xxhash
        return lambda b: xxhash.xxh3_128(b).hexdigest()
    except ImportError:
        try:
            return lambda b: hashlib.blake2b(b, digest_size=16).hexdigest()
        except:
            return lambda b: hashlib.sha256(b).hexdigest()

HASH = get_hasher()

def should_skip(path: Path) -> bool:
    s = str(path)
    for ex in EXCLUDE_DIRS:
        if ex in s:
            return True
    return False

def file_hash(path: Path, block=1<<20):
    h = HASH
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(block)
                if not chunk:
                    break
                # progressive
                pass  # real hash below
        # re-open for actual
        hasher = hashlib.sha256() if "sha256" in str(HASH) else None
        with open(path, "rb") as f:
            data = f.read()
            return HASH(data), len(data)
    except Exception as e:
        return None, 0

def scan(roots):
    size_map = collections.defaultdict(list)  # size -> [(path, mtime, inode, dev)]
    for root in roots:
        p = Path(root)
        if not p.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(p, followlinks=False):
            # prune
            dirnames[:] = [d for d in dirnames if not should_skip(Path(dirpath)/d)]
            for fn in filenames:
                fp = Path(dirpath) / fn
                if should_skip(fp):
                    continue
                try:
                    st = fp.stat()
                    if not st.st_size or st.st_size < MIN_SIZE:
                        continue
                    size_map[st.st_size].append((str(fp), st.st_mtime, st.st_ino, st.st_dev))
                except:
                    continue
    return size_map

def process_size_group(size, candidates):
    if len(candidates) < 2:
        return []
    # hash only same-size
    hash_groups = collections.defaultdict(list)
    for path, mtime, ino, dev in candidates:
        h, _ = file_hash(Path(path))
        if h:
            hash_groups[h].append((path, mtime, ino, dev))
    actions = []
    for h, group in hash_groups.items():
        if len(group) < 2:
            continue
        # keep decision
        if KEEP_POLICY == "newest":
            group.sort(key=lambda x: x[1], reverse=True)
        elif KEEP_POLICY == "largest":
            pass  # already same size
        keep = group[0]
        for path, mtime, ino, dev in group[1:]:
            same_fs = (dev == keep[3])
            actions.append({
                "keep": keep[0],
                "dupe": path,
                "hash": h,
                "size": size,
                "same_fs": same_fs,
                "action": "hardlink" if same_fs else "delete"
            })
    return actions

def execute(actions, dry=True):
    saved = 0
    linked = 0
    deleted = 0
    errors = []
    for a in actions:
        try:
            if dry:
                print(f"[DRY] {a['action']} {a['dupe']} -> {a['keep']}")
                saved += a["size"]
                continue
            if a["action"] == "hardlink":
                os.remove(a["dupe"])
                os.link(a["keep"], a["dupe"])
                linked += 1
            else:
                os.remove(a["dupe"])
                deleted += 1
            saved += a["size"]
            # ledger
            with open(LEDGER, "a") as f:
                f.write(json.dumps({**a, "ts": time.time()}) + "\n")
        except Exception as e:
            errors.append(str(e))
    return saved, linked, deleted, errors

def main():
    print("=== aggressive dedup start ===")
    size_map = scan(ROOTS)
    print(f"size groups with >1 file: {sum(1 for v in size_map.values() if len(v)>1)}")
    all_actions = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(process_size_group, sz, cands): sz for sz, cands in size_map.items() if len(cands)>1}
        for fut in as_completed(futs):
            all_actions.extend(fut.result())
    print(f"duplicate sets found: {len(all_actions)}")
    saved, linked, deleted, errors = execute(all_actions, dry=DRY_RUN)
    report = {
        "ts": time.time(),
        "dry_run": DRY_RUN,
        "bytes_saved": saved,
        "hardlinked": linked,
        "deleted": deleted,
        "errors": errors,
        "actions": len(all_actions)
    }
    Path(REPORT).parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    print("=== done ===")

if __name__ == "__main__":
    main()
