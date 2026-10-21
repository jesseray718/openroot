#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v22.py - synergetic compounding of sustained routing.

v2.1 blind spots (owned): (1) supply was EXOGENOUS constant 1.5/gen -
floors never fed back into supply; (2) nodes independent, no cross-terms.
v2.2 adds ONE mechanism (isolate the variable, permaculture small-slow):
  supply_g = BASE + kappa * (sum_sqrt(floors) - sum_sqrt(initial))
Concave production sqrt(f): a network produces by TRANSACTING, so a node's
output depends on peers near its own level - flattened distributions
maximize sum of sqrt. Sustained bottom-routing therefore compounds the
supply curve itself (synergetic compounding), IF kappa is large enough.
The sweep computes the flip threshold kappa*, the thesis-as-number.

Canary: AGCA2V22
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V22"
ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9
N = 100
GENS = 25
CAP = 1.0
FLOOR_MIN = 0.01
DECAY = 0.010
R_FRACTION = 0.10
BASE = 1.5
KAPPAS = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30)

def mk_nodes():
    return [
        {"id": i, "floor": round(0.02 + 0.73 * (i / (N - 1)) ** 2, 4)}
        for i in range(N)
    ]

def gini(xs):
    xs = sorted(xs)
    n, tot = len(xs), sum(xs)
    if tot <= 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2.0 * cum) / (n * tot) - (n + 1.0) / n

def allocate(nodes, s, policy):
    lo = [n for n in nodes if n["floor"] < 0.20]
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
        hi_share = sum(alloc[n["id"]] for n in hi)
        if hi_share > 0:
            flown = hi_share * R_FRACTION
            for n in hi:
                alloc[n["id"]] -= flown * alloc[n["id"]] / hi_share
            for n in lo:
                alloc[n["id"]] += flown / max(len(lo), 1)
    return alloc

def run(policy, kappa):
    nodes = mk_nodes()
    base_prod = sum(math.sqrt(n["floor"]) for n in nodes)
    welf, supplied = 0.0, 0.0
    for _ in range(GENS):
        s = BASE + kappa * max(0.0, sum(math.sqrt(n["floor"]) for n in nodes) - base_prod)
        supplied += s
        alloc = allocate(nodes, s, policy)
        for n in nodes:
            df = alloc[n["id"]]
            welf += math.log((n["floor"] + df) / n["floor"])
            n["floor"] = max(FLOOR_MIN, min(CAP, n["floor"] + df) - DECAY)
    fs = [n["floor"] for n in nodes]
    return {
        "policy": policy, "kappa": kappa,
        "final_min_floor": round(min(fs), 4),
        "final_gini": round(gini(fs), 4),
        "saturated_nodes": sum(1 for f in fs if f >= CAP),
        "total_supply": round(supplied, 1),
        "cumulative_welfare": round(welf, 2),
    }

def main():
    nodes = mk_nodes()
    headroom = sum(CAP - n["floor"] for n in nodes)
    lines = [
        "# Agape Cascade v2.2 - synergetic compounding (endogenous supply)",
        datetime.now(timezone.utc).isoformat(),
        "",
        "## Mechanism",
        "supply_g = BASE + kappa * (sum_sqrt(f) - sum_sqrt(f_init))",
        "Concave production: flattened floor distributions yield more total",
        "output. Sustained routing is an investment in the supply curve.",
        "",
        "## Sweep (GENS=%d, DECAY=%.3f, BASE=%.1f)" % (GENS, DECAY, BASE),
        "```",
        "%-6s %-14s %-8s %-7s %-6s %-11s %s" % (
            "kappa", "policy", "min_fl", "gini", "sat", "welfare", "tot_supply"),
    ]
    results = []
    for k in KAPPAS:
        for p in ("bottom-first", "equal", "merit-top"):
            r = run(p, k)
            results.append(r)
            lines.append("%-6s %-14s %-8s %-7s %-6s %-11s %s" % (
                k, r["policy"], r["final_min_floor"], r["final_gini"],
                r["saturated_nodes"], r["cumulative_welfare"], r["total_supply"]))
    lines += ["```", ""]
    flip = None
    for k in KAPPAS:
        wf = {r["policy"]: r["cumulative_welfare"]
              for r in results if r["kappa"] == k}
        bf, mt = wf["bottom-first"], wf["merit-top"]
        if flip is None and bf >= mt:
            flip = (k, bf, mt)
    if flip:
        lines += [
            "## Flip threshold (thesis as computed number)",
            "kappa* = %.2f : bottom-first welfare %.2f >= merit-top %.2f." % flip,
            "Above this coupling, sustained bottom-routing compounds supply",
            "faster than extractive routing harvests fixed supply.",
        ]
        verdict = 0
    else:
        lines += [
            "## No flip within sweep (honest negative)",
            "Bottom-first did NOT overtake merit-top at any tested kappa.",
            "Either coupling weaker than 0.30 in reality, or production is",
            "more linear than sqrt - regime needs rethink, not faith.",
        ]
        verdict = 1
    warn = [r for r in results if r["saturated_nodes"] > 0]
    if warn:
        lines += ["", "## SATURATION WARNING (v2 pathology watchdog)",
                  "%d run(s) touched CAP - those rows compress toward",
                  "path-independence; trust sub-saturation rows for ranking." % len(warn)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v22-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"headroom": round(headroom, 1), "runs": results,
         "flip_kappa": flip[0] if flip else None}, indent=1))
    print("[%s] headroom=%.1f" % (CANARY, headroom))
    for r in results:
        print("  k=%-5s %-14s min=%s gini=%s sat=%s welfare=%s supply=%s" % (
            r["kappa"], r["policy"], r["final_min_floor"], r["final_gini"],
            r["saturated_nodes"], r["cumulative_welfare"], r["total_supply"]))
    print("[%s] flip_kappa=%s verdict=%d" % (
        CANARY, flip[0] if flip else "none-within-sweep", verdict))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    return verdict

if __name__ == "__main__":
    raise SystemExit(main())
