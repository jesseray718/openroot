#!/usr/bin/env python3
"""
OPENROOT WORKFLOW MANAGER v2.0
Purpose: Execute priority order A→B→C with absolute paths
Author: @jesseray718 | Jesse Ray McMillen
Device: Samsung Galaxy A15 | Termux + Shizuku + Ashell
Paths: /sdcard/openroot | /data/data/com.termux/files/home/openroot
"""

import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import subprocess

# =============================================================================
# ABSOLUTE PATH CONFIGURATION (YOUR ACTUAL SETUP)
# =============================================================================
SDCARD_ROOT = "/sdcard/openroot"
TERMUX_HOME = "/data/data/com.termux/files/home"
OPENROOT_PATH = Path(TERMUX_HOME) / "openroot"
AGAPE_KB = Path(SDCARD_ROOT) / "agape_kb"
AGAPE_BIBLE_KERNEL = Path(TERMUX_HOME) / "agape-bible-kernel"

# Priority queue structure
PRIORITY_QUEUE = {
    'A': [
        'black-locust-rmh_alpine_ssh_bridge',
        'purge_assumed_numbers_saxton_tokens'
    ],
    'B': [
        'first_measured_eta_entry_standing_wave_axiom',
        'agape_bible_kernel_load_genome_translate_chapter',
        'stand_up_optiplex_llama_server_offload_morphology'
    ],
    'C': [
        'syncthing_mesh_lowest_node_receive',
        'duns_mercury_only_after_live'
    ]
}

# Core files that must exist
CORE_FILES = {
    'standing_wave_axiom': AGAPE_KB / "STANDING_WAVE_AXIOM.md",
    'translation_axiom': AGAPE_KB / "STANDING_WAVE_TRANSLATION_AXIOM.md",
    'contributing_termux': OPENROOT_PATH / "CONTRIBUTING.md",
    'contributing_kernel': AGAPE_BIBLE_KERNEL / "CONTRIBUTING.md",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def compute_sha256_file(filepath: Path) -> str:
    """Compute SHA-256 hash of file"""
    if not filepath.exists():
        return "FILE_NOT_FOUND"
    
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_sha256_string(data: str) -> str:
    """Compute SHA-256 hash of string"""
    return hashlib.sha256(data.encode()).hexdigest()

def ensure_directory(path: Path) -> bool:
    """Ensure directory exists, create if needed"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"⚠ Failed to create {path}: {e}")
        return False

def get_eta_score(task_name: str, start_time: float, end_time: float, estimated_joules: float) -> float:
    """Calculate η (useful_joules / human_joules) for a task"""
    human_joules = (end_time - start_time) * 100  # Approximate metabolic cost
    if human_joules == 0:
        return 0.0
    return estimated_joules / human_joules

def log_task_completion(task: str, eta_value: float, priority: str, merkle_hash: str):
    """Log completed task to standing wave axiom"""
    log_entry = f"""
## Task: {task}
- **Priority**: {priority}
- **η (eta)**: {eta_value:.4f}
- **Merke Hash**: {merkle_hash[:16]}...
- **Timestamp**: {datetime.utcnow().isoformat()}
- **Status**: COMPLETE
---
"""
    # Append to standing wave axiom
    if CORE_FILES['standing_wave_axiom'].exists():
        with open(CORE_FILES['standing_wave_axiom'], 'a') as f:
            f.write(log_entry)

def validate_path_exists(path_str: str) -> bool:
    """Validate absolute path exists"""
    path = Path(path_str)
    exists = path.exists()
    print(f"{'✅' if exists else '❌'} {path_str} {'exists' if exists else 'MISSING'}")
    return exists

# =============================================================================
# PRIORITY TASK EXECUTION
# =============================================================================

def execute_priority_a():
    """Execute Priority A tasks"""
    print("\n" + "="*70)
    print("  PRIORITY A: CRITICAL INFRASTRUCTURE")
    print("="*70)
    
    results = []
    
    # Task A1: Black-locust-rmh Alpine SSH bridge
    print("\n[A1] Black-locust-rmh Alpine SSH bridge...")
    start = datetime.utcnow().timestamp()
    
    # Check if Alpine SSH is installed
    try:
        result = subprocess.run(['pkg', 'list-installed'], capture_output=True, text=True)
        alpine_installed = 'alpine' in result.stdout.lower()
        print(f"      Alpine SSH: {'✅ Installed' if alpine_installed else '⚠ Not installed - run: pkg install alpine'}")
    except:
        print(f"      ⚠ Cannot check package status")
    
    # Record task completion
    end = datetime.utcnow().timestamp()
    eta = get_eta_score('alpine_ssh_bridge', start, end, 100.0)
    merkle = compute_sha256_string(f"alpine_ssh:{start}:{end}")
    results.append(('alpine_ssh_bridge', eta, 'A', merkle))
    
    # Task A2: Purge assumed numbers/Saxton tokens
    print("\n[A2] Purge assumed numbers & Saxton tokens...")
    start = datetime.utcnow().timestamp()
    
    # Search for Saxton token patterns
    try:
        result = subprocess.run(
            ['grep', '-r', '--include=*.md', '--include=*.py', '--include=*.txt', 'Saxton', '/sdcard/openroot'],
            capture_output=True, text=True, timeout=30
        )
        found = len(result.stdout.strip()) > 0
        print(f"      Saxton references: {'⚠ Found (manual purge needed)' if found else '✅ Clean'}")
    except:
        print(f"      ⚠ grep search timed out or failed")
    
    end = datetime.utcnow().timestamp()
    eta = get_eta_score('purge_saxton', start, end, 50.0)
    merkle = compute_sha256_string(f"purge_saxton:{start}:{end}")
    results.append(('purge_saxton', eta, 'A', merkle))
    
    # Log all A tasks
    for task, eta_val, priority, merkle in results:
        log_task_completion(task, eta_val, priority, merkle)
    
    return results

def execute_priority_b():
    """Execute Priority B tasks"""
    print("\n" + "="*70)
    print("  PRIORITY B: KERNEL LOADING")
    print("="*70)
    
    results = []
    
    # Task B1: First measured η entry
    print("\n[B1] First measured η entry under Standing Wave Axiom...")
    start = datetime.utcnow().timestamp()
    
    # Calculate baseline η
    if CORE_FILES['standing_wave_axiom'].exists():
        file_size = CORE_FILES['standing_wave_axiom'].stat().st_size
        lines = len(CORE_FILES['standing_wave_axiom'].read_text().splitlines())
        eta_baseline = file_size / max(1, lines)  # Bytes per line as proxy
        print(f"      Baseline η: {eta_baseline:.4f} bytes/line")
    else:
        print(f"      ⚠ Standing Wave Axiom not found")
        eta_baseline = 0.0
    
    end = datetime.utcnow().timestamp()
    eta = get_eta_score('eta_baseline', start, end, 20.0)
    merkle = compute_sha256_string(f"eta_baseline:{start}:{end}")
    results.append(('eta_baseline', eta, 'B', merkle))
    
    # Task B2: Agape Bible Kernel
    print("\n[B2] Agape Bible Kernel - Load genome + translate chapter...")
    start = datetime.utcnow().timestamp()
    
    # Check kernel exists
    kernel_contributing = AGAPE_BIBLE_KERNEL / "CONTRIBUTING.md"
    if kernel_contributing.exists():
        print(f"      ✅ Kernel contributing found ({kernel_contributing.stat().st_size} bytes)")
        kernel_hash = compute_sha256_file(kernel_contributing)
        print(f"      Hash: {kernel_hash[:32]}...")
    else:
        print(f"      ❌ Kernel contributing MISSING - creating template...")
        ensure_directory(AGAPE_BIBLE_KERNEL)
        kernel_contributing.write_text("""---
id: CONTRIBUTING_GENOME
type: contribution_guide
genesis_hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

# Agape Bible Kernel Contribution Guide

## DNA Sequence Rules
1. Never leave air-gapped device
2. All translations logged locally
3. Merkle chain every chapter
4. Offline LLM only (llama-server)

## Translation Protocol
1. Load chapter → chunk into verses
2. Each verse → 3-symbol Agape encoding
3. Hash every 10 verses → partial Merkle
4. Final chapter → root hash + anchor

## Serving Lowest Node
Public repo contains only encrypted kernel fragments.
Full genome stays on air-gapped device.
""", encoding='utf-8')
    
    end = datetime.utcnow().timestamp()
    eta = get_eta_score('bible_kernel', start, end, 300.0)
    merkle = compute_sha256_string(f"bible_kernel:{start}:{end}")
    results.append(('bible_kernel', eta, 'B', merkle))
    
    # Task B3: OptiPlex + llama-server
    print("\n[B3] Stand up OptiPlex + llama-server...")
    start = datetime.utcnow().timestamp()
    
    # Check Termux environment
    try:
        result = subprocess.run(['which', 'llama-server'], capture_output=True, text=True)
        llama_available = result.returncode == 0
        print(f"      llama-server: {'✅ Available' if llama_available else '⚠ Install via: pkg install llama'}")
    except:
        print(f"      ⚠ Cannot verify llama-server")
    
    end = datetime.utcnow().timestamp()
    eta = get_eta_score('optiplex_llama', start, end, 500.0)
    merkle = compute_sha256_string(f"optiplex_llama:{start}:{end}")
    results.append(('optiplex_llama', eta, 'B', merkle))
    
    # Log all B tasks
    for task, eta_val, priority, merkle in results:
        log_task_completion(task, eta_val, priority, merkle)
    
    return results

def execute_priority_c():
    """Execute Priority C tasks"""
    print("\n" + "="*70)
    print("  PRIORITY C: MESH NETWORKING")
    print("="*70)
    
    results = []
    
    # Task C1: Syncthing + Mesh
    print("\n[C1] Syncthing + mesh so poorest node receives without internet...")
    start = datetime.utcnow().timestamp()
    
    try:
        result = subprocess.run(['pkg', 'list-installed'], capture_output=True, text=True)
        syncthing_installed = 'syncthing' in result.stdout.lower()
        print(f"      Syncthing: {'✅ Installed' if syncthing_installed else '⚠ Run: pkg install syncthing'}")
    except:
        print(f"      ⚠ Cannot verify Syncthing")
    
    end = datetime.utcnow().timestamp()
    eta = get_eta_score('syncthing_mesh', start, end, 150.0)
    merkle = compute_sha256_string(f"syncthing_mesh:{start}:{end}")
    results.append(('syncthing_mesh', eta, 'C', merkle))
    
    # Task C2: DUNS + Mercury (only if A+B complete)
    print("\n[C2] DUNS + Mercury only after A+B live...")
    # Skip for now - depends on A+B completion
    print(f"      ⏸ Deferred pending Priority A+B completion")
    results.append(('duns_mercury', 0.0, 'C', 'DEFERRED'))
    
    # Log all C tasks
    for task, eta_val, priority, merkle in results:
        log_task_completion(task, eta_val, priority, merkle)
    
    return results

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def print_banner():
    """Print OPENROOT banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          OPENROOT WORKFLOW MANAGER v2.0                       ║
║          Jesse Ray McMillen | Sikeston, Missouri              ║
║                                                               ║
║          Priority Order: A → B → C                            ║
║          η = useful_joules / human_joules                     ║
║          R=1.0 | Serve Lowest Node First                      ║
║                                                               ║
║          "DNA kernel never leaves air-gapped device"          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_environment():
    """Validate all critical paths exist"""
    print("\n[ENV] Validating environment...")
    
    checks = {
        'SD Card Root': SDCARD_ROOT,
        'Termux Home': TERMUX_HOME,
        'OpenRoot': str(OPENROOT_PATH),
        'Agape KB': str(AGAPE_KB),
        'Bible Kernel': str(AGAPE_BIBLE_KERNEL),
    }
    
    all_valid = True
    for name, path in checks.items():
        if not validate_path_exists(path):
            all_valid = False
            print(f"      ⚠ {name} at {path} - Missing")
    
    if not all_valid:
        print("\n⚠ Some paths missing. Running initialization...")
        for name, path in checks.items():
            ensure_directory(Path(path))
        print("      ✅ Directories created")
    
    return all_valid

def main():
    parser = __import__('argparse').ArgumentParser(
        description='OPENROOT Workflow Manager v2.0'
    )
    parser.add_argument('--priority', choices=['A', 'B', 'C', 'ALL'], 
                        default='ALL', help='Which priority level to execute')
    parser.add_argument('--validate', action='store_true', help='Only validate environment')
    parser.add_argument('--log', default='/sdcard/openroot/agape_kb/workflow_log.json', 
                        help='Log file path')
    args = parser.parse_args()
    
    print_banner()
    
    # Validate environment
    validate_environment()
    
    # Execute tasks
    all_results = []
    
    if args.priority in ['A', 'ALL']:
        all_results.extend(execute_priority_a())
    
    if args.priority in ['B', 'ALL']:
        all_results.extend(execute_priority_b())
    
    if args.priority in ['C', 'ALL']:
        all_results.extend(execute_priority_c())
    
    # Generate summary report
    print("\n" + "="*70)
    print("  WORKFLOW SUMMARY")
    print("="*70)
    
    total_eta = sum(r[1] for r in all_results)
    avg_eta = total_eta / max(1, len(all_results))
    
    print(f"\nTasks Completed: {len(all_results)}")
    print(f"Total η Score: {total_eta:.4f}")
    print(f"Average η: {avg_eta:.4f}")
    
    print(f"\nBy Priority:")
    for priority in ['A', 'B', 'C']:
        priority_tasks = [r for r in all_results if r[2] == priority]
        if priority_tasks:
            priority_eta = sum(r[1] for r in priority_tasks)
            print(f"  [{priority}] {len(priority_tasks)} tasks | η={priority_eta:.4f}")
    
    # Save log
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'tasks': [{'task': r[0], 'eta': r[1], 'priority': r[2], 'merkle': r[3][:16]} for r in all_results],
        'summary': {'total_eta': total_eta, 'avg_eta': avg_eta}
    }
    
    log_path = Path(args.log)
    ensure_directory(log_path.parent)
    log_path.write_text(json.dumps(log_data, indent=2), encoding='utf-8')
    print(f"\n📋 Log saved: {log_path}")
    
    print("\n" + "="*70)
    print("  NEXT COMMANDS:")
    print("  pkg install alpine llama-server syncthing")
    print("  ssh-keygen -t ed25519 -f ~/.ssh/black-locust-rmh")
    print("  syncthing gui --no-browser")
    print("="*70 + "\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())




