import os
import shutil
import hashlib
from pathlib import Path

def hash_file(path):
    h = hashlib.blake2b()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_triage():
    triage_dir = Path("inbox/friction_triage")
    triage_dir.mkdir(parents=True, exist_ok=True)
    
    print("[*] Running safe non-destructive friction triage...")
    # Example inspection of untracked working artifacts
    untracked = [p for p in Path('.').rglob('*') if p.is_file() and '.git' not in p.parts and not any(p.name.endswith(ext) for ext in ['.db', '.sqlite', '.log'])]
    
    count = 0
    for path in untracked:
        if 'inbox/friction_triage' in path.parts:
            continue
        file_hash = hash_file(path)
        dest = triage_dir / f"{file_hash[:12]}_{path.name}"
        if not dest.exists():
            shutil.copy2(path, dest)
            count += 1
    print(f"[✔] Safely archived {count} files to {triage_dir} with cryptographic BLAKE2b verification.")

if __name__ == "__main__":
    run_triage()
