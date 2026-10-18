#!/usr/bin/env python3
import hashlib, json, os, subprocess, sys, time
from pathlib import Path

REPO = Path("/home/jesse/openroot")
GEN = REPO / "genesis"
PRIV = GEN / "genesis_ed25519.pem"
PUB  = GEN / "genesis_ed25519.pub"
RECEIPT = GEN / "receipt_v1_2.json"
SIG = GEN / "receipt_v1_2.sig"
CANON_TMP = GEN / ".canonical.tmp"
SIG_TMP = GEN / ".sig.tmp"
PROOFS_DIR = GEN / "proofs"
V1_1_RECEIPT = GEN / "receipt_v1_1.json"
V1_1_PARENT = "11f7934c5c1e42ca9303e939bae26425b905c186aa634190d63304092a5bfc57"

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
    print("[gate] GENESIS V1.2 SEAL — theorem proofs", file=sys.stderr)
    print(file=sys.stderr)
    if not PRIV.exists() or not PUB.exists():
        print("[held] Ed25519 keys missing"); sys.exit(1)

    if not V1_1_RECEIPT.exists():
        print("[held] v1.1 receipt missing — cannot chain"); sys.exit(1)
    v1_1_loaded = json.loads(V1_1_RECEIPT.read_text())
    v1_1_bytes = canonical(v1_1_loaded)
    v1_1_actual = hashlib.sha256(v1_1_bytes).hexdigest()
    if v1_1_actual != V1_1_PARENT:
        print(f"[held] v1.1 receipt_id mismatch!")
        print(f"  expected: {V1_1_PARENT}")
        print(f"  actual:   {v1_1_actual}")
        sys.exit(1)
    print(f"[banked] parent v1.1 receipt verified: {V1_1_PARENT[:16]}...", file=sys.stderr)

    proofs = []
    for p in sorted(PROOFS_DIR.glob("*.md")):
        proofs.append({"name": p.stem, "path": str(p.relative_to(REPO)), "sha256": sha256_file(str(p))})
        print(f"  [sealed] {p.name} ({proofs[-1]['sha256'][:16]}...)", file=sys.stderr)
    print(f"[banked] loaded {len(proofs)} proof files", file=sys.stderr)

    pub_pem = PUB.read_text().strip()
    receipt = {
        "schema_version": 1,
        "type": "theorem_proofs",
        "genesis_version": "v1.2",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "author": "Jesse McMillen / One Human Family",
        "author_pubkey_ed25519": pub_pem,
        "parent_receipt": V1_1_PARENT,
        "parent_version": "v1.1",
        "statement": "Theorem proofs receipt. Seals formal proofs for A6, P2, P4. Chains from v1.1 theorem registry. Closes the proof-pending loop opened in v1.1.",
        "proofs": proofs,
        "theorem_proof_status": {
            "A6_edge_abundance": "PROVEN_in_v1_2",
            "P2_popw_resists_speculation": "PROVEN_in_v1_2_with_limitations",
            "P3_instant_inference": "PROVEN_existence_proof_in_v1_0",
            "P4_modular_beats_monolith": "PROVEN_in_v1_2_with_limitations"
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
    print(file=sys.stderr)
    print(f"[gate] STAGE A — canonical receipt constructed", file=sys.stderr)
    print(f"  canonical bytes: {len(receipt_bytes)}", file=sys.stderr)
    print(f"  receipt_id (sha256): {receipt_id}", file=sys.stderr)

    print(file=sys.stderr)
    print(f"[gate] STAGE B — sign with Ed25519", file=sys.stderr)
    sig = sign(receipt_bytes)
    print(f"  signature length: {len(sig)} bytes", file=sys.stderr)

    print(file=sys.stderr)
    print(f"[gate] STAGE C — verify with public key (SEPARATE code path)", file=sys.stderr)
    ok, out = verify(receipt_bytes, sig)
    if ok:
        print(f"  [banked] {out.strip()}", file=sys.stderr)
    else:
        print(f"  [held] verification failed: {out}", file=sys.stderr)
        sys.exit(1)

    print(file=sys.stderr)
    print(f"[gate] STAGE D — write receipt + signature", file=sys.stderr)
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    SIG.write_bytes(sig)

    print(file=sys.stderr)
    print(f"[gate] STAGE E — re-verify from disk", file=sys.stderr)
    loaded = json.loads(RECEIPT.read_text())
    loaded_bytes = canonical(loaded)
    loaded_id = hashlib.sha256(loaded_bytes).hexdigest()
    ok2, _ = verify(loaded_bytes, SIG.read_bytes())
    if loaded_id == receipt_id and ok2:
        print(f"  [banked] disk-loaded receipt verified OK", file=sys.stderr)
        print(f"  [banked] receipt_id matches: {loaded_id}", file=sys.stderr)
    else:
        print(f"  [held] disk verification mismatch", file=sys.stderr)
        sys.exit(1)

    print(file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("GENESIS V1.2 RECEIPT SEALED — theorem proofs", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"  receipt_id:     {receipt_id}", file=sys.stderr)
    print(f"  timestamp:      {receipt['timestamp']}", file=sys.stderr)
    print(f"  parent_receipt: {V1_1_PARENT}", file=sys.stderr)
    print(f"  proofs sealed:  {len(proofs)}", file=sys.stderr)
    print(file=sys.stderr)
    # Pure stdout for downstream parsing
    print(f"GENESIS_V1_2_ID={receipt_id}")
    print(f"GENESIS_V1_2_TS={receipt['timestamp']}")

if __name__ == "__main__":
    main()
