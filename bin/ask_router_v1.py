#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
ask_router_v1.py

Two-stage query router:
  1) Lexical gate (cheap): keyword overlap against indexed paths/hints.
  2) Semantic placeholder: falls back to lexical for now, but returns scored hits.

Output:
  JSON lines with hash refs only:
    {"rank":1,"sha256":"...","path_hint":"...","score":..., "why":"lexical"}
Exit:
  0 on success with any result set (including empty)
  2 on hard error
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DB = ROOT / "data" / "rootkit.db"

STOP = {
    "the", "and", "or", "to", "in", "of", "for", "a", "an", "on", "is", "are", "be",
    "with", "by", "as", "that", "this", "it", "at", "from", "what", "which", "where",
    "how", "why"
}

def tokenize(q):
    toks = re.findall(r"[a-zA-Z0-9_\-\.]+", q.lower())
    return [t for t in toks if t not in STOP and len(t) >= 2]

def load_candidates(con, limit_scan=5000):
    rows = con.execute("""
        SELECT o.sha256, COALESCE(o.path_hint,''), COALESCE(ol.relpath,''), COALESCE(ol.abs_path,'')
        FROM objects o
        LEFT JOIN object_locations ol ON ol.sha256 = o.sha256
        LIMIT ?
    """, (limit_scan,)).fetchall()
    cands = []
    for sha, hint, rel, abs_p in rows:
        text = " ".join([hint, rel, abs_p]).lower()
        cands.append((sha, hint or rel or abs_p, text))
    return cands

def score_lexical(tokens, text):
    if not tokens:
        return 0.0
    hit = sum(1 for t in tokens if t in text)
    return hit / float(len(tokens))

def route_bucket(query):
    q = query.lower()
    if any(k in q for k in ["commit", "push", "branch", "merge", "pr", "release"]):
        return "gitops"
    if any(k in q for k in ["implement", "write", "edit", "patch", "spec"]):
        return "spec_builder_7b"
    if any(k in q for k in ["verify", "test", "grade", "validate", "check"]):
        return "grader_3b"
    return "fts5_search"

def main():
    ap = argparse.ArgumentParser(description="ask router")
    ap.add_argument("--query", required=True, help="natural language query")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    if not DB.exists():
        print(json.dumps({"error": f"missing db: {DB}"}))
        return 2

    con = sqlite3.connect(DB)
    toks = tokenize(args.query)
    bucket = route_bucket(args.query)
    cands = load_candidates(con, limit_scan=10000)
    con.close()

    scored = []
    for sha, path_hint, txt in cands:
        sc = score_lexical(toks, txt)
        if sc > 0:
            scored.append((sc, sha, path_hint))

    scored.sort(key=lambda x: (-x[0], x[2], x[1]))
    top = scored[: max(1, args.limit)]

    print(json.dumps({"route_bucket": bucket, "token_count": len(toks), "result_count": len(top)}))
    for i, (sc, sha, hint) in enumerate(top, start=1):
        print(json.dumps({
            "rank": i,
            "sha256": sha,
            "path_hint": hint,
            "score": round(sc, 6),
            "why": "lexical",
        }, sort_keys=True))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
