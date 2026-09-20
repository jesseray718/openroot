#!/data/data/com.termux/files/usr/bin/python3
import json, time
from pathlib import Path
OPENROOT = Path("/sdcard/openroot")
SEEDS = OPENROOT / "agape_kb" / "seeds"
MAP = OPENROOT / "context_bridge" / "system.map.json"
def main():
    SEEDS.mkdir(parents=True, exist_ok=True)
    MAP.parent.mkdir(parents=True, exist_ok=True)
    seeds = []
    for p in SEEDS.glob("*.seed"):
        try:
            d = json.loads(p.read_text())
            d["_seed_file"] = str(p)
            seeds.append(d)
        except: pass
    fed = [s for s in seeds if s.get("oracle_ingest_status") == "fed"]
    pending = [s for s in seeds if s.get("oracle_ingest_status") == "pending"]
    m = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fed_count": len(fed), "pending_count": len(pending), "total_seeds": len(seeds),
        "seeds_fed": [{"hash": s.get("content_hash"), "original": s.get("original_path"), "size": s.get("size_bytes")} for s in fed]
    }
    tmp = MAP.with_suffix(".tmp")
    tmp.write_text(json.dumps(m, indent=2))
    tmp.replace(MAP)
    print(f"map updated fed={len(fed)} pending={len(pending)} total={len(seeds)}")
if __name__ == "__main__": main()
