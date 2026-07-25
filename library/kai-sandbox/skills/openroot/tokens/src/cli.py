#!/usr/bin/env python3
"""ACRE Validator CLI"""
import sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) if (os := __import__('os')) else None
from acre_validator import ACREValidator

def print_usage():
    print("""
ACRE Token Validator

Commands:
    submit <claimant> <description> <score> [<evidence_url>]
    approve <claim_id> <validator_name>
    list [pending|approved_for_mint|minted]
    show <claim_id>
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    v = ACREValidator()
    cmd = sys.argv[1]
    if cmd == "submit":
        if len(sys.argv) < 5:
            print("Usage: submit <claimant> <description> <score> [<evidence_url>]")
            sys.exit(1)
        evidence = [sys.argv[5]] if len(sys.argv) > 5 else []
        v.submit_claim(sys.argv[2], sys.argv[3], int(sys.argv[4]), evidence)
    elif cmd == "approve":
        if len(sys.argv) < 4:
            print("Usage: approve <claim_id> <validator_name>")
            sys.exit(1)
        v.approve_claim(sys.argv[2], sys.argv[3])
    elif cmd == "list":
        v.list_claims(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "show":
        found = None
        for c in v.claims:
            if c.id == sys.argv[2]:
                found = c
        print(json.dumps(found.to_dict(), indent=2)) if found else print(f"Not found: {sys.argv[2]}")
    else:
        print_usage()
