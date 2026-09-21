#!/usr/bin/env python3
"""agape_cascade_v2.py - the thesis as simulation. AGCA2V2 canary.
Fixes v1.x bug: floor cap (100x100) sat BELOW supply line (300x100),
so tiers never activated - all v1 runs degenerated and proved nothing.
v2: caps live ABOVE supply; tiers activate; policies compete.

Model: log utility. Welfare of raising floor f by df = ln((f+df)/f).
Marginal value of a unit at floor f ~ 1/f. With f=0.02 vs f=0.75 the
ratio is 37.5x - computed, not asserted.

Generations: production = alpha * sum(floors). Policy splits production.
Capability feeds back: raised floors raise next-gen production. That is
the compounding loop. R_FRACTION = flow-through: fraction of top-node
gain routed to bottom tier next generation.
"""
import json, math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
EPS = 1e-9
ALPHA = 0.35          # production per unit of aggregate capability
GENS = 25
CAP = 1.0             # floor saturation (>= any single-gen supply)

def mk_nodes():
    return ([{"id": "b%d" % i, "floor": 0.02} for i in range(60)] +
            [{"id": "m%d" % i, "floor": 0.50} for i in range(30)] +
            [{"id": "t%d" % i, "floor": 0.75} for i in range(10)])

def supply(nodes):
    return ALPHA * sum(n["floor"] for n in nodes)

def welfare(f0, df):
    df = min(df, CAP - f0)
    if df <= 0:
        return 0.0
    return math.log((f0 + df) / max(f0, EPS))

def allocate(nodes, s, policy, rfraction=0.10):
    """Return per-node allocation. rfraction of TOP-tier-share gains
    flow through to bottom tier (flow-through doctrine)."""
    lo = [n for n in nodes if n["floor"] < 0.20]
    mid = [n for n in nodes if 0.20 <= n["floor"] < 0.65]
    hi = [n for n in nodes if n["floor"] >= 0.65]
    alloc = {n["id"]: 0.0 for n in nodes}
    if policy == "bottom-first":
        w = {n["id"]: 1.0 / (n["floor"] + EPS) for n in nodes}
        tot = sum(w.values())
        for n in nodes:
            alloc[n["id"]] = s * w[n["id"]] / tot
    elif policy == "equal":
        per = s / len(nodes)
        for n in nodes:
            alloc[n["id"]] = per
    elif policy == "merit-top":
        c = {n["id"]: n["floor"] for n in nodes}
        tot = sum(c.values())
        for n in nodes:
            alloc[n["id"]] = s * c[n["id"]] / tot
        # flow-through: rfraction of what the top got routes to bottom
        hi_share = sum(alloc[n["id"]] for n in hi)
        flown = hi_share * rfraction
        for n in hi:
            alloc[n["id"]] -= (flown * alloc[n["id"]] / hi_share) if hi_share else 0
        for n in lo:
            alloc[n["id"]] += flown / max(len(lo), 1)
    return alloc

def run(policy, gens=GENS):
    nodes = mk_nodes()
    floors_hist, welf = [], []
    for g in range(gens):
        s = supply(nodes)
        alloc = allocate(nodes, s, policy)
        w_total = 0.0
        for n in nodes:
            df = alloc[n["id"]]
            w_total += welfare(n["floor"], df)
            n["floor"] = min(CAP, n["floor"] + df)
        floors_hist.append([round(n["floor"], 4) for n in nodes])
        welf.append(round(w_total, 4))
    fs = [n["floor"] for n in nodes]
    import statistics
    return {
        "policy": policy,
        "final_min_floor": round(min(fs), 4),
        "final_mean_floor": round(statistics.mean(fs), 4),
        "gap": round(max(fs) - min(fs), 4),
        "cumulative_welfare": round(sum(welf), 2),
    }

def main():
    # 1. the 37.5x, computed
    f_lo, f_hi = 0.02, 0.75
    ratio = (1.0 / f_lo) / (1.0 / f_hi)
    lines = ["# Agape Cascade v2 - thesis as simulation",
             datetime.now(timezone.utc).isoformat(), "",
             "## Marginal utility identity (computed)",
             "1/f at f=0.02 : %.1f" % (1.0 / f_lo),
             "1/f at f=0.75 : %.3f" % (1.0 / f_hi),
             "RATIO: %.1fx  - a unit delivered at the bottom does" % ratio,
             "%.1f units of work vs the same unit at the top." % ratio, "",
             "## Generational cascade (25 gens, alpha=%.2f, R_FRACTION=0.10)" % ALPHA,
             "floor cap %.1f ABOVE any single-gen supply: tiers ACTIVATE." % CAP, ""]
    results = [run(p) for p in ("bottom-first", "equal", "merit-top")]
    hdr = ("%-14s %-8s %-8s %-8s %s" %
           ("policy", "min_fl", "mean_fl", "gap", "cum_welfare"))
    lines.append("```")
    lines.append(hdr)
    for r in results:
        lines.append("%-14s %-8s %-8s %-8s %s" % (
            r["policy"], r["final_min_floor"], r["final_mean_floor"],
            r["gap"], r["cumulative_welfare"]))
    lines.append("```")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    rp = wa / "cascade_report.md"
    rp.write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"marginal_ratio": round(ratio, 2), "runs": results}, indent=1))
    print("[AGCA2V2] marginal ratio computed: %.1fx" % ratio)
    for r in results:
        print("  %-14s min_floor=%s mean=%s welfare=%s" %
              (r["policy"], r["final_min_floor"],
               r["final_mean_floor"], r["cumulative_welfare"]))
    print("[REPORT] " + str(rp))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
