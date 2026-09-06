#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

BIN_DIR = Path("/home/jesse/openroot/kit/bin")
REPORT_DIR = Path("/home/jesse/openroot/reports")

def run_pass(dry_run=True):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    mode_str = "DRY-RUN (Simulation)" if dry_run else "ACTIVE EXECUTION"
    print(f"\n==================================================")
    print(f"=== OpenRoot Closed-Loop Automation: {mode_str} ===")
    print(f"==================================================")
    
    print("\n--- [Phase 1] Auditing Local Repos & Structure ---")
    subprocess.run([sys.executable, str(BIN_DIR / "repo_audit.py")])
    
    print("\n--- [Phase 2] Auditing & Merging GitHub PRs ---")
    if not dry_run:
        subprocess.run([sys.executable, str(BIN_DIR / "pr_forge.py")])
    else:
        print("[*] Simulation Mode: Skipping destructive PR merges. Review generated scripts.")

    manifest_path = REPORT_DIR / "pass_review_manifest.md"
    manifest_content = f"""# OpenRoot Automation Pass Manifest
**Execution Mode:** {mode_str}
**Host:** OptiPlex 3060 (`jesse@optiplex3060`)
**LLM Endpoint:** `http://127.0.0.1:8080/v1`

## System Topology & State
- **OptiPlex:** Workspace host, local 7B inference engine, git orchestrator.
- **A15 Phone:** Mobile operator terminal via SSH.
- **GitHub:** Remote repository mirror (`jesseray718`).

## Output Deliverables
1. Audit JSON: `/home/jesse/openroot/reports/audit_summary.json`
2. Generated Fix Scripts: `/home/jesse/openroot/reports/pr_fixes/`

To execute active modifications: `python3 /home/jesse/openroot/kit/bin/openroot_loop.py --execute`
"""
    manifest_path.write_text(manifest_content)
    print(f"\n[+] Manifest ready for AI verification: {manifest_path}")

if __name__ == "__main__":
    is_execute = "--execute" in sys.argv
    run_pass(dry_run=not is_execute)
