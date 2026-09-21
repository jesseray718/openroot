#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v23.py - seed reserves, floor ratchet, shock survival.

Thesis under test (jesse, 2026-09-21): "if each node keeps enough seeds
to redistribute and ensure survival upon immense sudden loss... the floor
continuously rises; ceiling rises, then floor rises - stairway."

Mechanism (ONE per version): seed buffer per node.
- Income pays decay FIRST (buffer holds high-water mark = hysteresis)
- Surplus fills seed reserve up to SEED_TARGET, rest lifts floor
- Catastrophe at SHOCK_GEN destroys SHOCK_LOSS of floors, SEED_LOSS of seeds
- Metric: post-shock recovery - gens to regain pre-shock min floor

Verdict semantics FIXED vs v2.2: negative results are data (exit 0);
hard-fail only on degenerate identical-row pathology.
Endogenous supply retained (kappa=0.15, mid-sweep).
Canary: AGCA2V23
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V23"
ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9
N = 100
GENS = 25
CAP = 1.0
FLOOR_MIN = 0.01
DECAY = 0.010
R_FRACTION = 0.10
BASE = 1.5
KAPPA = 0.15
SEED_TARGET = 0.50
SHOCK_GEN = 12
SHOCK_LOSS = 0.60
SEED_LOSS = 0.40

def mk_nodes():
    return [
        {"id": i, "floor": round(0.02 + 0.73 * (i / (N - 1)) ** 2, 4),
         "seed": 0.0, "hwm": 0.0}
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

def run(policy):
    nodes = mk_nodes()
    base_prod = sum(math.sqrt(n["floor"]) for n in nodes)
    welf = 0.0
    pre_shock_min = None
    post_shock_min = None
    recover_gens = None
    min_hist = []
    for g in range(1, GENS + 1):
        if g == SHOCK_GEN:
            for n in nodes:
                n["floor"] = max(FLOOR_MIN, n["floor"] * (1.0 - SHOCK_LOSS))
                n["seed"] *= (1.0 - SEED_LOSS)
            post_shock_min = min(n["floor"] for n in nodes)
        s = BASE + KAPPA * max(0.0, sum(
            math.sqrt(n["floor"]) for n in nodes) - base_prod)
        alloc = allocate(nodes, s, policy)
        for n in nodes:
            df = alloc[n["id"]]
            welf += math.log((n["floor"] + df) / n["floor"])
            income, need = df, DECAY
            if income >= need:
                rem = income - need
                to_seed = min(SEED_TARGET - n["seed"], rem)
                n["seed"] += to_seed
                n["floor"] = min(CAP, n["floor"] + rem - to_seed)
            else:
                deficit = need - income
                use = min(n["seed"], deficit)
                n["seed"] -= use
                n["floor"] = max(FLOOR_MIN, n["floor"] - (deficit - use))
            n["hwm"] = max(n["hwm"], n["floor"])
        mn = min(n["floor"] for n in nodes)
        min_hist.append(mn)
        if g == SHOCK_GEN - 1:
            pre_shock_min = mn
        if (post_shock_min is not None and pre_shock_min is not None
                and recover_gens is None and g > SHOCK_GEN
                and mn >= pre_shock_min):
            recover_gens = g - SHOCK_GEN
    fs = [n["floor"] for n in nodes]
    ss = [n["seed"] for n in nodes]
    return {
        "policy": policy,
        "pre_shock_min": round(pre_shock_min, 4),
        "post_shock_min": round(post_shock_min, 4),
        "recover_gens": recover_gens if recover_gens else "never",
        "final_min_floor": round(min(fs), 4),
        "final_gini": round(gini(fs), 4),
        "mean_seed_stock": round(sum(ss) / N, 4),
        "cumulative_welfare": round(welf, 2),
    }

def main():
    nodes = mk_nodes()
    lines = [
        "# Agape Cascade v2.3 - seed reserves + floor ratchet + shock",
        datetime.now(timezone.utc).isoformat(),
        "",
        "## Mechanism (seed-as-buffer hysteresis)",
        "income pays DECAY first; surplus fills seed reserve to %.1f,"
        % SEED_TARGET,
        "remainder lifts floor. Floor falls only when seeds are exhausted.",
        "Shock at gen %d: -%.0f%% floors, -%.0f%% seeds."
        % (SHOCK_GEN, 100 * SHOCK_LOSS, 100 * SEED_LOSS),
        "kappa=%.2f endogenous supply, BASE=%.1f, DECAY=%.3f."
        % (KAPPA, BASE, DECAY),
        "",
        "## Results",
        "```",
        "%-14s %-8s %-8s %-8s %-8s %-7s %-6s %s" % (
            "policy", "pre_min", "post_min", "recov", "fin_min",
            "gini", "seed", "welfare"),
    ]
    results = [run(p) for p in ("bottom-first", "equal", "merit-top")]
    for r in results:
        lines.append("%-14s %-8s %-8s %-8s %-8s %-7s %-6s %s" % (
            r["policy"], r["pre_shock_min"], r["post_shock_min"],
            r["recover_gens"], r["final_min_floor"], r["final_gini"],
            r["mean_seed_stock"], r["cumulative_welfare"]))
    lines += ["```", ""]
    wels = {r["policy"]: r["cumulative_welfare"] for r in results}
    if len(set(wels.values())) == 1:
        lines.append("## DEGENERATE: identical rows - hard fail")
        print("[%s] DEGENERATE rows - refusing success" % CANARY)
        return 1
    best = max(wels, key=wels.get)
    bf_rec = results[0]["recover_gens"]
    lines += [
        "## Verdict",
        "Best cumulative welfare: %s (%.2f)." % (best, wels[best]),
        "Bottom-first post-shock recovery: %s gens." % bf_rec,
        "Stairway confirmed iff bottom-first recovers (finite gens) AND",
        "final_min >= pre-shock min (floor resumed at ratcheted level).",
        "Seed stock column = resilience capital held by the network base.",
    ]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v23-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"regime": {"kappa": KAPPA, "seed_target": SEED_TARGET,
                     "shock_gen": SHOCK_GEN, "shock_loss": SHOCK_LOSS,
                     "seed_loss": SEED_LOSS}, "runs": results}, indent=1))
    print("[%s] shock gen %d: floors -%.0f%% seeds -%.0f%%" % (
        CANARY, SHOCK_GEN, 100 * SHOCK_LOSS, 100 * SEED_LOSS))
    for r in results:
        print("  %-14s pre=%s post=%s recov=%s fin=%s gini=%s seed=%s welf=%s" % (
            r["policy"], r["pre_shock_min"], r["post_shock_min"],
            r["recover_gens"], r["final_min_floor"], r["final_gini"],
            r["mean_seed_stock"], r["cumulative_welfare"]))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
