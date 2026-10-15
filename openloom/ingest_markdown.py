import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from .chunking import chunk_text
from .schema import init_pod

def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()

def ingest_markdown(pod_dir, source_path, batch_id):
    pod_db = Path(pod_dir) / "pod.db"
    init_pod(pod_db)
    connection = sqlite3.connect(pod_db)
    connection.execute("PRAGMA foreign_keys = ON")

    path = Path(source_path).resolve()
    raw = path.read_bytes()
    source_hash = sha256_bytes(raw)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    connection.execute(
        "INSERT OR IGNORE INTO sources "
        "(sha256, source_uri, source_class, mime_type, size_bytes, "
        "mtime_epoch, captured_at, ingest_batch_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            source_hash, path.as_uri(), "markdown", "text/markdown",
            len(raw), int(path.stat().st_mtime), now, batch_id
        )
    )

    text = raw.decode("utf-8", errors="replace")
    record_hash = sha256_bytes(
        json.dumps({"path": str(path)}, sort_keys=True).encode()
    )

    connection.execute(
        "INSERT OR IGNORE INTO records "
        "(record_sha256, source_sha256, record_type, title, canonical_json, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            record_hash, source_hash, "document", path.name,
            json.dumps({"path": str(path)}), now
        )
    )

    count = 0
    for index, chunk in enumerate(chunk_text(text)):
        chunk_hash = sha256_bytes(chunk.encode())
        connection.execute(
            "INSERT OR IGNORE INTO chunks "
            "(chunk_sha256, source_sha256, record_sha256, chunk_index, "
            "chunk_text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (chunk_hash, source_hash, record_hash, index, chunk, now)
        )
        count += 1

    connection.commit()
    connection.close()
    return {"source_sha256": source_hash, "chunks": count}
