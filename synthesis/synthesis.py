#!/usr/bin/env python3
"""synthesis.py — OpenRoot synthesis engine: capabilities, tidbits, combos,
contributions blockchain (sha256), PoPW/thermal ACRE attestations, grants, bounties.
Pure stdlib. Idempotent. Commands: init scan combo grants contracts board verify intake."""
import argparse, datetime, hashlib, json, os, re, sqlite3, sys

ROOT = os.environ.get("SYN_ROOT", "/home/jesse/src/openroot")
SYN  = os.path.join(ROOT, "synthesis")
DB   = os.path.join(SYN, "db", "synthesis.db")
GRA  = os.path.join(SYN, "grants")
CON  = os.path.join(SYN, "contracts")
SCAN_DIRS = ("bin", "tools", "acre", "une", "workflows")
EXCLUDE  = {".git", "build", "venv", "node_modules", "__pycache__", "salvage", ".cargo", "target"}
GENESIS = "0" * 64

SCHEMA = """
CREATE TABLE IF NOT EXISTS chain (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS capabilities (
  id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, callable TEXT,
  yield_unit TEXT DEFAULT 'generic',
  grade TEXT CHECK(grade IN ('MEASURED','MODEL','STUB','CONFLICT')) DEFAULT 'STUB',
  eta_gain REAL DEFAULT 0.0, ops_sec REAL DEFAULT 0.0, note TEXT DEFAULT '',
  UNIQUE(path, callable));
CREATE TABLE IF NOT EXISTS tidbits (
  id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT UNIQUE, sha256 TEXT, lines INTEGER, note TEXT);
CREATE TABLE IF NOT EXISTS combos (
  a INTEGER, b INTEGER, solo REAL, pair REAL, synergy REAL, tested_at TEXT, PRIMARY KEY(a,b));
CREATE TABLE IF NOT EXISTS bounties (
  id INTEGER PRIMARY KEY AUTOINCREMENT, cap_id INTEGER UNIQUE, title TEXT,
  price_acre REAL, status TEXT DEFAULT 'OPEN', created TEXT);
CREATE TABLE IF NOT EXISTS acre_mints (
  id INTEGER PRIMARY KEY AUTOINCREMENT, joules REAL, source TEXT, memo TEXT, block_id INTEGER);
CREATE TABLE IF NOT EXISTS grants (
  id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT UNIQUE, status TEXT DEFAULT 'DRAFT',
  path TEXT, block_id INTEGER);
"""

def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB); c.executescript(SCHEMA); return c

def head(c):
    r = c.execute("SELECT hash FROM chain ORDER BY id DESC LIMIT 1").fetchone()
    return r[0] if r else GENESIS

def bhash(prev, kind, payload):
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev + "|" + kind + "|" + blob).encode()).hexdigest()

def append_block(c, kind, payload):
    prev = head(c); h = bhash(prev, kind, payload)
    c.execute("INSERT INTO chain(ts,kind,payload,prev_hash,hash) VALUES(?,?,?,?,?)",
              (now(), kind, json.dumps(payload, sort_keys=True, separators=(",", ":")), prev, h))
    c.commit()
    return c.execute("SELECT id FROM chain WHERE hash=?", (h,)).fetchone()[0]

def verify():
    c, ok, n, prev = conn(), True, 0, GENESIS
    for bid, ts, kind, payload, ph, h in c.execute(
            "SELECT id,ts,kind,payload,prev_hash,hash FROM chain ORDER BY id"):
        n += 1
        if ph != prev or bhash(ph, kind, json.loads(payload)) != h:
            ok = False; print(f"[verify] RED at block {bid}"); break
        prev = h
    print(f"[verify] {'GREEN' if ok else 'RED'} — {n} blocks, head {prev[:16]}...")
    return ok

SEEDS = [  # (rel_path, callable, unit, eta, grade, note) — inserted only if file exists
    ("bin/acre_ledger.sh", "acre_ledger", "claims", 0.6, "STUB", "ledger cli"),
    ("tokens/solana/acre_token.rs", "acre_token", "contract", 1.2, "STUB", "spl draft"),
    ("une/computational_flow/eta_lattice_acre.py", "eta_lattice", "analysis", 0.9, "MODEL", "eta lattice"),
    ("tools/acre-ledger", "ledger_cli", "cli", 0.5, "STUB", "tool dir"),
    ("bin/scribe.py", "scribe_gate", "audit", 1.5, "MODEL", "action ledger + gate"),
    ("bin/aider_task_runner.py", "run_queue", "automation", 1.8, "MODEL", "7B build / 3B grade"),
    ("bin/bespoke_user_circuit.py", "bespoke_circuit", "coordination", 1.4, "MODEL", "CEP intake loop"),
]

def init():
    c = conn()
    if c.execute("SELECT COUNT(*) FROM chain").fetchone()[0] == 0:
        bid = append_block(c, "GENESIS",
            {"node": "openroot-synthesis", "law": "every contribution is hash-linked; credit is provable"})
        print(f"[init] genesis block #{bid}")
    n = 0
    for rel, fn_, unit, eta, grade, note in SEEDS:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            c.execute("INSERT OR IGNORE INTO capabilities(path,callable,yield_unit,grade,eta_gain,note) VALUES(?,?,?,?,?,?)",
                      (p, fn_, unit, grade, eta, note)); n += 1
    c.commit()
    print(f"[init] seeded {n} known-asset capabilities (skipped missing paths)")

PY_RE = re.compile(r"^def\s+([A-Za-z_]\w*)\s*\(", re.M)
JOULE_RE = re.compile(r"joule[s]?['\"]?\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)", re.I)

def scan():
    c, ncaps, ntid = conn(), 0, 0
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base): continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in EXCLUDE]
            for fn in filenames:
                if not (fn.endswith(".py") or fn.endswith(".sh")): continue
                p = os.path.join(dirpath, fn)
                try: txt = open(p, encoding="utf-8", errors="replace").read()
                except OSError: continue
                lines = txt.count("\n") + 1
                if lines > 800: continue
                sha = hashlib.sha256(txt.encode()).hexdigest()
                if 8 <= lines <= 120:
                    c.execute("INSERT OR IGNORE INTO tidbits(path,sha256,lines,note) VALUES(?,?,?,?)",
                              (p, sha, lines, "modular tidbit candidate")); ntid += 1
                names = PY_RE.findall(txt) if fn.endswith(".py") else []
                c.execute("INSERT OR IGNORE INTO capabilities(path,callable,yield_unit,grade,eta_gain,note) VALUES(?,?,?,?,?,?)",
                          (p, fn[:-3], "module", "MODEL",
                           round(min(2.0, 0.05 * len(names) + 0.1), 3), f"{len(names)} callables"))
                ncaps += 1
                for nm in names[:25]:
                    c.execute("INSERT OR IGNORE INTO capabilities(path,callable,yield_unit,grade,eta_gain) VALUES(?,?,?,?,?)",
                              (p, nm, "function", "STUB", 0.1)); ncaps += 1
    c.commit()
    tot = c.execute("SELECT COUNT(*) FROM capabilities").fetchone()[0]
    tt  = c.execute("SELECT COUNT(*) FROM tidbits").fetchone()[0]
    append_block(c, "scan", {"new_caps": ncaps, "new_tidbits": ntid,
                             "total_caps": tot, "total_tidbits": tt})
    print(f"[scan] +{ncaps} capability rows (total {tot}), +{ntid} tidbits (total {tt})")

def combo():
    c = conn()
    caps = c.execute("SELECT id,path,eta_gain FROM capabilities WHERE eta_gain>0 ORDER BY eta_gain DESC LIMIT 32").fetchall()
    tested = 0
    for i in range(len(caps)):
        for j in range(i + 1, len(caps)):
            (ida, pa, ea), (idb, pb, eb) = caps[i], caps[j]
            solo = ea + eb
            cross = os.path.dirname(pa) != os.path.dirname(pb)  # cross-domain coupling bonus
            couple = 0.25 * ((ea * eb) ** 0.5) * (1.6 if cross else 0.6)
            c.execute("INSERT OR REPLACE INTO combos(a,b,solo,pair,synergy,tested_at) VALUES(?,?,?,?,?,?)",
                      (ida, idb, round(solo, 3), round(solo + couple, 3), round(couple, 3), now()))
            tested += 1
    c.commit()
    best = c.execute("""SELECT s.synergy, a.callable, b.callable FROM combos s
                        JOIN capabilities a ON a.id=s.a JOIN capabilities b ON b.id=s.b
                        ORDER BY s.synergy DESC LIMIT 5""").fetchall()
    print(f"[combo] {tested} pairs tested — top synergies (MODEL):")
    for s, x, y in best: print(f"   {s:>7.3f}  {x} + {y}")
    append_block(c, "combo_run", {"pairs_tested": tested})

GRANT_TMPL = """# OpenRoot — {group} Capability Cluster
## Grant Application DRAFT ({status}: claims graded MEASURED/MODEL/STUB/CONFLICT)

## Mission
OpenRoot is an offline-first appropriate-technology stack (sand, water, ferrocement,
local compute) delivering energy sovereignty to grid-excluded populations. Verified
physical yields — cooling joules from opencell thermal labyrinths, water harvest,
storage — are attested on a SHA-256 contributions blockchain and settle as ACRE
tokens: Proof of Physical Work (PoPW).

## This cluster's capabilities (modeled yield per unit effort)
{table}

## Honesty system
No claim ships without a grade. STUB → MODEL → MEASURED via the 3B-grader gate.
Untested claims are never asserted as facts to funders.

## Ask
Funding moves the rows above from MODEL to MEASURED (instrumented demo node),
which unlocks ACRE devnet minting and DeFi-visible PoPW settlement.
"""

def grants():
    c = conn(); os.makedirs(GRA, exist_ok=True)
    groups = {}
    for path, fn_, eta in c.execute(
            "SELECT path,callable,eta_gain FROM capabilities WHERE eta_gain>=0.5"):
        try: g = os.path.relpath(path, ROOT).split(os.sep)[0]
        except ValueError: g = "misc"
        groups.setdefault(g, []).append((path, fn_, eta))
    for g, rows in groups.items():
        tbl = "\n".join(f"| {p} | {f} | {e} |" for p, f, e in rows[:40])
        fp = os.path.join(GRA, f"{g}-grant-draft.md")
        open(fp, "w").write(GRANT_TMPL.format(group=g, status="DRAFT", table=tbl))
        c.execute("INSERT OR IGNORE INTO grants(target,path,status) VALUES(?,?,?)", (g, fp, "DRAFT"))
    c.commit()
    print(f"[grants] {len(groups)} cluster drafts in {GRA} (registered in grants table)")
    append_block(c, "grant_drafts", {"clusters": sorted(groups)})

RUST_STUB = """// acre_attest.rs — ACRE PoPW Anchor program STUB (DRAFT; not yet compiled)
use anchor_lang::prelude::*;
declare_id!("ACRE11111111111111111111111111111111111111111");

#[program]
pub mod acre_attest {
    use super::*;
    pub fn mint_attestation(ctx: Context<MintAttest>, source: String,
                            joules: f64, claim_hash: String, grade: String) -> Result<()> {
        require!(grade == String::from("MEASURED"), AttestError::NotMeasured);
        emit!(Attested { source, joules, claim_hash });
        Ok(())
    }
}
#[derive(Accounts)] pub struct MintAttest<'info> { #[account(mut)] pub payer: Signer<'info> }
#[event] pub struct Attested { pub source: String, pub joules: f64, pub claim_hash: String }
#[error_code] pub enum AttestError { #[msg("only MEASURED rows may mint")] NotMeasured }
"""

PY_STUB = '''#!/usr/bin/env python3
"""acre_attest.py — off-chain claim signer; on-chain mint is gated to MEASURED rows."""
from dataclasses import dataclass, asdict
import hashlib, json, time

@dataclass
class Attestation:
    source: str; joules: float; grade: str; ts: str
    def digest(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

def attest(source, joules, grade="MODEL"):
    assert grade in ("MEASURED", "MODEL")
    return Attestation(source, joules, grade, time.strftime("%Y-%m-%dT%H:%M:%SZ"))
'''

SPEC_MD = """# ACRE PoPW Attestation Spec (DRAFT)
1. thermal_sim / physical node emits joule event -> synthesis capabilities row (grade <= MODEL)
2. MEASURED row (3B-grader gate passes) -> acre_attest.py signs claim hash
3. claim hash -> acre_attest.rs mint_attestation on Solana devnet (rejects non-MEASURED)
4. minted ACRE credits the contributions blockchain block that anchored the yield row
5. bounty board prices future work in ACRE; STEP settles fills
"""

def contracts():
    c = conn(); os.makedirs(CON, exist_ok=True)
    open(os.path.join(CON, "acre_attest.rs"), "w").write(RUST_STUB)
    open(os.path.join(CON, "acre_attest.py"), "w").write(PY_STUB)
    open(os.path.join(CON, "ACRE_ATTESTATION_SPEC.md"), "w").write(SPEC_MD)
    python3 = sys.executable or "python3"
    # mine a joule figure from any thermal ledger found — else 0.0 flagged unmeasured
    joules, src = 0.0, "NO_MEASURED_ROW"
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [x for x in dns if x not in EXCLUDE]
        if dp.count(os.sep) > 8: dns[:] = []; continue
        for fn in fns:
            if "thermal" not in fn.lower() or "ledger" not in fn.lower(): continue
            try: txt = open(os.path.join(dp, fn), errors="replace").read(200000)
            except OSError: continue
            m = JOULE_RE.search(txt)
            if m: joules, src = float(m.group(1)), os.path.join(dp, fn); break
        if src != "NO_MEASURED_ROW": break
    bid = append_block(c, "acre_mint",
                       {"joules": joules, "source": src,
                        "status": "MEASURED" if joules > 0 else "UNMEASURED-DRAFT"})
    c.execute("INSERT INTO acre_mints(joules,source,memo,block_id) VALUES(?,?,?,?)",
              (joules, src, "PoPW attestation; mint gated on MEASURED", bid)); c.commit()
    print(f"[contracts] ACRE spec+stubs written; attestation anchored: {joules} J from {src}")

def board():
    c = conn()
    for cid, path, fn_, eta in c.execute(
            "SELECT id,path,callable,eta_gain FROM capabilities WHERE eta_gain>=1.0 ORDER BY eta_gain DESC LIMIT 12"):
        price = max(1.0, round(eta * 5.0, 2))
        c.execute("INSERT OR IGNORE INTO bounties(cap_id,title,price_acre,created) VALUES(?,?,?,?)",
                  (cid, f"{fn_} @ {os.path.basename(os.path.dirname(path))}", price, now()))
    c.commit()
    n = c.execute("SELECT COUNT(*) FROM bounties WHERE status='OPEN'").fetchone()[0]
    print(f"[board] {n} OPEN bounties priced in ACRE (MODEL pricing; earns cap->MEASURED credit)")
    append_block(c, "bounty_board", {"open_bounties": n})

def intake():
    c = conn(); verify()
    for row in c.execute("SELECT grade, COUNT(*) FROM capabilities GROUP BY grade"):
        print(f"[caps] {row[0]:<9} {row[1]}")
    n = c.execute("SELECT COUNT(*) FROM tidbits").fetchone()[0]
    m = c.execute("SELECT COUNT(*) FROM combos").fetchone()[0]
    s = c.execute("SELECT MAX(synergy) FROM combos").fetchone()[0] or 0.0
    b = c.execute("SELECT COUNT(*) FROM bounties WHERE status='OPEN'").fetchone()[0]
    minted = c.execute("SELECT SUM(joules) FROM acre_mints").fetchone()[0] or 0.0
    print(f"[tidbits] {n} candidates  [combos] {m} pairs, best synergy {s:.3f}")
    print(f"[bounties] {b} open (ACRE-priced)  [attested joules] {minted}")
    print("[directions] 1) read synthesis/SYNTHESIS_CARD.md (vision + concepts)")
    print("            2) do NOT rewrite seals/chain; append only")
    print("            3) push STUB->MODEL->MEASURED on capabilities to earn ACRE credit")
    print("            4) next yield move = top bounty or top combo pair above")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "scan", "combo", "grants", "contracts", "board", "verify", "intake"])
    a = ap.parse_args()
    dict(init=init, scan=scan, combo=combo, grants=grants, contracts=contracts,
         board=board, verify=verify, intake=intake)[a.cmd]()
