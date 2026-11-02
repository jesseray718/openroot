#!/usr/bin/env python3
"""
OPENROOT SYNERGETIC WIRING ENGINE
Performs non-destructive discovery, classification, and metadata indexing
of all workspace artifacts (scripts, docs, data, blueprints, BOMs).
Target Metrics: R=1, C=0 (Zero-coordination execution)
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone

def run_synergetic_wiring():
    print("[*] Initializing OpenRoot Synergetic Wiring Protocol...")
    root_dir = Path(".")
    
    # Define file categories to weave together
    extensions = {
        'scripts': ['.py', '.sh', '.cu', '.comp', '.cpp', '.h', '.hpp'],
        'docs_and_txt': ['.md', '.txt'],
        'data_and_boms': ['.json', '.tsv', '.csv', '.sql', '.yaml', '.yml'],
        'build_and_configs': ['.cmake', '.make', 'config']
    }
    
    inventory = {cat: [] for cat in extensions}
    inventory['miscellaneous'] = []
    
    total_files = 0
    for path in root_dir.rglob("*"):
        if path.is_file() and not any(part.startswith(('.', 'venv', '__pycache__')) for part in path.parts):
            if 'inbox/friction_triage' in path.parts or 'pods_garden' in path.parts:
                continue # Skip isolated quarantine/pods for core wiring pass
            
            ext = path.suffix.lower()
            matched = False
            for cat, exts in extensions.items():
                if ext in exts or path.name in exts:
                    inventory[cat].append(str(path))
                    matched = True
                    break
            if not matched:
                inventory['miscellaneous'].append(str(path))
            total_files += 1

    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine": "synergetic_wiring_v1",
        "metrics": {"R": 1, "C": 0},
        "total_indexed_artifacts": total_files,
        "categories": {cat: len(files) for cat, files in inventory.items()},
        "inventory_map": inventory
    }
    
    output_path = Path("data/thermodynamics/synergetic_wiring_manifest.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"[✔] Synergetic wiring complete. Indexed {total_files} active workspace artifacts.")
    print(f"[✔] Manifest compiled and saved to {output_path}")

    # Log to contribution ledger
    ledger_entry = {
        "timestamp": manifest["timestamp"],
        "event": "synergetic_wiring_mesh_built",
        "metrics": {"R": 1, "C": 0},
        "status": "mesh_unified"
    }
    with open("data/thermodynamics/contribution_ledger.jsonl", "a") as f:
        f.write(json.dumps(ledger_entry) + "\n")
    print("[✔] Wiring event logged to contribution ledger.")

if __name__ == "__main__":
    run_synergetic_wiring()
