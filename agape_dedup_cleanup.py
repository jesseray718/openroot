#!/usr/bin/env python3
import os, json
def execute_dedup_cleanup():
    report_path = "workareas/release/duplicate_scan_report.json"
    if not os.path.exists(report_path):
        print(f"[error] Duplicate scan report not found")
        return
    print("[CLEANUP] Loading duplicate scan report...")
    with open(report_path, "r") as f:
        report = json.load(f)
    duplicate_groups = report.get("duplicate_groups", {})
    if not duplicate_groups:
        print("[info] No redundant duplicate groups found. Buffer is already clean.")
        return
    buffer_dir = "workareas/storage_overhaul_buffer"
    removed_count = 0
    saved_bytes = 0
    print(f"[CLEANUP] Processing {len(duplicate_groups)} duplicate sets for safe pruning...")
    for file_hash, filenames in duplicate_groups.items():
        canonical = filenames[0]
        redundants = filenames[1:]
        print(f"  [canonical] Retaining: {canonical}")
        for filename in redundants:
            target_path = os.path.join(buffer_dir, filename)
            if os.path.exists(target_path):
                try:
                    file_size = os.path.getsize(target_path)
                    os.remove(target_path)
                    removed_count += 1
                    saved_bytes += file_size
                    print(f"    [-] Removed redundant: {filename}")
                except Exception as e:
                    print(f"    [warn] Failed to remove {filename}: {e}")
    print("========================================================")
    print(f"=== Deduplication Cleanup Complete (R=1, c=0)       ===")
    print(f"    Files Pruned : {removed_count}")
    print(f"    Space Saved  : {round(saved_bytes / 1024, 2)} KB")
    print("========================================================")
if __name__ == "__main__":
    execute_dedup_cleanup()
