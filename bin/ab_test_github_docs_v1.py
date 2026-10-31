#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
ab_test_github_docs_v1.py

Controlled A/B comparison: do the GitHub how-to docs improve pod answers?

Conditions (same questions, model, prompt template, decoding options, scoring):
  A_with_docs     retrieval over every supplied pod, including the docs pod
  B_without_docs  retrieval over every supplied pod except the docs pod
  C_no_retrieval  (optional, --include-baseline) model with no evidence at all

Safety:
  * pod databases are opened with SQLite mode=ro and PRAGMA query_only=ON
  * each pod file is SHA-256 hashed before and after the run; any change aborts
  * output directory must not sit inside any pod directory or be a pod file
  * nothing is ever written to a pod; results go only to --out-dir (default runs/ab)

Offline-first: only talks to Ollama at localhost unless --ollama-url overrides it.
Exit: 0 ok, 2 usage/safety/hard error.
"""

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

STOP = {
    "the", "and", "or", "to", "in", "of", "for", "a", "an", "on", "is", "are", "be",
    "with", "by", "as", "that", "this", "it", "at", "from", "what", "which", "where",
    "how", "why", "do", "does", "can", "i", "my", "you", "your",
}

PROMPT_TEMPLATE = (
    "Answer the question using ONLY the evidence below. "
    "Cite every claim with its evidence tag, e.g. [pod:abcd1234]. "
    "If the evidence is insufficient, say so.\n\n"
    "EVIDENCE:\n{evidence}\n\nQUESTION: {question}\n\nANSWER:"
)
NO_EVIDENCE_PROMPT = (
    "Answer the question using ONLY the evidence below. "
    "Cite every claim with its evidence tag. "
    "If the evidence is insufficient, say so.\n\n"
    "EVIDENCE:\n(none)\n\nQUESTION: {question}\n\nANSWER:"
)


class SafetyError(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9_\-]+", text.lower()) if t not in STOP and len(t) >= 2]


def open_readonly(path):
    con = sqlite3.connect(f"{Path(path).resolve().as_uri()}?mode=ro", uri=True, timeout=30)
    con.execute("PRAGMA query_only = ON")
    return con


def parse_pod_spec(spec):
    if "=" not in spec:
        raise SafetyError(f"--pod must be NAME=PATH, got: {spec}")
    name, path = spec.split("=", 1)
    p = Path(path).expanduser().resolve()
    if not name or not p.is_file():
        raise SafetyError(f"pod database not found: {path}")
    return name, p


def check_out_dir(out_dir, pods):
    out = out_dir.resolve()
    for name, p in pods.items():
        if out == p or p.parent == out or p.parent in out.parents:
            raise SafetyError(f"refusing output dir inside pod '{name}' directory: {out}")


def pod_columns(con):
    cols = [r[1] for r in con.execute("PRAGMA table_info(chunks)")]
    if "chunk_text" not in cols:
        raise SafetyError("pod chunks table has no chunk_text column")
    id_col = next((c for c in ("chunk_sha256", "chunk_id") if c in cols), None)
    if id_col is None:
        raise SafetyError("pod chunks table has no chunk_sha256/chunk_id column")
    return id_col


def fts_query(question):
    toks = tokenize(question)
    return " OR ".join(f'"{t}"' for t in toks)


def retrieve_pod(name, con, question, k):
    """Lexical FTS5 retrieval. Returns list of hits with provenance."""
    id_col = pod_columns(con)
    q = fts_query(question)
    if not q:
        return []
    has_fts = con.execute(
        "SELECT 1 FROM sqlite_master WHERE name='chunks_fts'").fetchone() is not None
    if has_fts:
        rows = con.execute(
            f"""SELECT c.{id_col}, c.chunk_text, bm25(chunks_fts)
                FROM chunks_fts JOIN chunks c ON c.rowid = chunks_fts.rowid
                WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?""",
            (q, k)).fetchall()
    else:
        toks = tokenize(question)
        rows = []
        for cid, text in con.execute(f"SELECT {id_col}, chunk_text FROM chunks"):
            low = text.lower()
            hit = sum(1 for t in toks if t in low)
            if hit:
                rows.append((cid, text, -float(hit)))
        rows.sort(key=lambda r: r[2])
        rows = rows[:k]
    return [{"pod": name, "chunk_id": str(cid), "chunk_sha256": sha256_text(text),
             "score": float(score), "text": text} for cid, text, score in rows]


def retrieve(conns, question, k):
    hits = []
    for name, con in conns.items():
        hits.extend(retrieve_pod(name, con, question, k))
    # bm25 is not strictly comparable across indexes; ties break by pod name then id for determinism
    hits.sort(key=lambda h: (h["score"], h["pod"], h["chunk_id"]))
    return hits[:k]


def tag(hit):
    return f"{hit['pod']}:{hit['chunk_id'][:8]}"


def build_prompt(question, hits, max_chars):
    if not hits:
        return NO_EVIDENCE_PROMPT.format(question=question)
    ev = "\n\n".join(f"[{tag(h)}] {h['text'][:max_chars]}" for h in hits)
    return PROMPT_TEMPLATE.format(evidence=ev, question=question)


def ollama_generate(url, model, prompt, seed, timeout):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "seed": seed}}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data.get("response", ""), data.get("eval_count")


def score(question, expected, hits, answer, docs_pod):
    """Simple, deterministic signals; identical for every condition."""
    qtoks = set(tokenize(question))
    ev_text = " ".join(h["text"].lower() for h in hits)
    cov = (sum(1 for t in qtoks if t in ev_text) / len(qtoks)) if qtoks else 0.0
    tags = {tag(h) for h in hits}
    cited = set(re.findall(r"\[([^\[\]:\s]+:[0-9A-Za-z]+)\]", answer or ""))
    valid = cited & tags
    out = {
        "n_hits": len(hits),
        "docs_hits": sum(1 for h in hits if h["pod"] == docs_pod),
        "evidence_term_coverage": round(cov, 4),
        "citations": len(cited),
        "valid_citation_rate": round(len(valid) / len(cited), 4) if cited else 0.0,
        "answer_chars": len(answer or ""),
        "refused_insufficient": bool(re.search(r"insufficient|not enough evidence|cannot answer",
                                               (answer or "").lower())),
    }
    if expected:
        low = (answer or "").lower()
        out["expected_term_recall"] = round(
            sum(1 for t in expected if t.lower() in low) / len(expected), 4)
    return out


COMPOSITE_KEYS = ("evidence_term_coverage", "valid_citation_rate", "expected_term_recall")


def composite(sig):
    has_answer = sig["answer_chars"] > 0
    vals = [sig[k] for k in COMPOSITE_KEYS if k in sig and (has_answer or k == "evidence_term_coverage")]
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def load_questions(args):
    qs = [{"question": q, "expected_terms": []} for q in (args.question or [])]
    if args.questions_file:
        for line in Path(args.questions_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("{"):
                o = json.loads(line)
                qs.append({"question": o["question"], "expected_terms": o.get("expected_terms", [])})
            else:
                qs.append({"question": line, "expected_terms": []})
    return qs


def main():
    ap = argparse.ArgumentParser(description="A/B test: with vs without GitHub how-to docs pod")
    ap.add_argument("--pod", action="append", required=True, metavar="NAME=PATH",
                    help="pod sqlite database (repeatable); must include the docs pod")
    ap.add_argument("--docs-pod", default="github-docs", help="name of the GitHub docs pod")
    ap.add_argument("--question", action="append", help="question (repeatable)")
    ap.add_argument("--questions-file", help="one question per line, or JSONL with expected_terms")
    ap.add_argument("--model", default="qwen2.5-coder:7b")
    ap.add_argument("--ollama-url", default="http://localhost:11434")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--max-chunk-chars", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--no-generate", action="store_true", help="retrieval signals only")
    ap.add_argument("--include-baseline", action="store_true", help="add C_no_retrieval condition")
    ap.add_argument("--out-dir", default="runs/ab")
    args = ap.parse_args()

    try:
        pods = dict(parse_pod_spec(s) for s in args.pod)
        if args.docs_pod not in pods:
            raise SafetyError(f"docs pod '{args.docs_pod}' not among --pod names {sorted(pods)}")
        questions = load_questions(args)
        if not questions:
            raise SafetyError("no questions supplied")
        out_dir = Path(args.out_dir)
        check_out_dir(out_dir, pods)
    except (SafetyError, OSError, ValueError, KeyError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2

    before = {n: sha256_file(p) for n, p in pods.items()}
    conns = {}
    try:
        conns = {n: open_readonly(p) for n, p in pods.items()}
        for con in conns.values():
            pod_columns(con)
        conditions = {
            "A_with_docs": dict(conns),
            "B_without_docs": {n: c for n, c in conns.items() if n != args.docs_pod},
        }
        if args.include_baseline:
            conditions["C_no_retrieval"] = {}
        if not conditions["B_without_docs"] and not args.include_baseline:
            raise SafetyError("need at least one non-docs pod for condition B (or --include-baseline)")

        config = {
            "model": args.model, "seed": args.seed, "temperature": 0, "top_k": args.top_k,
            "max_chunk_chars": args.max_chunk_chars, "no_generate": args.no_generate,
            "prompt_template_sha256": sha256_text(PROMPT_TEMPLATE),
            "no_evidence_prompt_sha256": sha256_text(NO_EVIDENCE_PROMPT),
            "pods": {n: {"path": str(p), "sha256_before": before[n]} for n, p in pods.items()},
            "conditions": {c: sorted(m) for c, m in conditions.items()},
            "docs_pod": args.docs_pod,
        }
        results = []
        for qi, item in enumerate(questions):
            q = item["question"]
            row = {"question": q, "question_sha256": sha256_text(q), "conditions": {}}
            for cname, cconns in conditions.items():
                hits = retrieve(cconns, q, args.top_k) if cconns else []
                prompt = build_prompt(q, hits, args.max_chunk_chars)
                answer, tokens, elapsed = "", None, None
                if not args.no_generate:
                    t0 = time.time()
                    answer, tokens = ollama_generate(args.ollama_url, args.model, prompt,
                                                     args.seed, args.timeout)
                    elapsed = round(time.time() - t0, 2)
                sig = score(q, item["expected_terms"], hits, answer, args.docs_pod)
                sig["composite"] = composite(sig)
                row["conditions"][cname] = {
                    "prompt_sha256": sha256_text(prompt),
                    "evidence": [{k: h[k] for k in ("pod", "chunk_id", "chunk_sha256", "score")}
                                 for h in hits],
                    "answer": answer, "answer_sha256": sha256_text(answer),
                    "eval_tokens": tokens, "elapsed_s": elapsed, "signals": sig,
                }
            a = row["conditions"]["A_with_docs"]["signals"]["composite"]
            b = row["conditions"].get("B_without_docs", {}).get("signals", {}).get("composite", 0.0)
            row["delta_composite_A_minus_B"] = round(a - b, 4)
            results.append(row)
    except SafetyError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2
    except Exception as e:  # network/sqlite errors: fail loudly, write nothing
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}), file=sys.stderr)
        return 2
    finally:
        for con in conns.values():
            con.close()

    after = {n: sha256_file(p) for n, p in pods.items()}
    changed = [n for n in pods if before[n] != after[n]]
    if changed:
        print(json.dumps({"error": "pod file changed during run", "pods": changed}), file=sys.stderr)
        return 2
    for n in pods:
        config["pods"][n]["sha256_after"] = after[n]

    deltas = [r["delta_composite_A_minus_B"] for r in results]
    summary = {
        "questions": len(results),
        "mean_delta_composite_A_minus_B": round(sum(deltas) / len(deltas), 4),
        "wins_A": sum(1 for d in deltas if d > 0),
        "wins_B": sum(1 for d in deltas if d < 0),
        "ties": sum(1 for d in deltas if d == 0),
    }
    report = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "config": config, "summary": summary, "results": results}
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"ab_github_docs_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"{'question':<48} {'cond':<16} hits docs cov   cite  comp")
    for r in results:
        for cname, c in r["conditions"].items():
            s = c["signals"]
            print(f"{r['question'][:47]:<48} {cname:<16} {s['n_hits']:<4} {s['docs_hits']:<4} "
                  f"{s['evidence_term_coverage']:<5} {s['valid_citation_rate']:<5} {s['composite']}")
    print(json.dumps({"summary": summary, "report": str(path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
