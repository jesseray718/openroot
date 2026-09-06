#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

REQUIRED_FILES = ["README.md", "LICENSE", "install.sh", ".github/workflows/ci.yml"]

INSTALLER_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

echo "[*] Initializing {repo_name}..."
if ! command -v python3 &>/dev/null; then
    echo "[!] Python3 is required."
    exit 1
fi

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
fi

echo "[+] {repo_name} installation and workspace setup complete."
"""

def audit_workspace(root_dir="/home/jesse/src"):
    base = Path(root_dir)
    if not base.exists():
        base.mkdir(parents=True, exist_ok=True)

    audit_report = []

    for repo in base.iterdir():
        if repo.is_dir() and (repo / ".git").exists():
            print(f"[*] Auditing local repo: {repo.name}")
            repo_health = {"repo": repo.name, "missing": [], "created": []}
            
            for req in REQUIRED_FILES:
                target = repo / req
                if not target.exists():
                    repo_health["missing"].append(req)
                    if req == "install.sh":
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(INSTALLER_TEMPLATE.format(repo_name=repo.name))
                        target.chmod(0o755)
                        repo_health["created"].append("install.sh")
            
            audit_report.append(repo_health)

    report_path = Path("/home/jesse/openroot/reports/audit_summary.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(audit_report, indent=2))
    print(f"[+] Repository structure audit complete -> {report_path}")

if __name__ == "__main__":
    audit_workspace()
