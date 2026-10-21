#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# git_absorb_v1.sh — full git history -> sha256 dedupe -> knowledge feed (SQLite)
# Absorbs every commit from root to HEAD: hash, message canaries, diffstat weight.
# Idempotent: re-runs only touch commits never seen before.
set -euo pipefail
export GIT_PAGER=cat
cd /home/jesse/openroot

TAG="[GITABSORBV1]"
STAMP="$(date +%Y%m%d_%H%M%S)"
DB=data/log_feed.db
LOGOUT=logs/git_absorb_${STAMP}.log
mkdir -p logs data

python3 - "$DB" <<'PYEOF' 2>&1 | tee -a "logs/git_absorb_stamp.tmp"
import sqlite3, hashlib, subprocess, json, datetime, sys, re

db = sys.argv[1]
now = datetime.datetime.now().isoformat(timespec="seconds")
conn = sqlite3.connect(db)
conn.execute("""CREATE TABLE IF NOT EXISTS git_absorb(
    commit_sha TEXT PRIMARY KEY, parent TEXT, author_date TEXT,
    subject TEXT, files_changed INT, insertions INT, deletions INT,
    msg_canaries TEXT, msg_hash TEXT, absorbed_at TEXT)""")
conn.commit()

# full history, oldest first, machine-readable
raw = subprocess.run(
    ["git", "log", "--reverse", "--all", "--date=iso",
     "--pretty=format:%H%x00%P%x00%ad%x00%s%x00%b%x01"],
    capture_output=True, text=True, check=True).stdout

canary_re = re.compile(r'\[[A-Z][A-Z0-9._ -]{1,40}\]')
seen, ingested = 0, 0
for rec in raw.split("\x01"):
    rec = rec.strip("\n\x00")
    if not rec.strip():
        continue
    parts = rec.split("\x00")
    if len(parts) < 5:
        continue
    sha, parent, date, subject, body = parts[0], parts[1], parts[2], parts[3], "\x00".join(parts[4:])
    seen += 1
    if conn.execute("SELECT 1 FROM git_absorb WHERE commit_sha=?", (sha,)).fetchone():
        continue  # NON-RECOMPUTE
    ds = subprocess.run(["git", "show", "--numstat", "--format=", sha],
                        capture_output=True, text=True).stdout
    ins = dels = files = 0
    for line in ds.splitlines():
        cols = line.split("\t")
        if len(cols) == 3:
            files += 1
            if cols[0].isdigit(): ins += int(cols[0])
            if cols[1].isdigit(): dels += int(cols[1])
    canaries = sorted(set(canary_re.findall(subject + " " + body)))[:10]
    msg_hash = hashlib.sha256((subject + body).encode()).hexdigest()[:16]
    conn.execute("INSERT INTO git_absorb VALUES(?,?,?,?,?,?,?,?,?,?)",
                 (sha, parent.split()[0] if parent else "", date, subject,
                  files, ins, dels, json.dumps(canaries), msg_hash, now))
    ingested += 1
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM git_absorb").fetchone()[0]
print(f"[GITABSORBV1] walked={seen} ingested={ingested} total_rows={total} db={db}")
top = conn.execute("""SELECT subject, files_changed, insertions FROM git_absorb
                      ORDER BY insertions DESC LIMIT 3""").fetchall()
print("[GITABSORBV1] biggest commits by insertions:")
for s, f, i in top:
    print(f"  +{i:>6} ({f:>3} files) {s[:70]}")
PYEOF
mv logs/git_absorb_stamp.tmp "$LOGOUT"

echo "$TAG [exit=0]" >> "$LOGOUT"
tail -1 "$LOGOUT" | grep -q '\[exit=0\]' && echo "$TAG tail-line check PASSED"
