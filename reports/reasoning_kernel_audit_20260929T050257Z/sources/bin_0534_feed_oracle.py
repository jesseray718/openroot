#!/data/data/com.termux/files/usr/bin/python3
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
OPENROOT = Path("/sdcard/openroot")
SEEDS = OPENROOT / "agape_kb" / "seeds"
ENGINE = HOME / "une" / "computational_flow" / "agape_engine.py"
LOG = OPENROOT / "context_bridge" / "seed_oracle.log"
KB = OPENROOT / "agape_kb"
def log(msg):
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] FEED {msg}"
    print(line)
    with open(LOG, "a") as f: f.write(line + "\n")
def feed_one(seed_path):
    meta = json.loads(seed_path.read_text())
    if meta.get("oracle_ingest_status") == "fed": return True
    text = meta.get("preview") or f"[seed] {meta.get('content_hash')} {meta.get('original_path')}"
    ok = False
    if ENGINE.exists():
        try:
            r = subprocess.run([sys.executable, str(ENGINE), "learn", text[:6000]], capture_output=True, text=True, timeout=25, cwd=str(ENGINE.parent))
            if r.returncode == 0: ok = True
        except Exception as e: log(f"engine error {e}")
    if not ok:
        frag = KB / "pending_fragments"
        frag.mkdir(exist_ok=True)
        (frag / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".frag")).write_text(text[:8000])
        ok = True
        log("wrote fragment")
    if ok:
        meta["oracle_ingest_status"] = "fed"
        meta["fed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        seed_path.write_text(json.dumps(meta, indent=2))
        log(f"FED {seed_path.name}")
    return ok
def main(limit=30):
    SEEDS.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    fed = 0
    for p in sorted(SEEDS.glob("*.seed")):
        if fed >= limit: break
        try:
            if json.loads(p.read_text()).get("oracle_ingest_status") == "pending":
                if feed_one(p): fed += 1
        except: pass
    log(f"newly fed={fed}")
if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 30)
