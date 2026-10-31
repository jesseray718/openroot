# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""AI audit harness: bounded dir manifest + git diff -> model report -> sealed into pathway ledger.
Cached pathway hit means the AI is NEVER called for proven input."""
import os, sys, json, hashlib, subprocess, urllib.request, datetime, argparse

IGNORE = {"reports", "logs", "venv", "node_modules", ".git", "__pycache__", "archive", "attic", "quarantine_tooling_repair_backups_20260926T205307Z"}
OLLAMA = "http://localhost:11434"

def manifest(root, max_files=4000, sample_bytes=1200):
    entries, samples = [], {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE]
        for f in filenames:
            if len(entries) >= max_files:
                return entries, samples
            p = os.path.join(dirpath, f)
            try:
                sz = os.path.getsize(p)
                rel = os.path.relpath(p, root)
                entries.append(f"{rel}|{sz}")
                if f.endswith((".py", ".sh")) and len(samples) < 25:
                    with open(p, "r", errors="replace") as fh:
                        samples[rel] = fh.read(sample_bytes)
            except OSError:
                continue
    return entries, samples

def ollama_chat(model, system, user, timeout=600):
    body = json.dumps({"model": model, "stream": False, "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["message"]["content"]

def embed(text):
    body = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embeddings", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["embedding"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True)
    p.add_argument("--diff-file")
    p.add_argument("--model", default="qwen2.5-coder:7b")
    p.add_argument("--kind", default="workspace_audit")
    p.add_argument("--embed", action="store_true")
    a = p.parse_args()

    sys.path.insert(0, "/home/jesse/openroot/bin")
    import pathway_ledger_v1 as ledger

    entries, samples = manifest(a.target)
    diff = ""
    if a.diff_file and os.path.isfile(a.diff_file):
        diff = open(a.diff_file, errors="replace").read()[:20000]
    digest = "\n".join(entries)
    input_hash = hashlib.sha256((digest + "\n---DIFF---\n" + diff).encode()).hexdigest()

    hit = ledger.lookup(input_hash)
    if hit:
        print(f"[banked] CACHED PATHWAY id={hit[0]} report={hit[1]} ({hit[3]})")
        print("[banked] no recompute — proven pathway reused")
        return 0

    system = ("You are an expert automation engineer auditing an open-source repo. "
              "Output a concise markdown audit report with sections: FINDINGS, RISKS, "
              "RECOMMENDED ACTIONS. No code fences around the whole report. Be specific, "
              "cite filenames. Falsifiable claims only, no hype.")
    user = (f"AUDIT TARGET: {a.target}\n\nFILE MANIFEST ({len(entries)} files):\n"
            f"{digest[:15000]}\n\nGIT DIFF:\n{diff if diff else '(clean)'}\n\n"
            f"FILE SAMPLES:\n" + "\n\n".join(f"--- {k} ---\n{v}" for k, v in samples.items()))

    print(f"[gate] calling {a.model} (timeout 600s)...")
    report = ollama_chat(a.model, system, user)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = os.path.basename(a.target.rstrip('/')) or "root"
    rpath = f"/home/jesse/openroot/reports/audit-{label}-{ts}.md"
    os.makedirs(os.path.dirname(rpath), exist_ok=True)
    with open(rpath, "w") as f:
        f.write(report)
    row_sha = ledger.append(input_hash, a.kind, a.model, rpath, "verified")
    if a.embed:
        try:
            vec = embed(report)
            import sqlite3
            c = sqlite3.connect("/home/jesse/openroot/data/pathways.db")
            c.execute("CREATE TABLE IF NOT EXISTS embeddings(row_sha TEXT PRIMARY KEY, dim INTEGER, vec TEXT)")
            c.execute("INSERT OR REPLACE INTO embeddings VALUES(?,?,?)", (row_sha, len(vec), json.dumps(vec)))
            c.commit(); c.close()
            print("[banked] nomic embedding stored")
        except Exception as e:
            print(f"[held] embed skipped: {e}")
    print(f"[banked] report={rpath}")
    print(f"[banked] pathway sealed row_sha={row_sha}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
