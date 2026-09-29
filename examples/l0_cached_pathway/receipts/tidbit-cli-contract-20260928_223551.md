# Turing Tidbit CLI Contract

Timestamp: 2026-09-28T22:35:51-05:00
Tidbit kernel: /home/jesse/openroot/bin/turing_tidbits_v1.py

## ingest-json help

```
usage: turing_tidbits_v1.py ingest-json [-h] --label LABEL --type TYPE
                                        [--license LICENSE] [--author AUTHOR]
                                        [--source-uri SOURCE_URI] [--tag TAG]
                                        [--relation RELATION]
                                        json

positional arguments:
  json

options:
  -h, --help            show this help message and exit
  --label LABEL
  --type TYPE
  --license LICENSE
  --author AUTHOR
  --source-uri SOURCE_URI
  --tag TAG
  --relation RELATION
```

## ingest-file help

```
usage: turing_tidbits_v1.py ingest-file [-h] --label LABEL --type TYPE
                                        [--license LICENSE] [--author AUTHOR]
                                        [--source-uri SOURCE_URI] [--tag TAG]
                                        [--relation RELATION] [--mime MIME]
                                        path

positional arguments:
  path

options:
  -h, --help            show this help message and exit
  --label LABEL
  --type TYPE
  --license LICENSE
  --author AUTHOR
  --source-uri SOURCE_URI
  --tag TAG
  --relation RELATION
  --mime MIME
```

## verify help

```
usage: turing_tidbits_v1.py verify [-h] [sha256]

positional arguments:
  sha256

options:
  -h, --help  show this help message and exit
```

## list help

```
usage: turing_tidbits_v1.py list [-h]

options:
  -h, --help  show this help message and exit
```

## show help

```
usage: turing_tidbits_v1.py show [-h] sha256

positional arguments:
  sha256

options:
  -h, --help  show this help message and exit
```

## export-manifest help

```
usage: turing_tidbits_v1.py export-manifest [-h]

options:
  -h, --help  show this help message and exit
```

## parser construction

```python
189:def parse_relation(value: str) -> dict[str, str]:
200:def ingest_file(args: argparse.Namespace) -> int:
214:        relations=[parse_relation(item) for item in args.relation],
221:def ingest_json(args: argparse.Namespace) -> int:
235:        relations=[parse_relation(item) for item in args.relation],
327:def main() -> int:
332:        command.add_argument("--label", required=True)
333:        command.add_argument("--type", required=True)
334:        command.add_argument("--license", default="NOASSERTION")
335:        command.add_argument("--author", default="")
336:        command.add_argument("--source-uri", default="")
337:        command.add_argument("--tag", action="append", default=[])
338:        command.add_argument("--relation", action="append", default=[])
340:    file_parser = sub.add_parser("ingest-file")
341:    file_parser.add_argument("path")
343:    file_parser.add_argument("--mime", default="")
344:    file_parser.set_defaults(func=ingest_file)
346:    json_parser = sub.add_parser("ingest-json")
347:    json_parser.add_argument("json")
349:    json_parser.set_defaults(func=ingest_json)
351:    verify_parser = sub.add_parser("verify")
352:    verify_parser.add_argument("sha256", nargs="?")
353:    verify_parser.set_defaults(func=verify)
355:    show_parser = sub.add_parser("show")
356:    show_parser.add_argument("sha256")
357:    show_parser.set_defaults(func=show)
359:    list_parser = sub.add_parser("list")
360:    list_parser.set_defaults(func=listing)
362:    export_parser = sub.add_parser("export-manifest")
363:    export_parser.set_defaults(func=export_manifest)
369:if __name__ == "__main__":
```

## relation and ingest source

```python
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
```
