#!/usr/bin/env python3
"""Convert kai_corpus_manifest to lumo_ingest queue format."""
import os, sys, json, hashlib
from pathlib import Path
CB = "/home/jesse/openroot/context_bridge/lumo_inbox"
MANIFEST = f"{CB}/kai_corpus_manifest_20260930_070204.json"
QUEUE = f"{CB}/inbound/inbound_queue.jsonl"
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
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    records, skipped, added = 0, 0, 0
    existing_ids = set()
    if os.path.exists(QUEUE):
        for ln in open(QUEUE):
            try: rec = json.loads(ln.strip()); existing_ids.add(rec.get("id"))
            except: pass
    for entry in json.load(open(MANIFEST)):
        records += 1
        rel = entry["rel"]
        ext = Path(rel).suffix.lower()
        if ext not in EXTS:
            skipped += 1; continue
        full = f"/home/jesse/kai_recovery/extracted/{rel}"
        if not os.path.exists(full):
            skipped += 1; continue
        fid = f"kai:{sha256(full)[:16]}"
        if fid in existing_ids:
            skipped += 1; continue
        body = open(full, "r", errors="ignore").read()[:2000]  # truncate large files
        rec = {"id": fid, "ts": entry["ts"], "from": "kai9000", "priority": "normal",
               "subject": f"Kai Corpus: {rel[:80]}", "body": body.replace("\n", " ")[:1500]}
        with open(QUEUE, "a") as fh: fh.write(json.dumps(rec) + "\n")
        added += 1
        if added % 100 == 0: print(f"[gate] {added} queued...")
    print(f"[banked] queued {added} records ({records} scanned, {skipped} skipped)")
    print("[exit=0]")
    sys.exit(0)

if __name__ == "__main__":
    try: main()
    except Exception as e:
        import traceback; traceback.print_exc(); sys.exit(1)
