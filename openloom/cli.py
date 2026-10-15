import argparse
import json
import sqlite3
from pathlib import Path
from .schema import init_pod
from .ingest_markdown import ingest_markdown
from .ingest_csv import ingest_csv
from .manifest import build_manifest

def pod_db(pod):
    return Path(pod) / "pod.db"

def verify(pod):
    database = pod_db(pod)
    connection = sqlite3.connect(database)
    checks = {
        "sqlite_integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
        "sources": connection.execute("SELECT count(*) FROM sources").fetchone()[0],
        "chunks": connection.execute("SELECT count(*) FROM chunks").fetchone()[0],
        "embeddings": connection.execute("SELECT count(*) FROM embeddings").fetchone()[0],
        "fts_rows": connection.execute("SELECT count(*) FROM chunks_fts").fetchone()[0],
        "chunks_without_source": connection.execute(
            "SELECT count(*) FROM chunks WHERE source_sha256 NOT IN "
            "(SELECT sha256 FROM sources)"
        ).fetchone()[0],
        "embeddings_without_chunk": connection.execute(
            "SELECT count(*) FROM embeddings WHERE sha256 NOT IN "
            "(SELECT chunk_sha256 FROM chunks)"
        ).fetchone()[0]
    }
    connection.close()
    checks["passed"] = (
        checks["sqlite_integrity"] == "ok"
        and checks["chunks_without_source"] == 0
        and checks["embeddings_without_chunk"] == 0
        and checks["fts_rows"] == checks["chunks"]
    )
    print(json.dumps(checks, indent=2, sort_keys=True))
    return 0 if checks["passed"] else 1

def main():
    parser = argparse.ArgumentParser(prog="openloom")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--pod", required=True)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--pod", required=True)
    ingest_parser.add_argument("--source", required=True)
    ingest_parser.add_argument("--type", default="markdown")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--pod", required=True)

    args = parser.parse_args()

    if args.command == "init":
        Path(args.pod).mkdir(parents=True, exist_ok=True)
        init_pod(pod_db(args.pod))
        print(json.dumps({"status": "POD_INITIALIZED", "pod": args.pod}))
        return 0

    if args.command == "ingest":
        source = Path(args.source)
        if source.suffix.lower() in {".md", ".markdown", ".txt"}:
            result = ingest_markdown(args.pod, source, "cli-ingest-v1")
        elif source.suffix.lower() in {".csv", ".jsonl"}:
            result = ingest_csv(args.pod, source, "cli-ingest-v1")
        else:
            raise SystemExit(f"Unsupported source type: {source}")
        build_manifest(args.pod)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "verify":
        return verify(args.pod)

if __name__ == "__main__":
    raise SystemExit(main())
