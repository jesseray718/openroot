#!/usr/bin/env python3
"""generate_manifest_v2.py — dual-hash manifest builder (supersedes
generate_manifest.py v1).

Differences from v1:
  - errors are COUNTED and reported, never silently swallowed
  - skips databases/caches/hidden dirs (raw evidence stays untouched)
  - atomic write (tmp + rename): a crash never leaves a half manifest
  - hashes: SHA-256 always; BLAKE3 when the module exists, else
    SHA3-256 tagged "fallback_sha3_"

Usage:
  python3 generate_manifest_v2.py [DIR]     # default: current dir
"""
import hashlib
import json
import os
import sys

SKIP_FILES = {"manifest.json", "manifest.json.tmp"}
SKIP_DIRS = {"__pycache__", ".venv", ".git"}
SKIP_EXT = (".db", ".db-wal", ".db-shm", ".db-journal", ".sqlite3")


def compute_hashes(path, use_blake3):
    sha256 = hashlib.sha256()
    if use_blake3:
        import blake3
        b3 = blake3.blake3()
    else:
        b3 = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            sha256.update(chunk)
            b3.update(chunk)
    hexd = b3.hexdigest()
    if use_blake3:
        return sha256.hexdigest(), hexd
    return sha256.hexdigest(), "fallback_sha3_" + hexd


def main(root):
    root = os.path.abspath(root)
    try:
        import blake3  # noqa: F401
        use_blake3 = True
    except ImportError:
        use_blake3 = False

    assets, errors, total_bytes, count = [], 0, 0, 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name in SKIP_FILES or name.endswith(SKIP_EXT):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            count += 1
            try:
                st = os.stat(full)
                sha, b3 = compute_hashes(full, use_blake3)
                assets.append({
                    "file_path": rel,
                    "size_bytes": st.st_size,
                    "sha256": sha,
                    "blake3": b3,
                })
                total_bytes += st.st_size
            except Exception as e:
                errors += 1
                assets.append({"file_path": rel, "error": repr(e)})

    payload = {
        "schema": "openroot_manifest_v2",
        "root": os.path.basename(root),
        "total_files": count - errors,
        "errors": errors,
        "total_bytes": total_bytes,
        "hash_mode": "blake3" if use_blake3 else "sha3_fallback",
        "assets": assets,
    }
    tmp = os.path.join(root, "manifest.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    os.replace(tmp, os.path.join(root, "manifest.json"))
    print("MANIFEST_OK files=%d errors=%d bytes=%d hash_mode=%s root=%s"
          % (count - errors, errors, total_bytes,
             "blake3" if use_blake3 else "sha3_fallback", root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
