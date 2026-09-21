#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v21.py - desaturated cascade: discriminate policies.

v2 bug: all three policies returned IDENTICAL results (min=1.0,
welfare=258.39). Root cause: full saturation (every node hits CAP) makes
log utility path-INDEPENDENT - cumulative welfare = sum_i ln(CAP/f0_i)
by telescoping, regardless of allocation order.

v2.1: (a) supply ~40% of aggregate headroom (no saturation),
(b) additive DECAY per gen (path dependence),
(c) discrimination metrics: final Gini, gen-to-min-0.5, welfare.
Path-portable: ROOT derives from this file's location, not a hardcoded
host path. Canary: AGCA2V21
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V21"
ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9
N = 100
GENS = 25
CAP = 1.0
FLOOR_MIN = 0.01
DECAY = 0.010
R_FRACTION = 0.10
SUPPLY_PER_GEN = 1.5


def mk_nodes():
    return [
        {"id": i, "floor": round(0.02 + 0.73 * (i / (N - 1)) ** 2, 4)}
        for i in range(N)
    ]


def gini(xs):
    xs = sorted(xs)
    n = len(xs)
    tot = sum(xs)
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


def run(policy):
    nodes = mk_nodes()
    welf = 0.0
    gen_to_half = None
    for g in range(GENS):
        alloc = allocate(nodes, SUPPLY_PER_GEN, policy)
        for n in nodes:
            df = alloc[n["id"]]
            welf += math.log((n["floor"] + df) / n["floor"])
            n["floor"] = max(FLOOR_MIN, min(CAP, n["floor"] + df) - DECAY)
        mn = min(n["floor"] for n in nodes)
        if gen_to_half is None and mn >= 0.5:
            gen_to_half = g + 1
    fs = [n["floor"] for n in nodes]
    return {
        "policy": policy,
        "final_min_floor": round(min(fs), 4),
        "final_mean_floor": round(sum(fs) / N, 4),
        "final_gini": round(gini(fs), 4),
        "cumulative_welfare": round(welf, 2),
        "gen_to_min_half": gen_to_half if gen_to_half else "never",
        "saturated_nodes": sum(1 for f in fs if f >= CAP),
    }


def main():
    nodes = mk_nodes()
    headroom = sum(CAP - n["floor"] for n in nodes)
    total_supply = SUPPLY_PER_GEN * GENS
    lines = [
        "# Agape Cascade v2.1 - desaturated (policies can differ)",
        datetime.now(timezone.utc).isoformat(),
        "",
        "## Why v2 printed identical rows (path-independence proof)",
        "v2 supply saturated every node to CAP. Log utility telescopes:",
        "cum_welfare = sum_i ln(CAP/f0_i) - independent of allocation.",
        "258.39 was that constant. Fix: no saturation + additive decay.",
        "",
        "## Regime",
        "aggregate headroom: %.1f | total supply: %.1f (%.0f%% of headroom)" % (
            headroom, total_supply, 100.0 * total_supply / headroom),
        "DECAY=%.3f/gen | R_FRACTION=%.2f | GENS=%d | N=%d" % (
            DECAY, R_FRACTION, GENS, N),
        "",
        "## Results (%d gens)" % GENS,
        "```",
        "%-14s %-8s %-8s %-7s %-11s %-15s %s" % (
            "policy", "min_fl", "mean_fl", "gini", "cum_welfare",
            "gen_to_min_0.5", "sat"),
    ]
    results = [run(p) for p in ("bottom-first", "equal", "merit-top")]
    for r in results:
        lines.append("%-14s %-8s %-8s %-7s %-11s %-15s %s" % (
            r["policy"], r["final_min_floor"], r["final_mean_floor"],
            r["final_gini"], r["cumulative_welfare"], r["gen_to_min_half"],
            r["saturated_nodes"]))
    lines += ["```", ""]
    if len({r["cumulative_welfare"] for r in results}) == 1:
        lines.append("## FAIL: policies still identical - regime still degenerate")
        verdict = 1
    else:
        best = max(results, key=lambda r: r["cumulative_welfare"])["policy"]
        lines.append("## Verdict")
        lines.append("Policies differentiated. Best cumulative welfare: %s." % best)
        verdict = 0
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v21-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps({
        "regime": {"headroom": round(headroom, 1),
                    "total_supply": total_supply,
                    "decay": DECAY},
        "runs": results}, indent=1))
    print("[%s] headroom=%.1f supply=%.1f" % (CANARY, headroom, total_supply))
    for r in results:
        print("  %-14s min=%s mean=%s gini=%s welfare=%s half=%s sat=%s" % (
            r["policy"], r["final_min_floor"], r["final_mean_floor"],
            r["final_gini"], r["cumulative_welfare"], r["gen_to_min_half"],
            r["saturated_nodes"]))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    print("[%s] verdict=%d" % (CANARY, verdict))
    return verdict


if __name__ == "__main__":
    raise SystemExit(main())
