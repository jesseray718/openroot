#!/usr/bin/env python3
"""Search historical OpenRoot pod records and optionally answer locally."""

import argparse
import contextlib
import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(os.environ.get(
    "OPENROOT_ROOT", Path(__file__).resolve().parents[1]
)).resolve()
DB_PATH = Path(os.environ.get(
    "OPENROOT_POD_DB", ROOT / "data/thermodynamics/openroot_interactive_pods.db"
))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lumo_lib


def fts_query(text):
    terms = re.findall(r"[\w-]+", text, flags=re.UNICODE)
    if not terms:
        raise ValueError("Query must contain at least one searchable word.")
    return " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)


def search_pods(keyword, db_path=DB_PATH, limit=5):
    """Return matching records with stable IDs and their chain seal, if present."""
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(f"Database pod not found: {db_path}")
    sql = """
        SELECT pod_fts.block_height, pod_fts.timestamp, pod_fts.prompt_text,
               pod_fts.response_text, pod_fts.dossier_tags, chain.merkle_root
        FROM pod_fts
        LEFT JOIN interactive_chain AS chain
          ON chain.block_height = pod_fts.block_height
        WHERE pod_fts MATCH ?
        ORDER BY rank, pod_fts.block_height
        LIMIT ?
    """
    with contextlib.closing(sqlite3.connect(
        db_path.resolve().as_uri() + "?mode=ro", uri=True
    )) as conn:
        rows = conn.execute(sql, (fts_query(keyword), limit)).fetchall()

    records = []
    for height, timestamp, prompt, response, tags, merkle_root in rows:
        evidence = {
            "block_height": height,
            "timestamp": timestamp,
            "prompt": prompt,
            "response": response,
            "tags": tags,
            "merkle_root": merkle_root,
        }
        evidence_id = hashlib.sha256(
            json.dumps(evidence, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        records.append({"evidence_id": evidence_id, **evidence})
    return records


def database_sha256(db_path):
    wal = Path(str(db_path) + "-wal")
    if wal.exists() and wal.stat().st_size:
        raise RuntimeError(
            "Pod database has an active WAL; use a stable SQLite backup for comparison."
        )
    digest = hashlib.sha256()
    with Path(db_path).open("rb") as database:
        for block in iter(lambda: database.read(1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def answer_pods(query, db_path=DB_PATH, model=None, limit=3):
    """Answer only from local pod hits; missing evidence or model errors stay errors."""
    db_hash = database_sha256(db_path)
    records = search_pods(query, db_path=db_path, limit=limit)
    if database_sha256(db_path) != db_hash:
        raise RuntimeError("Pod database changed during retrieval; retry with a stable backup.")
    if not records:
        raise LookupError("No matching pod evidence; no answer was generated.")

    model = model or os.environ.get(
        "OPENROOT_QUERY_MODEL", lumo_lib.MODEL_BUILDER
    )
    passages = []
    for record in records:
        passages.append(
            f"[block {record['block_height']} | evidence {record['evidence_id']}]\n"
            f"Prompt: {record['prompt'][:1200]}\n"
            f"Response: {record['response'][:1800]}\n"
            f"Tags: {record['tags'] or ''}"
        )
    prompt = (
        "Answer the question using only the historical pod evidence below. "
        "Cite the block number for each factual claim. If the evidence does not "
        "answer the question, say that explicitly.\n\n"
        f"QUESTION:\n{query}\n\nEVIDENCE:\n" + "\n\n".join(passages)
    )
    answer = lumo_lib.ollama_generate_local(prompt, model=model)
    if not answer.strip():
        raise RuntimeError("The local model returned an empty answer.")
    if database_sha256(db_path) != db_hash:
        raise RuntimeError("Pod database changed during generation; retry with a stable backup.")
    return {
        "query": query,
        "database_sha256": db_hash,
        "model": model,
        "answer": answer,
        "evidence": records,
        "evidence_ids": [record["evidence_id"] for record in records],
    }


def print_records(records, keyword):
    print(f"[*] Search results for keyword: {keyword!r} (Found: {len(records)} matches)")
    for record in records:
        print("-" * 60)
        print(f"Block #{record['block_height']} | Timestamp: {record['timestamp']}")
        print(f"  Evidence ID: {record['evidence_id']}")
        print(f"  Merkle root: {record['merkle_root'] or 'not linked'}")
        print(f"  Tags: {record['tags']}")
        print(f"  Prompt: {record['prompt']}")
        print(f"  Response: {record['response']}")
    if records:
        print("-" * 60)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        argv = ["progressive-loop"]
    command = argv.pop(0) if argv[:1] and argv[0] in ("search", "ask") else "search"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="words to search for")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--model", default=None, help="local Ollama model for ask")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)
    query = " ".join(args.query)
    if args.limit < 1:
        parser.error("--limit must be positive")

    if command == "search":
        db_hash = database_sha256(args.db)
        records = search_pods(query, db_path=args.db, limit=args.limit)
        if database_sha256(args.db) != db_hash:
            raise RuntimeError("Pod database changed during retrieval; retry with a stable backup.")
        if args.json:
            print(json.dumps({
                "query": query,
                "database_sha256": db_hash,
                "evidence": records,
            }, ensure_ascii=False))
        else:
            print(f"[pod DB SHA-256: {db_hash}]")
            print_records(records, query)
        return 0

    result = answer_pods(query, db_path=args.db, model=args.model, limit=args.limit)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"[pod DB SHA-256: {result['database_sha256']}]")
        print(f"[local model: {result['model']}]")
        print(f"[evidence IDs: {', '.join(result['evidence_ids'])}]")
        print(result["answer"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, LookupError, OSError, RuntimeError, sqlite3.Error, ValueError) as exc:
        print(f"[held] {exc}", file=sys.stderr)
        raise SystemExit(1)
