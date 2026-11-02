#!/usr/bin/env python3
"""
OPENROOT QR CODE SYSTEM COMPRESSOR & UNIVERSAL BOOTSTRAPPER
Aggregates repository state, computes core cryptographic manifests,
and generates a compact bootstrap payload for cross-platform deployment.
"""

import os
import json
import hashlib
from pathlib import Path

def compute_manifest():
    print("[*] Scanning repository core artifacts for QR compression...")
    manifest = {
        "project": "OpenRoot",
        "version": "1.0.0",
        "doi": "10.5281/zenodo.20549528",
        "metrics": {"R": 1, "C": 0},
        "core_files": {}
    }
    
    bin_dir = Path("bin")
    if bin_dir.exists():
        for script in bin_dir.glob("*.py"):
            manifest["core_files"][script.name] = hashlib.blake2b(script.read_bytes(), digest_size=16).hexdigest()
            
    serialized = json.dumps(manifest, sort_keys=True)
    root_hash = hashlib.blake2b(serialized.encode("utf-8"), digest_size=32).hexdigest()
    
    payload = {
        "root_hash": root_hash,
        "repo_url": "https://github.com/jesseray718/openroot.git",
        "manifest": manifest
    }
    
    compact_str = json.dumps(payload, separators=(',', ':'))
    print(f"[✔] System Compressed Manifest Size: {len(compact_str)} bytes")
    print(f"[✔] Root Cryptographic Hash: {root_hash}")
    
    # Save compact payload to disk
    out_path = Path("data/thermodynamics/qr_system_payload.json")
    with open(out_path, "w") as f:
        f.write(compact_str)
        
    print(f"[✔] Compact payload saved to {out_path}")
    print("\n--- DEPLOYMENT QR PAYLOAD STRING ---")
    print(compact_str)
    print("------------------------------------")

if __name__ == "__main__":
    compute_manifest()
