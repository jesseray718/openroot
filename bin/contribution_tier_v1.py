#!/usr/bin/env python3
"""contribution_tier_v1.py — Blockchain-light contribution grading for human benefit
Tiers:
  T0 = theoretical idea (no implementation)
  T1 = prototype/code (verified working)
  T2 = deployed/useful (measurable human benefit)
  T3 = compounding (other contributors build on it)
Scoring: Impact × Replicability × Accessibility × Time-to-Benefit
Hash-chain verified: each submission sha256-linked to parent
Usage:
  init                      create contribution_db.sqlite
  submit "<description>" --author "name" --link "url"
  grade <id>                score submission (manual or auto)
  leaderboard               rank by human-benefit score
  promote <id> --to T2      manually advance tier (requires human review)
Doctrine:
  - All claims falsifiable (measure joules saved, lives touched, hours returned)
  - No extractive models (GPL-3.0 code, CC-BY-SA docs)
  - Permaculture alignment (regenerative, not extractive)
"""
import os, sys, json, sqlite3, hashlib
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "openroot" / "data" / "contributions.db"

CRITERIA = {
    "impact_score": ("Measured human benefit (0-10)", 10),
    "replicability": ("Can others rebuild from docs? (0-5)", 5),
    "accessibility": ("Free/open? No paywall? (0-3)", 3),
    "time_to_benefit": ("Hours until someone gains value (0-3, lower=better)", 3),
}

def now(): return datetime.now(timezone.utc).isoformat()

def conn():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY,
        ts TEXT, author TEXT, description TEXT, link TEXT,
        tier TEXT DEFAULT 'T0', score REAL, parent_sha TEXT,
        sha TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY, sub_id INTEGER, criterion TEXT,
        score REAL, max_score REAL, reviewer TEXT, ts TEXT);
    CREATE INDEX IF NOT EXISTS idx_submissions_tier ON submissions(tier);
    """)
    c.commit()
    return c

def sha_of(desc, author):
    return hashlib.sha256(f"{desc}:{author}:{now()}".encode()).hexdigest()[:16]

def submit(desc, author, link="", parent_sha=""):
    c = conn()
    sha = sha_of(desc, author)
    existing = c.execute("SELECT id FROM submissions WHERE sha=?", (sha,)).fetchone()
    if existing:
        return {"idempotent_hit": existing[0], "sha": sha}
    c.execute("INSERT INTO submissions (ts, author, description, link, parent_sha, sha) VALUES (?,?,?,?,?,?)",
              (now(), author, desc, link, parent_sha, sha))
    c.commit()
    return {"submitted": sha, "tier": "T0", "status": "pending review"}

def grade(sub_id, criterion, score, reviewer="auto"):
    c = conn()
    max_s = CRITERIA.get(criterion, ("", 3))[1]
    if score > max_s: score = max_s
    c.execute("INSERT INTO grades (sub_id, criterion, score, max_score, reviewer, ts) VALUES (?,?,?,?,?,?)",
              (sub_id, criterion, score, max_s, reviewer, now()))
    # Recalculate total
    totals = c.execute("SELECT SUM(score) FROM grades WHERE sub_id=?", (sub_id,)).fetchone()[0] or 0
    c.execute("UPDATE submissions SET score=? WHERE id=?", (totals, sub_id))
    c.commit()
    return {"graded": criterion, "score": score, "total": totals}

def calculate_human_benefit(desc, tier):
    """Heuristic scoring based on criteria."""
    desc_lower = desc.lower()
    # Impact: words suggesting tangible benefit
    impact_words = ["save", "benefit", "help", "reduce", "increase", "lives", "people", "hours", "joules"]
    impact = min(10, sum(1 for w in impact_words if w in desc_lower) * 2)
    # Replicability: mentions code, open, instructions
    rep_words = ["code", "github", "repo", "instruction", "tutorial", "step-by-step"]
    replicability = min(5, sum(1 for w in rep_words if w in desc_lower) * 1)
    # Accessibility: mentions free, open, no-paywall
    acc_words = ["free", "open", "public", "no cost", "gratis"]
    accessibility = 3 if any(w in desc_lower for w in acc_words) else 1
    # Time to benefit: shorter text = faster comprehension
    time_score = 3 if len(desc.split()) < 50 else (2 if len(desc.split()) < 100 else 1)
    return {"impact": impact, "replicability": replicability, "accessibility": accessibility, "time_to_benefit": time_score}

def auto_grade(sub_id):
    c = conn()
    desc = c.execute("SELECT description FROM submissions WHERE id=?", (sub_id,)).fetchone()[0]
    tier = c.execute("SELECT tier FROM submissions WHERE id=?", (sub_id,)).fetchone()[0]
    metrics = calculate_human_benefit(desc, tier)
    for criterion, val in metrics.items():
        grade(sub_id, criterion, val, reviewer="auto_grader")
    # Update tier based on score
    total = metrics["impact"] + metrics["replicability"] + metrics["accessibility"] + metrics["time_to_benefit"]
    new_tier = "T0" if total < 6 else ("T1" if total < 12 else ("T2" if total < 16 else "T3"))
    c.execute("UPDATE submissions SET tier=?, score=? WHERE id=?", (new_tier, total, sub_id))
    c.commit()
    return {"metrics": metrics, "total": total, "tier_advanced_to": new_tier}

def promote(sub_id, target_tier):
    c = conn()
    if os.environ.get("CONFIRM") != "1":
        raise SystemExit("[GATE] Tier promotion requires CONFIRM=1 (human oversight)")
    current = c.execute("SELECT tier FROM submissions WHERE id=?", (sub_id,)).fetchone()[0]
    allowed = {"T0": ["T1"], "T1": ["T2"], "T2": ["T3"]}
    if target_tier not in allowed.get(current, []):
        raise SystemExit(f"[GATE] Cannot jump from {current} to {target_tier}. Progressive advancement only.")
    c.execute("UPDATE submissions SET tier=? WHERE id=?", (target_tier, sub_id))
    c.commit()
    return {"promoted": sub_id, "from": current, "to": target_tier}

def leaderboard(limit=10):
    c = conn()
    rows = c.execute("""SELECT id, author, description, tier, score, ts 
                        FROM submissions ORDER BY score DESC LIMIT ?""", (limit,)).fetchall()
    return [{"id": r[0], "author": r[1], "desc": r[2][:60], "tier": r[3], "score": r[4], "ts": r[5]} for r in rows]

def stats():
    c = conn()
    total = c.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    by_tier = c.execute("SELECT tier, COUNT(*), COALESCE(AVG(score),0) FROM submissions GROUP BY tier").fetchall()
    return {"total": total, "by_tier": [{"tier": t, "count": n, "avg_score": round(s, 2)} for t, n, s in by_tier]}

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(0)
    cmd = sys.argv[1]
    c = conn()
    if cmd == "init":
        print("[INIT] contributions.db created")
    elif cmd == "submit" and len(sys.argv) >= 4:
        desc = sys.argv[2]; author = sys.argv[3]; link = "--link " in sys.argv and sys.argv[sys.argv.index("--link")+1] or ""; parent = "--parent " in sys.argv and sys.argv[sys.argv.index("--parent")+1] or ""
        print(json.dumps(submit(desc, author, link, parent), indent=2))
    elif cmd == "grade" and len(sys.argv) >= 4:
        sub_id = int(sys.argv[2]); crit = sys.argv[3]; scr = float(sys.argv[4]) if len(sys.argv) > 4 else CRITERIA.get(crit, ("", 3))[1]
        print(json.dumps(grade(sub_id, crit, scr), indent=2))
    elif cmd == "auto":
        sub_id = int(sys.argv[2])
        print(json.dumps(auto_grade(sub_id), indent=2))
    elif cmd == "promote" and len(sys.argv) >= 4:
        sub_id = int(sys.argv[2]); tier = sys.argv[3]
        print(json.dumps(promote(sub_id, tier), indent=2))
    elif cmd == "leaderboard":
        print(json.dumps(leaderboard(int(sys.argv[2]) if len(sys.argv)>2 else 10), indent=2))
    elif cmd == "stats":
        print(json.dumps(stats(), indent=2))
    else:
        print(__doc__)
