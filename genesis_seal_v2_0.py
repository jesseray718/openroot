#!/usr/bin/env python3
"""OpenRoot v2.0 Epoch Checkpoint - consolidates all state into one merkle root, chained from v1.2."""
import hashlib, json, os, subprocess, sys, time
from pathlib import Path

REPO = Path("/home/jesse/openroot")
GEN = REPO / "genesis"
PRIV = GEN / "genesis_ed25519.pem"
PUB  = GEN / "genesis_ed25519.pub"
RECEIPT = GEN / "receipt_v2_0.json"
SIG = GEN / "receipt_v2_0.sig"
CANON_TMP = GEN / ".canonical.tmp"
SIG_TMP = GEN / ".sig.tmp"
V1_2_RECEIPT = GEN / "receipt_v1_2.json"
V1_2_PARENT = "e194bfc179af841933446906482137b3ea1c43a7afe1d753023f0ccb4c50ca7c"

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

def hash_dir(dir_path):
    """Recursively hash a directory's contents into a merkle root."""
    dir_path = Path(dir_path)
    if not dir_path.exists():
        return None, 0, 0
    hashes = []
    total_files = 0
    total_bytes = 0
    for p in sorted(dir_path.rglob("*")):
        if p.is_file() and ".git" not in str(p):
            h = sha256_file(str(p))
            hashes.append(h)
            total_files += 1
            total_bytes += p.stat().st_size
    if not hashes:
        return None, 0, 0
    level = hashes[:]
    while len(level) > 1:
        if len(level) % 2: level.append(level[-1])
        level = [hashlib.sha256((level[i]+level[i+1]).encode()).hexdigest()
                 for i in range(0, len(level), 2)]
    return level[0], total_files, total_bytes

def main():
    print("[gate] OPENROOT v2.0 EPOCH CHECKPOINT SEAL", file=sys.stderr)
    print(file=sys.stderr)
    
    if not PRIV.exists() or not PUB.exists():
        print("[held] Ed25519 keys missing"); sys.exit(1)
    
    # Verify parent v1.2 chain
    if not V1_2_RECEIPT.exists():
        print("[held] v1.2 receipt missing — cannot chain"); sys.exit(1)
    v1_2_loaded = json.loads(V1_2_RECEIPT.read_text())
    v1_2_bytes = canonical(v1_2_loaded)
    v1_2_actual = hashlib.sha256(v1_2_bytes).hexdigest()
    if v1_2_actual != V1_2_PARENT:
        print(f"[held] v1.2 receipt_id mismatch!"); sys.exit(1)
    print(f"[banked] parent v1.2 verified: {V1_2_PARENT[:16]}...", file=sys.stderr)
    
    # Hash every major subsystem
    print(file=sys.stderr)
    print("[gate] STAGE A — hash all subsystems", file=sys.stderr)
    subsystems = {}
    
    # Genesis chain (v1.x receipts)
    gen_hashes = []
    for f in sorted(GEN.glob("receipt_v*.json")):
        h = sha256_file(str(f))
        gen_hashes.append(h)
        print(f"  [sealed] {f.name} ({h[:16]}...)", file=sys.stderr)
    subsystems["genesis_chain"] = {
        "files": len(gen_hashes),
        "merkle_root": hashlib.sha256("".join(gen_hashes).encode()).hexdigest() if gen_hashes else None
    }
    
    # Founding docs
    root, files, bytes_ = hash_dir(GEN / "founding_docs")
    subsystems["founding_docs"] = {"files": files, "bytes": bytes_, "merkle_root": root}
    print(f"  [sealed] founding_docs: {files} files, {bytes_} bytes", file=sys.stderr)
    
    # Proofs
    root, files, bytes_ = hash_dir(GEN / "proofs")
    subsystems["proofs"] = {"files": files, "bytes": bytes_, "merkle_root": root}
    print(f"  [sealed] proofs: {files} files, {bytes_} bytes", file=sys.stderr)
    
    # Pod garden (the knowledge base)
    root, files, bytes_ = hash_dir(REPO / "pods_garden")
    subsystems["pods_garden"] = {"files": files, "bytes": bytes_, "merkle_root": root}
    print(f"  [sealed] pods_garden: {files} files, {bytes_} bytes", file=sys.stderr)
    
    # Tool suite (bin/)
    root, files, bytes_ = hash_dir(REPO / "bin")
    subsystems["tool_suite"] = {"files": files, "bytes": bytes_, "merkle_root": root}
    print(f"  [sealed] tool_suite: {files} files, {bytes_} bytes", file=sys.stderr)
    
    # Receipt cache + ledger (data/)
    root, files, bytes_ = hash_dir(REPO / "data")
    subsystems["data_layer"] = {"files": files, "bytes": bytes_, "merkle_root": root}
    print(f"  [sealed] data_layer: {files} files, {bytes_} bytes", file=sys.stderr)
    
    # Mistake log (scars)
    ml_path = REPO / "data" / "mistakes" / "mistake_log.jsonl"
    if ml_path.exists():
        subsystems["mistake_log"] = {"sha256": sha256_file(str(ml_path))}
    
    # Compute the epoch merkle root (root of roots)
    epoch_leaves = []
    for name in sorted(subsystems.keys()):
        s = subsystems[name]
        if "merkle_root" in s and s["merkle_root"]:
            epoch_leaves.append(s["merkle_root"])
        elif "sha256" in s and s["sha256"]:
            epoch_leaves.append(s["sha256"])
    
    epoch_level = epoch_leaves[:]
    while len(epoch_level) > 1:
        if len(epoch_level) % 2: epoch_level.append(epoch_level[-1])
        epoch_level = [hashlib.sha256((epoch_level[i]+epoch_level[i+1]).encode()).hexdigest()
                       for i in range(0, len(epoch_level), 2)]
    epoch_root = epoch_level[0] if epoch_level else None
    print(file=sys.stderr)
    print(f"[banked] EPOCH ROOT: {epoch_root}", file=sys.stderr)
    
    # Build the v2.0 receipt
    pub_pem = PUB.read_text().strip()
    receipt = {
        "schema_version": 1,
        "type": "epoch_checkpoint",
        "genesis_version": "v2.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "author": "Jesse McMillen / One Human Family",
        "author_pubkey_ed25519": pub_pem,
        "parent_receipt": V1_2_PARENT,
        "parent_version": "v1.2",
        "statement": "Epoch checkpoint. Consolidates all OpenRoot state (genesis chain + founding docs + proofs + pod garden + tool suite + receipt cache + mistake log) into a single merkle root. Future receipts chain from this. The v1.x chain is preserved as historical record (the founding epoch). v2.x is the operational epoch.",
        "epoch_root": epoch_root,
        "subsystems": subsystems,
        "doctrine": [
            "The receipt is the constitution.",
            "Verifiers are pure code. Models propose. Code disposes.",
            "Receipts are canonical and independently verifiable.",
            "Act as One Human Family. Cut what harms. Grow what heals.",
            "Epoch checkpoints consolidate state. The chain stays honest."
        ],
    }
    
    receipt_bytes = canonical(receipt)
    receipt_id = hashlib.sha256(receipt_bytes).hexdigest()
    print(file=sys.stderr)
    print(f"[gate] STAGE B — canonical receipt constructed", file=sys.stderr)
    print(f"  canonical bytes: {len(receipt_bytes)}", file=sys.stderr)
    print(f"  receipt_id (sha256): {receipt_id}", file=sys.stderr)
    print(f"  epoch_root: {epoch_root}", file=sys.stderr)
    
    print(file=sys.stderr)
    print(f"[gate] STAGE C — sign with Ed25519", file=sys.stderr)
    sig = sign(receipt_bytes)
    print(f"  signature length: {len(sig)} bytes", file=sys.stderr)
    
    print(file=sys.stderr)
    print(f"[gate] STAGE D — verify with public key", file=sys.stderr)
    ok, out = verify(receipt_bytes, sig)
    if ok:
        print(f"  [banked] {out.strip()}", file=sys.stderr)
    else:
        print(f"  [held] verify failed: {out}", file=sys.stderr)
        sys.exit(1)
    
    print(file=sys.stderr)
    print(f"[gate] STAGE E — write + disk-verify", file=sys.stderr)
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    SIG.write_bytes(sig)
    
    loaded = json.loads(RECEIPT.read_text())
    loaded_bytes = canonical(loaded)
    loaded_id = hashlib.sha256(loaded_bytes).hexdigest()
    ok2, _ = verify(loaded_bytes, SIG.read_bytes())
    if loaded_id == receipt_id and ok2:
        print(f"  [banked] disk verify OK", file=sys.stderr)
    else:
        print(f"  [held] disk verify failed", file=sys.stderr)
        sys.exit(1)
    
    print(file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("OPENROOT v2.0 EPOCH CHECKPOINT SEALED", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"  receipt_id:     {receipt_id}", file=sys.stderr)
    print(f"  timestamp:     {receipt['timestamp']}", file=sys.stderr)
    print(f"  parent_receipt: {V1_2_PARENT}", file=sys.stderr)
    print(f"  epoch_root:     {epoch_root}", file=sys.stderr)
    print(file=sys.stderr)
    print(f"GENESIS_V2_0_ID={receipt_id}", file=sys.stderr)
    print(f"GENESIS_V2_0_TS={receipt['timestamp']}", file=sys.stderr)
    print(f"GENESIS_V2_0_EPOCH_ROOT={epoch_root}", file=sys.stderr)
    print(f"GENESIS_V2_0_ID_STDOUT={receipt_id}")

if __name__ == "__main__":
    main()
