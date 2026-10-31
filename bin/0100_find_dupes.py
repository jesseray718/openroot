import os
import hashlib
import json
import sys

# Internal storage + your specific external SD card mount point
SEARCH_ROOTS = [
    "/sdcard",
    "/storage/0000-0000"
]

OUTPUT_FILE = "duplicate_report.json"

def get_hash(filepath, block_size=65536):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(block_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def scan_for_duplicates():
    size_map = {}
    print("Step 1: Scanning file system and grouping by file size...")
    
    total_scanned = 0
    for root_path in SEARCH_ROOTS:
        if not os.path.exists(root_path):
            print(f"Skipping unreadable root: {root_path}")
            continue
        print(f"Scanning root: {root_path}")
        for root, dirs, files in os.walk(root_path):
            # Exclude runtime system mounts & heavy build directories
            dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.venv', 'proc', 'sys', 'dev', 'Android')]
            
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    if os.path.islink(filepath):
                        continue
                    size = os.path.getsize(filepath)
                    if size == 0:
                        continue
                    
                    if size not in size_map:
                        size_map[size] = []
                    size_map[size].append(filepath)
                    
                    total_scanned += 1
                    if total_scanned % 10000 == 0:
                        print(f"Scanned {total_scanned} files...")
                except Exception:
                    pass

    print(f"\nCompleted initial scan. Total files scanned: {total_scanned}")
    
    candidates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    print(f"Found {len(candidates)} size collisions (potential duplicate sets).")

    print("\nStep 2: Hashing potential duplicate candidates...")
    duplicates = {}
    hash_count = 0
    
    for size, paths in candidates.items():
        hash_map = {}
        for path in paths:
            f_hash = get_hash(path)
            if f_hash:
                if f_hash not in hash_map:
                    hash_map[f_hash] = []
                hash_map[f_hash].append(path)
                hash_count += 1
                if hash_count % 500 == 0:
                    print(f"Hashed {hash_count} candidate files...")
        
        for f_hash, matched_paths in hash_map.items():
            if len(matched_paths) > 1:
                duplicates[f_hash] = {
                    "size_bytes": size,
                    "count": len(matched_paths),
                    "files": matched_paths
                }

    print(f"\nScan complete! Found {len(duplicates)} exact duplicate file sets.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, indent=2)
    
    print(f"Report saved to {OUTPUT_FILE}")

def summarize_dupes():
    if not os.path.exists(OUTPUT_FILE):
        print("No duplicate report found. Run 'python find_dupes.py --scan' first.")
        return

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_wasted_bytes = 0
    total_dupe_files = 0

    print(f"\n--- DUPLICATE SUMMARY (Top Matches) ---")
    for f_hash, info in list(data.items())[:15]:
        wasted = info['size_bytes'] * (info['count'] - 1)
        total_wasted_bytes += wasted
        total_dupe_files += info['count']
        
        print(f"\n[Size: {info['size_bytes'] / 1024:.2f} KB | Wasted Space: {wasted / 1024:.2f} KB]")
        for path in info['files']:
            print(f"  - {path}")

    print(f"\nTotal duplicate sets: {len(data)}")
    print(f"Estimated reclaimable space: {total_wasted_bytes / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        scan_for_duplicates()
        summarize_dupes()
    else:
        summarize_dupes()
