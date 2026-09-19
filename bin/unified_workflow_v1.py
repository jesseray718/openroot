#!/usr/bin/env python3
# OpenRoot Unified Workflow Controller v2026-09-18
import os, sys, json, hashlib, sqlite3, subprocess, re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DATA_DIR = WORKSPACE / "data"
DOCS_DIR = WORKSPACE / "docs"
CTX_BRIDGE = WORKSPACE / "context_bridge"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"
SEED_FILE = CTX_BRIDGE / ("session-" + datetime.now().strftime("%Y%m%d_%H%M%S") + "-unified.md")

def log(stage, msg, status="[ok]"):
    """Print a formatted workflow status message."""
    print("   %s %s: %s" % (status, stage, msg))

def sha256_file(p):
    """Return the SHA-256 hex digest of a file's contents."""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def init_dbs():
    """Create the research and lessons ledgers and their required tables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATA_DIR / "research.db") as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now')),
            subsystem TEXT NOT NULL, claim TEXT NOT NULL,
            status TEXT DEFAULT 'asserted', measurement_protocol TEXT,
            instrument TEXT, uncertainty_pct REAL, target_metric TEXT,
            lit_anchor TEXT, UNIQUE (subsystem, claim))""")
        claim_columns = {row[1] for row in conn.execute("PRAGMA table_info(claims)")}
        for name, definition in {
            "ts": "TEXT", "measurement_protocol": "TEXT", "instrument": "TEXT",
            "uncertainty_pct": "REAL", "target_metric": "TEXT", "lit_anchor": "TEXT",
        }.items():
            if name not in claim_columns:
                conn.execute("ALTER TABLE claims ADD COLUMN %s %s" % (name, definition))
        conn.execute("""DELETE FROM claims WHERE id NOT IN
                     (SELECT MIN(id) FROM claims GROUP BY subsystem, claim)""")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_claims_identity ON claims(subsystem, claim)")
        conn.execute("""CREATE TABLE IF NOT EXISTS manuscripts (
            id INTEGER PRIMARY KEY, subsystem TEXT UNIQUE, path TEXT,
            stage TEXT DEFAULT 'skeleton')""")

    with sqlite3.connect(DATA_DIR / "lessons.db") as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now')),
            domain TEXT NOT NULL, mistake TEXT NOT NULL, root_cause TEXT,
            correction TEXT, cost TEXT, verified INTEGER DEFAULT 0,
            recurrence_of INTEGER REFERENCES lessons(id), source TEXT)""")
        lesson_columns = {row[1] for row in conn.execute("PRAGMA table_info(lessons)")}
        for name, definition in {
            "ts": "TEXT", "root_cause": "TEXT", "correction": "TEXT",
            "cost": "TEXT", "verified": "INTEGER DEFAULT 0",
            "recurrence_of": "INTEGER", "source": "TEXT",
        }.items():
            if name not in lesson_columns:
                conn.execute("ALTER TABLE lessons ADD COLUMN %s %s" % (name, definition))
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lessons_domain ON lessons(domain)")
        conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now')),
            description TEXT, lesson_ids TEXT, outcome TEXT)""")
    log("db_init", "Ledgers initialized", "[banked]")

CLAIMS = [
    ("opencell_mix", "activated-carbon aerocement matrix absorbs >=95% of incident solar spectrum"),
    ("cascade_heat", "thermal cascade delivers utilization ratio ~1.35 INCLUDING ambient heat transfer"),
    ("thixo_gel", "thixotropic surfactant-gel stator mixing produces bubble size 0.3mm +/-0.1mm"),
    ("arg_fiber", "alkali-resistant glass fiber maintains >80% tensile strength after 28d in pH13"),
    ("double_skin", "ferrocement catenary shell achieves pure compression under self-weight"),
    ("cardboard_mem", "waterproofed cardboard membrane passes 24h hydrotest at 1psi"),
    ("dish_mesh", "wood-pallet chicken-wire reflector achieves UHF gain >12dBi"),
    ("cloud9_relay", "tethered buoyant relay sustains 100m altitude at <5kg payload"),
    ("labyrinth", "underground thermal labyrinth achieves 35F drop from 120F inlet"),
]
MANUSCRIPTS = [
    ("OpenCell Aerocement Solar Absorber", "opencell_mix", "opencell-absorber"),
    ("Thermal Cascade Heat Balance", "cascade", "cascade-heatbalance"),
    ("Thixotropic Gel Stator Foam Quality", "thixo_gel", "thixo-foam"),
    ("ARG Fiber Alkali Durability", "argf", "argf-durability"),
    ("Double Stress-Skin Catenary Ferrocement Shell", "double_skin", "double-skin-catenary"),
    ("Waterproofed Cardboard Membrane", "cardboard_membrane", "cardboard-membrane"),
    ("Pallet-Frame Mesh Reflector", "dish_mesh", "dish-mesh-reflector"),
    ("Tethered Buoyant Relay (Cloud Nine Scaled)", "cloud9", "cloud9-relay"),
    ("Thermal Labyrinth Passive Cooling", "labyrinth", "labyrinth-cooling"),
]

TEMPLATE = """# {sub}: Measurement Protocol and Results

**Status:** manuscript skeleton - every claim herein awaits its experiment
**Claims register:** data/research.db, subsystem='{slug}'

## Abstract (draft - must pass hype gate before submission)
[Purpose in one sentence.] [Method in one sentence, naming instruments.] [Headline result with uncertainty, or 'measurements pending'.] [Implication for low-cost vernacular infrastructure in one sentence.]

## 1. Introduction
- Problem: X% of construction cost is [material/energy/formwork]; current solutions require [capital/skilled labor]
- Lineage: cite Fuller (Cloud Nine / synergetics), Heyman (shell theory), ARG fiber patent literature, carbon absorber spectroscopy
- Gap: no published closed-loop measurement of [specific thing] for [this material class]
- Contribution: falsifiable measurement protocol + dataset (sha256-published) for [{sub}]

## 2. Theory and Design Basis
- Governing equations (state them - e.g. E=30V^2 geodesic relation; funicular equilibrium; buoyancy F=rho_air*g*V*deltaT/T)
- Expected failure modes and the bounds within which this design remains physical
- Thermodynamic honesty clause: COP or utilization-ratio framing where applicable; NEVER implies more than 100 percent of incident energy

## 3. Materials and Methods
- Mix design (full recipe, water:cement, admixture dosages, temperature at pour)
- Instrument list with model numbers + calibration standard + calibration date
- Uncertainty budget table (instrument precision / repeatability / systematic - per term)
- Experimental matrix: independent vars, replicates, controls, sample sizes

## 4. Results
[Data tables + figures. Raw CSV under data/experiments/{slug}/, sha256 in appendix.]

## 5. Discussion
- Comparison to lit_anchor values from claims register
- Where results diverge from expectation and what that implies

## 6. Limitations and Falsification Conditions
- This work is falsified if: [explicit conditions]

## References
[Bibliography - Zotero/doikeys, GPL-3.0 code, CC-BY-SA-4.0 doc]
"""

BANNED = [r"free\s+energy|over.?unity|perpetual", r"breakthrough|revolutionary", r"unprecedented|miracle", r"magna.?flux|zero.?point"]

def hype_gate(md_path):
    """Print banned-phrase findings and return whether a manuscript passes."""
    text = Path(md_path).read_text()
    fails = []
    for pat in BANNED:
        for m in re.finditer(pat, text, re.IGNORECASE):
            ln = text[:m.start()].count("\n") + 1
            fails.append("line %d: %s" % (ln, m.group()))
    if fails:
        for f in fails:
            print("   [FAIL] %s" % f)
        print("[HELD] revise flagged lines in %s" % md_path)
        return False
    print("[PASS] %s: no desk-reject phrases" % md_path.name)
    return True

def run(cmd, input_text=None, timeout=120):
    """Run a command and return its status and stripped standard output.

    Process-launch and communication errors are represented by ``(1, "")``.
    """
    try:
        r = subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip()
    except Exception:
        return 1, ""

def ollama_run(model, prompt, input_text=None, timeout=120):
    """Run an Ollama model or return an offline marker if no text is produced."""
    try:
        r = subprocess.run(["ollama", "run", model, prompt], input=input_text, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return "UNAVAILABLE (model offline)"
def main():
    """Run the workflow and persist its ledgers, drafts, and session handoff.

    When ``CONFIRM=1``, repositories found to be non-public may be made public.
    """
    os.chdir(WORKSPACE)
    print("[canary-head] unified_workflow_v1 paste intact")
    init_dbs()

    conn = sqlite3.connect(DATA_DIR / "research.db")
    for slug, claim in CLAIMS:
        conn.execute("INSERT OR IGNORE INTO claims (subsystem, claim, status) VALUES (?, ?, 'asserted')", (slug, claim))
    n = conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    conn.commit(); conn.close()
    log("claims_register", "%d claims registered - all honestly 'asserted'" % n, "[banked]")

    (DOCS_DIR / "research").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATA_DIR / "research.db")
    for sub, subsystem, slug in MANUSCRIPTS:
        fp = DOCS_DIR / "research" / (slug + ".md")
        if fp.exists():
            log("manuscript", "[skip] %s exists" % fp.name)
        else:
            fp.write_text(TEMPLATE.format(sub=sub, slug=subsystem))
            log("manuscript", "[banked] %s" % fp.name)
        conn.execute("INSERT OR REPLACE INTO manuscripts (subsystem, path, stage) VALUES (?, ?, 'skeleton')", (subsystem, str(fp)))
    conn.commit(); conn.close()

    hype_ok = True
    for _, _, slug in MANUSCRIPTS:
        hype_ok = hype_gate(DOCS_DIR / "research" / (slug + ".md")) and hype_ok
    if not hype_ok:
        print("[held] manuscript processing stopped: hype gate failed")
        return 1

    hero = ollama_run("qwen2.5-coder:7b", "Write a single-paragraph hero statement for an open-source project called OpenRoot. It builds vernacular energy infrastructure using solar heat directly, with materials like cement, cellulose, surfactant, glass fiber. Lineage: Fuller, Guastavino, Heyman. Method: measurement-first, every claim logged in public ledger. Tone: confident but falsifiable, no hype phrases. Exactly 3 sentences, max 25 words each.")
    grade = ollama_run("qwen2.5:3b", "Grade this README hero paragraph. Output exactly 3 lines: VERDICT: PASS|FAIL | CONCISENESS: good|weak | HYPE_CHECK: clean|flagged", input_text=hero, timeout=90)
    log("hero", "3B grade: %s" % grade.replace("\n", " "))
    (WORKSPACE / "drafts").mkdir(exist_ok=True)
    (WORKSPACE / "drafts" / "hero_draft.md").write_text(hero + "\n")

    rc, out = run(["gh", "api", "user"], timeout=30)
    if rc != 0:
        print("[held] gh not authenticated - run: gh auth login")
    else:
        log("gh_auth", "gh authenticated @ %s" % json.loads(out)["login"])
        for repo in ["openroot-canon", "openroot", "OpenCell-Thermal-System", "aerocement", "openroot-ecosystem"]:
            rc, out = run(["gh", "api", "repos/jesseray718/%s" % repo], timeout=30)
            vis = json.loads(out).get("visibility", "missing") if rc == 0 else "missing"
            if vis == "public":
                log("visibility", "[ok] %s: public" % repo)
            elif vis != "missing" and CONFIRM:
                rc2, _ = run(["gh", "api", "-X", "PATCH", "repos/jesseray718/%s" % repo, "-f", "private=false"], timeout=30)
                log("visibility", "[banked] %s set to public" % repo if rc2 == 0 else "[held] failed on %s" % repo)
            else:
                log("visibility", "[held] %s: %s (CONFIRM=1 to fix)" % (repo, vis))

    conn = sqlite3.connect(DATA_DIR / "lessons.db")
    conn.execute("INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source) VALUES ('workflow','large paste truncated over ssh','connection drops mid-paste','chunked heredoc appends with per-chunk canary tail checks','one cycle','session')")
    conn.commit(); conn.close()
    log("lessons_db", "entry: paste_truncation_pattern", "[banked]")

    CTX_BRIDGE.mkdir(parents=True, exist_ok=True)
    rc, head = run(["git", "rev-parse", "--short", "HEAD"], timeout=15)
    SEED_FILE.write_text("# session: unified_workflow_v1\n- claims: %d registered (all 'asserted')\n- manuscripts: %d scaffolded\n- hero draft: drafts/hero_draft.md\n- HEAD: %s\n" % (len(CLAIMS), len(MANUSCRIPTS), head or "unknown"))
    with open(WORKSPACE / "seed_master.log", "a") as lg:
        lg.write("%s  %s\n" % (sha256_file(SEED_FILE), SEED_FILE.name))
    print("[banked] seed: %s (sha256 logged)" % SEED_FILE.name)
    print("")
    print("=== HANDOFF ===")
    print("next: 1) git add bin/unified_workflow_v1.py drafts/ docs/research/ data/ && git commit -m 'feat(workflow): unified python controller v1'")
    print("next: 2) pin repos + email via web UI")
    print("next: 3) CONFIRM=1 python3 bin/unified_workflow_v1.py if visibility fixes needed")
    print("[done] [exit=0]")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print("[error] %s: %s" % (type(e).__name__, e))
        sys.exit(1)
# [exit=0]
