"""Append-only correction holds for exact query-pathway identities."""
import argparse
import hashlib
import json
import os
from pathlib import Path

class CorrectionHeld(Exception):
    pass

def _hash(record):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in record.items() if k != "hash"},
        sort_keys=True, ensure_ascii=True,
    ).encode()).hexdigest()

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CorrectionHeld("duplicate JSON key")
        result[key] = value
    return result

def _constant(value):
    raise CorrectionHeld("nonstandard JSON constant")

def _hex(value):
    return (
        isinstance(value, str) and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )

def _read(path, allow_absent=False):
    if path.is_symlink():
        raise CorrectionHeld("ledger symlink refused")
    if not path.exists():
        if allow_absent:
            return []
        raise CorrectionHeld("required ledger missing")
    if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        raise CorrectionHeld("ledger unavailable or exceeds budget")
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise CorrectionHeld("incomplete ledger final line")
    rows = []
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            raise CorrectionHeld("blank ledger line")
        obj = json.loads(
            line, object_pairs_hook=_pairs,
            parse_constant=_constant,
        )
        if not isinstance(obj, dict):
            raise CorrectionHeld("non-object ledger record")
        rows.append(obj)
    return rows

def _corrections(root):
    path = Path(root) / "ledger/query_corrections.jsonl"
    rows = _read(path, allow_absent=True)
    previous = None
    for seq, row in enumerate(rows, 1):
        if (
            type(row.get("seq")) is not int
            or row["seq"] != seq
            or row.get("prev") != previous
            or row.get("hash") != _hash(row)
            or row.get("action") != "BLOCK"
            or not _hex(row.get("pathway_hash"))
            or not _hex(row.get("question_hash"))
            or not isinstance(row.get("reason"), str)
            or not row["reason"].strip()
        ):
            raise CorrectionHeld("correction ledger validation failed")
        previous = row["hash"]
    return rows

def check_corrections(root, pathway):
    for row in _corrections(root):
        if row["pathway_hash"] == pathway.get("ph"):
            if row["question_hash"] != pathway.get("question_hash"):
                raise CorrectionHeld("correction target identity mismatch")
            raise CorrectionHeld(
                "cached pathway blocked by correction " + row["hash"]
            )

def block(root, pathway_hash, reason):
    import datetime
    import fcntl
    root = Path(root).resolve(strict=True)
    if not _hex(pathway_hash) or not reason.strip():
        raise CorrectionHeld("exact pathway hash and reason required")
    if len(reason) > 8000:
        raise CorrectionHeld("correction reason exceeds budget")

    # This lock coordinates this command, not unrelated ledger writers.
    lock = root / "ledger/query_corrections.lock"
    fd = os.open(
        lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(fd, "r+") as lock_stream:
        fcntl.flock(lock_stream, fcntl.LOCK_EX)
        pathways = _read(root / "ledger/query_pathways.jsonl")
        previous = None
        targets = []
        for row in pathways:
            expected = hashlib.blake2b(json.dumps(
                {k: v for k, v in row.items() if k != "ph"},
                sort_keys=True,
            ).encode(), digest_size=32).hexdigest()
            if row.get("prev") != previous or row.get("ph") != expected:
                raise CorrectionHeld("query ledger validation failed")
            previous = expected
            if row.get("ph") == pathway_hash:
                targets.append(row)
        if len(targets) != 1:
            raise CorrectionHeld("target pathway not uniquely resolved")
        target = targets[0]
        if not _hex(target.get("question_hash")):
            raise CorrectionHeld("target question hash invalid")

        corrections = _corrections(root)
        for row in corrections:
            if row["pathway_hash"] == pathway_hash:
                return {
                    "status": "ALREADY_BLOCKED",
                    "correction_hash": row["hash"],
                    "pathway_hash": pathway_hash,
                }

        row = {
            "seq": len(corrections) + 1,
            "prev": corrections[-1]["hash"] if corrections else None,
            "action": "BLOCK",
            "pathway_hash": pathway_hash,
            "question_hash": target["question_hash"],
            "reason": reason.strip(),
            "recorded_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "authority": "local_operator",
        }
        row["hash"] = _hash(row)
        path = root / "ledger/query_corrections.jsonl"
        append_fd = os.open(
            path, os.O_CREAT | os.O_APPEND | os.O_WRONLY | os.O_NOFOLLOW,
            0o600,
        )
        payload = (json.dumps(row, sort_keys=True) + "\n").encode()
        with os.fdopen(append_fd, "ab") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _corrections(root)
        return {
            "status": "CORRECTION_BLOCK_RECORDED",
            "correction_hash": row["hash"],
            "pathway_hash": pathway_hash,
        }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path,
        default=Path.home() / "openroot",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("block")
    command.add_argument("--pathway-hash", required=True)
    command.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        result = block(args.root, args.pathway_hash, args.reason)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "HELD", "reason": str(exc)}))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
