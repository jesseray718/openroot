#!/usr/bin/env python3
"""Offline η³ ranker — prioritizes intentional OpenRoot + Agape + continuity material"""
import os, re, json
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/openroot")
SKIP = {".git", "__pycache__", "models", "node_modules", ".venv", "sync-from-kai", "gguf-py", "build"}

BOOST_KEYWORDS = [
    r"\bagape\b", r"\bη\b", r"\beta\b", r"lowest.?node", r"hand.?up",
    r"ledger", r"thermodynamic", r"circuit.?closure", r"human.?continuity",
    r"primitive", r"fusion", r"resilience", r"anti.?fragil", r"floor.?rais",
    r"openroot", r"seed.?core", r"cloud.?9", r"nanobot", r"swarm"
]

PENALTY_PATHS = ["sync-from-kai", "gguf", "node_modules", "models", ".git"]

def score_file(path: Path, text: str) -> float:
    lines = text.strip().splitlines()
    if not lines:
        return 0.0
    useful = sum(1 for l in lines if l.strip() and not l.strip().startswith(("#", "//", "/*")))
    density = useful / max(len(lines), 1)
    keyword_hits = sum(len(re.findall(k, text, re.I)) for k in BOOST_KEYWORDS)
    score = (density * 12) + (keyword_hits * 3.5)

    # path penalties
    path_str = str(path).lower()
    for p in PENALTY_PATHS:
        if p in path_str:
            score *= 0.15
            break

    # strong boost for foundation / continuity / agape material
    if "human-continuity" in path_str or "foundation_library" in path_str:
        score *= 2.8
    if "agape" in path_str or "seed-core" in path_str or "cloud9" in path_str:
        score *= 1.8

    return round(score, 3)

def scan():
    results = []
    for p in ROOT.rglob("*"):
        if any(s in p.parts for s in SKIP):
            continue
        if p.suffix.lower() not in {".md", ".py", ".sh", ".json", ".txt"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")[:60000]
            sc = score_file(p, text)
            if sc > 1.0:
                results.append((sc, str(p.relative_to(ROOT)), len(text)))
        except Exception:
            pass
    results.sort(reverse=True)
    return results

if __name__ == "__main__":
    ranked = scan()
    print("=== Offline η³ Ranked Knowledge Nodes (OpenRoot-priority) ===\n")
    for i, (sc, path, size) in enumerate(ranked[:40], 1):
        print(f"{i:2}. η³≈{sc:7.2f}  {path}  ({size} bytes)")
    print(f"\nTotal ranked nodes: {len(ranked)}")
    out = ROOT / "context_bridge" / "offline_rank.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump([{"rank": i+1, "eta3": sc, "path": p, "bytes": sz} for i, (sc, p, sz) in enumerate(ranked)], f, indent=2)
    print(f"Full dataset written to: {out}")
