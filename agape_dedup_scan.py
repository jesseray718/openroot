#!/usr/bin/env python3
import os, hashlib, json, time
def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None
def scan_for_duplicates():
    buffer_dir = "workareas/storage_overhaul_buffer"
    if not os.path.exists(buffer_dir):
        print(f"[error] Storage buffer not found at {buffer_dir}")
        return
    print("[DEDUP] Scanning ingested storage buffer for cryptographic duplicates...")
    hash_map = {}
    total_files = 0
    for filename in os.listdir(buffer_dir):
        full_path = os.path.join(buffer_dir, filename)
        if os.path.isfile(full_path):
            total_files += 1
            file_hash = compute_sha256(full_path)
            if file_hash:
                hash_map.setdefault(file_hash, []).append(filename)
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    unique_count = len(hash_map)
    duplicate_count = sum(len(files) - 1 for files in duplicates.values())
    report = {
        "total_scanned": total_files,
        "unique_files": unique_count,
        "redundant_files_identified": duplicate_count,
        "duplicate_groups": duplicates,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    out_path = "workareas/release/duplicate_scan_report.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[ok] Scan complete. Scanned: {total_files} | Unique: {unique_count} | Redundant: {duplicate_count}")
    print(f"[ok] Duplicate scan report written to -> {out_path}")
if __name__ == "__main__":
    scan_for_duplicates()
