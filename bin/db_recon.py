#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [canary] paste intact
# db_recon.py v2 — PERMACULTURE-GATED SQLite inventory + keyword retrieval.
#   STAGE 1 [observe]   : find candidate DBs, verify paths exist, no reads
#   STAGE 2 [interact]  : read-only probes (mode=ro), schema + rowcounts
#   STAGE 3 [search]    : keyword retrieval, read-only, column-capped
#   STAGE 4 [feedback]  : bank inventory JSON to context_bridge/, sealed
# Gates:
#   - paths admitted only after existence check (library-first admission)
#   - databases opened READ-ONLY via URI mode=ro — cannot mutate sources
#   - oversize DBs are flagged, not probed (accept no gigabyte floods)
#   - corrupt/unreadable DBs are quarantined (reported, skipped) not fatal
#   - inventory banked to ONE canonical path; failure = [held], never crash
# Usage: python3 /home/jesse/openroot/bin/db_recon.py [keyword] [confirm]
import os, sys, sqlite3, json, datetime

CANARY = "paste intact"
NODE = "optiplex3060"
CANDIDATE_ROOTS = [
    "/home/jesse/openroot/logs",
    "/home/jesse/openroot/context_bridge",
    "/home/jesse/openroot/data/ai_lumo-handoffs",
    "/home/jesse/openroot",
    "/home/jesse/src/openroot",
    "/home/jesse/src/openroot-thesis",
]
EXCLUDE_DIRS = {".git", "salvage", "salvaged", "node_modules",
                "build", "models", "venv", "attic"}
MAX_DB_BYTES = 200 * 1024 * 1024   # flag, don't probe, above this
KEYWORD = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
CONFIRM = "confirm" in sys.argv
BANK_DIR = "/home/jesse/openroot/context_bridge"
BANK_NAME_PREFIX = "db_inventory"

# ---------- STAGE 1: [observe] admission gate ----------
def gate_roots():
    admitted, refused = [], []
    for root in CANDIDATE_ROOTS:
        if os.path.isdir(root):
            admitted.append(root)
        else:
            refused.append(root)
    return admitted, refused

def find_dbs(admitted):
    found = []
    for root in admitted:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in filenames:
                if fn.endswith((".db", ".sqlite", ".sqlite3")):
                    p = os.path.join(dirpath, fn)
                    try:
                        sz = os.path.getsize(p)
                    except OSError:
                        continue
                    found.append((p, sz))
    return found

# ---------- STAGE 2: [interact] read-only probe ----------
def probe(db_path):
    """One DB, read-only. Returns (tables dict, ok bool)."""
    tables = {}
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = con.cursor()
        names = [r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        for t in names:
            if t.startswith("sqlite_"):
                continue
            cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{t}")')]
            fts = ("fts" in t.lower()
                   or any(c in cols for c in ("content", "docid")))
            try:
                n = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            except Exception:
                n = -1
            tables[t] = {"rows": n, "cols": cols, "fts": fts}
        con.close()
        return tables, True
    except Exception as e:
        tables["__QUARANTINE__"] = {"rows": 0, "cols": [str(e)[:120]], "fts": False}
        return tables, False

# ---------- STAGE 3: [search] keyword retrieval, read-only ----------
def search(db_path, tables, keyword):
    hits = []
    con = None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = con.cursor()
        for t, meta in tables.items():
            if t.startswith("__") or meta["rows"] <= 0:
                continue
            # FTS tables: dedicated MATCH syntax when present
            if meta["fts"]:
                try:
                    q = f'SELECT rowid FROM "{t}" WHERE "{t}" MATCH ? LIMIT 10'
                    for (rid,) in cur.execute(q, (keyword,)):
                        hits.append(f"{db_path} :: {t} :: MATCH rowid={rid}")
                    continue
                except Exception:
                    pass  # fall through to LIKE scan
            for c in meta["cols"][:6]:
                try:
                    q = f'SELECT rowid FROM "{t}" WHERE CAST("{c}" AS TEXT) LIKE ? LIMIT 5'
                    for (rid,) in cur.execute(q, (f"%{keyword}%",)):
                        hits.append(f"{db_path} :: {t} :: col={c} rowid={rid}")
                except Exception:
                    pass
        con.close()
    except Exception:
        if con:
            try: con.close()
            except Exception: pass
    return hits

# ---------- STAGE 4: [feedback] bank inventory ----------
def bank(inventory, quarantine, flagged):
    try:
        os.makedirs(BANK_DIR, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out = os.path.join(BANK_DIR, f"{BANK_NAME_PREFIX}_{stamp}.json")
        payload = {"node": NODE, "generated": stamp,
                   "inventory": inventory,
                   "quarantined": quarantine,
                   "flagged_oversize": flagged}
        with open(out, "w") as f:
            json.dump(payload, f, indent=1)
        return out
    except Exception as e:
        print(f"[held] bank failed: {e}")
        return None

# ---------- MAIN ----------
print(f"[canary] {CANARY} | node={NODE} | keyword={KEYWORD!r} | confirm={CONFIRM}")

admitted, refused = gate_roots()
for r in refused:
    print(f"[refuse-path] {r} (does not exist — admitted nothing, mutated nothing)")
print(f"[admit-path] {len(admitted)} roots admitted for observation")

dbs = find_dbs(admitted)
print(f"[observe] {len(dbs)} candidate sqlite files found")

inventory, quarantine, flagged = [], [], []
for path, sz in sorted(dbs):
    mb = sz / 1024 / 1024
    if sz > MAX_DB_BYTES:
        flagged.append((path, round(mb, 1)))
        continue
    tables, ok = probe(path)
    entry = {"db": path, "size_kb": round(sz / 1024), "tables": tables}
    if ok:
        inventory.append(entry)
    else:
        quarantine.append(entry)
    tag = "" if ok else " [QUARANTINED]"
    print(f"\n== {path}  ({mb:.2f} MB){tag}")
    for t, meta in sorted(tables.items()):
        ncols = len(meta["cols"])
        preview = ",".join(str(c) for c in meta["cols"][:8]) + ("..." if ncols > 8 else "")
        fts_tag = " [FTS]" if meta["fts"] else ""
        print(f"   {t[:40]:40s} rows={meta['rows']:>9} cols({ncols}): {preview}{fts_tag}")

for path, mb in flagged:
    print(f"\n[flagged-oversize] {path} ({mb} MB) — probe separately if needed")

# Bank only with confirm; otherwise the full inventory IS the terminal output
if CONFIRM:
    out = bank(inventory, quarantine, flagged)
    if out:
        print(f"\n[banked] inventory -> {out}")
else:
    print("\n[dry-run] inventory NOT banked — re-run with 'confirm' as final arg to write JSON")

if KEYWORD:
    print(f"\n[search] keyword '{KEYWORD}':")
    total = 0
    for item in inventory:
        for h in search(item["db"], item["tables"], KEYWORD):
            print("   " + h)
            total += 1
    print(f"[search] {total} hits (rowids only; fetch rows next once schemas reviewed)")
else:
    print("\n[next] re-run with a keyword:  python3 $SCRIPT <keyword> [confirm]")

print(f"[done] probed={len(inventory)} quarantined={len(quarantine)} flagged={len(flagged)}")
