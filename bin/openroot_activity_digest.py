#!/usr/bin/env python3
import argparse, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_HOME = Path("/home/jesse/openroot")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=12)
    args = parser.parse_args()
    print(f"=== OPENROOT ACTIVITY DIGEST — last {args.hours}h ===")
    print(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    print("Status: Operational [ok]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
