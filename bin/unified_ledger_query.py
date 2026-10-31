# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Frontend for unified agape+thermo ledger with semantic routing"""
import json, sqlite3, sys, hashlib
from pathlib import Path

DB = Path("/home/jesse/openroot/ledger/unified/unified_ledger.sqlite")

def sha256_short(data):
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def query(cmd, args=None):
    if not DB.exists():
        print("[held] unified ledger not built — run agape_thermo_merge_v1.py first")
        sys.exit(1)
    
    conn = sqlite3.connect(str(DB))
    
    if cmd == "find":
        q = args or ""
        print(f"[gate] semantic search: {q} (nomic embed pending)")
        
    elif cmd == "bridge":
        rows = conn.execute("""
            SELECT a.id, t.joules_total 
            FROM unified_entries a 
            LEFT JOIN unified_entries t ON t.domain='thermo'
            WHERE a.domain='agape'
        """).fetchall()
        if rows:
            for a_id, joules in rows:
                j_str = f"{joules:.0f}J" if joules else "0J"
            print(f"AGAPE {a_id}: linked thermo = {j_str}")
        else:
            print("[held] no agape-thermo bridges yet")
            
    elif cmd == "genesis":
        genesis = conn.execute("""
            SELECT id, payload FROM unified_entries WHERE kind='genesis'
        """).fetchone()
        if genesis:
            p = json.loads(genesis[1])
            print(f"Genesis: {genesis[0][:16]}")
            print(f"  Anchor: {p.get('anchor_term', 'N/A')}")
            print(f"  Claim: {p.get('hypothesis', {}).get('claim', 'N/A')}")
        else:
            print("[held] no genesis block found")
    
    conn.close()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "genesis"
    arg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    query(cmd, arg)
    print(f"[banked] unified query: {cmd}")
    print("[exit=0]")
