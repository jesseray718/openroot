#!/usr/bin/env python3
"""OpenRoot Genesis Chain v1 - seal the receipt cache into immutable, parent-linked epochs.

What this gives you
  * compression   : canonical JSONL export of receipt_cache.db, lzma-packed
                    (typically 5-20x smaller than the live db)
  * immutability  : receipts_root = sha256 over sorted per-receipt hashes;
                    any byte changed anywhere in the epoch breaks verification
  * chaining      : every epoch header carries parent_head = previous epoch's
                    head hash. Epoch 2 ("the second genesis block") chains back
                    to epoch 1; also accepts an external --parent-hash /
                    --parent-hash-file (e.g. the prev_hash seed from your
                    existing genesis artifacts) so chains can be grafted.
  * idempotence   : seal twice with no state change -> identical receipts_root
                    -> no-op, no duplicate epoch
  * verifiability : `verify` recomputes every hash from the epoch files and
                    walks the parent links end to end

Ledger layout (default $OPENROOT_REPO/data/ledger/)
  chain.jsonl                     append-only head record per epoch
  epoch_0001_receipts.jsonl.xz    canonical receipt export (lzma)
  epoch_0001_header.json          standalone copy of that epoch's header

stdlib only, per OpenRoot doctrine.

Usage
  python3 genesis_chain_v1.py seal [--parent-hash HEX | --parent-hash-file F] [--force]
  python3 genesis_chain_v1.py verify
  python3 genesis_chain_v1.py stats
"""
import argparse
import hashlib
import json
import lzma
import os
import sqlite3
import sys
import time
from pathlib import Path

SCHEMA = "openroot.genesis_epoch.v1"
TOOL = "genesis_chain_v1"
GENESIS_PARENT = "0" * 64  # the first epoch's parent: nothing before it

RECEIPT_FIELDS = [
    "cache_key", "question_sha256", "dossier_sha256", "ai_output",
    "translated_code", "citations_json", "provider", "model",
    "tokens_used", "created_at", "hit_count", "last_used_at",
]


def log(m): print(f"[gate] {m}", file=sys.stderr)
def ok(m): print(f"[banked] {m}", file=sys.stderr)
def held(m):
    print(f"[held] {m}", file=sys.stderr)
    sys.exit(1)


def canon(obj):
    """Byte-deterministic JSON. Same data -> same bytes -> same hash."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_receipts(db_path):
    """Read every receipt, sorted by cache_key. Read-only; never touches the live db."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f"SELECT {', '.join(RECEIPT_FIELDS)} FROM receipt_cache ORDER BY cache_key"
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        # canonicalize nested citations json so exports are byte-stable
        if d.get("citations_json"):
            try:
                d["citations_json"] = canon(json.loads(d["citations_json"]))
            except Exception:
                pass  # keep raw text rather than fail the seal
        out.append(d)
    return out


def receipts_root(receipts):
    """sha256 over per-receipt hashes in cache_key order. Change one byte anywhere -> new root."""
    h = hashlib.sha256()
    for r in sorted(receipts, key=lambda x: x["cache_key"]):
        h.update(hashlib.sha256(canon(r).encode()).hexdigest().encode())
        h.update(b"\n")
    return h.hexdigest()


def last_record(ledger_dir):
    chain = ledger_dir / "chain.jsonl"
    if not chain.exists():
        return None
    last = None
    for line in chain.read_text().splitlines():
        line = line.strip()
        if line:
            last = json.loads(line)
    return last


# ---------------------------------------------------------------- commands --

def cmd_seal(args):
    repo = Path(args.repo)
    db = Path(args.db) if args.db else repo / "data" / "receipt_cache.db"
    ledger = Path(args.out_dir) if args.out_dir else repo / "data" / "ledger"
    ledger.mkdir(parents=True, exist_ok=True)
    if not db.exists():
        held(f"no cache db at {db}")

    log(f"reading {db} (read-only)")
    receipts = load_receipts(db)
    root = receipts_root(receipts)
    prev = last_record(ledger)

    if prev and prev["header"]["receipts_root"] == root and not args.force:
        ok(f"no state change since epoch {prev['header']['epoch']:04d} "
           f"(root {root[:16]}...) - idempotent no-op, nothing to seal")
        return

    epoch = (prev["header"]["epoch"] + 1) if prev else 1
    if prev:
        parent = prev["head_sha256"]
    elif args.parent_hash_file:
        parent = Path(args.parent_hash_file).read_text().strip().splitlines()[0].strip()
    elif args.parent_hash:
        parent = args.parent_hash.strip()
    else:
        parent = GENESIS_PARENT
    if len(parent) != 64:
        held(f"parent hash must be 64 hex chars, got: {parent!r}")

    total_tokens = sum(int(r["tokens_used"] or 0) for r in receipts)
    header = {
        "schema": SCHEMA,
        "tool": TOOL,
        "epoch": epoch,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parent_head": parent,
        "receipts_root": root,
        "receipt_count": len(receipts),
        "tokens_total": total_tokens,
        "source_db_sha256": file_sha256(db),
    }
    head_sha = hashlib.sha256(canon(header).encode()).hexdigest()

    payload = "\n".join(canon(r) for r in receipts).encode()
    efile = ledger / f"epoch_{epoch:04d}_receipts.jsonl.xz"
    efile.write_bytes(lzma.compress(payload, preset=9 | lzma.PRESET_EXTREME))
    (ledger / f"epoch_{epoch:04d}_header.json").write_text(
        json.dumps(header, indent=2, sort_keys=True) + "\n")

    with (ledger / "chain.jsonl").open("a") as f:
        f.write(canon({"type": "epoch_header", "head_sha256": head_sha,
                       "header": header}) + "\n")

    orig, comp = db.stat().st_size, efile.stat().st_size
    ratio = orig / comp if comp else 0.0
    ok(f"epoch {epoch:04d} sealed: {len(receipts)} receipts, root {root[:16]}...")
    ok(f"parent: {parent[:16]}...  head: {head_sha[:16]}...")
    ok(f"compressed: {orig / 1e6:.2f} MB db -> {comp / 1e6:.2f} MB epoch file ({ratio:.1f}x)")
    print(json.dumps({"epoch": epoch, "head_sha256": head_sha,
                      "receipts_root": root, "receipt_count": len(receipts),
                      "file": str(efile)}, indent=2))


def cmd_verify(args):
    repo = Path(args.repo)
    ledger = Path(args.out_dir) if args.out_dir else repo / "data" / "ledger"
    chain = ledger / "chain.jsonl"
    if not chain.exists():
        held(f"no chain at {chain}")

    prev, n, fails = None, 0, []
    for lineno, line in enumerate(chain.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        h = rec.get("header", {})
        ep = h.get("epoch", lineno)
        want_head = hashlib.sha256(canon(h).encode()).hexdigest()
        if want_head != rec.get("head_sha256"):
            fails.append(f"line {lineno}: head hash mismatch (epoch {ep})")
        if prev and h.get("parent_head") != prev["head_sha256"]:
            fails.append(f"epoch {ep}: parent link broken "
                         f"(expected {prev['head_sha256'][:16]}..., "
                         f"got {h.get('parent_head', '')[:16]}...)")
        efile = ledger / f"epoch_{h.get('epoch', 0):04d}_receipts.jsonl.xz"
        if not efile.exists():
            fails.append(f"epoch {ep}: epoch file missing: {efile.name}")
        else:
            try:
                receipts = [json.loads(l)
                            for l in lzma.decompress(efile.read_bytes()).decode().splitlines()
                            if l]
            except (lzma.LZMAError, UnicodeDecodeError, json.JSONDecodeError) as e:
                fails.append(f"epoch {ep}: epoch file unreadable/corrupt: {e}")
                prev, n = rec, n + 1
                continue
            if receipts_root(receipts) != h.get("receipts_root"):
                fails.append(f"epoch {ep}: receipts_root mismatch (content altered)")
            if len(receipts) != h.get("receipt_count"):
                fails.append(f"epoch {ep}: receipt count mismatch "
                             f"({len(receipts)} vs header {h.get('receipt_count')})")
        prev, n = rec, n + 1

    if fails:
        for f_ in fails:
            print(f"[held] {f_}", file=sys.stderr)
        held(f"chain verification FAILED ({n} epochs checked)")
    ok(f"chain verified end-to-end: {n} epoch(s), every hash recomputed, "
       f"every parent link intact")
    ok(f"head: {prev['head_sha256']} (epoch {prev['header']['epoch']:04d})")
    print(json.dumps({"epochs": n, "head_sha256": prev["head_sha256"],
                      "tip_epoch": prev["header"]["epoch"],
                      "status": "VERIFIED"}, indent=2))


def cmd_stats(args):
    repo = Path(args.repo)
    ledger = Path(args.out_dir) if args.out_dir else repo / "data" / "ledger"
    prev = last_record(ledger)
    if not prev:
        held("chain is empty - run `seal` first")
    h = prev["header"]
    efile = ledger / f"epoch_{h['epoch']:04d}_receipts.jsonl.xz"
    receipts = [json.loads(l)
                for l in lzma.decompress(efile.read_bytes()).decode().splitlines() if l]
    by_provider, by_model = {}, {}
    for r in receipts:
        p = r.get("provider") or "unknown"
        m = r.get("model") or "unknown"
        by_provider[p] = by_provider.get(p, 0) + 1
        by_model[m] = by_model.get(m, 0) + 1
    top_hits = sorted(receipts, key=lambda r: -(int(r.get("hit_count") or 0)))[:10]
    print(json.dumps({
        "chain_tip": {"epoch": h["epoch"], "head_sha256": h and prev["head_sha256"]},
        "receipts": h["receipt_count"],
        "tokens_total": h["tokens_total"],
        "by_provider": by_provider,
        "by_model": by_model,
        "epoch_file_bytes": efile.stat().st_size,
        "top_cache_hits": [{"cache_key": r["cache_key"][:16],
                            "hits": r.get("hit_count"), "model": r.get("model")}
                           for r in top_hits],
    }, indent=2))


def main():
    p = argparse.ArgumentParser(description="OpenRoot Genesis Chain v1")
    p.add_argument("--repo", default=os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
    p.add_argument("--db", default=None, help="override receipt cache db path")
    p.add_argument("--out-dir", default=None, help="override ledger dir (default <repo>/data/ledger)")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("seal", help="export + hash + compress current cache into a chained epoch")
    ps.add_argument("--parent-hash", default=None,
                    help="external parent hash for the FIRST epoch (e.g. your existing genesis/prev_hash)")
    ps.add_argument("--parent-hash-file", default=None,
                    help="file whose first line is the parent hash (e.g. prev_hash seed)")
    ps.add_argument("--force", action="store_true",
                    help="seal a new epoch even if receipts_root is unchanged")

    sub.add_parser("verify", help="recompute all hashes, walk parent links")
    sub.add_parser("stats", help="cache composition + compression report")

    args = p.parse_args()
    print(f"[gate] CANARY:OPENROOT-GENESIS-CHAIN-V1", file=sys.stderr)
    if args.cmd == "seal":
        cmd_seal(args)
    elif args.cmd == "verify":
        cmd_verify(args)
    elif args.cmd == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
