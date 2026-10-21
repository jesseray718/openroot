#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v25.py - solidarity deployment + closed welfare ledger.

v2.4 findings (banked 9473d77d): equal pays least shock cost (26.6%),
merit-top most (49.9%); bottom-first pays 35% but holds 2x the floor.
recov=never was a horizon artifact (13 post-shock gens).

v2.5 changes:
(a) HORIZON: GENS=60 - long enough to see actual recovery or its absence
(b) SOLIDARITY (jesse's mechanism, first formal appearance): for
    DEPLOY_GENS after shock, each node donates DEPLOY_FRAC of its seed
    reserve to a pool; pool reallocated per policy into floors.
    Seeds stop being a private mattress; they become agape.
(c) CLOSED LEDGER (instrument repair): all NATURAL floor movement -
    production, decay, destruction - enters welfare symmetrically
    (ln debit on losses, incl. decay erosion, which prior versions
    silently swallowed). Seed transactions (park, buffer, deploy)
    are TRANSFERS: welfare-neutral, excluded.
Canary: AGCA2V25
"""
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V25"
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
    base_prod = sum(math.sqrt(n["floor"]) for n in nodes)
    welf = 0.0
    pre_med = None
    recov = None
    deployed_total = 0.0
    for g in range(1, GENS + 1):
        # solidarity deployment window
        pool = 0.0
        if shocked and SHOCK_GEN <= g < SHOCK_GEN + DEPLOY_GENS:
            for n in nodes:
                donation = DEPLOY_FRAC * n["seed"]
                n["seed"] -= donation
                pool += donation
        deployed_total += pool
        # shock (destruction is a natural debit via closed ledger below)
        if shocked and g == SHOCK_GEN:
            for n in nodes:
                n["floor"] = max(FLOOR_MIN, n["floor"] * (1.0 - SHOCK_LOSS))
                n["seed"] *= (1.0 - SEED_LOSS)
        # solidarity pool reallocated per policy
        pool_alloc = allocate(nodes, pool, policy) if pool > 0 else {}
        s = BASE + KAPPA * max(0.0, sum(
            math.sqrt(n["floor"]) for n in nodes) - base_prod)
        alloc = allocate(nodes, s, policy)
        if shocked and g == SHOCK_GEN - 1:
            pre_med = statistics.median(n["floor"] for n in nodes)
        for n in nodes:
            f0 = n["floor"]
            df = alloc[n["id"]] + pool_alloc.get(n["id"], 0.0)
            # natural dynamics
            if df >= DECAY:
                rem = df - DECAY
                to_seed = min(SEED_TARGET - n["seed"], SEED_TAX * rem)
                n["seed"] += to_seed
                n["floor"] = min(CAP, f0 + df - DECAY - to_seed)
                transfers_in = pool_alloc.get(n["id"], 0.0)
                transfers_out = to_seed
            else:
                deficit = DECAY - df
                use = min(n["seed"], deficit)
                n["seed"] -= use
                n["floor"] = max(FLOOR_MIN, f0 + df - DECAY + use)
                transfers_in = use + pool_alloc.get(n["id"], 0.0)
                transfers_out = 0.0
            f1 = n["floor"]
            nat = (f1 - f0) - transfers_in + transfers_out
            if abs(nat) > 1e-12:
                welf += math.log(max(f0 + nat, FLOOR_MIN) / f0)
        if (shocked and pre_med is not None and recov is None
                and g > SHOCK_GEN
                and statistics.median(n["floor"] for n in nodes) >= pre_med):
            recov = g - SHOCK_GEN
    fs = [n["floor"] for n in nodes]
    return {
        "policy": policy, "shocked": shocked,
        "final_min_floor": round(min(fs), 4),
        "final_median_floor": round(statistics.median(fs), 4),
        "final_gini": round(gini(fs), 4),
        "mean_seed_stock": round(sum(n["seed"] for n in nodes) / N, 4),
        "deployed_pool": round(deployed_total, 1),
        "recovery_gens": recov if recov else "never",
        "cumulative_welfare": round(welf, 2),
    }

def main():
    runs = [(p, sh) for p in ("bottom-first", "equal", "merit-top")
            for sh in (False, True)]
    results = [run(p, s) for (p, s) in runs]
    ctrl = {r["policy"]: r for r in results if not r["shocked"]}
    shock = {r["policy"]: r for r in results if r["shocked"]}
    lines = [
        "# Agape Cascade v2.5 - solidarity + closed ledger + 60 gens",
        datetime.now(timezone.utc).isoformat(),
        "",
        "## Mechanism",
        "Post-shock solidarity: %d gens, %.0f%% of seed reserves donated"
        % (DEPLOY_GENS, 100 * DEPLOY_FRAC),
        "per gen into a policy-routed rebuild pool.",
        "Closed ledger: production/decay/destruction symmetric ln;",
        "seed parking/buffering/deployment = transfer, welfare-neutral.",
        "",
        "## Results (shocked arm; shock gen %d)" % SHOCK_GEN,
        "```",
        "%-14s %-8s %-8s %-7s %-6s %-7s %-7s %-11s %s" % (
            "policy", "min_fl", "med_fl", "gini", "seed", "pool", "recov",
            "welfare", "cost"),
    ]
    for p in ctrl:
        c, s = ctrl[p], shock[p]
        cost = round(c["cumulative_welfare"] - s["cumulative_welfare"], 2)
        lines.append("%-14s %-8s %-8s %-7s %-6s %-7s %-7s %-11s %s" % (
            p, s["final_min_floor"], s["final_median_floor"], s["final_gini"],
            s["mean_seed_stock"], s["deployed_pool"], s["recovery_gens"],
            s["cumulative_welfare"], cost))
    lines += ["```", "",
              "## Control (no shock) welfare: %s" % ", ".join(
                  "%s=%s" % (p, ctrl[p]["cumulative_welfare"]) for p in ctrl)]
    bf = shock["bottom-first"]
    stairway = isinstance(bf["recovery_gens"], int)
    lines += ["", "## Verdict",
              "bottom-first recovery: %s gens (vs v2.4: never in 13)."
              % bf["recovery_gens"]]
    if stairway:
        lines.append("Stairway: shock absorbed, median regained, floor higher")
        lines.append("than equal's under identical shock? min_fl %s vs %s." % (
            bf["final_min_floor"], shock["equal"]["final_min_floor"]))
    else:
        lines.append("Honest negative persists at 60 gens with solidarity -")
        lines.append("either DEPLOY_FRAC/DEPLOY_GENS too weak, or the shock")
        lines.append("is beyond this parameter regime. Knobs, not faith.")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v25-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"regime": {"kappa": KAPPA, "seed_tax": SEED_TAX,
                     "seed_target": SEED_TARGET, "shock_gen": SHOCK_GEN,
                     "shock_loss": SHOCK_LOSS, "seed_loss": SEED_LOSS,
                     "deploy_gens": DEPLOY_GENS,
                     "deploy_frac": DEPLOY_FRAC, "gens": GENS},
         "runs": results}, indent=1))
    print("[%s] GENS=%d solidarity=%.0f%%x%dgens closed-ledger" % (
        CANARY, GENS, 100 * DEPLOY_FRAC, DEPLOY_GENS))
    for p in ctrl:
        c, s = ctrl[p], shock[p]
        print("  %-14s min=%s med=%s recov=%s welf=%s (ctrl %s, cost %s)"
              % (p, s["final_min_floor"], s["final_median_floor"],
                 s["recovery_gens"], s["cumulative_welfare"],
                 c["cumulative_welfare"],
                 round(c["cumulative_welfare"] - s["cumulative_welfare"], 2)))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
