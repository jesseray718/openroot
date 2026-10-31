#!/usr/bin/env python3
"""Unified Agape+Thermo Ledger — merges semantic genesis chain with RAPL/POPW thermo accounting"""
import json, hashlib, sqlite3, sys, pathlib, datetime
from pathlib import Path

REPO = "/home/jesse/openroot"
AGAPE_LEDGER = Path(REPO + "/ledger/agape/chain.jsonl")
THERMO_LEDGER = REPO + "/openroot-edge/thermo_ledger.jsonl"
MERGED_DB = Path(REPO + "/ledger/unified/unified_ledger.sqlite")

def sha256_canonical(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()

def load_agape_records():
    if not AGAPE_LEDGER.exists():
        return []
    records = []
    for line in AGAPE_LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            records.append({
                "domain": "agape",
                "id": r["id"],
                "kind": r["kind"],
                "created_utc": r["created_utc"],
                "payload": r["payload"],
                "sha": r["id"]
            })
    return records

def load_thermo_blocks():
    if not Path(THERMO_LEDGER).exists():
        print("[held] thermo ledger not found at $THERMO_LEDGER")
        return []
    blocks = []
    for line in Path(THERMO_LEDGER).read_text(encoding="utf-8").splitlines():
        if line.strip():
            b = json.loads(line)
            blocks.append({
                "domain": "thermo",
                "id": b.get("id", sha256_canonical(b)),
                "kind": b.get("kind", "block"),
                "created_utc": b.get("created_utc", datetime.datetime.utcnow().isoformat()),
                "payload": {
                    "joules_generated": b.get("joules_generated", 0),
                    "joules_verified": b.get("joules_verified", 0),
                    "popw_proof": b.get("popw_proof", b.get("proof_of_physical_work")),
                    "rapl_source": b.get("source", "estimate"),
                    "block_index": b.get("index", b.get("block"))
                },
                "sha": b.get("id", sha256_canonical(b))
            })
    return blocks

def build_unified_db():
    MERGED_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(MERGED_DB))
    
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS unified_entries (
            id TEXT PRIMARY KEY,
            domain TEXT NOT NULL,
            kind TEXT NOT NULL,
            created_utc TEXT NOT NULL,
            payload TEXT NOT NULL,
            sha TEXT NOT NULL,
            agape_score REAL,
            joules_total REAL
        );
        CREATE TABLE IF NOT EXISTS cross_domain_links (
            source_id TEXT,
            target_id TEXT,
            link_type TEXT,
            weight REAL
        );
        CREATE INDEX IF NOT EXISTS idx_domain ON unified_entries(domain);
        CREATE INDEX IF NOT EXISTS idx_joules ON unified_entries(joules_total);
    """)
    
    all_entries = load_agape_records() + load_thermo_blocks()
    
    for entry in all_entries:
        agape_score = 1.0 if entry["domain"] == "agape" else 0.0
        joules_total = entry["payload"].get("joules_generated", 0) if entry["domain"] == "thermo" else 0.0
        
        conn.execute(
            "INSERT OR IGNORE INTO unified_entries VALUES (?,?,?,?,?,?,?,?)",
            (entry["id"], entry["domain"], entry["kind"], entry["created_utc"],
             json.dumps(entry["payload"], ensure_ascii=False), entry["sha"],
             agape_score, joules_total)
        )
    
    conn.commit()
    print(f"[banked] unified db built with {len(all_entries)} entries")
    return conn

def query_unified(cmd="show", domain_filter=None):
    if not MERGED_DB.exists():
        build_unified_db()
    
    conn = sqlite3.connect(str(MERGED_DB))
    
    if cmd == "show":
        sql = "SELECT id,domain,kind,created_utc,joules_total FROM unified_entries ORDER BY rowid"
        if domain_filter:
            sql += f" WHERE domain='{domain_filter}'"
        for row in conn.execute(sql):
            j_mark = f" ({row[4]:.0f}J)" if row[4] else ""
            print(f"{row[1][:1]} {row[0][:16]} kind={row[2]}{j_mark} ts={row[3][:19]}")
            
    elif cmd == "totals":
        agg = conn.execute(
            "SELECT SUM(joules_total), AVG(agape_score), COUNT(*) FROM unified_entries"
        ).fetchone()
        j_val = f"{agg[0]:.0f}" if agg[0] else "0"
        s_val = f"{agg[1]:.4f}" if agg[1] else "N/A"
        print(f"TOTALS: Joules={j_val}, AvgAgapeScore={s_val}, Entries={agg[2]}")
        
    elif cmd == "stats":
        for row in conn.execute("SELECT domain, COUNT(*), SUM(joules_total) FROM unified_entries GROUP BY domain"):
            j_val = f"{row[2]:.0f}" if row[2] else "0"
            print(f"{row[0]}: {row[1]} entries, {j_val}J total")
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
    
    conn.close()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    domain = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd in ["stats", "totals"]:
        build_unified_db()
    query_unified(cmd, domain)
    print(f"[banked] unified ledger query complete")
    print("[exit=0]")

# --- Self-accounting block (appended) ---
def measure_script_joules():
    """Measure own execution via RAPL or estimate."""
    import os, time
    
    rapl_path = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
    start = 0
    end = 0
    
    try:
        if os.path.exists(rapl_path):
            with open(rapl_path, 'r') as f:
                start = int(f.read().strip())
            time.sleep(0.01)  # Allow time to pass during db build
            with open(rapl_path, 'r') as f:
                end = int(f.read().strip())
            joules = (end - start) / 1_000_000  # Convert µJ → J
            return {"source": "rapl", "joules": joules}
        else:
            # Fallback: estimate from TDP × wall_time (crude but falsifiable)
            import datetime
            wall_time = time.time() - getattr(measure_script_joules, '_start_time', time.time())
            est = 65 * wall_time  # TDP 65W for OptiPlex 3060-ish
            return {"source": "estimate", "joules": est, "wall_time_s": wall_time}
    except Exception as e:
        return {"source": "error", "joules": 0, "error": str(e)}

# Call at end of main
if __name__ == "__main__":
    measure_script_joules._start_time = time.time()  # Mark start
    # ... rest of existing main code ...
    
    # AFTER build_unified_db(), add:
    energy = measure_script_joules()
    print(f"[accounting] script joules: {energy['joules']:.3f}J (source={energy['source']})")

# --- Self-accounting block (appended) ---
def measure_script_joules():
    """Measure own execution via RAPL or estimate."""
    import os, time
    
    rapl_path = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
    start = 0
    end = 0
    
    try:
        if os.path.exists(rapl_path):
            with open(rapl_path, 'r') as f:
                start = int(f.read().strip())
            time.sleep(0.01)  # Allow time to pass during db build
            with open(rapl_path, 'r') as f:
                end = int(f.read().strip())
            joules = (end - start) / 1_000_000  # Convert µJ → J
            return {"source": "rapl", "joules": joules}
        else:
            # Fallback: estimate from TDP × wall_time (crude but falsifiable)
            import datetime
            wall_time = time.time() - getattr(measure_script_joules, '_start_time', time.time())
            est = 65 * wall_time  # TDP 65W for OptiPlex 3060-ish
            return {"source": "estimate", "joules": est, "wall_time_s": wall_time}
    except Exception as e:
        return {"source": "error", "joules": 0, "error": str(e)}

# Call at end of main
if __name__ == "__main__":
    measure_script_joules._start_time = time.time()  # Mark start
    # ... rest of existing main code ...
    
    # AFTER build_unified_db(), add:
    energy = measure_script_joules()
    print(f"[accounting] script joules: {energy['joules']:.3f}J (source={energy['source']})")
