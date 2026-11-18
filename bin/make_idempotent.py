#!/usr/init/env python3
import os
import re
from pathlib import Path

def audit_and_patch_script(file_path: Path):
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    modified = False
    
    if file_path.suffix == ".sh":
        if "set -euo pipefail" not in content and "set -u" not in content:
            lines = content.splitlines()
            if lines and lines[0].startswith("#!"):
                lines.insert(1, "set -euo pipefail")
                content = "\n".join(lines) + "\n"
                modified = True

    if file_path.suffix == ".py":
        if "CREATE TABLE " in content and "IF NOT EXISTS" not in content:
            content = re.sub(r"CREATE TABLE\s+([a-zA-Z0-9_]+)", r"CREATE TABLE IF NOT EXISTS \1", content, flags=re.IGNORECASE)
            modified = True

    if modified:
        file_path.write_text(content, encoding="utf-8")
        print(f"[+] Patched for idempotency: {file_path.name}")
    else:
        print(f"[=] Already idempotent or clean: {file_path.name}")

if __name__ == "__main__":
    bin_dir = Path("bin")
    if not bin_dir.exists():
        print("Error: 'bin/' directory not found in current path.")
        exit(1)
        
    print(f"Auditing scripts in {bin_dir.resolve()} for idempotency...")
    for script in bin_dir.glob("*"):
        if script.is_file() and script.suffix in [".sh", ".py"]:
            audit_and_patch_script(script)
    print("[+] Idempotency audit and patch complete.")
