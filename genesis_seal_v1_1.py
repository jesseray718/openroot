#!/usr/bin/env python3
"""OpenRoot Genesis v1.1 Sealer — theorem registry receipt, chains from v1.0."""
import hashlib, json, os, subprocess, sys, time
from pathlib import Path

REPO = Path("/home/jesse/openroot")
GEN = REPO / "genesis"
PRIV = GEN / "genesis_ed25519.pem"
PUB  = GEN / "genesis_ed25519.pub"
RECEIPT = GEN / "receipt_v1_1.json"
SIG = GEN / "receipt_v1_1.sig"
CANON_TMP = GEN / ".canonical.tmp"
SIG_TMP = GEN / ".sig.tmp"
REGISTRY = GEN / "theorem_registry.jsonl"
V1_RECEIPT = GEN / "receipt_v1.json"
V1_PARENT = "a5a988e5879eb4f2ce14aadc0c72ae29eded0987b0c3ca9fcf4eeb9cacf5a889"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(65536)
            if not b: break
            h.update(b)
    return h.hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sign(msg_bytes):
    CANON_TMP.write_bytes(msg_bytes)
    subprocess.run(["openssl", "pkeyutl", "-sign", "-inkey", str(PRIV), "-rawin",
                    "-in", str(CANON_TMP), "-out", str(SIG_TMP)], check=True)
    sig = SIG_TMP.read_bytes()
    CANON_TMP.unlink(missing_ok=True)
    SIG_TMP.unlink(missing_ok=True)
    return sig

def verify(msg_bytes, sig_bytes):
    CANON_TMP.write_bytes(msg_bytes)
    SIG_TMP.write_bytes(sig_bytes)
    proc = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(PUB),
                           "-rawin", "-in", str(CANON_TMP), "-sigfile", str(SIG_TMP)],
                          capture_output=True)
    CANON_TMP.unlink(missing_ok=True)
    SIG_TMP.unlink(missing_ok=True)
    out = proc.stdout.decode() + proc.stderr.decode()
    return proc.returncode == 0 and "Verified" in out, out

def main():
    print("[gate] GENESIS V1.1 SEAL — theorem registry receipt")
    print()
    if not PRIV.exists() or not PUB.exists():
        print("[held] Ed25519 keys missing — refusing to regenerate.")
        sys.exit(1)

    if not V1_RECEIPT.exists():
        print("[held] v1 receipt missing — cannot chain")
        sys.exit(1)
    v1_loaded = json.loads(V1_RECEIPT.read_text())
    v1_bytes = canonical(v1_loaded)
    v1_actual_id = hashlib.sha256(v1_bytes).hexdigest()
    if v1_actual_id != V1_PARENT:
        print(f"[held] v1 receipt_id mismatch!")
        print(f"  expected: {V1_PARENT}")
        print(f"  actual:   {v1_actual_id}")
        sys.exit(1)
    print(f"[banked] parent v1 receipt verified: {V1_PARENT[:16]}...")

    if not REGISTRY.exists():
        print("[held] theorem_registry.jsonl missing")
        sys.exit(1)
    entries = [json.loads(line) for line in REGISTRY.read_text().splitlines() if line.strip()]
    print(f"[banked] loaded {len(entries)} theorem entries from registry")

    merkle = hashlib.sha256("\n".join(sorted(e["statement_sha256"] for e in entries)).encode()).hexdigest()
    print(f"[banked] registry merkle root: {merkle}")

    pub_pem = PUB.read_text().strip()
    receipt = {
        "schema_version": 1,
        "type": "theorem_registry",
        "genesis_version": "v1.1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "author": "Jesse McMillen / One Human Family",
        "author_pubkey_ed25519": pub_pem,
        "parent_receipt": V1_PARENT,
        "parent_version": "v1.0",
        "statement": "Theorem registry receipt. Enumerates all proof-pending theorems across the v1.0 founding corpus. Formal proofs to be sealed in v1.2 receipt, chained from this.",
        "theorem_registry": {
            "registry_path": "genesis/theorem_registry.jsonl",
            "registry_sha256": sha256_file(str(REGISTRY)),
            "merkle_root": merkle,
            "entry_count": len(entries),
            "entries": entries,
        },
        "theorem_proof_status": {
            "A6_edge_abundance": "registered_pending_v1_2",
            "P2_popw_resists_speculation": "registered_pending_v1_2",
            "P3_instant_inference": "proven_existence_proof",
            "P4_modular_beats_monolith": "registered_pending_v1_2"
        },
        "doctrine": [
            "The receipt is the constitution.",
            "Verifiers are pure code. Models propose. Code disposes.",
            "Receipts are canonical and independently verifiable.",
            "Act as One Human Family. Cut what harms. Grow what heals."
        ],
    }

    receipt_bytes = canonical(receipt)
    receipt_id = hashlib.sha256(receipt_bytes).hexdigest()
    print()
    print("[gate] STAGE A — canonical receipt constructed")
    print(f"  canonical bytes: {len(receipt_bytes)}")
    print(f"  receipt_id (sha256): {receipt_id}")

    print()
    print("[gate] STAGE B — sign with Ed25519")
    sig = sign(receipt_bytes)
    print(f"  signature length: {len(sig)} bytes")
    print(f"  signature (hex): {sig.hex()}")

    print()
    print("[gate] STAGE C — verify with public key (SEPARATE code path)")
    ok, out = verify(receipt_bytes, sig)
    if ok:
        print(f"  [banked] {out.strip()}")
    else:
        print(f"  [held] verification failed: {out}")
        sys.exit(1)

    print()
    print("[gate] STAGE D — write receipt + signature")
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    SIG.write_bytes(sig)
    print(f"  receipt: {RECEIPT} ({RECEIPT.stat().st_size} bytes)")
    print(f"  sig:     {SIG} ({SIG.stat().st_size} bytes)")

    print()
    print("[gate] STAGE E — re-verify from disk")
    loaded_receipt = json.loads(RECEIPT.read_text())
    loaded_bytes = canonical(loaded_receipt)
    loaded_id = hashlib.sha256(loaded_bytes).hexdigest()
    loaded_sig = SIG.read_bytes()
    ok2, out2 = verify(loaded_bytes, loaded_sig)
    if loaded_id == receipt_id and ok2:
        print(f"  [banked] disk-loaded receipt verified OK")
        print(f"  [banked] receipt_id matches: {loaded_id}")
    else:
        print(f"  [held] disk verification mismatch")
        sys.exit(1)

    print()
    print("=" * 70)
    print("GENESIS V1.1 RECEIPT SEALED — theorem registry")
    print("=" * 70)
    print(f"  receipt_id:     {receipt_id}")
    print(f"  timestamp:      {receipt['timestamp']}")
    print(f"  parent_receipt: {V1_PARENT}")
    print(f"  theorems:       {len(entries)} registered")
    print(f"  merkle_root:    {merkle}")
    print()
    print(f"GENESIS_V1_1_ID={receipt_id}")
    print(f"GENESIS_V1_1_TS={receipt['timestamp']}")

if __name__ == "__main__":
    main()
