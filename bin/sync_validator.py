#!/usr/bin/env python3
"""
sync_validator.py - Compare ledgers across Termux/OptiPlex
Run on both devices, compare outputs
"""

import hashlib
import json
from pathlib import Path

# Paths differ by pane
import sys
IS_ANDROID = "termux" in sys.version.lower() or "/data/data/com.termux" in str(Path.home())

if IS_ANDROID:
    BASE = Path("/storage/emulated/0/openroot")
    LEDGERS = [
        "thermo_ledger/eta_moves.jsonl",
        "parallel_analysis/ledger/ideas.jsonl",
        "data/oracle_etha_ledger.jsonl",
    ]
else:
    BASE = Path("/home/jesse/openroot")
    LEDGERS = [
        "data/oracle_etha_ledger.jsonl",
        "data/parallel_ideas.jsonl",
        "context_bridge/audit_trail.jsonl",
    ]

def compute_file_hash(path):
    """SHA256 of file content, truncated to 16 chars"""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def scan_ledgers():
    results = []
    for ledger_rel in LEDGERS:
        full_path = BASE / ledger_rel
        exists = full_path.exists()
        size = full_path.stat().st_size if exists else 0
        line_count = 0
        first_hash = None
        
        if exists:
            with open(full_path) as f:
                lines = [l for l in f if l.strip()]
                line_count = len(lines)
                if lines:
                    try:
                        first_hash = hashlib.sha256(
                            lines[0].encode()
                        ).hexdigest()[:16]
                    except:
                        pass
        
        results.append({
            "path": ledger_rel,
            "exists": exists,
            "size": size,
            "lines": line_count,
            "first_entry_hash": first_hash
        })
    
    return results

def main():
    pane = "ANDROID" if IS_ANDROID else "OPTIPLEX"
    print(f"=== SYNC VALIDATOR [{pane}] ===")
    print(f"Base: {BASE}")
    print(f"Timestamp: {__import__('datetime').datetime.now().isoformat()}")
    
    results = scan_ledgers()
    
    print(f"\nLedger status ({len(results)} files):")
    for r in results:
        status = "✅" if r["exists"] else "❌"
        print(f"  {status} {r['path']}")
        print(f"      Size: {r['size']:,}B | Lines: {r['lines']:,}")
        if r["first_entry_hash"]:
            print(f"      Hash: {r['first_entry_hash']}")
    
    # Output JSON for comparison
    out = {
        "pane": pane,
        "results": results
    }
    print(f"\nJSON OUTPUT (for cross-compare):")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
