#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
OpenRoot local vector-index calibration.

A bounded, local-first SQLite vector store backed by Ollama embeddings.
It stores source text, provenance, model identity, vector dimensionality, and
the raw embedding payload. It is intentionally not a substitute for evidence
validation or human review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO / "data" / "embeddings.db"
DEFAULT_MODEL = "nomic-embed-text:latest"
DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/embeddings"
SCHEMA_VERSION = "2"
CALIBRATION_TEXT = "OpenRoot local evidence retrieval calibration."
CALIBRATION_SOURCE = "internal://vector-index-calibration"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS index_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_uri TEXT NOT NULL UNIQUE,
            content_sha256 TEXT NOT NULL,
            text_content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL UNIQUE,
            model TEXT NOT NULL,
            dimensions INTEGER NOT NULL CHECK(dimensions > 0),
            vector_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model);
        """
    )
    stamp = now_utc()
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "database_role": "OpenRoot local provenance-preserving vector index",
        "last_initialized_at": stamp,
    }
    conn.executemany(
        """
        INSERT INTO index_metadata(key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """,
        [(key, value, stamp) for key, value in metadata.items()],
    )
    conn.commit()


def request_embedding(text: str, model: str, endpoint: str) -> list[float]:
    payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            decoded: dict[str, Any] = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama embedding request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama returned invalid JSON: {exc}") from exc

    vector = decoded.get("embedding")
    if not isinstance(vector, list) or not vector:
        raise RuntimeError(f"Ollama response lacks a nonempty embedding: keys={sorted(decoded)}")
    if not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in vector):
        raise RuntimeError("Ollama embedding contains non-finite or non-numeric values")
    return [float(value) for value in vector]


def upsert_document_embedding(
    conn: sqlite3.Connection,
    source_uri: str,
    text: str,
    vector: list[float],
    model: str,
) -> tuple[int, int]:
    stamp = now_utc()
    digest = sha256_text(text)
    conn.execute(
        """
        INSERT INTO documents(source_uri, content_sha256, text_content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(source_uri) DO UPDATE SET
            content_sha256=excluded.content_sha256,
            text_content=excluded.text_content,
            updated_at=excluded.updated_at
        """,
        (source_uri, digest, text, stamp, stamp),
    )
    document_id = int(
        conn.execute("SELECT id FROM documents WHERE source_uri=?", (source_uri,)).fetchone()["id"]
    )
    conn.execute(
        """
        INSERT INTO embeddings(document_id, model, dimensions, vector_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(document_id) DO UPDATE SET
            model=excluded.model,
            dimensions=excluded.dimensions,
            vector_json=excluded.vector_json,
            created_at=excluded.created_at
        """,
        (document_id, model, len(vector), json.dumps(vector, separators=(",", ":")), stamp),
    )
    embedding_id = int(
        conn.execute("SELECT id FROM embeddings WHERE document_id=?", (document_id,)).fetchone()["id"]
    )
    conn.commit()
    return document_id, embedding_id


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError(f"dimension mismatch: query={len(left)} candidate={len(right)}")
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        raise ValueError("zero-norm vector cannot be compared")
    return numerator / (left_norm * right_norm)


def search(conn: sqlite3.Connection, query_vector: list[float], model: str, limit: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT d.id AS document_id, d.source_uri, d.content_sha256, d.text_content,
               e.id AS embedding_id, e.model, e.dimensions, e.vector_json, e.created_at
        FROM embeddings AS e
        JOIN documents AS d ON d.id=e.document_id
        WHERE e.model=? AND e.dimensions=?
        """,
        (model, len(query_vector)),
    ).fetchall()
    results: list[dict[str, Any]] = []
    for row in rows:
        vector = json.loads(row["vector_json"])
        score = cosine_similarity(query_vector, vector)
        results.append(
            {
                "document_id": row["document_id"],
                "embedding_id": row["embedding_id"],
                "source_uri": row["source_uri"],
                "content_sha256": row["content_sha256"],
                "model": row["model"],
                "dimensions": row["dimensions"],
                "similarity": score,
                "excerpt": row["text_content"][:240],
                "created_at": row["created_at"],
            }
        )
    return sorted(results, key=lambda item: item["similarity"], reverse=True)[:limit]


def require_local_model(model: str, endpoint: str) -> None:
    base = endpoint.rsplit("/api/", 1)[0] + "/api/tags"
    request = urllib.request.Request(base, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            decoded: dict[str, Any] = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama tag check failed: {exc}") from exc
    names = {item.get("name") for item in decoded.get("models", []) if isinstance(item, dict)}
    if model not in names:
        raise RuntimeError(f"required local model absent: {model}; available={sorted(name for name in names if name)}")


def calibrate(db_path: Path, model: str, endpoint: str) -> int:
    require_local_model(model, endpoint)
    vector = request_embedding(CALIBRATION_TEXT, model, endpoint)
    conn = connect(db_path)
    try:
        initialize(conn)
        document_id, embedding_id = upsert_document_embedding(
            conn, CALIBRATION_SOURCE, CALIBRATION_TEXT, vector, model
        )
        rows = search(conn, vector, model, limit=1)
        if len(rows) != 1:
            raise RuntimeError(f"expected exactly one calibration search result, got {len(rows)}")
        result = rows[0]
        if result["source_uri"] != CALIBRATION_SOURCE:
            raise RuntimeError(f"unexpected calibration source: {result['source_uri']}")
        if result["dimensions"] != len(vector):
            raise RuntimeError(
                f"stored dimension mismatch: stored={result['dimensions']} actual={len(vector)}"
            )
        if result["similarity"] < 0.999999:
            raise RuntimeError(f"self-retrieval similarity too low: {result['similarity']:.9f}")
        stamp = now_utc()
        conn.execute(
            """
            INSERT INTO index_metadata(key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            ("last_calibration", json.dumps({
                "at": stamp,
                "model": model,
                "dimensions": len(vector),
                "document_id": document_id,
                "embedding_id": embedding_id,
                "source_uri": CALIBRATION_SOURCE,
                "similarity": result["similarity"],
            }, sort_keys=True), stamp),
        )
        conn.commit()
        print(f"[banked] Vector database initialized: {db_path}")
        print(f"[banked] model={model}")
        print(f"[banked] dimensions={len(vector)}")
        print(f"[banked] calibration_document_id={document_id}")
        print(f"[banked] calibration_embedding_id={embedding_id}")
        print(f"[banked] calibration_source={CALIBRATION_SOURCE}")
        print(f"[banked] self_retrieval_similarity={result['similarity']:.9f}")
        print("[banked] vector calibration PASS")
        return 0
    finally:
        conn.close()


def run_query(db_path: Path, model: str, endpoint: str, query: str, limit: int) -> int:
    if not db_path.is_file():
        raise RuntimeError(f"index database does not exist: {db_path}; run --light-init first")
    vector = request_embedding(query, model, endpoint)
    conn = connect(db_path)
    try:
        results = search(conn, vector, model, limit)
    finally:
        conn.close()
    print(json.dumps({"query": query, "model": model, "results": results}, indent=2, sort_keys=True))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenRoot local provenance-preserving vector index"
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--light-init", action="store_true", help="initialize and calibrate the local index")
    parser.add_argument("--query", help="embed and search a calibrated local index")
    parser.add_argument("--limit", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.light_init:
        return calibrate(args.db.expanduser().resolve(), args.model, args.endpoint)
    if args.query:
        if args.limit < 1:
            raise RuntimeError("--limit must be at least 1")
        return run_query(args.db.expanduser().resolve(), args.model, args.endpoint, args.query, args.limit)
    raise RuntimeError("choose --light-init or --query")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, OSError, sqlite3.Error) as exc:
        print(f"[held] {exc}", file=sys.stderr)
        raise SystemExit(1)
