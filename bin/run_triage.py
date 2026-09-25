#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
import json, shutil, sqlite3, subprocess, sys, os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/openroot")
OUTDIR = Path("/storage/emulated/0/openroot/outbox")
DATADIR = ROOT / "data"

for d in (ROOT / "bin", OUTDIR, DATADIR):
    d.mkdir(parents=True, exist_ok=True)

# FTS5 Indexing over local Markdown vault (Action #3)
ftsdb = DATADIR / "md_fts_v1.db"
conn = sqlite3.connect(ftsdb)
conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS md USING fts5(path, body)")
conn.execute("DELETE FROM md")
n = 0
for p in ROOT.rglob("*.md"):
    if any(x in str(p) for x in ("/.git/", "/venv/", "/node_modules/", "__pycache__")):
        continue
    try:
        body = p.read_text(errors="ignore")[:200000]
        conn.execute("INSERT INTO md(path, body) VALUES (?,?)", (str(p), body))
        n += 1
    except OSError:
        pass
conn.commit()
conn.close()

# Generate Field Documents (Action #36, #87, #96)
(OUTDIR / "batch_cards_v1.md").write_text("""# OpenRoot Batch Cards v1
- w/c target 0.35-0.38 [MODEL - grade OPEN]
- NightHawk gel: ingredient UNRESOLVED (Xanthan/Dawn on N14 reject list)
- Record mass_kg + photo into popw_hang.py same day.
""", encoding="utf-8")

(OUTDIR / "service_flyer_v1.md").write_text("""# Concrete Repair & Site Prep - Sikeston area
- Local flatwork repair & structural pouring.
- Every job logged into OpenRoot PoPW ledger.
""", encoding="utf-8")

(OUTDIR / "customer_contract_v1.md").write_text("""# Service Contract (1 Page)
- Scope & Pricing defined per job site visit.
- Ledger & photo record retained locally.
""", encoding="utf-8")

print(json.dumps({
    "status": "TRIAGE_EXECUTED",
    "fts5_indexed_files": n,
    "outbox_artifacts": [str(x) for x in OUTDIR.glob("*.md")]
}, indent=2))
