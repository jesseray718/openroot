#!/usr/bin/env python3
"""sync_bridge.py — merge indexes from multiple AgapeMesh nodes"""
import json, hashlib, sys
from pathlib import Path
from datetime import datetime, timezone

def merge(dirs):
    merged = {"devices": {}, "concepts": {}, "synced_at": datetime.now(timezone.utc).isoformat()}
    for d in dirs:
        p = Path(d)
        for candidate in ["meta_index.json", "akashic_hyperindex.json", "merged_meta_index.json"]:
            f = p / candidate
            if not f.exists(): continue
            data = json.loads(f.read_text())
            device = p.name
            concepts = data.get("concepts", data) if isinstance(data, dict) else {}
            if not isinstance(concepts, dict): continue
            merged["devices"][device] = {"source": str(f), "count": len(concepts)}
            for k, v in concepts.items():
                h = hashlib.sha256(str(k).encode()).hexdigest()[:12]
                if h not in merged["concepts"]:
                    merged["concepts"][h] = {"concept": k, "sources": [device], "payload": v}
                else:
                    if device not in merged["concepts"][h]["sources"]:
                        merged["concepts"][h]["sources"].append(device)
    out = Path.home() / "agapemesh-ledger" / "merged_meta_index.json"
    out.write_text(json.dumps(merged, indent=2))
    print(f"Merged {len(merged['concepts'])} unique concepts from {len(merged['devices'])} devices → {out}")

if __name__ == "__main__":
    dirs = sys.argv[1:] or [str(Path.home() / "agapemesh-ledger")]
    merge(dirs)
