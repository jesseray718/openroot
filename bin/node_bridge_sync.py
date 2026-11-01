#!/usr/bin/env python3
"""Dry-run-first, receipt-sealed sync of OpenRoot blueprints to the hub."""

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "data" / "bridge_receipts.jsonl"
GENESIS_HASH = "0" * 64
SYNC_FILES = (
    Path("data/wealth_retention"),
    Path("bin/ewaste_manager.py"),
)


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries without shell evaluation."""
    if not path.exists():
        return
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key.strip()):
            raise ValueError(f"Invalid .env entry at {path}:{line_number}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _validate_target(host: str, user: str, remote_path: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", host):
        raise ValueError("OPENROOT_HUB_HOST must be a hostname or IP address")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", user):
        raise ValueError("OPENROOT_HUB_USER contains unsupported characters")
    if not re.fullmatch(r"(?:/|~/)[A-Za-z0-9._~+/-]*", remote_path):
        raise ValueError("OPENROOT_HUB_PATH must be an absolute or ~/ path")
    if ".." in Path(remote_path.replace("~/", "/home/user/")).parts:
        raise ValueError("OPENROOT_HUB_PATH must not traverse parent directories")


def _file_manifest(root: Path) -> list[dict[str, str]]:
    files = []
    for relative in SYNC_FILES:
        source = root / relative
        if source.is_symlink():
            raise ValueError(f"Refusing to sync symlinked source: {relative}")
        paths = sorted(source.rglob("*")) if source.is_dir() else [source]
        for path in paths:
            if path.is_symlink():
                raise ValueError(f"Refusing to sync symlinked source: {path.relative_to(root)}")
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                files.append({"path": path.relative_to(root).as_posix(), "sha256": digest})
    if not files:
        raise FileNotFoundError("No configured blueprint or logistics files were found")
    return files


def _read_receipts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid bridge receipt at {path}:{line_number}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Invalid bridge receipt at {path}:{line_number}")
            claimed_hash = record.get("hash")
            unsigned = {key: value for key, value in record.items() if key != "hash"}
            expected_hash = hashlib.sha256(
                json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            expected_previous = records[-1]["hash"] if records else GENESIS_HASH
            if claimed_hash != expected_hash or record.get("previous_hash") != expected_previous:
                raise ValueError(f"Broken bridge receipt chain at {path}:{line_number}")
            records.append(record)
    return records


def _append_receipt(path: Path, records: list[dict[str, Any]], event_id: str,
                    mode: str, target: str, files: list[dict[str, str]],
                    status: str, error: str | None = None) -> None:
    if any(
        record.get("event_id") == event_id and record.get("status") == status
        for record in records
    ):
        return
    record: dict[str, Any] = {
        "block_id": len(records),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "NODE_BRIDGE_SYNC",
        "event_id": event_id,
        "mode": mode,
        "target": target,
        "status": status,
        "files": files,
        "previous_hash": records[-1]["hash"] if records else GENESIS_HASH,
    }
    if error:
        record["error"] = error
    record["hash"] = hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def sync(root: Path, apply: bool = False) -> str:
    """Run rsync in dry-run mode unless explicitly asked to apply."""
    load_env_file(root / ".env")
    host = os.getenv("OPENROOT_HUB_HOST", "")
    user = os.getenv("OPENROOT_HUB_USER", "")
    remote_path = os.getenv("OPENROOT_HUB_PATH", "")
    _validate_target(host, user, remote_path)

    files = _file_manifest(root)
    mode = "apply" if apply else "dry-run"
    target = f"{user}@{host}:{remote_path.rstrip('/')}/"
    stable_event = json.dumps(
        {"mode": mode, "target": target, "files": files}, sort_keys=True, separators=(",", ":")
    )
    event_id = hashlib.sha256(stable_event.encode("utf-8")).hexdigest()
    arguments = [
        "rsync", "--archive", "--checksum", "--relative", "--itemize-changes",
    ]
    if not apply:
        arguments.append("--dry-run")
    # Keep rsync's relative paths rooted at the repository, without syncing
    # generated state or unrelated local files.
    arguments.extend(f"{root}/./{relative.as_posix()}" for relative in SYNC_FILES)
    arguments.append(target)

    receipts_file = root / RECEIPTS.relative_to(ROOT)
    lock_file = receipts_file.with_suffix(".lock")
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    with lock_file.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        records = _read_receipts(receipts_file)
        try:
            completed = subprocess.run(arguments, check=True, text=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            error = str(exc)
            _append_receipt(
                receipts_file, records, event_id, mode, target, files, "failed", error
            )
            raise RuntimeError(f"Bridge sync failed; failure receipt recorded: {error}") from exc
        _append_receipt(
            receipts_file, records, event_id, mode, target, files, "complete"
        )
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument(
        "--apply", action="store_true",
        help="perform the sync; without this flag, rsync is dry-run only",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.env_file:
            load_env_file(args.env_file)
        output = sync(root, apply=args.apply)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"[error] {exc}\n")
    print(output or "[bridge] No file changes required.")
    print(f"[bridge] {'Applied' if args.apply else 'Dry-run'} receipt sealed in data/bridge_receipts.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
