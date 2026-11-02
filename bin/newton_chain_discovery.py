#!/usr/bin/env python3
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_OUTPUT = "data/discovery_chain.jsonl"
ALLOWED_EXTENSIONS = {".md", ".txt", ".rst", ".html"}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def get_previous_chain_tip(output_path: Path) -> Optional[str]:
    if not output_path.exists(): return None
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines: return json.loads(lines[-1].strip()).get("hash")
    except (json.JSONDecodeError, OSError, KeyError):
        return None
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", nargs="+", type=str, default=None)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    roots = [Path(r) for r in args.roots] if args.roots else [Path("/home/jesse/aerocement-selected-ubf7nZRr/documents")]
    output_path = Path(args.output)
    print(f"[info] Discovery target initialized to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
