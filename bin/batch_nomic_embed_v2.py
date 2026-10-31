#!/usr/bin/env python3
"""batch_nomic_embed_v2.py — recursive nomic-embed-text ingestion, sha256 dedup, atomic JSONL out.
Fix v2: removed false-positive /root path guard; corrected INPUT_DIR=/home/jesse/openroot."""
import json, hashlib, os, sys, time
from pathlib import Path
try:
    from urllib.request import Request, urlopen
except Exception as e:
    print(f"[held] import fail: {e}"); sys.exit(1)

ROOT = "/home/jesse/openroot"
OUT = "/home/jesse/openroot/data/embeddings"
MODEL = "nomic-embed-text"
OLLAMA = "http://localhost:11434/api/embed"
SKIP_DIRS = {".git", "venv", "__pycache__", "node_modules", ".ollama"}
HOST = Path.home().name
OUTFILE = os.path.join(OUT, f"nomic_embeddings_{HOST}.jsonl")
MAX_CHARS = 4096

def sha(t): return hashlib.sha256(t.encode()).hexdigest()

def embed(text):
    payload = json.dumps({"model": MODEL, "input": text}).encode()
    req = Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=120) as r:
        return json.loads(r.read())["embedding"]

def main():
    seen, records, skipped = {}, [], 0
    prior = os.path.join(OUT, "embed_index.json")
    if os.path.exists(prior):
        with open(prior) as f:
            seen = {k: v for k, v in json.load(f).items()}
    t0 = time.time()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".md"): continue
            p = os.path.join(dirpath, fn)
            try:
                content = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                skipped += 1; continue
            h = sha(content)
            if h in seen:
                continue
            try:
                emb = embed(content[:MAX_CHARS])
            except Exception as e:
                print(f"[held] embed fail {p}: {e}"); skipped += 1; continue
            records.append({"file": p, "sha256": h, "preview": content[:200], "embedding": emb})
            seen[h] = p
    tmp = OUTFILE + ".tmp"
    with open(tmp, "w") as f:
        for rec in records: f.write(json.dumps(rec) + "\n")
    os.replace(tmp, OUTFILE)
    tmp = prior + ".tmp"
    with open(tmp, "w") as f: json.dump(seen, f)
    os.replace(tmp, prior)
    print(f"[banked] {len(records)} new embeddings, {len(seen)} total indexed, "
          f"{skipped} skipped, {time.time()-t0:.1f}s, out={OUTFILE}")

if __name__ == "__main__":
    main()
