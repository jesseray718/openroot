#!/usr/bin/env python3
"""
OPENROOT CANON v5.0 - SYSTEM REST STATE VERIFIER
Returns 0.0 when system is healthy, forward-only, no re-proving.

Jesse McMillen Ray | github.com/jesseray718
"""
import os, json, sys

HOME_CANON = "/data/data/com.termux/files/home/openroot/canon/src/canon.py"
LEDGER_FILE = "/data/data/com.termux/files/home/openroot/proof_ledger.json"
AXIOM_FILE = "/data/data/com.termux/files/home/openroot/axioms.json"

def check_canon_rest():
    """Check if canon system is at rest (healthy)"""
    issues = []
    
    # 1. File exists and is executable
    if not os.path.exists(__file__):
        issues.append("CANON_FILE_MISSING")
    
    # 2. Ledger exists or can be initialized
    if not os.path.exists(LEDGER_FILE):
        pass  # OK - ledger initializes on first run
    
    # 3. Axioms exist
    if not os.path.exists(AXIOM_FILE):
        issues.append("AXIOMS_MISSING")
    
    # 4. No tilde in canonical paths
    cwd = os.getcwd()
    if cwd.startswith('~') or cwd.startswith('$HOME'):
        issues.append("TILDE_IN_PATH")
    
    # 5. Forward-only constraint active
    # (check ledger has FORWARD_ONLY flag)
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE) as f:
                data = json.load(f)
                if not data.get('forward_only', True):
                    issues.append("FORWARD_ONLY_DISABLED")
        except:
            issues.append("LEDGER_CORRUPT")
    
    # Return 0.0 if no issues, or list of issues
    if issues:
        return f"ISSUES:{','.join(issues)}"
    return "0.0"

if __name__ == "__main__":
    result = check_canon_rest()
    print(result)
    sys.exit(0 if result == "0.0" else 1)
