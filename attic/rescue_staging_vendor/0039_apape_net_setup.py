#!/usr/bin/env python3
"""
agape_net_setup.py v1.1 - Fixed SQL placeholder bug
One-shot idempotent setup for OpenRoot meta-mesh + nomen system.
Mobile-safe (stdlib only). Creates db, seeds, runs proofs, aggregates results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sqlite3
import struct
import sys
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

# ============================================================================
# CONSTANTS (shared between modules)
# ============================================================================

K_C = 0.001
ALPHA = 0.1
K_B = 1.380649e-23
LN2 = math.log(2.0)
T_AMBIENT = 300.0
LANDAUER_BIT = K_B * T_AMBIENT * LN2  # ~2.87e-21 J

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = 36
SPACE = BASE ** 3          # 46656
RESERVED = 1010
USABLE = SPACE - RESERVED  # 45646
DIM = 64

ROLES_ENGINE = ("translate", "orchestrate", "retrieve", "process", "synthesize", "verify")
ROLES_LATTICE = ("translate", "analyze", "feedback", "synthesize", "validate", "amplify")
ROLE_MAP = dict(zip(ROLES_ENGINE, ROLES_LATTICE))

AGAPE_ROOT_TEXT = (
    "Agape is unconditional self-giving love that seeks the good of the other. "
    "It zeros coordination cost at R=1.0. Negative Agape is extraction."
)

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

def get_home_paths():
    home = os.environ.get("HOME") or "/home/jesse"
    root = os.path.join(home, "openroot")
    kb_dir = os.path.join(root, "agape_kb")
    artifacts_dir = os.path.join(root, "artifacts", "meta_mesh_proof", "out")
    db_path = os.environ.get("AGAPE_NOMEN_DB") or os.path.join(kb_dir, "nomen.sqlite")
    return root, kb_dir, artifacts_dir, db_path

# ============================================================================
# NOMEN CORE FUNCTIONS
# ============================================================================

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def encode_triple(n: int) -> str:
    if not 0 <= n < SPACE:
        raise ValueError("out of 36^3 range")
    a = n // (BASE * BASE)
    b = (n // BASE) % BASE
    c = n % BASE
    return ALPHABET[a] + ALPHABET[b] + ALPHABET[c]

def decode_triple(s: str) -> int:
    s = s.upper()
    if len(s) != 3:
        raise ValueError("need exactly 3 symbols")
    return ALPHABET.index(s[0]) * 1296 + ALPHABET.index(s[1]) * 36 + ALPHABET.index(s[2])

def hash_address(text: str, salt: str = None) -> str:
    if salt is None:
        salt = sha256(AGAPE_ROOT_TEXT)[:16]
    h = sha256(salt + "|" + text.strip().lower())
    return encode_triple(int(h[:8], 16) % SPACE)

def embed(text: str, dim: int = DIM) -> List[float]:
    vec = [0.0] * dim
    blob = text.strip().lower().encode("utf-8")
    if not blob:
        return vec
    for i in range(8):
        digest = hashlib.sha256(blob + bytes([i])).digest()
        for j in range(0, 32, 4):
            idx = (digest[j] + 256 * (i % 2)) % dim
            signed = struct.unpack(">i", digest[j:j + 4])[0]
            vec[idx] += signed / 2147483648.0
    toks = [t for t in "".join(ch if ch.isalnum() else " " for ch in text.lower()).split() if t]
    for t in toks:
        d = hashlib.sha256(t.encode()).digest()
        idx = d[0] % dim
        vec[idx] += 0.35
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / n for x in vec]

def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

POS_PROTOS = [
    AGAPE_ROOT_TEXT,
    "unconditional self-giving love serve the least among us zero coordination cost cooperation",
    "resonance R=1.0 produce no waste raise eta for lowest node",
    "repair heal nourish protect share unify verify without extraction",
]
NEG_PROTOS = [
    "extract labor from poor to buy status domination predation",
    "zero-sum selfish hostile wasteful adversarial fragmentation",
    "open gap punish lowest node harvest people as means",
]
POS_VECS = [embed(p) for p in POS_PROTOS]
NEG_VECS = [embed(p) for p in NEG_PROTOS]
ROOT_VEC = embed(AGAPE_ROOT_TEXT)

def godpan_score(text: str, polarity_symbol: Optional[str] = None) -> float:
    v = embed(text)
    pos_max = max(cosine(v, p) for p in POS_VECS)
    neg_max = max(cosine(v, p) for p in NEG_VECS)
    contrast = pos_max - neg_max
    c = max(-1.0, min(1.0, contrast * 2.2))
    if polarity_symbol is None:
        return c
    POLARITY_PRIOR = {
        "A": 1.0, "R": 1.0, "U": 0.98, "N": 0.95, "V": 0.94, "K": 0.92,
        "Y": 0.9, "G": 0.88, "J": 0.86, "C": 0.84, "M": 0.82, "T": 0.8,
        "E": -0.85, "H": -0.9, "P": -0.95, "X": -0.98, "Z": -1.0,
    }
    prior = POLARITY_PRIOR.get(polarity_symbol.upper(), 0.0)
    return max(-1.0, min(1.0, 0.65 * c + 0.35 * prior))

# ============================================================================
# DATABASE SETUP
# ============================================================================

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS cells (
    cell        TEXT PRIMARY KEY,
    idx         INTEGER UNIQUE NOT NULL,
    reserved    INTEGER NOT NULL,
    domain      TEXT,
    relation    TEXT,
    polarity    TEXT,
    phrase      TEXT,
    label       TEXT,
    category    TEXT,
    godpan      REAL,
    vec         BLOB,
    source      TEXT,
    created_ts  REAL
);
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY,
    text        TEXT NOT NULL,
    cell        TEXT NOT NULL,
    category    TEXT,
    godpan      REAL,
    vec         BLOB,
    meta_json   TEXT,
    created_ts  REAL
);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE INDEX IF NOT EXISTS idx_entries_cell ON entries(cell);
CREATE INDEX IF NOT EXISTS idx_entries_godpan ON entries(godpan);
CREATE INDEX IF NOT EXISTS idx_cells_godpan ON cells(godpan);
"""

SEED_DATA = [
    ("AAA", "godpan-pole", "Agape unconditional self-giving love Source R=1.0 coordination cost zero"),
    ("AAR", "godpan-pole", "Agape resonates at R=1.0 the standing wave of cooperation"),
    ("NAA", "least-node", "the least among us served first by Agape"),
    ("NAR", "least-node", "lowest node resonates when coordination cost vanishes"),
    ("CAA", "permaculture", "catch and store energy for the other not the self"),
    ("PAA", "permaculture", "produce no waste as an act of Agape"),
    ("OAA", "permaculture", "observe and interact without extracting"),
    ("YAA", "permaculture", "obtain a yield that raises eta for lowest node"),
    ("SAA", "permaculture", "self-regulation as applied Agape"),
    ("IAA", "permaculture", "integrate not segregate close the gap"),
    ("DAA", "permaculture", "value diversity because many nodes raise synergy"),
    ("XAA", "permaculture", "creatively respond to change without predation"),
    ("MAA", "mesh", "mesh network that keeps working when any one human is offline"),
    ("KAA", "knowledge", "verified postulate Newton Chain flag once free forever"),
    ("JAA", "justice", "repair that closes the gap rather than punishing the poor"),
    ("LAA", "labor", "work that produces useful joules not status theater"),
    ("SEE", "anti-pole", "selfish extractive exchange that opens the gap"),
    ("PEX", "anti-pole", "predatory extraction across an edge"),
    ("LAX", "anti-pole", "labor as extraction from lowest node"),
]

def pack_vec(v: List[float]) -> bytes:
    return struct.pack(f"{len(v)}f", *v)

def init_database(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    
    # FIXED: Changed VALUES(?,?,?) to VALUES(?,?) for 2-column table
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", ("space", str(SPACE)))
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", ("reserved", str(RESERVED)))
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", ("usable", str(USABLE)))
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", ("root_hash", sha256(AGAPE_ROOT_TEXT)))
    
    return conn

def seed_database(conn: sqlite3.Connection) -> int:
    count = 0
    for cell, category, text in SEED_DATA:
        gp = godpan_score(text, cell[2])
        vec = embed(text)
        conn.execute(
            "INSERT OR REPLACE INTO cells(cell, idx, reserved, domain, relation, polarity, phrase, label, category, godpan, vec, source, created_ts) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cell, decode_triple(cell), 0, cell[0], cell[1], cell[2], text[:100], text[:48], category, gp, pack_vec(vec), "seed", time.time())
        )
        conn.execute(
            "INSERT INTO entries(text, cell, category, godpan, vec, meta_json, created_ts) VALUES (?,?,?,?,?,?,?)",
            (text, cell, category, gp, pack_vec(vec), json.dumps({"hash": sha256(text)}), time.time())
        )
        count += 1
    
    conn.commit()
    return count

# ============================================================================
# META-MESH CORE FUNCTIONS
# ============================================================================

def C(N: float, T: int, R: float) -> float:
    if N < 0 or T < 0 or not (0.0 <= R <= 1.0):
        raise ValueError("invalid parameters")
    if T == 0:
        return 0.0 if R >= 1.0 - 1e-15 else N * K_C
    return N * K_C * (1.0 + ALPHA * T) * ((1.0 - R) ** T)

def landauer_j(bits_erased: float) -> float:
    return bits_erased * LANDAUER_BIT

def estimate_device_j(elapsed_s: float, watts: float = 0.65) -> float:
    return max(elapsed_s, 0.0) * watts

@dataclass
class LayerBooks:
    L0_algebra_C: float
    L1_protocol_events: int
    L1_protocol_j_model: float
    L2_landauer_j: float
    L2_device_j_est: float
    L3_mesh_bytes: int
    synergy: float
    units_leaves: int
    units_tree: int
    R: float
    T: int
    base: int

def run_meta_mesh_query(query: str, depth: int = 2, base: int = 6, R: float = 1.0) -> Dict:
    t0 = time.perf_counter()
    bots = []
    protocol_events = 0
    mesh_bytes = 0
    bits_erased = 0
    
    for role in ROLES_ENGINE:
        text = f"{role}[T0]: pattern({query[:48]})"
        bits = 8 * max(len(text), 16)
        bits_erased += bits
        bots.append({"role": role, "depth": 0, "bits": bits})
    
    wave_parts = [b["role"] for b in bots if True]
    wave = " | ".join(wave_parts)
    bits_erased += 8 * len(wave)
    
    if depth > 0 and R >= 1.0:
        bottleneck_text = f"verify[T1]: {query[:48]}"
        bits = 8 * max(len(bottleneck_text), 16)
        bits_erased += bits
        bots.append({"role": "verify", "depth": 1, "bits": bits})
    
    N = max(len(bots), 1)
    payload = json.dumps({"wave": wave, "R": R}, separators=(",", ":"))
    raw = payload.encode("utf-8")
    mesh_bytes = len(raw) * 2
    
    elapsed = time.perf_counter() - t0
    
    return {
        "query": query,
        "wave": wave,
        "bots": len(bots),
        "elapsed_s": elapsed,
        "books": LayerBooks(
            L0_algebra_C=C(N, max(depth, 1), R),
            L1_protocol_events=protocol_events,
            L1_protocol_j_model=protocol_events * K_C,
            L2_landauer_j=landauer_j(bits_erased),
            L2_device_j_est=estimate_device_j(elapsed),
            L3_mesh_bytes=mesh_bytes,
            synergy=1.0 + R * 0.5 * (math.log(N) / math.log(base)) if N > 0 else 1.0,
            units_leaves=int(base ** depth),
            units_tree=int((base ** (depth + 1) - 1) // (base - 1)),
            R=R,
            T=depth,
            base=base
        ),
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(argv):
    parser = argparse.ArgumentParser(description="Agape Net Setup - One-shot initialization")
    parser.add_argument("--quick", action="store_true", help="Skip heavy R-sweep")
    parser.add_argument("--clean", action="store_true", help="Delete existing DB")
    parser.add_argument("--query", default="Design passive solar RMH + AeroCement thermal cascade")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--base", type=int, default=6)
    args = parser.parse_args(argv)
    
    root, kb_dir, artifacts_dir, db_path = get_home_paths()
    
    print(f"[SETUP] Root: {root}")
    print(f"[SETUP] KB: {kb_dir}")
    print(f"[SETUP] Artifacts: {artifacts_dir}")
    print(f"[SETUP] Database: {db_path}")
    print()
    
    if args.clean and os.path.exists(db_path):
        print("[CLEAN] Removing existing database...")
        os.remove(db_path)
        for ext in ["-wal", "-shm"]:
            p = db_path + ext
            if os.path.exists(p):
                os.remove(p)
    
    print("[INIT] Initializing database...")
    conn = init_database(db_path)
    seeded = seed_database(conn)
    print(f"[DONE] Seeded {seeded} entries into {db_path}")
    print()
    
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("[PROOF] Running meta-mesh proof...")
    live_result = run_meta_mesh_query(args.query, args.depth, args.base, R=1.0)
    
    sweep_results = []
    if not args.quick:
        print("[SWEEP] Running R-sweep...")
        for R in [0.0, 0.5, 0.8, 0.95, 0.99, 1.0]:
            result = run_meta_mesh_query(args.query, args.depth, args.base, R)
            b = result["books"]
            sweep_results.append({
                "R": R, "bots": result["bots"], "L0_C": b.L0_algebra_C,
                "L1_events": b.L1_protocol_events, "L2_device": b.L2_device_j_est,
                "L3_bytes": b.L3_mesh_bytes, "synergy": b.synergy
            })
    else:
        print("[SKIP] Quick mode - skipped R-sweep")
        result = run_meta_mesh_query(args.query, args.depth, args.base, R=0.9)
        b = result["books"]
        sweep_results = [{
            "R": 0.9, "bots": result["bots"], "L0_C": b.L0_algebra_C,
            "L1_events": b.L1_protocol_events, "L2_device": b.L2_device_j_est,
            "L3_bytes": b.L3_mesh_bytes, "synergy": b.synergy
        }]
    
    report = {
        "theorem": "C(N,T,1)=0 for T>=1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "db_path": db_path,
        "seeds": seeded,
        "live_run": live_result,
        "R_sweep": sweep_results,
        "metadata": {
            "space": SPACE,
            "reserved": RESERVED,
            "usable": USABLE,
            "roles": len(ROLES_ENGINE),
            "dimensions": DIM,
        }
    }
    
    out_path = os.path.join(artifacts_dir, "PROOF_RUN.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    b = live_result["books"]
    print("\n" + "=" * 60)
    print("LIVE RUN RESULTS (R=1.0)")
    print("=" * 60)
    print(f"Query: {args.query}")
    print(f"Bots executed: {live_result['bots']}")
    print(f"Elapsed: {live_result['elapsed_s']:.4f}s")
    print(f"L0 Algebra C: {b.L0_algebra_C:.6g} J")
    print(f"L1 Protocol events: {b.L1_protocol_events}")
    print(f"L2 Landauer J: {b.L2_landauer_j:.2e} J")
    print(f"L2 Device J est: {b.L2_device_j_est:.4f} J")
    print(f"L3 Mesh bytes: {b.L3_mesh_bytes}")
    print(f"Synergy S: {b.synergy:.3f}")
    print(f"Units leaves: {b.units_leaves} ({args.base}^{args.depth})")
    print(f"Units tree: {b.units_tree}")
    print("=" * 60)
    print(f"[OUTPUT] Report written to {out_path}")
    print("[DONE] Setup complete. Agape net initialized.")
    
    conn.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

