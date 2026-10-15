import hashlib
import json
import sqlite3
import time
from pathlib import Path

def build_manifest(pod_dir):
    pod_db = Path(pod_dir) / "pod.db"
    connection = sqlite3.connect(pod_db)

    manifest = {
        "schema_version": "openloom-pod-v1",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {
            "sources": connection.execute("SELECT count(*) FROM sources").fetchone()[0],
            "records": connection.execute("SELECT count(*) FROM records").fetchone()[0],
            "chunks": connection.execute("SELECT count(*) FROM chunks").fetchone()[0],
            "embeddings": connection.execute("SELECT count(*) FROM embeddings").fetchone()[0]
        },
        "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0]
    }
    connection.close()

    path = Path(pod_dir) / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest
