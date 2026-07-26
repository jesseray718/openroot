#!/usr/bin/env python3
"""Offline η³ ranker — scans local openroot repo, no network, no API"""
import os, re, json
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/openroot")
SKIP = {".git", "__pycache__", "models", "node_modules", ".venv"}

def score_file(path: Path, text: str) -> float:
    """Simple transparent η³ proxy: useful density / complexity"""
    lines = text.strip().splitlines()
    if not lines:
        return 0.0
    useful = sum(1 for l in lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//"))
    density = useful / max(len(lines), 1)
    # bonus for Agape / lowest-node / ledger / open language
    keywords = len(re.findall(r"agape|lowest.?node|hand-?up|ledger|open.?source|η|eta|zero.?dep|mutual", text, re.I))
    return round((density * 10) + (keywords * 1.5), 3)

def scan():
    results = []
    for p in ROOT.rglob("*"):
        if any(s in p.parts for s in SKIP):
            continue
        if p.suffix.lower() not in {".md", ".py", ".sh", ".json", ".txt"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")[:50000]
            sc = score_file(p, text)
            if sc > 0.5:
                results.append((sc, str(p.relative_to(ROOT)), len(text)))
        except Exception:
            pass
    results.sort(reverse=True)
    return results

if __name__ == "__main__":
    ranked = scan()
    print("=== Offline η³ Ranked Knowledge Nodes (local repo only) ===\n")
    for i, (sc, path, size) in enumerate(ranked[:40], 1):
        print(f"{i:2}. η³≈{sc:6.2f}  {path}  ({size} bytes)")
    print(f"\nTotal ranked nodes: {len(ranked)}")
    # also write dataset
    out = ROOT / "context_bridge" / "offline_rank.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump([{"rank": i+1, "eta3": sc, "path": p, "bytes": sz} for i, (sc, p, sz) in enumerate(ranked)], f, indent=2)
    print(f"Full dataset written to: {out}")
