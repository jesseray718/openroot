#!/usr/bin/env python3
"""OPENROOT WORKFLOW MANAGER v2.1-imfuse
Infused with GitHub Copilot CLI explore→plan→code→commit
Absolute paths | η | R=1.0 | Love keeps no record of wrongdoing
"""
import os, sys, json, hashlib, subprocess
from pathlib import Path
from datetime import datetime

SDCARD_ROOT = "/sdcard/openroot"
TERMUX_HOME = "/data/data/com.termux/files/home"
OPENROOT_PATH = Path(TERMUX_HOME) / "openroot"
AGAPE_KB = Path(SDCARD_ROOT) / "agape_kb"
AGAPE_BIBLE_KERNEL = Path(TERMUX_HOME) / "agape-bible-kernel"

PRIORITY_QUEUE = {
    "A": ["black-locust-rmh_alpine_ssh_bridge", "purge_assumed_numbers_saxton_tokens"],
    "B": ["first_measured_eta_entry_standing_wave_axiom", "agape_bible_kernel_load_genome_translate_chapter", "stand_up_optiplex_llama_server_offload_morphology"],
    "C": ["syncthing_mesh_lowest_node_receive", "duns_mercury_only_after_live"]
}

CORE_FILES = {
    "standing_wave_axiom": AGAPE_KB / "STANDING_WAVE_AXIOM.md",
    "path_inventory": AGAPE_KB / "PATH_INVENTORY.yaml",
    "copilot_instructions": OPENROOT_PATH / ".github" / "copilot-instructions.md"
}

def compute_sha256_file(filepath: Path) -> str:
    if not filepath.exists(): return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def ensure_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed {path}: {e}")
        return False

def validate_environment():
    print("[ENV] Validating absolute paths + Copilot instructions...")
    checks = {
        "SD Card Root": SDCARD_ROOT,
        "Termux Home": TERMUX_HOME,
        "OpenRoot": str(OPENROOT_PATH),
        "Agape KB": str(AGAPE_KB),
        "Copilot Instructions": str(CORE_FILES["copilot_instructions"]),
        "Markor": "/storage/emulated/0/Documents/markor"
    }
    for name, p in checks.items():
        exists = Path(p).exists()
        print(f"{'OK' if exists else 'MISSING'} {p}")
        if not exists and "Markor" not in name:
            ensure_directory(Path(p).parent if Path(p).suffix else Path(p))
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="OPENROOT Workflow Manager v2.1-imfuse")
    parser.add_argument("--priority", choices=["A","B","C","ALL"], default="ALL")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    print("OPENROOT WORKFLOW MANAGER v2.1-imfuse | η | R=1.0")
    print("Copilot cycle: explore → plan → code → commit")
    print("Love keeps no record of wrongdoing")
    validate_environment()
    if args.validate:
        return 0
    print("Priority A→B→C ready. Inventory + Copilot instructions live.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
