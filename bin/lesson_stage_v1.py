#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""lesson_stage_v1.py - staging chain + graduation gateway for lessons.db

Foundational entry point. Main chain stays append-only and immutable.
Everything lands in staging first, runs deterministic gates, graduates
only via human gate CONFIRM=1. Flunked entries retained forever.

Commands:
  stage "<mistake>" "<root_cause>" "<correction>" [domain]
  check          advance intakes that pass gates to checked
  graduate <id>  copy to main chain (requires CONFIRM=1)
  flunk <id> "<reason>"
  report
"""
import sqlite3, hashlib, sys, os, json
from datetime import datetime, timezone

DB = os.path.expanduser("~/openroot/data/lessons.db")

def now(): return datetime.now(timezone.utc).isoformat()

def conn():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS staging_lessons (
        staging_id INTEGER PRIMARY KEY,
        ts TEXT, domain TEXT, mistake TEXT, root_cause TEXT, correction TEXT,
        stage TEXT,
        check_report TEXT,
        flunk_reason TEXT,
        mistake_sha TEXT, solution_sha TEXT, link_sha TEXT,
        stage_prev_sha TEXT,
        stage_sha TEXT UNIQUE,
        graduated_to_id INTEGER,
        source TEXT);
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY, ts TEXT, domain TEXT, mistake TEXT,
        root_cause TEXT, correction TEXT, cost TEXT, verified TEXT,
        recurrence_of TEXT,
        mistake_sha TEXT, solution_sha TEXT, link_sha TEXT);
    """)
    c.commit()
    return c

def shas(mistake, correction):
    msha = hashlib.sha256(mistake.encode()).hexdigest()[:16]
    ssha = hashlib.sha256(correction.encode()).hexdigest()[:16]
    return msha, ssha, hashlib.sha256((msha + ssha).encode()).hexdigest()[:16]

def last_stage_sha(c):
    r = c.execute("SELECT stage_sha FROM staging_lessons ORDER BY staging_id DESC LIMIT 1").fetchone()
    return r[0] if r else "GENESIS"

def run_checks(c, mistake, root_cause, correction):
    rep = {}
    rep["complete"] = bool(mistake.strip() and root_cause.strip() and correction.strip())
    rep["length_ok"] = len(mistake) >= 10 and len(correction) >= 10
    rep["distinct"] = mistake.strip() != correction.strip()
    rep["clean_text"] = all(ord(ch) >= 32 for ch in mistake + correction)
    lsha = shas(mistake, correction)[2]
    dup_main = c.execute("SELECT COUNT(*) FROM lessons WHERE link_sha=?", (lsha,)).fetchone()[0]
    dup_stage = c.execute("SELECT COUNT(*) FROM staging_lessons WHERE link_sha=? AND stage<>?", (lsha, "flunked")).fetchone()[0]
    rep["not_duplicate"] = (dup_main + dup_stage) == 0
    passed = all(rep.values())
    return passed, rep

def stage(mistake, root_cause, correction, domain, source="direct"):
    c = conn()
    msha, ssha, lsha = shas(mistake, correction)
    if c.execute("SELECT staging_id FROM staging_lessons WHERE link_sha=?", (lsha,)).fetchone():
        return "[IDEMPOTENT-HIT] already in staging"
    passed, rep = run_checks(c, mistake, root_cause, correction)
    prev = last_stage_sha(c)
    full = hashlib.sha256((prev + lsha + now()).encode()).hexdigest()[:16]
    c.execute("""INSERT INTO staging_lessons
        (ts, domain, mistake, root_cause, correction, stage, check_report,
         mistake_sha, solution_sha, link_sha, stage_prev_sha, stage_sha, source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (now(), domain, mistake, root_cause, correction,
         "checked" if passed else "intake",
         json.dumps(rep), msha, ssha, lsha, prev, full, source))
    c.commit()
    sid = c.execute("SELECT staging_id FROM staging_lessons WHERE stage_sha=?", (full,)).fetchone()[0]
    tag = "checked" if passed else "intake - gates FAILED, flunk candidate"
    return "[STAGED] id=" + str(sid) + " stage_sha=" + full + " -> " + tag

def check_all():
    c = conn()
    updated = 0
    for row in c.execute("SELECT staging_id, mistake, root_cause, correction FROM staging_lessons WHERE stage=?", ("intake",)).fetchall():
        sid, m, rc, co = row
        passed, rep = run_checks(c, m, rc, co)
        if passed:
            c.execute("UPDATE staging_lessons SET stage=?, check_report=? WHERE staging_id=?",
                      ("checked", json.dumps(rep), sid))
            updated += 1
    c.commit()
    return "[CHECK] " + str(updated) + " intakes advanced to checked; failures held for flunk review"

def graduate(sid):
    if os.environ.get("CONFIRM") != "1":
        return "[GATE] graduation requires CONFIRM=1 - human is the gate"
    c = conn()
    row = c.execute("SELECT mistake, root_cause, correction, domain, link_sha, stage FROM staging_lessons WHERE staging_id=?", (sid,)).fetchone()
    if not row:
        return "[ERROR] staging id " + str(sid) + " not found"
    m, rc, co, dom, lsha, stg = row
    if stg == "flunked":
        return "[GATE] staging id " + str(sid) + " is FLUNKED - flunked entries never graduate"
    if c.execute("SELECT 1 FROM lessons WHERE link_sha=?", (lsha,)).fetchone():
        c.execute("UPDATE staging_lessons SET stage=? WHERE staging_id=?", ("graduated", sid))
        c.commit()
        return "[IDEMPOTENT-HIT] already in main chain"
    msha, ssha, _ = shas(m, co)
    c.execute("""INSERT INTO lessons
        (ts, domain, mistake, root_cause, correction, verified,
         mistake_sha, solution_sha, link_sha) VALUES (?,?,?,?,?,?,?,?,?)""",
        (now(), dom, m, rc, co, "human-verified", msha, ssha, lsha))
    lid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.execute("UPDATE staging_lessons SET stage=?, graduated_to_id=? WHERE staging_id=?",
              ("graduated", lid, sid))
    c.commit()
    return "[GRADUATED] staging " + str(sid) + " -> main chain id " + str(lid)

def flunk(sid, reason):
    c = conn()
    row = c.execute("SELECT stage FROM staging_lessons WHERE staging_id=?", (sid,)).fetchone()
    if not row:
        return "[ERROR] staging id " + str(sid) + " not found"
    if row[0] == "graduated":
        return "[GATE] already in main chain - immutable, cannot flunk retroactively"
    c.execute("UPDATE staging_lessons SET stage=?, flunk_reason=? WHERE staging_id=?",
              ("flunked", reason, sid))
    c.commit()
    return "[FLUNKED] staging id " + str(sid) + " retained forever with reason: " + reason

def report():
    c = conn()
    lines = []
    for st, n in c.execute("SELECT stage, COUNT(*) FROM staging_lessons GROUP BY stage").fetchall():
        lines.append("  " + st + ": " + str(n))
    total = c.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    return "staging chain:\n" + "\n".join(lines) + "\nmain chain: " + str(total) + " entries (immutable)"

if __name__ == "__main__":
    cmds = {
        "stage": lambda: stage(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "infra"),
        "check": lambda: check_all(),
        "graduate": lambda: graduate(int(sys.argv[2])),
        "flunk": lambda: flunk(int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "unspecified"),
        "report": lambda: report(),
    }
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(0)
    print(cmds[sys.argv[1]]())
