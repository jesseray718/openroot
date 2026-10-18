#!/usr/bin/env python3
"""OpenRoot Genesis v1 Sealer — uses founding_docs/ corpus."""
import hashlib, json, os, subprocess, sys, time, glob
from pathlib import Path

REPO = Path("/home/jesse/openroot")
GEN = REPO / "genesis"
PRIV = GEN / "genesis_ed25519.pem"
PUB  = GEN / "genesis_ed25519.pub"
RECEIPT = GEN / "receipt_v1.json"
SIG = GEN / "receipt_v1.sig"
CANON_TMP = GEN / ".canonical.tmp"
SIG_TMP = GEN / ".sig.tmp"
FOUNDING = GEN / "founding_docs"

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

def discover_docs():
    found = []
    for p in sorted(FOUNDING.glob("*.md")):
        if p.name == "MANIFEST.sha256": continue
        rel = os.path.relpath(str(p), REPO)
        found.append({"name": p.stem, "path": rel, "sha256": sha256_file(str(p))})
        print(f"  [sealed] {p.name} ({found[-1]['sha256'][:16]}...)")
    return found

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
    print("[gate] GENESIS V1 SEAL")
    print()
    if not PRIV.exists() or not PUB.exists():
        print("[held] Ed25519 keys missing — refusing to regenerate. Restore from backup.")
        sys.exit(1)
    print(f"[banked] using existing keys:")
    print(f"  priv: {PRIV}")
    print(f"  pub:  {PUB}")
    print()
    print("[gate] STAGE A — discover founding docs")
    docs = discover_docs()
    print(f"  total sealed: {len(docs)}")
    print()
    print("[gate] STAGE B — construct canonical receipt")
    pub_pem = PUB.read_text().strip()
    receipt = {
        "schema_version": 1,
        "type": "genesis",
        "genesis_version": "v1.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "author": "Jesse McMillen / One Human Family",
        "author_pubkey_ed25519": pub_pem,
        "supersedes": "receipt_v0 (partial, 4 docs, 2026-10-18T09:21:54Z)",
        "statement": "Founding artifact of OpenRoot federated organism. All future receipts chain from this. Verifiers are pure code. Models propose, code disposes. Theorems marked proof-pending will be sealed in v1.1.",
        "documents": docs,
        "theorem_proof_status": {
            "A6_edge_abundance": "pending_v1_1",
            "P2_popw_resists_speculation": "pending_v1_1",
            "P3_instant_inference": "proven_existence_proof",
            "P4_modular_beats_monolith": "pending_v1_1"
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
    print(f"  canonical bytes: {len(receipt_bytes)}")
    print(f"  receipt_id (sha256): {receipt_id}")
    print()
    print("[gate] STAGE C — sign with Ed25519 private key")
    sig = sign(receipt_bytes)
    print(f"  signature length: {len(sig)} bytes")
    print(f"  signature (hex): {sig.hex()}")
    print()
    print("[gate] STAGE D — verify with public key (SEPARATE code path)")
    ok, out = verify(receipt_bytes, sig)
    if ok:
        print(f"  [banked] {out.strip()}")
    else:
        print(f"  [held] verification failed: {out}")
        sys.exit(1)
    print()
    print("[gate] STAGE E — write receipt + signature to genesis/")
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    SIG.write_bytes(sig)
    print(f"  receipt: {RECEIPT} ({RECEIPT.stat().st_size} bytes)")
    print(f"  sig:     {SIG} ({SIG.stat().st_size} bytes)")
    print()
    print("[gate] STAGE F — re-verify from disk")
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
    print("GENESIS V1 RECEIPT SEALED")
    print("=" * 70)
    print(f"  receipt_id:  {receipt_id}")
    print(f"  timestamp:   {receipt['timestamp']}")
    print(f"  documents:   {len(docs)}")
    print(f"  supersedes:  receipt_v0 (partial)")
    print()
    print(f"GENESIS_V1_ID={receipt_id}")
    print(f"GENESIS_V1_TS={receipt['timestamp']}")

if __name__ == "__main__":
    main()
