#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
PY="/home/jesse/openroot/bin/turing_tidbits_v1.py"
ROOT="/home/jesse/openroot/data/turing_tidbits"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

cd "$REPO"
mkdir -p "$ROOT"/{objects,metadata,events,exports}

if [ -f "$PY" ]; then
    BACKUP="/home/jesse/openroot/bin/turing_tidbits_v1.py.pre_build.${STAMP}.bak"
    cp --preserve=mode,timestamps "$PY" "$BACKUP"
    test -s "$BACKUP"
    echo "[banked] existing kernel backup=$BACKUP"
fi

cat <<'PY' >"$PY"
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
[TURINGTIDBITSV1] Portable content-addressed knowledge kernel.

The tidbit format is intentionally local-first and transport-neutral:
- object bytes are addressed by SHA-256;
- metadata is canonical JSON and separately hashed;
- provenance, licensing, relations, and verification travel with the object;
- any node can rebuild its index from tidbit metadata and object files.

No delete command is implemented. Source files are read, never moved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path("/home/jesse/openroot")
ROOT = REPO / "data" / "turing_tidbits"
OBJECTS = ROOT / "objects"
METADATA = ROOT / "metadata"
EVENTS = ROOT / "events"
EXPORTS = ROOT / "exports"
LEDGER = EVENTS / "events.jsonl"
SCHEMA = "openroot.turing_tidbit/v1"
TAG = "[TURINGTIDBITSV1]"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_mkdirs() -> None:
    for path in (OBJECTS, METADATA, EVENTS, EXPORTS):
        path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_path(content_sha256: str) -> Path:
    return METADATA / f"{content_sha256}.json"


def object_path(content_sha256: str) -> Path:
    return OBJECTS / content_sha256[:2] / content_sha256[2:4] / content_sha256


def append_event(event: dict[str, Any]) -> str:
    safe_mkdirs()
    body = dict(event)
    body["schema"] = SCHEMA
    body["event_at"] = utc_now()
    encoded = canonical_json(body)
    event_sha256 = sha256_bytes(encoded)
    record = {
        "event_sha256": event_sha256,
        "event": body,
    }
    with LEDGER.open("ab") as handle:
        handle.write(canonical_json(record))
    return event_sha256


def source_descriptor(path: Path | None, source_uri: str | None) -> dict[str, Any]:
    if path is None:
        return {
            "kind": "inline_json",
            "source_uri": source_uri or "",
            "observed_path": "",
            "observed_mtime_ns": None,
            "observed_size": None,
        }
    stat = path.stat()
    return {
        "kind": "file",
        "source_uri": source_uri or "",
        "observed_path": str(path.resolve()),
        "observed_mtime_ns": stat.st_mtime_ns,
        "observed_size": stat.st_size,
    }


def store_bytes(
    payload: bytes,
    *,
    label: str,
    tidbit_type: str,
    source: dict[str, Any],
    license_id: str,
    author: str,
    relations: list[dict[str, str]],
    tags: list[str],
    mime: str,
) -> tuple[str, bool]:
    safe_mkdirs()
    content_sha256 = sha256_bytes(payload)
    target = object_path(content_sha256)
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    if existed:
        if sha256_file(target) != content_sha256:
            raise RuntimeError(f"hash collision or corrupted object at {target}")
    else:
        tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
        tmp.write_bytes(payload)
        os.replace(tmp, target)
    metadata = {
        "schema": SCHEMA,
        "content_sha256": content_sha256,
        "content_bytes": len(payload),
        "content_mime": mime or "application/octet-stream",
        "label": label,
        "tidbit_type": tidbit_type,
        "license_id": license_id,
        "author": author,
        "source": source,
        "relations": sorted(
            relations,
            key=lambda item: (
                item.get("relation", ""),
                item.get("target_sha256", ""),
                item.get("note", ""),
            ),
        ),
        "tags": sorted(set(tags)),
        "object_relpath": str(target.relative_to(ROOT)),
        "created_at": utc_now(),
    }
    stable = dict(metadata)
    stable.pop("created_at")
    metadata["metadata_sha256"] = sha256_bytes(canonical_json(stable))
    mpath = metadata_path(content_sha256)
    if mpath.exists():
        existing = read_json(mpath)
        if existing.get("content_sha256") != content_sha256:
            raise RuntimeError(f"metadata content mismatch at {mpath}")
        metadata = existing
    else:
        tmp = mpath.with_name(f".{mpath.name}.{os.getpid()}.tmp")
        tmp.write_bytes(canonical_json(metadata))
        os.replace(tmp, mpath)
    event_sha256 = append_event(
        {
            "event_type": "ingest",
            "content_sha256": content_sha256,
            "metadata_sha256": metadata["metadata_sha256"],
            "deduplicated": existed,
            "label": metadata["label"],
            "tidbit_type": metadata["tidbit_type"],
        }
    )
    print(f"[banked] content_sha256={content_sha256}")
    print(f"[banked] metadata_sha256={metadata['metadata_sha256']}")
    print(f"[banked] event_sha256={event_sha256}")
    print(f"[banked] deduplicated={'yes' if existed else 'no'}")
    return content_sha256, existed


def parse_relation(value: str) -> dict[str, str]:
    parts = value.split(":", 2)
    if len(parts) < 2:
        raise ValueError("relation must be RELATION:TARGET_SHA256[:NOTE]")
    return {
        "relation": parts[0],
        "target_sha256": parts[1],
        "note": parts[2] if len(parts) == 3 else "",
    }


def ingest_file(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        print(f"[held] input is not a readable file: {path}")
        return 0
    payload = path.read_bytes()
    mime = args.mime or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    store_bytes(
        payload,
        label=args.label or path.name,
        tidbit_type=args.type,
        source=source_descriptor(path, args.source_uri),
        license_id=args.license,
        author=args.author,
        relations=[parse_relation(item) for item in args.relation],
        tags=args.tag,
        mime=mime,
    )
    return 0


def ingest_json(args: argparse.Namespace) -> int:
    try:
        payload_object = json.loads(args.json)
    except json.JSONDecodeError as exc:
        print(f"[held] invalid JSON payload: {exc}")
        return 0
    payload = canonical_json(payload_object)
    store_bytes(
        payload,
        label=args.label,
        tidbit_type=args.type,
        source=source_descriptor(None, args.source_uri),
        license_id=args.license,
        author=args.author,
        relations=[parse_relation(item) for item in args.relation],
        tags=args.tag,
        mime="application/json",
    )
    return 0


def verify_one(content_sha256: str) -> bool:
    mpath = metadata_path(content_sha256)
    opath = object_path(content_sha256)
    if not mpath.is_file() or not opath.is_file():
        print(f"[held] missing metadata or object for {content_sha256}")
        return False
    metadata = read_json(mpath)
    content_ok = sha256_file(opath) == content_sha256
    stable = dict(metadata)
    stored_metadata_hash = stable.pop("metadata_sha256", "")
    stable.pop("created_at", None)
    metadata_ok = sha256_bytes(canonical_json(stable)) == stored_metadata_hash
    relpath_ok = metadata.get("object_relpath") == str(opath.relative_to(ROOT))
    if content_ok and metadata_ok and relpath_ok:
        print(f"[banked] verified={content_sha256}")
        return True
    print(
        f"[held] verification failed={content_sha256} "
        f"content_ok={content_ok} metadata_ok={metadata_ok} relpath_ok={relpath_ok}"
    )
    return False


def verify(args: argparse.Namespace) -> int:
    safe_mkdirs()
    if args.sha256:
        verify_one(args.sha256)
        return 0
    ids = sorted(path.stem for path in METADATA.glob("*.json"))
    good = sum(1 for item in ids if verify_one(item))
    print(f"[banked] verify_total={len(ids)}")
    print(f"[banked] verify_good={good}")
    if good != len(ids):
        print("[held] one or more tidbits failed verification")
    return 0


def show(args: argparse.Namespace) -> int:
    path = metadata_path(args.sha256)
    if not path.is_file():
        print(f"[held] tidbit metadata missing: {args.sha256}")
        return 0
    print(json.dumps(read_json(path), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def listing(_: argparse.Namespace) -> int:
    safe_mkdirs()
    rows = []
    for path in sorted(METADATA.glob("*.json")):
        metadata = read_json(path)
        rows.append(
            {
                "sha256": metadata["content_sha256"],
                "type": metadata["tidbit_type"],
                "label": metadata["label"],
                "bytes": metadata["content_bytes"],
                "license": metadata["license_id"],
                "tags": metadata["tags"],
            }
        )
    for row in rows:
        print(json.dumps(row, ensure_ascii=False, sort_keys=True))
    print(f"[banked] tidbits={len(rows)}")
    return 0


def export_manifest(_: argparse.Namespace) -> int:
    safe_mkdirs()
    rows = []
    for path in sorted(METADATA.glob("*.json")):
        rows.append(read_json(path))
    manifest = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "count": len(rows),
        "tidbits": rows,
    }
    out = EXPORTS / "tidbits_manifest.json"
    out.write_bytes(canonical_json(manifest))
    print(f"[banked] manifest={out}")
    print(f"[banked] manifest_sha256={sha256_file(out)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="turing_tidbits_v1.py")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--label", required=True)
        command.add_argument("--type", required=True)
        command.add_argument("--license", default="NOASSERTION")
        command.add_argument("--author", default="")
        command.add_argument("--source-uri", default="")
        command.add_argument("--tag", action="append", default=[])
        command.add_argument("--relation", action="append", default=[])

    file_parser = sub.add_parser("ingest-file")
    file_parser.add_argument("path")
    common(file_parser)
    file_parser.add_argument("--mime", default="")
    file_parser.set_defaults(func=ingest_file)

    json_parser = sub.add_parser("ingest-json")
    json_parser.add_argument("json")
    common(json_parser)
    json_parser.set_defaults(func=ingest_json)

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("sha256", nargs="?")
    verify_parser.set_defaults(func=verify)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("sha256")
    show_parser.set_defaults(func=show)

    list_parser = sub.add_parser("list")
    list_parser.set_defaults(func=listing)

    export_parser = sub.add_parser("export-manifest")
    export_parser.set_defaults(func=export_manifest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
PY

chmod 0755 "$PY"
python3 -m py_compile "$PY"
grep -Fq "SPDX-License-Identifier: GPL-3.0-only" "$PY"
grep -Fq "[TURINGTIDBITSV1]" "$PY"

python3 "$PY" ingest-file \
    "/home/jesse/openroot/bin/a1_core_v1.py" \
    --label "A1 Core V1" \
    --type "source_code" \
    --license "GPL-3.0-only" \
    --author "Jesse Ray McMillen" \
    --source-uri "file:///home/jesse/openroot/bin/a1_core_v1.py" \
    --tag "openroot" \
    --tag "ledger" \
    --tag "local-first"

python3 "$PY" ingest-file \
    "/home/jesse/openroot/bin/compost_v1.py" \
    --label "Compost V1" \
    --type "source_code" \
    --license "GPL-3.0-only" \
    --author "Jesse Ray McMillen" \
    --source-uri "file:///home/jesse/openroot/bin/compost_v1.py" \
    --tag "openroot" \
    --tag "waste-stream" \
    --tag "non-destructive"

python3 "$PY" ingest-json \
    '{"kind":"sensor_or_sync_contract","rule":"same content SHA-256 yields same tidbit identifier on every node","transport":"filesystem|git|rsync|syncthing|mesh|removable_media","human_gate":"required for destructive or public actions"}' \
    --label "Portable node contract" \
    --type "system_contract" \
    --license "GPL-3.0-only" \
    --author "Jesse Ray McMillen" \
    --tag "portable" \
    --tag "sensor" \
    --tag "sync" \
    --tag "provenance"

python3 "$PY" verify
python3 "$PY" export-manifest
python3 "$PY" list

test -s "$ROOT/exports/tidbits_manifest.json"
grep -Fq "openroot.turing_tidbit/v1" "$ROOT/exports/tidbits_manifest.json"
grep -Fq "Portable node contract" "$ROOT/exports/tidbits_manifest.json"

echo "[banked] portable Turing tidbit kernel verified"
echo "[held] no source files were moved, deleted, committed, or pushed"
echo "# [TURINGTIDBITSBUILDV1]"
echo "[exit=0]"
