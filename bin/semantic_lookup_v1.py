# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Solution 3: thresholded semantic routing over the pathway embedding store.

Layers (hash-first is handled by callers/the router; this provides the rest):
  embed-second: cosine similarity vs embeddings table, thresholded
  model-last:  callers invoke the model only when score < threshold

Usage:
  semantic_lookup_v1.py probe                        # calibrate threshold on live embeddings
  semantic_lookup_v1.py query "question text"        # scored neighbor search
  semantic_lookup_v1.py route "question text"        # full decision: HASH / SEMANTIC / MODEL
Options:
  --threshold F   cosine gate (default 0.75, override after probe)
"""
import sqlite3, json, math, hashlib, urllib.request, sys, argparse

DB = "/home/jesse/openroot/data/pathways.db"
OLLAMA = "http://localhost:11434"
DEFAULT_THRESHOLD = 0.42

PROBES_RELATED = [
    "what risks did the audit find in the openroot repository",
    "summarize the workspace audit findings and recommended actions",
    "which bin scripts have defects or security issues",
]
PROBES_UNRELATED = [
    "how to bake sourdough bread at high altitude",
    "what is the capital of Australia",
    "explain the mating habits of octopi",
]

def embed(text):
    body = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embeddings", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["embedding"]

def load_embeddings():
    c = sqlite3.connect(DB)
    try:
        c.execute("CREATE TABLE IF NOT EXISTS embeddings(row_sha TEXT PRIMARY KEY, dim INTEGER, vec TEXT)")
        rows = c.execute("SELECT row_sha, vec FROM embeddings").fetchall()
        c.close()
        return {sha: json.loads(v) for sha, v in rows}
    except Exception:
        c.close()
        return {}

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def nearest(query_vec, store, top_k=3):
    scored = [(sha, cosine(query_vec, vec)) for sha, vec in store.items()]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:top_k]

def cmd_probe(threshold):
    store = load_embeddings()
    if not store:
        print("[held] no embeddings stored — run an audit with --embed first")
        return 1
    print(f"[gate] probing against {len(store)} stored embeddings")
    related_scores, unrelated_scores = [], []
    for q in PROBES_RELATED:
        s = nearest(embed(q), store, 1)
        related_scores.append(s[0][1] if s else 0.0)
        print(f"  RELATED   score={s[0][1]:.4f}  q={q[:60]}" if s else f"  RELATED   none  q={q[:60]}")
    for q in PROBES_UNRELATED:
        s = nearest(embed(q), store, 1)
        unrelated_scores.append(s[0][1] if s else 0.0)
        print(f"  UNRELATED score={s[0][1]:.4f}  q={q[:60]}" if s else f"  UNRELATED none  q={q[:60]}")
    hi = min(related_scores) if related_scores else 0.0
    lo = max(unrelated_scores) if unrelated_scores else 0.0
    mid = (hi + lo) / 2.0
    verdict = "SEPARABLE" if hi > lo else "OVERLAPPING"
    print(f"[banked] related-floor={hi:.4f} unrelated-ceiling={lo:.4f} midpoint={mid:.4f} verdict={verdict}")
    print(f"[gate] suggested --threshold {max(mid, 0.5):.2f} (default was {threshold})")
    return 0

def cmd_query(question, threshold):
    store = load_embeddings()
    if not store:
        print("[held] no embeddings stored"); return 1
    qv = embed(question)
    hits = nearest(qv, store)
    any_hit = False
    for sha, score in hits:
        gate = "HIT " if score >= threshold else "miss"
        print(f"[{gate}] {score:.4f} {sha[:12]}")
        any_hit = any_hit or score >= threshold
    return 0 if any_hit else 2

def cmd_route(question, threshold):
    # Layer 1: hash-first (exact query text hash)
    qhash = hashlib.sha256(question.strip().lower().encode()).hexdigest()
    c = sqlite3.connect(DB)
    try:
        c.execute("CREATE TABLE IF NOT EXISTS queries(query_sha TEXT PRIMARY KEY, answer_path TEXT, created_utc TEXT)")
        exact = c.execute("SELECT answer_path FROM queries WHERE query_sha=?", (qhash,)).fetchone()
        c.close()
    except Exception:
        c.close(); exact = None
    if exact:
        print(f"DECISION=HASH answer={exact[0]}")
        return 0
    # Layer 2: embed-second (semantic neighbor, thresholded)
    store = load_embeddings()
    if store:
        qv = embed(question)
        best_sha, best_score = nearest(qv, store, 1)[0] if store else (None, 0.0)
        print(f"[gate] best neighbor {best_sha[:12]} score={best_score:.4f} threshold={threshold}")
        if best_score >= threshold:
            print(f"DECISION=SEMANTIC row_sha={best_sha[:12]} score={best_score:.4f}")
            return 0
    # Layer 3: model-last (caller invokes — this tool reports the miss)
    print("DECISION=MODEL (no hash hit, no semantic neighbor above threshold — call model, then seal)")
    return 3

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["probe", "query", "route"])
    p.add_argument("question", nargs="?")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    a = p.parse_args()
    if a.cmd == "probe":
        sys.exit(cmd_probe(a.threshold))
    if not a.question:
        sys.exit("question text required")
    if a.cmd == "query":
        sys.exit(cmd_query(a.question, a.threshold))
    else:
        sys.exit(cmd_route(a.question, a.threshold))
