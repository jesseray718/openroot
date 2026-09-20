#!/data/data/com.termux/files/usr/bin/python3
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
OPENROOT = Path("/sdcard/openroot")
SEEDS = OPENROOT / "agape_kb" / "seeds"
LOG = OPENROOT / "context_bridge" / "seed_oracle.log"
TEXT_EXT = {".md",".py",".json",".txt",".sh",".yml",".yaml",".toml",".csv",".log"}
def ensure():
    SEEDS.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
def log(msg):
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}"
    print(line)
    with open(LOG, "a") as f: f.write(line + "\n")
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1<<20), b""): h.update(b)
    return h.hexdigest()
def process_file(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0: return
    if path.suffix.lower() not in TEXT_EXT: return
    if path.stat().st_size > 512*1024: return
    h = sha256_file(path)
    seed = SEEDS / f"{h[:16]}_{path.name}.seed"
    if seed.exists(): return
    data = path.read_bytes()
    meta = {
        "original_path": str(path), "content_hash": h, "size_bytes": len(data),
        "mtime": int(path.stat().st_mtime), "eta_score": 0.8,
        "oracle_ingest_status": "pending", "archive_status": "none",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "preview": data.decode("utf-8", errors="replace")[:3000]
    }
    seed.write_text(json.dumps(meta, indent=2))
    log(f"SEEDED {path} -> {seed.name}")
def walk(roots, limit=60):
    ensure()
    n = 0
    for root in roots:
        root = Path(root)
        if not root.exists(): continue
        log(f"Scanning {root}")
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in {".git","__pycache__",".cache","node_modules"}]
            for name in filenames:
                if n >= limit: return n
                try:
                    process_file(Path(dirpath)/name)
                    n += 1
                except Exception as e: log(f"SKIP {e}")
    return n
if __name__ == "__main__":
    import sys
    roots = sys.argv[1:] or ["/sdcard/openroot/session_seeds", "/data/data/com.termux/files/home/une/computational_flow", "/sdcard/openroot/agape_kb"]
    walk(roots)
