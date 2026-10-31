# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot Ride-Along Dossier Engine v1 — budget-capped BM25 across multiple pods."""
import argparse, json, os, sqlite3, sys, time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
PODS_ROOT = REPO / "pods_garden"

def dossier_for_query(pods, query, top_k=18, char_budget=8000):
    all_chunks = []
    for pod_name in pods:
        pod_path = PODS_ROOT / pod_name
        if not (pod_path / "pod.db").exists(): continue
        conn = sqlite3.connect(str(pod_path / "pod.db"))
        safe = '"' + query.replace('"','""') + '"'
        sql = """SELECT c.chunk_blake3, c.doc_sha256, c.text, c.char_count,
                   bm25(chunks_fts) score, d.path
                 FROM chunks_fts JOIN chunks c ON chunks_fts.chunk_blake3 = c.chunk_blake3
                 JOIN documents d ON c.doc_sha256 = d.sha256
                 WHERE chunks_fts MATCH ? ORDER BY score LIMIT ?"""
        cur = conn.execute(sql, (safe, top_k*2))
        for ch, ds, text, cc, score, path in cur.fetchall():
            all_chunks.append({"pod":pod_name, "chunk_blake3":ch,
                "doc_sha256":ds, "doc_path":path, "text":text,
                "char_count":cc, "bm25_score":-score})
        conn.close()
    all_chunks.sort(key=lambda x: -x["bm25_score"])
    dossier, total, seen = [], 0, set()
    for chunk in all_chunks:
        if total + chunk["char_count"] > char_budget: continue
        if chunk["doc_sha256"] in seen and len(dossier) > top_k // 2: continue
        chunk["text"] = " ".join(chunk["text"].split())
        dossier.append(chunk); seen.add(chunk["doc_sha256"])
        total += chunk["char_count"]
        if len(dossier) >= top_k or total >= char_budget: break
    return {"query":query, "pods_searched":pods,
            "chunks_returned":len(dossier), "total_chars":total,
            "docs_cited":len(seen), "dossier":dossier,
            "generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def main():
    p = argparse.ArgumentParser(description="OpenRoot Dossier Engine v1")
    p.add_argument("--pods", nargs="+", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--top-k", type=int, default=18)
    p.add_argument("--budget", type=int, default=8000)
    p.add_argument("--output")
    args = p.parse_args()
    print(f"[gate] CANARY:OPENROOT-DOSSIER-V1 {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", file=sys.stderr)
    r = dossier_for_query(args.pods, args.query, args.top_k, args.budget)
    out = json.dumps(r, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out)
        print(f"[banked] dossier -> {args.output}", file=sys.stderr)
        print(f"  chunks: {r['chunks_returned']}", file=sys.stderr)
        print(f"  chars:  {r['total_chars']}", file=sys.stderr)
        print(f"  docs:   {r['docs_cited']}", file=sys.stderr)
    else:
        print(out)

if __name__ == "__main__":
    main()
