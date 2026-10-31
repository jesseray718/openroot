#!/usr/bin/env python3
"""
OpenRoot Mobile Sync Tracker v2.0
Identifies and tracks files synced from OptiPlex to A15 mobile node.

SPDX-License-Identifier: GPL-3.0-only
Author: Jesse McMillen Ray (OpenRoot)
"""

import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Configuration
OPTIPLEX_ROOT = "/home/jesse/openroot"
A15_SCP_PATTERN = r"scp\s+(\S+)\s+(?:jesse@)?(?:100\.122\.169\.43|a15|[^\s]*termux[^\s]*)"
TERMUX_PATH = "/data/data/com.termux/files/home/openroot"

SYNC_CATEGORIES = {
    "thermal_ledger": ["thermal_frontier", "thermal_balance", "thermal_"],
    "session_handoff": ["session-", "handoff", "context_bridge", "SARE"],
    "simulations": ["cascade", "simulation", "sim_", "agape_"],
    "router_logs": ["router", "lumo_exchange", "agent_", "bot_"],
    "documentation": ["SUPERLINEAR", "GOALS", "MASTER_TODO", "README", "methodology"],
    "lessons": ["lesson_", "mistake", "chain_"],
}


def sha256_file(filepath: str) -> Optional[str]:
    """Calculate SHA256 hash of file for integrity verification."""
    try:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def get_file_size_pretty(filepath: str) -> str:
    """Return human-readable file size."""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    except Exception:
        return "??"


def scan_for_sync_commands(log_dir: str) -> List[Dict]:
    """Scan session logs for SCP commands targeting A15."""
    sync_commands = []
    root_path = Path(log_dir)
    if not root_path.exists():
        return sync_commands
    for filepath in sorted(root_path.rglob('*')):
        if filepath.suffix not in ('.md', '.log', '.jsonl', '.txt'):
            continue
        try:
            content = filepath.read_text(errors='replace')
            for match in re.findall(A15_SCP_PATTERN, content):
                sync_commands.append({
                    'source': match,
                    'destination': 'A15 (Termux)',
                    'found_in': str(filepath),
                })
        except Exception:
            pass
    return sync_commands


def enumerate_sync_targets(root_dir: str = OPTIPLEX_ROOT) -> Dict[str, List[Dict]]:
    """Find all files eligible for A15 sync, categorized by type."""
    targets_by_category = {cat: [] for cat in SYNC_CATEGORIES}
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"[WARN] Root directory {root_dir} not found")
        return targets_by_category

    excluded_dirs = {'.venv', '.git', '__pycache__', 'node_modules', 'venv'}

    for filepath in root_path.rglob('*'):
        if filepath.is_dir():
            continue
        rel_path = str(filepath.relative_to(root_path))
        parts = rel_path.split(os.sep)
        if any(excluded in parts[:-1] for excluded in excluded_dirs):
            continue
        file_name = filepath.name
        for category, patterns in SYNC_CATEGORIES.items():
            if any(p in file_name for p in patterns):
                try:
                    stat = filepath.stat()
                    targets_by_category[category].append({
                        'path': rel_path,
                        'size': get_file_size_pretty(str(filepath)),
                        'sha256': sha256_file(str(filepath)),
                        'modified': datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat(),
                    })
                except Exception:
                    pass
                break

    return targets_by_category


def generate_sync_manifest(
    targets: Dict[str, List[Dict]],
    sync_commands: List[Dict],
    output_path: str = "data/mobile_sync_manifest.json",
) -> Dict:
    """Generate JSON manifest of all files eligible for A15 sync."""
    manifest = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'author': 'Jesse McMillen Ray',
        'source_host': 'optiplex3060',
        'target_host': 'a15-termux',
        'termux_path': TERMUX_PATH,
        'total_files': sum(len(v) for v in targets.values()),
        'scp_commands_found': len(sync_commands),
        'recent_sync_commands': sync_commands[-10:],
        'categories': {},
    }
    for category, files in targets.items():
        manifest['categories'][category] = {
            'count': len(files),
            'files': sorted(
                files, key=lambda x: x.get('modified', ''), reverse=True
            )[:20],
        }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return manifest


def render_sync_dashboard(manifest: Dict) -> str:
    """Render a formatted dashboard view of sync targets."""
    output = []
    bar = "=" * 70
    output.append(bar)
    output.append("  OPENROOT MOBILE SYNC DASHBOARD (OptiPlex -> A15)")
    output.append(f"  Generated: {manifest['generated_at']}")
    output.append(f"  Author: {manifest['author']}")
    output.append(bar)
    output.append("")
    output.append(f"  TOTAL FILES TRACKED: {manifest['total_files']}")
    output.append(f"  SCP COMMANDS FOUND IN LOGS: {manifest['scp_commands_found']}")
    output.append("")

    for category, data in manifest['categories'].items():
        if data['count'] > 0:
            output.append(f"  [{category.upper()}] ({data['count']} files)")
            output.append("-" * 50)
            for i, f in enumerate(data['files'][:5]):
                sha_short = f['sha256'][:16] if f['sha256'] else "N/A"
                output.append(f"    {i+1}. {f['path']}")
                output.append(
                    f"       Size: {f['size']}"
                    f" | Modified: {f['modified'].split('T')[0]}"
                )
                output.append(f"       Hash: {sha_short}...")
            output.append("")

    output.append(bar)
    output.append("  QUICK COPY COMMANDS FOR SCP TO A15:")
    output.append("-" * 50)
    sample_files = []
    for category in ['thermal_ledger', 'session_handoff', 'router_logs']:
        files = manifest['categories'].get(category, {}).get('files', [])
        if files:
            sample_files.append(files[0]['path'])
    for sf in sample_files[:3]:
        output.append(f"  scp {sf} <a15-host>:{TERMUX_PATH}/{os.path.dirname(sf)}")
    output.append("")
    output.append("[exit=0] SYNC_MANIFEST_V2")
    output.append(bar)
    return "\n".join(output)


def main():
    print("[SYNC_SCAN] Scanning OpenRoot for A15 sync targets...")

    targets = enumerate_sync_targets(OPTIPLEX_ROOT)
    sync_commands = scan_for_sync_commands(
        os.path.join(OPTIPLEX_ROOT, "context_bridge")
    )

    manifest = generate_sync_manifest(targets, sync_commands)
    dashboard = render_sync_dashboard(manifest)
    print(dashboard)

    md_path = os.path.join(OPTIPLEX_ROOT, "data", "mobile_sync_dashboard.md")
    with open(md_path, 'w') as f:
        f.write("# OpenRoot Mobile Sync Dashboard\n\n```\n")
        f.write(dashboard)
        f.write("\n```\n")

    print(f"\n[banked] Manifest: data/mobile_sync_manifest.json")
    print(f"[banked] Dashboard: data/mobile_sync_dashboard.md")


if __name__ == "__main__":
    main()
