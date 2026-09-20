#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# openroot triage_100 v1 — classify + gate the 100-action list, execute the A15-safe
# digital subset, bank field queue. Idempotent. Absolute paths only. No measured claims.
from __future__ import annotations
import json, shutil, sqlite3, subprocess, sys, os
from datetime import datetime, timezone
from pathlib import Path

CANARY = "[canary] triage_100 v1 intact"
TS = datetime.now(timezone.utc).isoformat()

def pane():
    h = str(Path.home())
    if h.startswith("/data/data/com.termux"): return "A15"
    if h == "/home/jesse": return "SSH"
    return "OTHER"

def die(msg): print(f"[gate] REFUSE: {msg}", file=sys.stderr); sys.exit(1)

P = pane()
ROOT = Path("/data/data/com.termux/files/home/openroot") if P == "A15" else Path("/home/jesse/openroot")
OUTDIR = Path("/storage/emulated/0/openroot/outbox") if P == "A15" else ROOT / "outbox"
DATADIR = ROOT / "data"
for d in (ROOT / "bin", OUTDIR, DATADIR): d.mkdir(parents=True, exist_ok=True)

def log(stage, msg): print(f"[{stage}] {msg}")

# ---------- the 100 actions: (id, pillar, title) ----------
ACTIONS = [
 (1,1,"Pin Termux core toolchains"),(2,1,"Lock SSH/Mosh connection profiles"),(3,1,"Set local SQLite FTS5 index"),
 (4,1,"Deploy Qwen 7B local endpoint"),(5,1,"Configure nomic-embed vector store"),(6,1,"Auto-sync git worktree workflow"),
 (7,1,"1-line sync script"),(8,1,"Sanitize .gitignore"),(9,1,"Lightweight JSON payload parser"),(10,1,"Offline state caching"),
 (11,1,"Strict file permission boundaries"),(12,1,"RAM clear cron job"),(13,1,"GGUF weights on external SSD"),
 (14,1,"1-file execution runner"),(15,1,"Standardize log outputs"),(16,1,"Pre-built C++ binaries"),(17,1,"SQLite backup mirror"),
 (18,1,"Map system aliases"),(19,1,"Automate git commit tagging"),(20,1,"Fallback local DNS"),
 (21,2,"Pre-mix xanthan gum slurry"),(22,2,"Calibrate Dawn Ultra surfactant ratio"),(23,2,"Standardize AR-glass fiber length"),
 (24,2,"Batch hemp fiber alkali pretreat"),(25,2,"Optimize stator motor speed"),(26,2,"Pour density test cubes"),
 (27,2,"Drill-and-bucket foam generator"),(28,2,"Quick-set slurry formulation"),(29,2,"Reusable cardboard dome form"),
 (30,2,"Slump-flow consistency test"),(31,2,"Volumetric void ratio test"),(32,2,"Ferrocement wire layout"),(33,2,"Carbon black pigment mix"),
 (34,2,"Standardize w/c ratio 0.35-0.38"),(35,2,"Portable cure tent"),(36,2,"Batch weight template cards"),
 (37,2,"Freeze-thaw test"),(38,2,"Portable slump cone"),(39,2,"Edge forms"),(40,2,"Surface sealant comparison"),
 (41,3,"Cast open-cell solar panel"),(42,3,"Transparent UV cover"),(43,3,"Print Aero-Disc radial core"),
 (44,3,"Seal + pressure test housing"),(45,3,"Calibrate 12V DC pump"),(46,3,"Install DS18B20 probes"),
 (47,3,"Log baseline dT"),(48,3,"Coppice Black Locust stand"),(49,3,"RMH burn tunnel sizing"),(50,3,"Cast cob thermal mass"),
 (51,3,"Dig earth battery trench"),(52,3,"Gravel fill subterranean bed"),(53,3,"Thermal cascade manifold"),
 (54,3,"Insulate subterranean perimeter"),(55,3,"Test thermosiphon loop"),(56,3,"Calibrate flow-rate meter"),
 (57,3,"Air-purge valve"),(58,3,"Coat heat exchanger"),(59,3,"Thermostatic relay ESP32"),(60,3,"Log thermal decay curve"),
 (61,4,"Verify PoPW ACRE-0001 schema"),(62,4,"Log local work entry"),(63,4,"Run local audit script"),(64,4,"Merge salvage PRs"),
 (65,4,"UND primitive 1-page spec"),(66,4,"wisdom-scaffold CLI"),(67,4,"Offline field manual export"),
 (68,4,"Bench-test local P2P sync"),(69,4,"Agape eta math functions"),(70,4,"Clean repository READMEs"),
 (71,4,"1-script env installer"),(72,4,"Formatting pre-commit hook"),(73,4,"Local hardware state monitor"),
 (74,4,"Physical asset register"),(75,4,"Standardize payload <2KB"),(76,4,"CC-BY-SA-4.0 doc headers"),
 (77,4,"GPL-3.0 code headers"),(78,4,"Index permaculture principles RAG"),(79,4,"Terminal system dashboard"),
 (80,4,"Full system compilation test"),
 (81,5,"Local concrete flatwork repair offers"),(82,5,"Scrap electronics recovery"),(83,5,"Map Sikeston land parcels"),
 (84,5,"LLC entity framework"),(85,5,"Reconditioned 55-gal drums"),(86,5,"Portable tool kit box"),
 (87,5,"Commercial service flyer"),(88,5,"Local aggregate source"),(89,5,"Rainwater catchment prototype"),
 (90,5,"Map regional coppice sites"),(91,5,"Portable fiber cutter"),(92,5,"Aeroponic tower prototype"),
 (93,5,"Cardboard geodesic hub connector"),(94,5,"Scrap metal salvage loop"),(95,5,"Mobile solar charging station"),
 (96,5,"1-page customer contract"),(97,5,"Log job revenue into ACRE ledger"),(98,5,"Black Locust nursery"),
 (99,5,"Low-cost slump testing table"),(100,5,"Execute local site build"),
]

# ---------- gate: N14 reject list + A15 hardware bans ----------
REJECT = {
 21:"N14 REJECT: xanthan barred as NightHawk gel ingredient",
 22:"N14 REJECT: Dawn barred as NightHawk gel ingredient",
}
A15_BAN = {
 4:"A15 ban: no 7B on phone — OptiPlex pane only",
 5:"A15 ban: no nomic on phone — OptiPlex pane only; FTS5 first anyway",
}
DIGITAL = {1,2,3,6,7,8,10,14,15,17,18,19,20,36,61,63,64,65,66,67,69,70,71,72,73,74,75,76,77,78,79,80,87,96}
NOW_PRIORITY = {  # aligned to operator NOW list
 3:"P1 SSH FTS5 probe before any nomic",
 26:"P1 NightHawk 1:2 cubes + 21-day wet tent",
 35:"P1 wet tent = cube cure requirement",
 41:"P1 H-003 1m2 cast for dT log",
 46:"P1 H-003 probe placement",
 47:"P1 H-003 baseline dT (h003_log.py, grade OPEN)",
 87:"P2 paid patch flyer — then popw_hang.py with photo",
 97:"P2 ACRE only AFTER confirmed hang (N08/N09)",
}

def classify(i):
    if i in REJECT:    return ("reject", REJECT[i])
    if i in A15_BAN:
        return ("defer_ssh" if P == "A15" else "digital_queue", A15_BAN[i])
    if P != "A15" and i in (4, 5): return ("digital_queue", "OptiPlex pane: allowed here")
    if i in NOW_PRIORITY: return ("field_priority", NOW_PRIORITY[i])
    if i in DIGITAL:   return ("digital_queue", "pure-software task, A15-safe or SSH")
    return ("field_queue", "physical work — instrument before claim")

classified = [(i, pl, t, *classify(i)) for i, pl, t in ACTIONS]

# ---------- execute the safe digital subset (instrument audit FIRST) ----------
log("gate", f"pane={P} root={ROOT} outbox={OUTDIR}")

# [1] audit existing bin/ scripts (py_compile + marker grep = the instrument gate)
bin_results = []
for name in ("need_gate.py", "h003_log.py", "popw_hang.py"):
    fp = ROOT / "bin" / name
    if not fp.is_file():
        bin_results.append({"script": name, "verdict": "MISSING"}); continue
    r = subprocess.run([sys.executable, "-m", "py_compile", str(fp)], capture_output=True)
    body = fp.read_text(errors="replace")
    marker = "REFUSE" in body or "MODEL" in body or "JSON" in body
    v = "PASS" if (r.returncode == 0 and marker) else "FAIL"
    bin_results.append({"script": name, "verdict": v, "rc": r.returncode})

# [2] FTS5 full-text index over local markdown vault (action #3 — executed now)
fts = {"files_indexed": 0, "engine": "fts5"}
try:
    ftsdb = DATADIR / "md_fts_v1.db"
    conn = sqlite3.connect(ftsdb)
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS md USING fts5(path, body)")
    conn.execute("DELETE FROM md")
    n = 0
    for p in ROOT.rglob("*.md"):
        s = str(p)
        if any(x in s for x in ("/.git/", "/venv/", "/node_modules/", "__pycache__")): continue
        try: body = p.read_text(errors="ignore")[:200000]
        except OSError: continue
        conn.execute("INSERT INTO md(path, body) VALUES (?,?)", (s, body)); n += 1
        if n >= 5000: break
    conn.commit(); conn.close(); fts["files_indexed"] = n
except Exception as e:
    fts["engine"] = f"fts5_unavailable: {e}"
log("banked", f"FTS5 index: {fts['files_indexed']} md files")

# [3] toolchain presence (action #1 partial)
tools = {t: bool(shutil.which(t)) for t in ("git", "python3", "clang", "mosh", "sqlite3")}

# [4] field-ready paper artifacts — all measurement claims graded MODEL/OPEN
(OUTDIR / "batch_cards_v1.md").write_text(
"""# OpenRoot Batch Cards v1 (laminate before field pour)
w/c target 0.35-0.38 [MODEL - grade OPEN until cube data]
NightHawk gel: ingredient UNRESOLVED - xanthan/Dawn on N14 reject list. Decide before pour.
1:2 mix (mass basis) per 4x4 cube; record mass_kg + photo into popw_hang.py the same day.
""", encoding="utf-8")
(OUTDIR / "service_flyer_v1.md").write_text(
"""# [DRAFT] Concrete Repair & Site Prep - Sikeston area
Patch/flatwork repair. Flat quote available on-site visit.
Every job logged with photo + joule estimate into the OpenRoot ledger (proof of work).
Contact: ____________
""", encoding="utf-8")
(OUTDIR / "customer_contract_v1.md").write_text(
"""# [DRAFT - review before use] Service Contract (1 page)
Scope: _____. Price: $____ (labor $___ / materials $___).
Payment terms: _____. Warranty: workmanship only, ___ days.
Photo + ledger record retained by OpenRoot LLC. Not legal advice - review locally.
""", encoding="utf-8")

# [5] queue ledger db
db = DATADIR / "queue_v1.db"
conn = sqlite3.connect(db)
conn.executescript("DROP TABLE IF EXISTS actions; CREATE TABLE actions(id INTEGER, pillar INT, title TEXT, cls TEXT, why TEXT, ts TEXT)")
conn.executemany("INSERT INTO actions VALUES (?,?,?,?,?,?)", [(i, pl, t, c, w, TS) for i, pl, t, c, w in classified])
conn.commit(); conn.close()

# [6] triage markdown (the actual field plan)
counts = {}
for _, _, _, c, _ in classified: counts[c] = counts.get(c, 0) + 1
lines = [f"# TRIAGE 100 — {TS}", f"pane={P}", "", "## Gate verdicts"]
lines += [f"- {i}: {t} -> {c.upper()} ({w})" for i, pl, t, c, w in classified]
lines += ["", "## NOW-order (operator list)", "1. cubes 1:2 + wet tent (26/35)", "2. H-003 cast + probe + dT log (41/46/47)", "3. paid patch + photo hang (87 -> popw_hang.py)", "4. SSH FTS5 (done this run)" , "5. ACRE 97 ONLY after hang confirmed"]
(OUTDIR / "TRIAGE_100.md").write_text("\n".join(lines), encoding="utf-8")

# [7] gate report row
rep = {"ts": TS, "schema": "TRIAGE100-1", "pane": P, "counts": counts, "bin_audit": bin_results,
       "fts": fts, "tools": tools, "claims": {"service_ratio_1_34": "MODEL", "h1_mpa": "OPEN"}}
with (OUTDIR / "gate_report.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps(rep, separators=(",", ":")) + "\n")

print(json.dumps({"written": ["data/queue_v1.db", "data/md_fts_v1.db", "outbox/TRIAGE_100.md", "outbox/batch_cards_v1.md", "outbox/service_flyer_v1.md", "outbox/customer_contract_v1.md", "outbox/gate_report.jsonl"], "counts": counts, "bin_audit": bin_results, "fts_files": fts["files_indexed"]}, indent=2))
print(f"PANE {P} | 1.34 MODEL | H1 OPEN | ACRE locked until hang", file=sys.stderr)
print(CANARY)
print("[exit=0]")
sys.exit(0)
