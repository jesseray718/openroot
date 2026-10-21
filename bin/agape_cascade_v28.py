#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v28.py - single-book path integral (double-count fix).

v2.7 audit: leak == welf EXACTLY on every arm (231.397/231.4,
228.75/228.75, -27.28/-27.28). The path integral was written TWICE per
node-gen: credit term AND realized term. Telescope measured ~2x realized.

v2.8 bookkeeping law:
- PATH (the telescope): exactly ONE log per realized floor change -
  destruction, clamps, park/draw/grant all included. Realized change
  is ground truth; telescoping is then exact by construction.
- WELF (flow ledger): natural-flow credits only (production, decay,
  destruction measured at pre-transfer state). NON-telescoping by
  design; welf - path = TRANSFER WEDGE (parking/withdrawal/grant
  revaluation) - declared, printed, never silently swallowed.
- COST RANKINGS: computed from path (telescope-verified), NOT welf.

Canary: AGCA2V28
"""
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V28"
ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9
N = 100
GENS = 40
CAP = 1.0
FLOOR_MIN = 0.01
DECAY = 0.010
R_FRACTION = 0.10
BASE = 1.5
KAPPA = 0.08
SEED_TARGET = 0.50
SEED_TAX = 0.30
SHOCK_GEN = 12
SHOCK_LOSS = 0.60
SEED_LOSS = 0.40
DEPLOY_GENS = 5
DEPLOY_FRAC = 0.50
EDGE_BONUS = 1.5
GROWTH_CAP = 0.08
RETURN_FRAC = 0.30
POLICIES = ("bottom-first", "equal", "merit-top", "permaculture")


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
        if hi_share > 0 and lo:
            flown = hi_share * R_FRACTION
            for n in hi:
                alloc[n["id"]] -= flown * alloc[n["id"]] / hi_share
            for n in lo:
                alloc[n["id"]] += flown / max(len(lo), 1)
    elif policy == "permaculture":
        w = {}
        for n in nodes:
            v = 1.0 / math.sqrt(n["floor"] + EPS)
            if 0.20 <= n["floor"] < 0.65:
                v *= EDGE_BONUS
            w[n["id"]] = v
        tot = sum(w.values())
        for n in nodes:
            alloc[n["id"]] = s * w[n["id"]] / tot
        hi_share = sum(alloc[n["id"]] for n in hi)
        if hi_share > 0 and lo:
            tax = hi_share * RETURN_FRAC
            for n in hi:
                alloc[n["id"]] -= tax * alloc[n["id"]] / hi_share
            lw = sum(1.0 / (n["floor"] + EPS) for n in lo)
            for n in lo:
                alloc[n["id"]] += tax * (1.0 / (n["floor"] + EPS)) / lw
        for _ in range(12):
            capped = {nid for nid, a in alloc.items() if a > GROWTH_CAP}
            if not capped:
                break
            spill = 0.0
            for nid in capped:
                spill += alloc[nid] - GROWTH_CAP
                alloc[nid] = GROWTH_CAP
            active = [nid for nid, a in alloc.items()
                      if nid not in capped and a < GROWTH_CAP]
            if not active:
                break
            tw = sum(w[i] for i in active)
            for i in active:
                alloc[i] += spill * w[i] / tw
    return alloc


def run(policy, shocked):
    nodes = mk_nodes()
    f0_all = [n["floor"] for n in nodes]
    base_prod = sum(math.sqrt(f) for f in f0_all)
    welf = 0.0        # flow ledger: natural-flow credits only
    path_log = 0.0    # telescope: ONE log per realized change
    flow = {"parked": 0.0, "drawn": 0.0, "granted": 0.0,
            "overflow_cap": 0.0}
    pre_med = None
    recov = None
    for g in range(1, GENS + 1):
        pool = 0.0
        if shocked and SHOCK_GEN <= g < SHOCK_GEN + DEPLOY_GENS:
            for n in nodes:
                donation = DEPLOY_FRAC * n["seed"]
                n["seed"] -= donation
                pool += donation
        if shocked and g == SHOCK_GEN:
            for n in nodes:  # destruction: realized, BOTH books
                f_old = n["floor"]
                f_new = max(FLOOR_MIN, f_old * (1.0 - SHOCK_LOSS))
                term = math.log(max(f_new, EPS) / max(f_old, EPS))
                welf += term
                path_log += term
                n["floor"] = f_new
                n["seed"] *= (1.0 - SEED_LOSS)
        pool_alloc = allocate(nodes, pool, policy) if pool > 0 else {}
        s = BASE + KAPPA * max(0.0, sum(
            math.sqrt(n["floor"]) for n in nodes) - base_prod)
        alloc = allocate(nodes, s, policy)
        if shocked and g == SHOCK_GEN - 1:
            pre_med = statistics.median(n["floor"] for n in nodes)
        for n in nodes:
            f0 = n["floor"]
            nat = alloc[n["id"]] - DECAY
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
            grant = pool_alloc.get(n["id"], 0.0)
            if grant > 0:
                room = max(0.0, CAP - fw)
                fw += min(grant, room)
                flow["granted"] += min(grant, room)
            n["floor"] = fw
            # FIX: single realized-change write - THE telescope book
            if n["floor"] != f0:
                path_log += math.log(max(n["floor"], EPS) / max(f0, EPS))
        floors_now = [n["floor"] for n in nodes]
        if (shocked and pre_med is not None and recov is None
                and g > SHOCK_GEN
                and statistics.median(floors_now) >= pre_med):
            recov = g - SHOCK_GEN
    fs = [n["floor"] for n in nodes]
    final_gain = sum(
        math.log(max(a, EPS) / max(b, EPS)) for a, b in zip(fs, f0_all))
    return {
        "policy": policy, "shocked": shocked,
        "final_min_floor": round(min(fs), 4),
        "final_median_floor": round(statistics.median(fs), 4),
        "final_gini": round(gini(fs), 4),
        "frac_at_cap": round(
            sum(1 for f in fs if f >= CAP - 1e-6) / N, 3),
        "mean_seed_stock": round(sum(n["seed"] for n in nodes) / N, 4),
        "recovery_gens": recov if recov else "never",
        "welf_flow_ledger": round(welf, 2),
        "path_gain": round(path_log, 2),
        "transfer_wedge": round(welf - path_log, 2),
        "ledger_leak": round(path_log - final_gain, 9),
        "flow": {k: round(v, 2) for k, v in flow.items()},
    }


def main():
    runs = [(p, sh) for p in POLICIES for sh in (False, True)]
    results = [run(p, s) for (p, s) in runs]
    ctrl = {r["policy"]: r for r in results if not r["shocked"]}
    shock = {r["policy"]: r for r in results if r["shocked"]}
    lines = [
        "# Agape Cascade v2.8 - single-book path integral",
        datetime.now(timezone.utc).isoformat(),
        "",
        "v2.7 own goal: path written twice per node-gen (leak == welf).",
        "v2.8: one log per REALIZED change -> telescope exact by",
        "construction. Costs ranked on path (verified), welf declared",
        "separately with its transfer wedge (park/draw/grant revaluation).",
        "",
        "## Shocked arm (gen %d, -%.0f%% floors, -%.0f%% seeds)"
        % (SHOCK_GEN, 100 * SHOCK_LOSS, 100 * SEED_LOSS),
        "```",
        "%-14s %-8s %-8s %-7s %-6s %-6s %-8s %s" % (
            "policy", "min_fl", "med_fl", "gini", "cap%", "recov",
            "path", "cost_path"),
    ]
    for p in POLICIES:
        c, sh = ctrl[p], shock[p]
        cost = round(c["path_gain"] - sh["path_gain"], 2)
        lines.append("%-14s %-8s %-8s %-7s %-6s %-6s %-8s %s" % (
            p, sh["final_min_floor"], sh["final_median_floor"],
            sh["final_gini"], sh["frac_at_cap"],
            sh["recovery_gens"], sh["path_gain"], cost))
    lines += ["```", "", "## Control (no shock)", "```",
              "%-14s %-8s %-8s %-7s %-6s %-8s %-8s %s" % (
                  "policy", "min_fl", "med_fl", "gini", "cap%",
                  "path", "welf", "wedge")]
    for p in POLICIES:
        c = ctrl[p]
        lines.append("%-14s %-8s %-8s %-7s %-6s %-8s %-8s %s" % (
            p, c["final_min_floor"], c["final_median_floor"],
            c["final_gini"], c["frac_at_cap"], c["path_gain"],
            c["welf_flow_ledger"], c["transfer_wedge"]))
    lines += ["```", ""]
    max_leak = max(abs(r["ledger_leak"]) for r in results)
    lines += ["## Telescope integrity",
              "max |path - final_gain| = %s (expect ~1e-9)" % max_leak]
    verdict = 0
    if max_leak > 1e-6:
        lines.append("[LEAK] implementation bug - results INVALID")
        verdict = 1
    else:
        lines.append("[PASS] telescope exact - path rankings trustworthy")
    voided = [p for p in POLICIES
              if shock[p]["frac_at_cap"] > 0.5 or ctrl[p]["frac_at_cap"] > 0.5]
    if voided:
        lines += ["## SATURATION VOID LIST: %s" % ", ".join(voided)]
    else:
        lines += ["Saturation gate: all rows sub-ceiling - valid."]
    costs = {p: round(ctrl[p]["path_gain"] - shock[p]["path_gain"], 2)
             for p in POLICIES}
    best = min(costs, key=lambda p: costs[p])
    lines += ["", "## Path-verified shock costs (ctrl - shock)",
              "costs: %s" % costs,
              "lowest cost: %s at %.2f" % (best, costs[best]),
              "", "## Wedges (welf - path) - transfers, not losses:",
              " ".join("%s=%s" % (p, ctrl[p]["transfer_wedge"])
                       for p in POLICIES)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v28-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"regime": {"kappa": KAPPA, "gens": GENS, "decay": DECAY,
                     "seed_tax": SEED_TAX, "seed_target": SEED_TARGET,
                     "shock_gen": SHOCK_GEN, "shock_loss": SHOCK_LOSS,
                     "seed_loss": SEED_LOSS, "deploy_gens": DEPLOY_GENS,
                     "deploy_frac": DEPLOY_FRAC, "edge_bonus": EDGE_BONUS,
                     "growth_cap": GROWTH_CAP, "return_frac": RETURN_FRAC},
         "runs": results}, indent=1))
    print("[%s] single-book telescope, 4 policies" % CANARY)
    for r in results:
        print("  %-14s %-3s min=%s med=%s path=%s welf=%s wedge=%s leak=%s"
              % (r["policy"], "SHK" if r["shocked"] else "CTL",
                 r["final_min_floor"], r["final_median_floor"],
                 r["path_gain"], r["welf_flow_ledger"],
                 r["transfer_wedge"], r["ledger_leak"]))
    for p in POLICIES:
        print("  cost_path[%s] = %.2f | flow: %s"
              % (p, costs[p], shock[p]["flow"]))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    print("[%s] verdict=%d (bank proceeds regardless - negative is data)"
          % (CANARY, verdict))
    return verdict


if __name__ == "__main__":
    raise SystemExit(main())
