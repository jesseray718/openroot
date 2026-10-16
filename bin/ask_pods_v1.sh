#!/usr/bin/env bash
# ask_pods_v1.sh "question text" — FTS retrieval across all populated pods,
# qwen2.5-coder:7b answers from context. READ-ONLY: mode=ro URIs throughout.
set -eu
Q="${1:?usage: ask_pods_v1.sh <question>}"
export TERM=dumb
python3 - "$Q" <<'PYEOF'
import sqlite3, json, urllib.request, sys
q = sys.argv[1]
pods = ["/home/jesse/pods/github-docs", "/home/jesse/pods/pod_github-history",
        "/home/jesse/pods/pod_self-corpus"]
conns = [(p.split("/")[-1], sqlite3.connect(f"file:{p}/pod.db?mode=ro", uri=True)) for p in pods]
words = [w for w in q.split() if len(w) > 3]
match = " OR ".join(f'"{w}"' for w in words[:6])
hits = []
for name, c in conns:
    try:
        hits += [(name, r[1] or "", r[0]) for r in c.execute(
            "SELECT snippet(chunks_fts,-1,'>>>','<<<',' ',24), section_path FROM chunks_fts "
            "WHERE chunks_fts MATCH ? LIMIT 3", (match,))]
    except Exception: pass
print(f"[retrieved] {len(hits)} chunks: {', '.join(sorted(set(h[0] for h in hits))) or 'none'}")
ctx = "\n---\n".join(f"[{n}|{s}] {t}" for n, s, t in hits[:5]) or "(no hits)"
body = json.dumps({"model": "qwen2.5-coder:7b", "prompt":
    f"Answer briefly using ONLY this context:\n{q}\n\nCONTEXT:\n{ctx}", "stream": False}).encode()
req = urllib.request.Request("http://localhost:11434/api/generate", data=body,
    headers={"Content-Type": "application/json"})
print(f"[7b-coder] {json.loads(urllib.request.urlopen(req, timeout=300).read())['response'].strip()}")
PYEOF
