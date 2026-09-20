#!/usr/bin/env python3
"""contribution_tier_v2.py — Bottom-floor weighted contribution grading
Core law: utility of benefit scales with (1 - recipient_percentile)^2.
Same benefit delivered to bottom decile = ~25x the weighted value of top decile.
Primary metric: FLOOR_LIFT (weighted benefit to the least)
Spread compression (reducing top-bottom gap) outranks aggregate volume.

Usage:
  submit --desc "..." --author "name" [--percentiles 10,30,50 --benefits 100,50,20]
  auto <id>        grade by floor-lift calculation
  leaderboard      ranked by FLOOR_LIFT (bottom-first)
  promote <id> --to T1|T2|T3   (requires CONFIRM=1)
  stats
"""
import os, sys, json, sqlite3, hashlib, argparse
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "openroot" / "data" / "contributions.db"

def now(): return datetime.now(timezone.utc).isoformat()

def conn():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS submissions_v2 (
        id INTEGER PRIMARY KEY, ts TEXT, author TEXT, description TEXT,
        link TEXT, tier TEXT DEFAULT 'T0',
        floor_lift REAL, aggregate_benefit REAL, spread_compression REAL,
        parent_sha TEXT, sha TEXT UNIQUE);
    """)
    c.commit()
    return c

def weighted_utility(percentiles, benefits):
    """Utility = sum(benefit_i * (1 - percentile_i/100)^2). Bottom = max weight."""
    if not percentiles:
        return 0.0
    return sum(b * ((1 - p/100) ** 2) for p, b in zip(percentiles, benefits))

def spread_compression(percentiles, benefits):
    """Does benefit go disproportionately DOWN the ladder? >1 = compresses spread."""
    if not percentiles or len(percentiles) < 2:
        return 1.0
    bottom_weight = sum(b for p, b in zip(percentiles, benefits) if p <= 30)
    top_weight = sum(b for p, b in zip(percentiles, benefits) if p >= 70)
    if top_weight == 0:
        return 99.0 if bottom_weight > 0 else 1.0
    return bottom_weight / top_weight

def auto_grade(sub_id, desc, percentiles, benefits):
    agg = sum(benefits) if benefits else 0
    floor_lift = weighted_utility(percentiles, benefits)
    compression = spread_compression(percentiles, benefits)
    # Tier on FLOOR_LIFT (primary), not aggregate
    if floor_lift >= 100:   tier = "T3"
    elif floor_lift >= 40:  tier = "T2"
    elif floor_lift >= 10:  tier = "T1"
    else:                   tier = "T0"
    return {"floor_lift": round(floor_lift, 2),
            "aggregate_benefit": agg,
            "spread_compression": round(compression, 2),
            "tier": tier,
            "note": "ranked by floor lift, not volume"}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("submit")
    s.add_argument("--desc", required=True)
    s.add_argument("--author", required=True)
    s.add_argument("--link", default="")
    s.add_argument("--percentiles", default="50", help="comma list: 10=highest need, 90=wealthiest")
    s.add_argument("--benefits", default="1", help="comma list matching percentiles")
    g = sub.add_parser("auto"); g.add_argument("id", type=int)
    l = sub.add_parser("leaderboard")
    p = sub.add_parser("promote"); p.add_argument("id", type=int); p.add_argument("--to", required=True)
    sub.add_parser("stats")
    args = ap.parse_args()
    c = conn()

    if args.cmd == "submit":
        pcts = [float(x) for x in args.percentiles.split(",")]
        bens = [float(x) for x in args.benefits.split(",")]
        sha = hashlib.sha256(f"{args.desc}:{args.author}".encode()).hexdigest()[:16]
        res = auto_grade(None, args.desc, pcts, bens)
        c.execute("""INSERT OR IGNORE INTO submissions_v2
            (ts, author, description, link, tier, floor_lift, aggregate_benefit, spread_compression, sha)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (now(), args.author, args.desc, args.link, res["tier"],
             res["floor_lift"], res["aggregate_benefit"], res["spread_compression"], sha))
        c.commit()
        print(json.dumps({"submitted": sha, **res}, indent=2))

    elif args.cmd == "auto":
        print("[NOTE] v2 grades at submit time; use 'leaderboard' to view")

    elif args.cmd == "leaderboard":
        rows = c.execute("""SELECT id, author, description, tier, floor_lift,
                            aggregate_benefit, spread_compression FROM submissions_v2
                            ORDER BY floor_lift DESC LIMIT 10""").fetchall()
        for r in rows:
            print(f"T{r[3]} | floor_lift={r[4]:>7} | agg={r[5]:>6} | compr={r[6]:>5} | {r[1]}: {r[2][:50]}")

    elif args.cmd == "promote":
        if os.environ.get("CONFIRM") != "1":
            raise SystemExit("[GATE] Promotion requires CONFIRM=1 (human is the gate)")
        cur = c.execute("SELECT tier FROM submissions_v2 WHERE id=?", (args.id,)).fetchone()
        if not cur: raise SystemExit("[ERROR] not found")
        allowed = {"T0": "T1", "T1": "T2", "T2": "T3"}
        if allowed.get(cur[0]) != args.to:
            raise SystemExit(f"[GATE] {cur[0]} -> {args.to} not allowed; progressive only")
        c.execute("UPDATE submissions_v2 SET tier=? WHERE id=?", (args.to, args.id)); c.commit()
        print(f"[BANKED] promoted {args.id} to {args.to}")

    elif args.cmd == "stats":
        rows = c.execute("SELECT tier, COUNT(*) FROM submissions_v2 GROUP BY tier").fetchall()
        print(json.dumps({"by_tier": {t: n for t, n in rows}}, indent=2))

if __name__ == "__main__":
    main()
