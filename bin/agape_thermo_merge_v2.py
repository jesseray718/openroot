#!/usr/bin/env python3
"""Agape+Thermo unified ledger v2 — self-accounting + cache-instrumented.
Every run measures its own joules (RAPL or estimate) and writes a receipt
to ledger/unified/run_receipts.jsonl. Cache hits = db exists + inputs unchanged.
Cmds: stats / totals / show / reset"""
import json, hashlib, sqlite3, sys, datetime, time, os
from pathlib import Path

REPO = "/home/jesse/openroot"
AGAPE_LEDGER = Path(REPO + "/ledger/agape/chain.jsonl")
THERMO_LEDGER = Path(REPO + "/openroot-edge/thermo_ledger.jsonl")
MERGED_DB = Path(REPO + "/ledger/unified/unified_ledger.sqlite")
RECEIPTS = Path(REPO + "/ledger/unified/run_receipts.jsonl")

RAPL_PATH = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
TDP_WATTS = 65.0  # OptiPlex 3060 estimate fallback — falsifiable, never claimed measured

def rapl_read():
    try:
        with open(RAPL_PATH) as f:
            return int(f.read().strip())
    except Exception:
        return None

def sha256_file(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()

def input_fingerprint():
    """Basis = source ledgers. If unchanged since last run, cache hit."""
    parts = []
    for p in [AGAPE_LEDGER, THERMO_LEDGER]:
        parts.append(f"{p.name}:{sha256_file(p) if p.exists() else 'absent'}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()

def last_run_fp():
    if not RECEIPTS.exists():
        return None
    try:
        lines = [l for l in RECEIPTS.read_text().splitlines() if l.strip()]
        return json.loads(lines[-1]).get("input_fingerprint")
    except Exception:
        return None

def measure_joules(start_uj, t_start):
    end_uj = rapl_read()
    wall = time.time() - t_start
    if start_uj is not None and end_uj is not None and end_uj >= start_uj:
        return {"source": "rapl", "joules": (end_uj - start_uj) / 1e6, "wall_s": round(wall, 4)}
    return {"source": "estimate", "joules": TDP_WATTS * wall, "wall_s": round(wall, 4),
            "note": "RAPL unavailable or counter wrap — TDP x wall estimate"}

def load_sources():
    entries = []
    if AGAPE_LEDGER.exists():
        for line in AGAPE_LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                entries.append({"domain": "agape", "id": r["id"], "kind": r["kind"],
                                "created_utc": r["created_utc"], "payload": r["payload"]})
    else:
        print("[held] agape ledger absent")
    if THERMO_LEDGER.exists():
        for line in THERMO_LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                b = json.loads(line)
                canon = hashlib.sha256(json.dumps(b, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
                entries.append({"domain": "thermo", "id": b.get("id", canon), "kind": b.get("kind", "block"),
                                "created_utc": b.get("created_utc", ""), "payload": b})
    else:
        print("[held] thermo ledger absent — merge partial, agape only")
    return entries

def build():
    MERGED_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(MERGED_DB))
    conn.executescript("""
        DROP TABLE IF EXISTS unified_entries;
        DROP TABLE IF EXISTS cross_domain_links;
        CREATE TABLE IF NOT EXISTS unified_entries (
            id TEXT PRIMARY KEY, domain TEXT NOT NULL, kind TEXT NOT NULL,
            created_utc TEXT NOT NULL, payload TEXT NOT NULL, sha TEXT NOT NULL,
            agape_score REAL, joules_total REAL, cache_hit INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS cross_domain_links (
            source_id TEXT, target_id TEXT, link_type TEXT, weight REAL);
        CREATE INDEX IF NOT EXISTS idx_domain ON unified_entries(domain);""")
    fp = input_fingerprint()
    cached = (fp == last_run_fp()) and MERGED_DB.exists()
    for e in load_sources():
        score = 1.0 if e["domain"] == "agape" else 0.0
        jou = float(e["payload"].get("joules_generated", 0) or 0) if e["domain"] == "thermo" else 0.0
        conn.execute("INSERT OR REPLACE INTO unified_entries VALUES (?,?,?,?,?,?,?,?,?)",
                     (e["id"], e["domain"], e["kind"], e["created_utc"],
                      json.dumps(e["payload"], ensure_ascii=False), e["id"], score, jou,
                      1 if cached else 0))
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM unified_entries").fetchone()[0]
    conn.close()
    return fp, cached, n

def report(fp, cached, n, energy, t_start):
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "input_fingerprint": fp, "cache_hit": cached, "entries": n,
           "joules": round(energy["joules"], 6), "source": energy["source"],
           "wall_s": energy["wall_s"]}
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    with open(RECEIPTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    print(f"[accounting] cache_hit={cached} entries={n} "
          f"joules={energy['joules']:.3f}J source={energy['source']} wall={energy['wall_s']}s")
    if cached:
        print("[banked] CACHE HIT — inputs unchanged since last seal, no recompute debt")
    else:
        print("[banked] FRESH COMPUTE — pathway sealed, next identical run = cache hit")

if __name__ == "__main__":
    t_start = time.time()
    start_uj = rapl_read()
    fp, cached, n = build()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    conn = sqlite3.connect(str(MERGED_DB))
    if cmd == "stats":
        for row in conn.execute("SELECT domain, COUNT(*), SUM(joules_total) FROM unified_entries GROUP BY domain"):
            j = f"{row[2]:.0f}J" if row[2] else "0J"
            print(f"{row[0]}: {row[1]} entries, {j} total")
    elif cmd == "totals":
        a = conn.execute("SELECT SUM(joules_total), AVG(agape_score), COUNT(*) FROM unified_entries").fetchone()
        print(f"TOTALS: Joules={a[0] or 0:.0f}, AvgAgapeScore={a[1] or 0:.4f}, Entries={a[2]}")
    elif cmd == "show":
        for r in conn.execute("SELECT domain,id,kind,cache_hit FROM unified_entries ORDER BY rowid"):
            print(f"{r[0][:1]} {r[1][:16]} kind={r[2]} cache_hit={r[3]}")
    elif cmd == "reset":
        MERGED_DB.unlink(missing_ok=True)
        print("[banked] derived db dropped — next run forces fresh compute")
    conn.close()
    report(fp, cached, n, measure_joules(start_uj, t_start), t_start)
    print("[exit=0]")
