#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v26.py - conservation-law ledger (telescope audit).

v2.5 audit (own goal confessed): shocked arms BEAT controls (-90.9
welfare) with identical saturated endpoints - violating telescoping.
Leaks found: (a) ln-credit included to_seed (phantom floor growth),
(b) seed capital: park = unlogged, solidarity-grant = logged income
(asymmetric minting - deploy printed welfare from parked value).

v2.6 ledger law:
- LOGGED (natural flow): production income, decay, destruction
- NEUTRAL (store moves): seed park, seed draw, solidarity grant
- DECLARED (not vanished): overflow beyond CAP, grants clipped at CAP
- TELESCOPE CHECK: path-integral of ln(floor ratios) MUST equal
  ln(final/initial) summed - any residual = implementation bug,
  printed as [LEAK], verdict hard-fails only on this.

Canary: AGCA2V26
"""
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V26"
ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9
N = 100
GENS = 60
CAP = 1.0
FLOOR_MIN = 0.01
DECAY = 0.010
R_FRACTION = 0.10
BASE = 1.5
KAPPA = 0.15
SEED_TARGET = 0.50
SEED_TAX = 0.30
SHOCK_GEN = 12
SHOCK_LOSS = 0.60
SEED_LOSS = 0.40
DEPLOY_GENS = 5
DEPLOY_FRAC = 0.50

def mk_nodes():
    return [
        {"id": i, "floor": round(0.02 + 0.73 * (i / (N - 1)) ** 2, 4),
         "seed": 0.0}
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

def run(policy, shocked):
    nodes = mk_nodes()
    f0_all = [n["floor"] for n in nodes]
    base_prod = sum(math.sqrt(f) for f in f0_all)
    welf = 0.0
    path_log = 0.0
    flow = {"parked": 0.0, "drawn": 0.0, "granted": 0.0,
            "overflow_cap": 0.0, "grant_clipped": 0.0}
    pre_med = None
    recov = None
    idle_gens = 0
    for g in range(1, GENS + 1):
        pool = 0.0
        if shocked and SHOCK_GEN <= g < SHOCK_GEN + DEPLOY_GENS:
            for n in nodes:
                donation = DEPLOY_FRAC * n["seed"]
                n["seed"] -= donation
                pool += donation
        if shocked and g == SHOCK_GEN:
            # destruction: natural flow, LOGGED
            for n in nodes:
                welf += math.log(1.0 - SHOCK_LOSS)
                n["floor"] = max(FLOOR_MIN, n["floor"] * (1.0 - SHOCK_LOSS))
                n["seed"] *= (1.0 - SEED_LOSS)
        pool_alloc = allocate(nodes, pool, policy) if pool > 0 else {}
        s = BASE + KAPPA * max(0.0, sum(
            math.sqrt(n["floor"]) for n in nodes) - base_prod)
        alloc = allocate(nodes, s, policy)
        if shocked and g == SHOCK_GEN - 1:
            pre_med = statistics.median(n["floor"] for n in nodes)
        for n in nodes:
            f0 = n["floor"]
            prod = alloc[n["id"]]
            grant = pool_alloc.get(n["id"], 0.0)
            # --- natural flow: LOGGED ---
            nat = prod - DECAY
            f_nat = f0 + nat
            if f_nat > CAP:
                credit = CAP - f0
                flow["overflow_cap"] += f_nat - CAP
                f_nat = CAP
            elif f_nat < FLOOR_MIN:
                credit = FLOOR_MIN - f0
                f_nat = FLOOR_MIN
            else:
                credit = nat
            if abs(credit) > 1e-12:
                welf += math.log(max(f0 + credit, EPS) / max(f0, EPS))
            # --- store moves: NEUTRAL ---
            fw = f_nat
            if credit > 0:
                to_seed = min(SEED_TARGET - n["seed"], SEED_TAX * credit)
                n["seed"] += to_seed
                fw -= to_seed
                flow["parked"] += to_seed
            elif credit < 0:
                draw = min(n["seed"], -credit)
                n["seed"] -= draw
                fw += draw
                flow["drawn"] += draw
            if grant > 0:
                room = max(0.0, CAP - fw)
                fw += min(grant, room)
                flow["granted"] += min(grant, room)
                flow["grant_clipped"] += max(0.0, grant - room)
            n["floor"] = fw
            if n["floor"] != f0:
                path_log += math.log(max(n["floor"], EPS) / max(f0, EPS))
        floors_now = [n["floor"] for n in nodes]
        if min(floors_now) >= CAP - 1e-6:
            idle_gens += 1
        if (shocked and pre_med is not None and recov is None
                and g > SHOCK_GEN
                and statistics.median(floors_now) >= pre_med):
            recov = g - SHOCK_GEN
    fs = [n["floor"] for n in nodes]
    final_gain = sum(
        math.log(max(a, EPS) / max(b, EPS)) for a, b in zip(fs, f0_all))
    leak = path_log - final_gain
    return {
        "policy": policy, "shocked": shocked,
        "final_min_floor": round(min(fs), 4),
        "final_median_floor": round(statistics.median(fs), 4),
        "final_gini": round(gini(fs), 4),
        "mean_seed_stock": round(sum(n["seed"] for n in nodes) / N, 4),
        "idle_gens_at_cap": idle_gens,
        "recovery_gens": recov if recov else "never",
        "cumulative_welfare": round(welf, 2),
        "path_log": round(path_log, 2),
        "final_gain": round(final_gain, 2),
        "ledger_leak": round(leak, 6),
        "flow": {k: round(v, 2) for k, v in flow.items()},
    }

def main():
    runs = [(p, sh) for p in ("bottom-first", "equal", "merit-top")
            for sh in (False, True)]
    results = [run(p, s) for (p, s) in runs]
    ctrl = {r["policy"]: r for r in results if not r["shocked"]}
    shock = {r["policy"]: r for r in results if r["shocked"]}
    lines = [
        "# Agape Cascade v2.6 - conservation-law ledger",
        datetime.now(timezone.utc).isoformat(),
        "",
        "## Ledger law",
        "LOGGED: production, decay, destruction. NEUTRAL: park/draw/grant.",
        "Telelescope check: path-integral must equal ln(final/initial).",
        "",
        "## Results (SHOCKED arm)",
        "```",
        "%-14s %-8s %-8s %-7s %-6s %-7s %-6s %-11s %s" % (
            "policy", "min_fl", "med_fl", "gini", "seed", "idle", "recov",
            "welfare", "cost"),
    ]
    for p in ctrl:
        c, sh = ctrl[p], shock[p]
        cost = round(c["cumulative_welfare"] - sh["cumulative_welfare"], 2)
        lines.append("%-14s %-8s %-8s %-7s %-6s %-7s %-6s %-11s %s" % (
            p, sh["final_min_floor"], sh["final_median_floor"],
            sh["final_gini"], sh["mean_seed_stock"], sh["idle_gens_at_cap"],
            sh["recovery_gens"], sh["cumulative_welfare"], cost))
    lines += ["```", "",
              "## Control (no shock)", "```",
              "%-14s %-8s %-8s %-7s %-6s %-6s %-11s" % (
                  "policy", "min_fl", "med_fl", "gini", "seed", "idle",
                  "welfare")]
    for p in ctrl:
        c = ctrl[p]
        lines.append("%-14s %-8s %-8s %-7s %-6s %-6s %-11s" % (
            p, c["final_min_floor"], c["final_median_floor"], c["final_gini"],
            c["mean_seed_stock"], c["idle_gens_at_cap"],
            c["cumulative_welfare"]))
    lines += ["```", ""]
    max_leak = max(abs(r["ledger_leak"]) for r in results)
    lines += ["## Telescope integrity",
              "max |path_log - final_gain| across runs: %s" % max_leak]
    if max_leak > 1e-3:
        lines.append("[LEAK] implementation bug - results INVALID")
        verdict = 1
    else:
        verdict = 0
        costs = {p: round(ctrl[p]["cumulative_welfare"]
                          - shock[p]["cumulative_welfare"], 2) for p in ctrl}
        lines += ["Integrity holds. Costs (ctrl - shock): %s" % costs]
        if any(v < -1e-6 for v in costs.values()):
            lines += ["NEGATIVE cost persists post-fix: transfers are",
                      "provably neutral now, so a negative cost would be a",
                      "REAL result (e.g. rebuild-phase log fertility) -",
                      "report it, do not bury it."]
        else:
            lines += ["All costs positive - v2.5's negative costs were",
                      "ledger artifacts (phantom parking + minted grants).",
                      "The stairway verdict now rests on honest numbers."]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v26-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"regime": {"kappa": KAPPA, "seed_tax": SEED_TAX,
                     "seed_target": SEED_TARGET, "shock_gen": SHOCK_GEN,
                     "shock_loss": SHOCK_LOSS, "seed_loss": SEED_LOSS,
                     "deploy_gens": DEPLOY_GENS, "deploy_frac": DEPLOY_FRAC,
                     "gens": GENS}, "runs": results}, indent=1))
    print("[%s] flow-ledger + telescope check" % CANARY)
    for r in results:
        print("  %-14s %-7s min=%s med=%s recov=%s welf=%s leak=%s" % (
            r["policy"], "SHK" if r["shocked"] else "CTL",
            r["final_min_floor"], r["final_median_floor"],
            r["recovery_gens"], r["cumulative_welfare"], r["ledger_leak"]))
    for p in ctrl:
        print("  cost[%s] = %.2f | flow: %s" % (
            p, ctrl[p]["cumulative_welfare"]
            - shock[p]["cumulative_welfare"], shock[p]["flow"]))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    print("[%s] verdict=%d" % (CANARY, verdict))
    return verdict

if __name__ == "__main__":
    raise SystemExit(main())
