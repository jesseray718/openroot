#!/usr/bin/env python3
"""
OpenRoot Thermodynamic Ledger
Local-first append-only chain. No miners, no gas, no Solana.

A block is:
  prev_hash + payload_sha256 + physical mass + thermo + time
  block_hash = SHA256(canonical JSON without block_hash)

Proof of Physical Work (minimum viable):
  weigh the object (kg) and bind that number to the file hash.
  You can lie. A second photo hash or a witness makes lying harder.
  Honesty is the consensus. The chain only makes lying *auditable*.

Install (Termux):
  mkdir -p /sdcard/openroot/thermo/{cas,chain,payloads}
  python3 thermo_ledger.py genesis --root /sdcard/openroot/thermo
  python3 thermo_ledger.py put FILE --root /sdcard/openroot/thermo
  python3 thermo_ledger.py seal FILE --mass-kg 12.4 --what "panel A" --root /sdcard/openroot/thermo
  python3 thermo_ledger.py verify --root /sdcard/openroot/thermo
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

LEDGER_VERSION = "1.0.0"
GENESIS_PREV = "0" * 64


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(obj: Any) -> bytes:
    """One and only serialization. If this changes, old hashes break. Do not change."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def block_hash(block: dict) -> str:
    body = {k: v for k, v in block.items() if k != "block_hash"}
    return sha256_bytes(canonical(body))


def merkle_root(hashes: list[str]) -> str:
    """Pairwise SHA256 merkle. Odd tail is duplicated (Bitcoin-style). Empty = genesis zero."""
    if not hashes:
        return GENESIS_PREV
    layer = [h.lower() for h in hashes]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        nxt = []
        for i in range(0, len(layer), 2):
            nxt.append(sha256_bytes(bytes.fromhex(layer[i] + layer[i + 1])))
        layer = nxt
    return layer[0]


class Lattice:
    def __init__(self, root: Path):
        self.root = root
        self.cas = root / "cas"
        self.chain_path = root / "chain.jsonl"
        self.tip_path = root / "tip.json"
        self.index_path = root / "index.json"
        self.payloads = root / "payloads"
        for p in (self.cas, self.payloads):
            p.mkdir(parents=True, exist_ok=True)

    def load_chain(self) -> list[dict]:
        if not self.chain_path.exists():
            return []
        blocks = []
        with self.chain_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    blocks.append(json.loads(line))
        return blocks

    def tip(self) -> dict | None:
        blocks = self.load_chain()
        return blocks[-1] if blocks else None

    def write_index(self, index: dict) -> None:
        tmp = self.index_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.index_path)

    def load_index(self) -> dict:
        if not self.index_path.exists():
            return {"version": LEDGER_VERSION, "blobs": {}, "paths": {}}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def cas_put_file(self, src: Path) -> str:
        digest = sha256_file(src)
        dest = self.cas / digest
        if not dest.exists():
            dest.write_bytes(src.read_bytes())
        return digest

    def cas_put_obj(self, obj: Any) -> str:
        raw = canonical(obj)
        digest = sha256_bytes(raw)
        dest = self.cas / digest
        if not dest.exists():
            dest.write_bytes(raw)
        return digest

    def append(self, block: dict) -> dict:
        block["block_hash"] = block_hash(block)
        with self.chain_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(block, sort_keys=True, separators=(",", ":")) + "\n")
        tip = {
            "block_index": block["block_index"],
            "block_hash": block["block_hash"],
            "payload_sha256": block["payload_sha256"],
            "time_unix": block["time_unix"],
        }
        self.tip_path.write_text(json.dumps(tip, indent=2, sort_keys=True), encoding="utf-8")
        return block

    def genesis(self, author: str, statement: str) -> dict:
        if self.chain_path.exists() and self.chain_path.stat().st_size > 0:
            raise SystemExit("genesis already exists — do not overwrite a living chain")
        payload = {
            "type": "genesis",
            "ledger": "openroot-thermo-lattice",
            "version": LEDGER_VERSION,
            "author": author,
            "statement": statement,
            "law": {
                "eta": "useful_joules / human_joules",
                "gamma": "Y*L*P*F / (Jh+Je+C)",
                "coordination": "C(N,T,R)=N*0.001*(1+0.1*T)*(1-R)^T",
                "resonance_zero_cost": "R=1.0 => C=0 for T>=1",
            },
            "consensus": "local honesty + append-only SHA256 + optional mass witness",
            "not": ["public blockchain", "token", "miner", "gas", "smart contract"],
        }
        payload_hash = self.cas_put_obj(payload)
        now = time.time()
        block = {
            "ledger_version": LEDGER_VERSION,
            "block_index": 0,
            "prev_hash": GENESIS_PREV,
            "payload_sha256": payload_hash,
            "payload_type": "genesis",
            "physical": None,
            "thermo": {
                "human_joules": 0.0,
                "embodied_joules": 0.0,
                "useful_joules": 0.0,
                "eta": None,
                "gamma": None,
            },
            "time_unix": int(now),
            "time_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "note": statement,
        }
        block = self.append(block)
        (self.payloads / "genesis.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        return block

    def hang_file(
        self,
        src: Path,
        mass_kg: float | None,
        what: str,
        human_joules: float,
        embodied_joules: float,
        useful_joules: float,
        gamma: float | None,
        note: str,
        photo: Path | None,
    ) -> dict:
        if not src.is_file():
            raise SystemExit(f"not a file: {src}")
        tip = self.tip()
        if tip is None:
            raise SystemExit("no genesis — run genesis first")
        digest = self.cas_put_file(src)
        photo_hash = self.cas_put_file(photo) if photo and photo.is_file() else None
        payload = {
            "type": "hang",
            "original_name": src.name,
            "original_path": str(src.resolve()),
            "size_bytes": src.stat().st_size,
            "mtime_unix": int(src.stat().st_mtime),
            "what": what,
            "note": note,
        }
        payload_hash = self.cas_put_obj(payload)
        # bind file + payload + optional photo into one merkle so the block hangs ALL of it
        root = merkle_root([h for h in (digest, payload_hash, photo_hash) if h])
        eta = (useful_joules / human_joules) if human_joules > 0 else None
        physical = None
        if mass_kg is not None:
            physical = {
                "mass_kg": float(mass_kg),
                "what": what,
                "method": "single_scale_reading",
                "photo_sha256": photo_hash,
                "bound_file_sha256": digest,
                "warning": "mass is a witness not a proof against a determined liar",
            }
        now = time.time()
        block = {
            "ledger_version": LEDGER_VERSION,
            "block_index": tip["block_index"] + 1,
            "prev_hash": tip["block_hash"],
            "payload_sha256": root,
            "payload_type": "hang",
            "files": {"artifact": digest, "meta": payload_hash, "photo": photo_hash},
            "physical": physical,
            "thermo": {
                "human_joules": float(human_joules),
                "embodied_joules": float(embodied_joules),
                "useful_joules": float(useful_joules),
                "eta": eta,
                "gamma": gamma,
            },
            "time_unix": int(now),
            "time_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "note": note or what,
        }
        block = self.append(block)
        index = self.load_index()
        index["blobs"][digest] = {
            "name": src.name,
            "size_bytes": src.stat().st_size,
            "block_index": block["block_index"],
            "mass_kg": mass_kg,
            "what": what,
        }
        index["paths"][str(src.resolve())] = digest
        self.write_index(index)
        return block

    def verify(self) -> dict:
        blocks = self.load_chain()
        if not blocks:
            return {"ok": False, "error": "empty chain"}
        errors = []
        for i, b in enumerate(blocks):
            recomputed = block_hash(b)
            if b.get("block_hash") != recomputed:
                errors.append(f"block {i}: hash mismatch")
            if i == 0:
                if b.get("prev_hash") != GENESIS_PREV:
                    errors.append("genesis prev_hash is not zero")
                if b.get("block_index") != 0:
                    errors.append("genesis index is not 0")
            else:
                if b.get("prev_hash") != blocks[i - 1].get("block_hash"):
                    errors.append(f"block {i}: broken prev link")
                if b.get("block_index") != blocks[i - 1].get("block_index") + 1:
                    errors.append(f"block {i}: index gap")
            for key in ("artifact", "meta", "photo"):
                h = (b.get("files") or {}).get(key)
                if h and not (self.cas / h).exists():
                    errors.append(f"block {i}: missing cas blob {key}={h[:12]}")
            if b.get("payload_sha256") and b.get("payload_type") == "genesis":
                if not (self.cas / b["payload_sha256"]).exists():
                    errors.append(f"block {i}: missing genesis payload")
        return {
            "ok": not errors,
            "blocks": len(blocks),
            "tip": blocks[-1]["block_hash"],
            "errors": errors,
        }


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--root", default="/sdcard/openroot/thermo", help="ledger root (absolute)")
    p = argparse.ArgumentParser(description="OpenRoot thermodynamic ledger", parents=[parent])
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("genesis", help="create block 0 once", parents=[parent])
    g.add_argument("--author", default="Jesse Ray / jesseray718")
    g.add_argument(
        "--statement",
        default="One local thermodynamic chain. Weight + SHA256. No public chain required.",
    )

    h = sub.add_parser("hang", help="put a file in CAS and append a block", parents=[parent])
    h.add_argument("file")
    h.add_argument("--mass-kg", type=float, default=None)
    h.add_argument("--what", default="")
    h.add_argument("--human-j", type=float, default=0.0)
    h.add_argument("--embodied-j", type=float, default=0.0)
    h.add_argument("--useful-j", type=float, default=0.0)
    h.add_argument("--gamma", type=float, default=None)
    h.add_argument("--note", default="")
    h.add_argument("--photo", default=None)

    sub.add_parser("verify", help="recompute every hash and every link", parents=[parent])
    sub.add_parser("tip", help="print the last block", parents=[parent])
    sub.add_parser("log", help="print chain as JSON", parents=[parent])

    s = sub.add_parser("hash", help="print sha256 of a file (no chain write)", parents=[parent])
    s.add_argument("file")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    lat = Lattice(root)

    if args.cmd == "genesis":
        b = lat.genesis(args.author, args.statement)
        print(json.dumps(b, indent=2, sort_keys=True))
        return 0
    if args.cmd == "hang":
        src = Path(args.file)
        photo = Path(args.photo) if args.photo else None
        what = args.what or src.name
        b = lat.hang_file(
            src,
            args.mass_kg,
            what,
            args.human_j,
            args.embodied_j,
            args.useful_j,
            args.gamma,
            args.note,
            photo,
        )
        print(json.dumps(b, indent=2, sort_keys=True))
        return 0
    if args.cmd == "verify":
        print(json.dumps(lat.verify(), indent=2, sort_keys=True))
        return 0 if lat.verify()["ok"] else 2
    if args.cmd == "tip":
        print(json.dumps(lat.tip(), indent=2, sort_keys=True))
        return 0
    if args.cmd == "log":
        print(json.dumps(lat.load_chain(), indent=2, sort_keys=True))
        return 0
    if args.cmd == "hash":
        print(sha256_file(Path(args.file)))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
