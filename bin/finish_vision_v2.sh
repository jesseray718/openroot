#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# finish_vision_v2.sh — complete vision_all run after stage1 banked + lock incident.
# Rewrites dedup_pipeline with periodic commits + heartbeat, runs sweep, rung 8, seal.
# CANARY: FINISHV2. CONFIRM=1 to execute, dry-run otherwise. Idempotent: stage1 skipped.
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
CONFIRM="${CONFIRM:-0}"

cat <<'PYEOF' > /home/jesse/openroot/bin/dedup_pipeline_v2.py
# SPDX-License-Identifier: GPL-3.0-only
"""dedup_pipeline_v2.py — fixed v1: WAL + busy_timeout + periodic commits + heartbeat.
Fixes incident b35f1f72118121c9: single end-of-run transaction caused DB lock."""
import hashlib, json, os, sqlite3, time
DB = "/home/jesse/openroot/data/dedup_ledger.db"
ROOTS = ["/home/jesse/openroot"]
EXCLUDE = (".git", "node_modules", "__pycache__", ".venv", "venv", "quarantine",
            "archive", "attic", "consolidation-backups", "local_archive", "workareas")

def fp1(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(4096))
    return h.hexdigest()

def fp2(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    con = sqlite3.connect(DB, timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=30000")
    con.execute("""CREATE TABLE IF NOT EXISTS files(
        path TEXT PRIMARY KEY, size INT, mtime REAL, fp1 TEXT, sha256 TEXT,
        scanned_at REAL)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_fp1 ON files(fp1)")
    t0 = time.time(); t1 = 0; t2 = 0; since_commit = 0
    for root_dir in ROOTS:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
            for fn in files:
                p = os.path.join(root, fn)
                try:
                    st = os.stat(p)
                    f1 = fp1(p)
                except OSError:
                    continue
                t1 += 1
                row = con.execute("SELECT size, fp1 FROM files WHERE path=?", (p,)).fetchone()
                if row and row[1] == f1 and row[0] == st.st_size:
                    continue
                h2 = fp2(p); t2 += 1; since_commit += 1
                con.execute("INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?)",
                            (p, st.st_size, st.st_mtime, f1, h2, time.time()))
                if since_commit >= 2000:
                    con.commit(); since_commit = 0
                if t2 % 500 == 0:
                    print(f"[DEDUPV2-PROGRESS] tier2={t2} tier1={t1}", flush=True)
    con.commit()
    dups = con.execute(
        "SELECT COUNT(*) FROM (SELECT sha256 FROM files GROUP BY sha256 HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    redundant = con.execute(
        "SELECT COALESCE(SUM(c-1),0) FROM (SELECT COUNT(*) c FROM files GROUP BY sha256 HAVING c > 1)"
    ).fetchone()[0]
    con.close()
    out = {"tier1_seen": t1, "tier2_hashed": t2, "dup_groups": dups,
           "redundant_copies": redundant, "elapsed_s": round(time.time()-t0, 2)}
    print("[DEDUPV2]", out, flush=True)
    with open("/home/jesse/openroot/data/dedup_stream_latest.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
PYEOF
python3 -m py_compile /home/jesse/openroot/bin/dedup_pipeline_v2.py
grep -q "periodic commits" /home/jesse/openroot/bin/dedup_pipeline_v2.py

# rung 8 content already banked by v1 run (docs/OPEN_INVITATION.md) — verify, don't rewrite
grep -q "Credit is architectural" docs/OPEN_INVITATION.md && echo "[banked] OPEN_INVITATION.md confirmed present"

if [ "$CONFIRM" = "1" ]; then
  python3 bin/dedup_pipeline_v2.py
  python3 bin/launch_ladder_v1.py acknowledge open_invitation
  python3 bin/launch_ladder_v1.py status
  python3 bin/mistake_engine_v1.py solve b35f1f72118121c9 'single end-of-run sqlite transaction locked DB; fix=WAL+busy_timeout+commit-every-2000 (dedup_pipeline_v2.py)'
  git add bin/dedup_pipeline_v2.py bin/finish_vision_v2.sh docs/OPEN_INVITATION.md data/dedup_stream_latest.json
  git reset -q data/dedup_ledger.db 2>/dev/null || true
  git commit -m "[FIX] dedup v2: periodic commits+WAL heal lock incident b35f1f72181c9; rung 8 open_invitation (AI-assisted, human-gated)"
  echo "[gate] push when ready: git push origin main"
else
  echo "[dry-run] would run dedup sweep v2 + acknowledge rung 8 + seal mistake b35f1f72181c9 + commit"
fi
echo "[FINISHV2] tail-line: FINISHV2-COMPLETE"
