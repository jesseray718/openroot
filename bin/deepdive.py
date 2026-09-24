#!/usr/bin/env python3
"""
deepdive.py - Scans all JSONL ledgers for content
Jesse Ray (OpenRoot) - GPL-3.0
"""

import json
import glob
import os
from pathlib import Path

BASE = Path("/home/jesse/openroot")
LEDGER_GLOBS = [
    "data/**/*.jsonl",
    "context_bridge/**/*.jsonl",
    "data/sdcard-sync/**/ledger.jsonl",
]

def scan_ledgers():
    """Discover all JSONL files and report stats"""
    results = []
    for pattern in LEDGER_GLOBS:
        for f in glob.glob(str(BASE / pattern), recursive=True):
            p = Path(f)
            try:
                with open(p) as fh:
                    lines = [l for l in fh if l.strip()]
                    size = p.stat().st_size
                    results.append({
                        "path": str(p.relative_to(BASE)),
                        "lines": len(lines),
                        "bytes": size,
                        "first_hash": None
                    })
                    if lines:
                        h = lines[0][:80] if len(lines[0]) > 80 else lines[0]
                        results[-1]["sample"] = h[:64] + "..." if len(h) > 64 else h
            except Exception as e:
                results.append({"path": str(p.relative_to(BASE)), "error": str(e)})
    
    # Sort by size desc
    results.sort(key=lambda x: x.get("bytes", 0), reverse=True)
    return results

def main():
    print("=== DEEPDIVE LEDGER SCAN ===")
    ledgers = scan_ledgers()
    
    total_bytes = sum(r.get("bytes", 0) for r in ledgers)
    total_lines = sum(r.get("lines", 0) for r in ledgers)
    
    print(f"\nFound {len(ledgers)} ledger files")
    print(f"Total size: {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
    print(f"Total entries: {total_lines:,}")
    
    print("\nTOP 10 BY SIZE:")
    for i, r in enumerate(ledgers[:10], 1):
        path = r["path"]
        sz = r.get("bytes", 0)
        ln = r.get("lines", 0)
        sample = r.get("sample", "")
        err = r.get("error", "")
        
        if err:
            print(f"  {i}. ERROR: {path} - {err}")
        else:
            print(f"  {i}. {sz:>10,}B  {ln:>8,}  {path[:50]}")
            if sample:
                print(f"      {sample}")
    
    # Special check for parallel_ideas
    pi_path = BASE / "data/parallel_ideas.jsonl"
    if pi_path.exists():
        size = pi_path.stat().st_size
        with open(pi_path) as f:
            lines = len([l for l in f if l.strip()])
        print(f"\n[KEY] parallel_ideas.jsonl: {size:,}B ({size/1024:.1f} KB), {lines} entries")

if __name__ == "__main__":
    main()
