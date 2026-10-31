# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Layer2 SQLite index rebuilds from Layer1 chain.jsonl; cmds: show/anchors/drift"""
import json, pathlib, sqlite3, sys
REPO = "/home/jesse/openroot"
LEDGER = pathlib.Path(REPO + "/ledger/agape/chain.jsonl")
DB = REPO + "/ledger/agape/index.sqlite"
conn = sqlite3.connect(DB)
conn.executescript(
    "CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, kind TEXT NOT NULL,"
    " parents TEXT, created_utc TEXT NOT NULL, payload TEXT NOT NULL,"
    " supersedes TEXT, license TEXT);"
    "CREATE TABLE IF NOT EXISTS measurements(token TEXT, lang TEXT,"
    " century INTEGER, agape_score REAL, record_id TEXT REFERENCES records(id));"
    "CREATE INDEX IF NOT EXISTS idx_kind ON records(kind);")
if conn.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 0 and LEDGER.exists():
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        conn.execute("INSERT OR IGNORE INTO records VALUES (?,?,?,?,?,?,?)",
            (r["id"], r["kind"], json.dumps(r.get("parents", [])), r["created_utc"],
             json.dumps(r["payload"], ensure_ascii=False), r.get("supersedes"),
             r.get("license", "CC BY-SA 4.0")))
    conn.commit()
cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
if cmd == "show":
    for rid, kind, ts, sup in conn.execute(
            "SELECT id,kind,created_utc,supersedes FROM records ORDER BY rowid"):
        mark = "->" if sup else "  "
        print(f"{mark} {rid[:16]} kind={kind} created={ts}")
elif cmd == "anchors":
    row = conn.execute("SELECT payload FROM records WHERE kind='genesis'").fetchone()
    if row:
        p = json.loads(row[0])
        print(f"Axiom 0 anchor: {p['anchor_term']} ({p['anchor_translit']})")
        print(f"do NOT gloss as: {', '.join(p['do_not_gloss_as'])}")
        print(f"hypothesis: {p['hypothesis']['claim']}")
elif cmd == "drift":
    rows = conn.execute("SELECT token,lang,century,agape_score FROM measurements"
                        " ORDER BY century").fetchall()
    if not rows:
        print("[held] no measurements yet — etymon corpus not imported")
    for tok, lang, cent, score in rows:
        print(f"{tok} {lang} c{cent} score={score:.4f}")
else:
    print(f"unknown: {cmd}")
    sys.exit(1)
conn.close()
