#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [EMBEDWARMV1] Corpus warmer for embed_cache — canary marker
"""
embed_warm_corpus.py — pre-populate data/embed_cache.db from existing corpora
so solve.py Tier 1 starts hot (zero first-query misses).

Sources (runtime state, never git-add):
  - data/solve_cache.jsonl   (prior task->solution pairs = Tier 1 lookup targets)
  - data/lessons.jsonl       (lesson chain text)
  - data/grounding.md        (canonical facts, chunked)

Usage: embed_warm_corpus.py            (dry-run: shows counts only)
       CONFIRM=1 embed_warm_corpus.py  (executes warm batches)
"""
import json, sys
from pathlib import Path

sys.path.insert(0, "/home/jesse/openroot/bin")
from embed_cache import embed_cached, CANARY

DATA = Path("/home/jesse/openroot/data")
CONTENT_KEYS = ("task", "text", "content", "body", "title", "question",
                "problem", "solution", "answer", "summary", "note")
CHUNK = 1500

def harvest_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    texts, seen = [], set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        for k, v in rec.items():
            if isinstance(v, str) and any(c in k.lower() for c in CONTENT_KEYS) \
               and 20 <= len(v) <= 50_000 and v not in seen:
                seen.add(v)
                texts.append(v)
    return texts

def harvest_md(path: Path) -> list:
    if not path.exists():
        return []
    t = path.read_text(encoding="utf-8", errors="replace")
    return [t[i:i+CHUNK] for i in range(0, len(t), CHUNK)] or [t]

def main() -> int:
    sources = {
        "solve_cache.jsonl": harvest_jsonl(DATA / "solve_cache.jsonl"),
        "lessons.jsonl":     harvest_jsonl(DATA / "lessons.jsonl"),
        "grounding.md":     harvest_md(DATA / "grounding.md"),
    }
    total = sum(len(v) for v in sources.values())
    for name, items in sources.items():
        print(f"[{CANARY}] {name}: {len(items)} units harvested")
    print(f"[{CANARY}] TOTAL {total} units")
    if not total:
        print("[held] nothing to warm — [exit=0]")
        return 0
    import os
    if os.environ.get("CONFIRM") != "1":
        print("[held] dry-run only — rerun with CONFIRM=1 to warm")
        return 0
    import time
    t0 = time.time()
    for name, items in sources.items():
        if not items:
            continue
        embed_cached(items)  # misses batched per source; re-run = all hits, ~0s
        print(f"[banked] {name}: {len(items)} units warm")
    print(f"[{CANARY}] WARM COMPLETE in {time.time()-t0:.1f}s "
          f"— rerun this script to verify (second pass should take <1s, proving cache)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
