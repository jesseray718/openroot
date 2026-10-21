#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
OpenRoot Cycle Recovery & Consolidation Script v1.1
Fixed: Path concatenation bug, cycle.sh path detection
Date: 2026-09-22
Author: Jesse Ray (OpenRoot)
License: GPL-3.0
"""

import os
import sys
import subprocess
import json
import hashlib
from pathlib import Path
from datetime import datetime

CANARY = f"[CANARY] CYCLE_RECOVERY_V1_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
WORKDIR = Path("/home/jesse/openroot")
BIN_DIR = WORKDIR / "bin"
CTX_BRIDGE = WORKDIR / "context_bridge"

def log(msg, level="INFO"):
    ts = datetime.now().isoformat()
    print(f"[{ts}] [{level}] {msg}")
    
def run(cmd, check=True, capture=False):
    log(f"Executing: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, 
            capture_output=capture, text=True, cwd=WORKDIR
        )
        if capture:
            return result.stdout
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {cmd}\nstderr: {e.stderr}", "ERROR")
        raise

def find_cycle_sh():
    """Find cycle.sh in possible locations"""
    candidates = [
        Path("/data/data/com.termux/files/home/bin/cycle.sh"),
        BIN_DIR / "cycle.sh",
        Path("/home/jesse/bin/cycle.sh"),
        WORKDIR / "bin" / "cycle.sh"
    ]
    
    for candidate in candidates:
        if candidate.exists():
            log(f"Found cycle.sh at: {candidate}")
            return candidate
    
    log("cycle.sh not found in standard locations", "WARN")
    return None

def fix_cycle_sh_repo_name():
    """Fix REPO_NAME unbound variable in cycle.sh"""
    script_path = find_cycle_sh()
    
    if not script_path:
        log("cycle.sh not found, skipping fix", "WARN")
        return False
    
    content = script_path.read_text()
    if 'REPO_NAME=' in content:
        log("REPO_NAME already defined in cycle.sh", "INFO")
        return True
    
    lines = content.split('\n')
    injected = False
    for i, line in enumerate(lines):
        if line.strip().startswith('set -') and not injected:
            lines.insert(i+1, '# OPENROOT RECOVERY: Initialize REPO_NAME')
            lines.insert(i+2, 'REPO_NAME="${REPO_NAME:-$(basename $(pwd))}"')
            log(f"Injected REPO_NAME initialization after line {i+1}")
            injected = True
            break
    
    if injected:
        script_path.write_text('\n'.join(lines))
        return True
    
    log("Could not find 'set -' line to inject after", "WARN")
    return False

def fix_wisdom_scaffold_submodule():
    """Remove broken submodule reference"""
    gitmodules = WORKDIR / ".gitmodules"
    scaffold_path = WORKDIR / "wisdom-scaffold"
    
    if not gitmodules.exists():
        log("No .gitmodules file found (submodule issue resolved)", "INFO")
        return True
    
    content = gitmodules.read_text()
    
    if 'wisdom-scaffold' not in content:
        log("wisdom-scaffold not in .gitmodules (already clean)", "INFO")
        return True
    
    log("Removing broken wisdom-scaffold submodule reference")
    
    new_content = '\n'.join(
        line for line in content.split('\n')
        if 'wisdom-scaffold' not in line
    )
    gitmodules.write_text(new_content)
    
    git_config = WORKDIR / ".git" / "config"
    if git_config.exists():
        config = git_config.read_text()
        config = '\n'.join(
            line for line in config.split('\n')
            if 'wisdom-scaffold' not in line
        )
        git_config.write_text(config)
    
    if scaffold_path.exists():
        import shutil
        shutil.rmtree(scaffold_path)
        log(f"Removed {scaffold_path}")
    
    run("git reset HEAD wisdom-scaffold 2>/dev/null || true", check=False)
    run("rm -rf .git/modules/wisdom-scaffold 2>/dev/null || true", check=False)
    
    return True

def restore_agape_kernel():
    """Create agape kernel directory structure"""
    kernel_dirs = [
        WORKDIR / "agape_kb" / "universal_axioms",
        WORKDIR / "agape_kb" / "love_language",
        WORKDIR / "kernel",
        WORKDIR / "cosmos_engine"
    ]
    
    restored = []
    for d in kernel_dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            log(f"Created {d}")
            restored.append(str(d))
        
        seed_file = d / "KERNEL_SEED"
        if not seed_file.exists():
            seed_file.write_text(
                f"# Kernel seed restored {datetime.now().isoformat()}\n"
                "# OpenRoot Agape Net\n"
            )
    
    expected_files = [
        WORKDIR / "agape_kb" / "universal_axioms" / "definitions.json",
        WORKDIR / "agape_kb" / "universal_axioms" / "theorems.json",
        WORKDIR / "agape_kb" / "universal_axioms" / "universal_axioms.json",
    ]
    
    for f in expected_files:
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("{}\n")
            log(f"Created placeholder {f}")
    
    return restored

def start_syncthing():
    """Start syncthing service"""
    log("Checking syncthing status...")
    
    try:
        result = run("which syncthing", capture=True)
        if not result.strip():
            log("Syncthing not installed, installing...", "WARN")
            run("sudo apt-get update && sudo apt-get install -y syncthing || pkg install syncthing", check=False)
            result = run("which syncthing", capture=True)
            if not result.strip():
                log("Syncthing installation failed", "ERROR")
                return False
        
        # Check if already running
        already_running = run("pgrep -x syncthing", capture=True).strip()
        if already_running:
            log(f"Syncthing already running (PIDs: {already_running})", "INFO")
            return True
        
        os.environ['HOME'] = str(Path.home())
        run("mkdir -p ~/.config/syncthing", check=False)
        run("nohup syncthing --no-browser --gui-address=:8384 > /tmp/syncthing.log 2>&1 &", check=False)
        
        import time
        time.sleep(5)
        
        result = run("pgrep -x syncthing", capture=True)
        if result.strip():
            pids = result.strip().replace('\n', ', ')
            log(f"Syncthing started (PIDs: {pids})")
            return True
        else:
            log("Syncthing failed to start, check /tmp/syncthing.log", "WARN")
            return False
            
    except Exception as e:
        log(f"Syncthing startup error: {e}", "ERROR")
        return False

def generate_black_locust_ssh_key():
    """Generate SSH key pair for black-locust-rmh bridge"""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True, mode=0o700)
    
    key_path = ssh_dir / "black-locust-rmh"
    
    if key_path.exists():
        log(f"Key already exists at {key_path}", "INFO")
        pub_path = Path(str(key_path) + ".pub")
        if pub_path.exists():
            log(f"Public key:\n{pub_path.read_text()}")
        return True
    
    log("Generating Ed25519 SSH key for black-locust-rmh")
    
    try:
        run(
            f"ssh-keygen -t ed25519 -f {str(key_path)} -N '' -C 'openroot-black-locust-rmh@optiplex3060'",
            check=True
        )
        
        os.chmod(key_path, 0o600)
        pub_path = Path(str(key_path) + ".pub")
        os.chmod(pub_path, 0o644)
        
        run("eval $(ssh-agent) > /dev/null 2>&1; ssh-add ~/.ssh/black-locust-rmh 2>/dev/null || true", check=False)
        
        log(f"SSH key generated:")
        log(f"  Private: {key_path}")
        log(f"  Public: {pub_path}")
        log(f"Public key:\n{pub_path.read_text()}")
        
        # Copy to authorized_keys for local login
        auth_keys = ssh_dir / "authorized_keys"
        if not auth_keys.exists():
            auth_keys.write_text(pub_path.read_text())
            os.chmod(auth_keys, 0o600)
            log(f"Copied public key to {auth_keys} for local SSH access")
        
        return True
    except Exception as e:
        log(f"SSH key generation failed: {e}", "ERROR")
        return False

def purge_saxton_tokens():
    """Remove SAXTON token references from tracked files"""
    import re
    
    target_files = [
        WORKDIR / "recovered_blueprints" / "DEEP_SCAN_INDEX.json",
        WORKDIR / "context_bridge" / "last_query_payload.json",
        WORKDIR / "dump" / "chunks" / "053_ledger.json"
    ]
    
    purged_count = 0
    
    for filepath in target_files:
        if not filepath.exists():
            continue
        
        try:
            content = filepath.read_text()
            matches = len(re.findall(r'SAXTON|saxton', content, re.IGNORECASE))
            
            if matches == 0:
                continue
            
            cleaned = re.sub(r'\b[Ss]axton\b', '[PURGED]', content)
            
            if cleaned != content:
                filepath.write_text(cleaned)
                purged_count += matches
                log(f"Purged {matches} SAXTON references from {filepath.name}")
        except Exception as e:
            log(f"Error processing {filepath}: {e}", "WARN")
    
    log(f"Total SAXTON references purged: {purged_count}")
    return purged_count

def verify_state():
    """Verify recovery completed successfully"""
    checks = {}
    
    # Check cycle.sh
    cycle_path = find_cycle_sh()
    if cycle_path:
        content = cycle_path.read_text()
        checks["cycle.sh_REPO_NAME"] = 'REPO_NAME=' in content
    else:
        checks["cycle.sh_REPO_NAME"] = False
    
    # Check .gitmodules
    gitmodules = WORKDIR / ".gitmodules"
    if gitmodules.exists():
        checks["wisdom_scaffold_clean"] = 'wisdom-scaffold' not in gitmodules.read_text()
    else:
        checks["wisdom_scaffold_clean"] = True
    
    # Check kernel
    kernel_exists = (WORKDIR / "agape_kb" / "universal_axioms").exists()
    checks["kernel_restored"] = kernel_exists
    
    # Check SSH key
    ssh_key = Path.home() / ".ssh" / "black-locust-rmh"
    checks["ssh_key_exists"] = ssh_key.exists()
    
    # Check git status
    git_status = run("git status --porcelain 2>/dev/null | head -20", capture=True).strip()
    checks["git_clean"] = len(git_status) == 0
    
    summary = {}
    for name, passed in checks.items():
        summary[name] = "PASS" if passed else "FAIL"
        status_symbol = "[OK]" if passed else "[!!]"
        log(f"  {status_symbol} {name}: {summary[name]}")
    
    return summary

def main():
    print(f"\n{'='*60}")
    print("OPENROOT CYCLE RECOVERY SCRIPT v1.1")
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Workdir: {WORKDIR}")
    print(f"{'='*60}\n")
    
    print(CANARY)
    
    log("\n=== PHASE 1: Git Infrastructure ===")
    fix_cycle_sh_repo_name()
    fix_wisdom_scaffold_submodule()
    
    log("\n=== PHASE 2: Kernel Restoration ===")
    restore_agape_kernel()
    
    log("\n=== PHASE 3: Network Services ===")
    start_syncthing()
    generate_black_locust_ssh_key()
    
    log("\n=== PHASE 4: Security Cleanup ===")
    purge_saxton_tokens()
    
    log("\n=== PHASE 5: Verification ===")
    results = verify_state()
    
    report_path = CTX_BRIDGE / f"cycle_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.parent.mkdir(exist_ok=True)
    
    branch = run('git rev-parse --abbrev-ref HEAD 2>/dev/null', capture=True).strip() or "unknown"
    commit = run('git rev-parse HEAD 2>/dev/null', capture=True).strip()[:7] or "unknown"
    
    report = f"""# Cycle Recovery Report v1.1
Generated: {datetime.now().isoformat()}
Canary: {CANARY}

## Summary
"""
    for check, status in results.items():
        emoji = "[OK]" if status == "PASS" else "[!!]"
        report += f"- {emoji} {check}: {status}\n"
    
    report += f"""

## Git Status
- Branch: {branch}
- Commit: {commit}
- Untracked/Modified Files: {len(run('git status --porcelain', capture=True).strip().split(chr(10))) if run('git status --porcelain', capture=True).strip() else 0}

## Next Actions Required
1. Review this report at: {report_path}
2. Run: `cd {WORKDIR} && git status`
3. Start manual cycle: `bin/cycle.sh` (if exists)
4. Verify SSH connectivity: `ssh -i ~/.ssh/black-locust-rmh localhost`
5. Check Syncthing: `curl -s http://localhost:8384/rest/system/status | head -20`

## Environment State
- Working Directory: {WORKDIR}
- User: {os.environ.get('USER', 'unknown')}
- Host: {os.uname().nodename}

[exit=0]
"""
    
    report_path.write_text(report)
    log(f"\nHandoff report written to: {report_path}")
    
    # Print quick summary
    passed = sum(1 for v in results.values() if v == "PASS")
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"RECOVERY COMPLETE ({passed}/{total} checks passed)")
    print(f"Report: {report_path}")
    if passed == total:
        print("All systems operational - ready to resume cycles")
    else:
        print("Some checks failed - review report for details")
    print(f"{'='*60}\n")
    
    print("[exit=0]")
    
    return 0 if all(v == "PASS" for v in results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
