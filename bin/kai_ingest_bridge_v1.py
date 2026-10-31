#!/usr/bin/env python3
"""Minimal Kai corpus indexer — writes to lumo_inbox for existing ingestion pipeline."""
import os, sys, json, hashlib
from datetime import datetime, timezone
from pathlib import Path

CORPUS = "/home/jesse/kai_recovery/extracted"
INBOX = "/home/jesse/openroot/context_bridge/lumo_inbox"
EXTS = {".md", ".txt", ".json", ".py", ".yaml", ".yml"}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1<<20)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    os.makedirs(INBOX, exist_ok=True)
    manifest, scanned = [], 0
    for root, _, files in os.walk(CORPUS):
        for fn in files:
            ext = Path(fn).suffix.lower()
            if ext not in EXTS: continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, CORPUS)
            size = os.path.getsize(full)
            h = sha256(full)
            scanned += 1
            manifest.append({"rel": rel, "size": size, "sha256": h, "ts": datetime.now(timezone.utc).isoformat()})
    out = os.path.join(INBOX, f"kai_corpus_manifest_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, "w") as fh: json.dump(manifest, fh, indent=2)
    print(f"[banked] indexed {scanned} files -> {out}")
    print("[exit=0]")
    sys.exit(0)

if __name__ == "__main__":
    try: main()
    except Exception as e:
        import traceback; traceback.print_exc(); sys.exit(1)
