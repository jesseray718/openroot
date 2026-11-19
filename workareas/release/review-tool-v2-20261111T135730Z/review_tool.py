#!/usr/bin/env python3
"""Noncanonical OpenRoot sandbox review tool. No canonical promotion."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VERSION = "openroot-sandbox-review-v2"
RULES = {
    "version": "heuristic-rules-v2",
    "observation_minimum_days": 7,
    "observation_penalty": 6,
    "missing_feedback_penalty": 8,
    "unaccounted_compute_penalty": 6,
    "threshold": 40,
    "meaning": "heuristic screening only; not scientific verification",
}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_BYTES = 16 * 1024 * 1024

def encode(obj):
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False
    ).encode("utf-8")

def digest(obj):
    return hashlib.sha256(encode(obj)).hexdigest()

def core_hash(obj):
    return digest({k: v for k, v in obj.items() if k != "hash"})

def now():
    return datetime.now(timezone.utc).isoformat()

def reject_constant(value):
    raise ValueError("nonfinite JSON value: " + value)

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def parse(raw):
    return json.loads(
        raw, object_pairs_hook=unique_pairs,
        parse_constant=reject_constant
    )

def safe_path(path):
    p = Path(os.path.abspath(os.fspath(path)))
    for component in (p, *p.parents):
        if component.is_symlink():
            raise ValueError("symlink path refused: " + str(component))
    return p

def read_bytes(path):
    p = safe_path(path)
    flags = os.O_RDONLY | os.O_NOFOLLOW
    fd = os.open(p, flags)
    with os.fdopen(fd, "rb") as f:
        data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("file exceeds configured size limit")
    return data

def load(path):
    return parse(read_bytes(path))

def atomic_write(path, data):
    p = safe_path(path)
    if not p.parent.is_dir():
        raise ValueError("output directory absent")
    fd, temp = tempfile.mkstemp(prefix=".pending-", dir=p.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        safe_path(p)
        os.replace(temp, p)
        dfd = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def verify_rows(rows):
    previous = "genesis"
    seen = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"entry {index}: object required")
        h = row.get("hash")
        if not isinstance(h, str) or not HASH_RE.fullmatch(h):
            raise ValueError(f"entry {index}: invalid hash")
        if h in seen:
            raise ValueError(f"entry {index}: duplicate entry hash")
        if row.get("previous_hash") != previous:
            raise ValueError(f"entry {index}: previous-hash mismatch")
        if core_hash(row) != h:
            raise ValueError(f"entry {index}: content-hash mismatch")
        seen.add(h)
        previous = h
    return previous

def read_chain(path, allow_absent=False):
    p = safe_path(path)
    if not p.exists():
        if allow_absent:
            return []
        raise ValueError("ledger absent: " + str(p))
    raw = read_bytes(p)
    if not raw:
        raise ValueError("empty ledger")
    if not raw.endswith(b"\n"):
        raise ValueError("ledger lacks final newline")
    lines = raw.splitlines()
    if any(not line.strip() for line in lines):
        raise ValueError("blank ledger line refused")
    rows = [parse(line) for line in lines]
    verify_rows(rows)
    return rows

def exact_entry(rows, h):
    if not HASH_RE.fullmatch(h):
        raise ValueError("full lowercase SHA-256 required")
    matches = [r for r in rows if r["hash"] == h]
    if len(matches) != 1:
        raise ValueError("entry must match exactly once")
    return matches[0]

def number(task, key, minimum=0, maximum=None):
    v = task.get(key)
    if type(v) not in (int, float) or not math.isfinite(v):
        raise ValueError(key + ": finite number required")
    if v < minimum or (maximum is not None and v > maximum):
        raise ValueError(key + ": out of range")
    return v

def evaluate(task):
    if not isinstance(task, dict):
        raise ValueError("task object required")
    if not isinstance(task.get("name"), str) or not task["name"].strip():
        raise ValueError("nonempty task name required")
    base = number(task, "base_eta", 0, 100)
    days = number(task, "observation_days")
    joules = number(task, "compute_joules")
    for key in ("feedback", "involves_compute"):
        if type(task.get(key)) is not bool:
            raise ValueError(key + ": boolean required")

    checks = [
        ("R001", days >= 7, 6, "observation_days", days),
        ("R002", task["feedback"], 8, "feedback", task["feedback"]),
        ("R003", not task["involves_compute"] or joules > 0,
         6, "compute_joules", joules),
    ]
    trace = [
        {
            "rule": rule, "passed": passed,
            "penalty": 0 if passed else penalty,
            "input_field": field, "input_value": value
        }
        for rule, passed, penalty, field, value in checks
    ]
    score = max(0.0, min(100.0, base - sum(x["penalty"] for x in trace)))
    layer = [digest(x) for x in trace]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [
            hashlib.sha256((layer[i] + layer[i + 1]).encode()).hexdigest()
            for i in range(0, len(layer), 2)
        ]
    return {
        "heuristic_score": score,
        "threshold_passed": score >= RULES["threshold"],
        "rule_trace": trace,
        "merkle_root": layer[0],
        "rules_sha256": digest(RULES),
        "rules_version": RULES["version"],
        "evidence_status": "unverified_user_supplied_inputs",
        "canonical_status": "not_canonical",
    }

class Store:
    def __init__(self, root):
        self.root = safe_path(root)
        if not self.root.is_dir():
            raise ValueError("store directory absent")
        self.ledger = self.root / "review_events.jsonl"
        self.lock = self.root / ".review.lock"

    @contextlib.contextmanager
    def locked(self):
        safe_path(self.lock)
        fd = os.open(
            self.lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600
        )
        with os.fdopen(fd, "a+b") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            yield

    def append(self, event_type, payload, dedupe):
        with self.locked():
            rows = read_chain(self.ledger, allow_absent=True)
            existing = [r for r in rows if r.get("dedupe_key") == dedupe]
            if existing:
                return {"status": "already_recorded", "entry": existing[0]}
            entry = {
                "schema": VERSION,
                "sequence": len(rows) + 1,
                "timestamp": now(),
                "type": event_type,
                "canonical_status": "not_canonical",
                "dedupe_key": dedupe,
                "previous_hash": rows[-1]["hash"] if rows else "genesis",
                "payload": payload,
            }
            entry["hash"] = core_hash(entry)
            rows.append(entry)
            atomic_write(self.ledger, b"".join(encode(r) + b"\n" for r in rows))
            return {"status": "recorded", "entry": entry}

    def verify(self):
        rows = read_chain(self.ledger)
        for i, row in enumerate(rows, 1):
            if row.get("sequence") != i:
                raise ValueError("sequence mismatch")
            if row.get("canonical_status") != "not_canonical":
                raise ValueError("unexpected canonical label")
        return {
            "status": "PASS", "entries": len(rows),
            "tip": rows[-1]["hash"],
            "ledger": str(self.ledger),
            "canonical_status": "not_canonical",
        }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("evaluate")
    p.add_argument("--task", required=True)
    p.add_argument("--record", action="store_true")

    p = sub.add_parser("audit-legacy")
    p.add_argument("--ledger", required=True)

    sub.add_parser("verify")

    p = sub.add_parser("stage")
    p.add_argument("--source-ledger", required=True)
    p.add_argument("--entry-hash", required=True)
    p.add_argument("--record", action="store_true")

    p = sub.add_parser("approve-test")
    p.add_argument("--stage-hash", required=True)
    p.add_argument("--approver", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--record", action="store_true")

    args = ap.parse_args()
    store = Store(Path(__file__).resolve().parent)

    if args.command == "evaluate":
        raw = read_bytes(args.task)
        task = parse(raw)
        payload = {
            "task_sha256": hashlib.sha256(raw).hexdigest(),
            "task_snapshot": task,
            "tool_sha256": hashlib.sha256(read_bytes(__file__)).hexdigest(),
            "evaluation": evaluate(task),
        }
        result = (
            store.append("sandbox_evaluation", payload, digest(payload))
            if args.record else {"status": "preview_only", "payload": payload}
        )

    elif args.command == "audit-legacy":
        rows = read_chain(args.ledger)
        result = {
            "status": "PASS", "entries": len(rows),
            "tip": rows[-1]["hash"],
            "scope": "hash integrity and linkage only",
        }

    elif args.command == "verify":
        result = store.verify()

    elif args.command == "stage":
        raw = read_bytes(args.source_ledger)
        rows = read_chain(args.source_ledger)
        source = exact_entry(rows, args.entry_hash)
        payload = {
            "source_path": str(safe_path(args.source_ledger)),
            "source_file_sha256": hashlib.sha256(raw).hexdigest(),
            "source_entry": source,
            "review_status": "pending_human_review",
            "evidence_status": "not_independently_verified",
        }
        result = (
            store.append(
                "sandbox_review_staged", payload,
                digest({"stage_source_hash": source["hash"]})
            )
            if args.record else {"status": "preview_only", "payload": payload}
        )

    else:
        if not args.approver.strip() or not args.reason.strip():
            raise ValueError("approver and reason must be nonempty")
        rows = read_chain(store.ledger)
        source = exact_entry(rows, args.stage_hash)
        if source.get("type") != "sandbox_review_staged":
            raise ValueError("selected entry is not a staged review")
        payload = {
            "stage_hash": source["hash"],
            "approver_label": args.approver,
            "reason": args.reason,
            "approval_scope": "sandbox_workflow_test_only",
            "identity_status": "self_asserted_not_authenticated",
            "canonical_status": "not_canonical",
        }
        result = (
            store.append(
                "sandbox_test_review_approved", payload,
                digest({"approved_stage": source["hash"]})
            )
            if args.record else {"status": "preview_only", "payload": payload}
        )

    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
