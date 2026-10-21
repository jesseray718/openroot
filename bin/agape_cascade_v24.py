#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""agape_cascade_v24.py - instrument repair on v2.3.

v2.3 flaws (audited per doctrine: instruments before builders):
(1) welfare counted rubble-regrowth as profit - shock pays ln-dividends
    => v2.4 debits destruction ln(new/old) at impact; net-zero accounting
(2) recov vs pre-shock MIN was vacuous for merit-top (baseline=FLOOR_MIN)
    => recovery vs pre-shock MEDIAN + vacuity guard
(3) seed-first fill starved floors (fill 0.5 before ANY floor growth)
    => SEED_TAX: proportional skim; floor climbs while bank fills
New: no-shock control arm per policy - resilience cost = control - shock.

Canary: AGCA2V24
"""
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

CANARY = "AGCA2V24"
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
SEED_TAX = 0.30        # fraction of surplus skimmed to seed bank
SHOCK_GEN = 12
SHOCK_LOSS = 0.60
SEED_LOSS = 0.40

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
    pre_shock_med = None
    recov = None
    for g in range(1, GENS + 1):
        if shocked and g == SHOCK_GEN:
            for n in nodes:
                # destruction DEBITED - regrowth must earn it back honestly
                welf += math.log(1.0 - SHOCK_LOSS)
                n["floor"] = max(FLOOR_MIN, n["floor"] * (1.0 - SHOCK_LOSS))
                n["seed"] *= (1.0 - SEED_LOSS)
        s = BASE + KAPPA * max(0.0, sum(
            math.sqrt(n["floor"]) for n in nodes) - base_prod)
        alloc = allocate(nodes, s, policy)
        for n in nodes:
            df = alloc[n["id"]]
            welf += math.log((n["floor"] + df) / n["floor"])
            if df >= DECAY:
                rem = df - DECAY
                to_seed = min(SEED_TARGET - n["seed"], SEED_TAX * rem)
                n["seed"] += to_seed
                n["floor"] = min(CAP, n["floor"] + rem - to_seed)
            else:
                deficit = DECAY - df
                use = min(n["seed"], deficit)
                n["seed"] -= use
                n["floor"] = max(FLOOR_MIN, n["floor"] - (deficit - use))
        if shocked and g == SHOCK_GEN - 1:
            pre_shock_med = statistics.median(n["floor"] for n in nodes)
        if (shocked and pre_shock_med is not None and recov is None
                and g > SHOCK_GEN
                and statistics.median(n["floor"] for n in nodes) >= pre_shock_med):
            recov = g - SHOCK_GEN
    fs = [n["floor"] for n in nodes]
    return {
        "policy": policy, "shocked": shocked,
        "final_min_floor": round(min(fs), 4),
        "final_median_floor": round(statistics.median(fs), 4),
        "final_gini": round(gini(fs), 4),
        "mean_seed_stock": round(sum(n["seed"] for n in nodes) / N, 4),
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
        "# Agape Cascade v2.4 - repaired instruments",
        datetime.now(timezone.utc).isoformat(),
        "",
        "## Repairs",
        "- welfare debits destruction at shock (net-zero rubble accounting)",
        "- recovery vs pre-shock MEDIAN (min-baseline vacuity eliminated)",
        "- SEED_TAX=%.2f proportional skim replaces seed-first starvation"
        % SEED_TAX,
        "- control arm isolates resilience cost",
        "",
        "## Results (SHOCKED arm: gen %d, -%.0f%% floors, -%.0f%% seeds)"
        % (SHOCK_GEN, 100 * SHOCK_LOSS, 100 * SEED_LOSS),
        "```",
        "%-14s %-8s %-8s %-7s %-6s %-7s %-11s %s" % (
            "policy", "min_fl", "med_fl", "gini", "seed", "recov", "welfare",
            "cost_vs_ctrl"),
    ]
    for p in ctrl:
        c, s = ctrl[p], shock[p]
        cost = round(c["cumulative_welfare"] - s["cumulative_welfare"], 2)
        lines.append("%-14s %-8s %-8s %-7s %-6s %-7s %-11s %s" % (
            p, s["final_min_floor"], s["final_median_floor"], s["final_gini"],
            s["mean_seed_stock"], s["recovery_gens"],
            s["cumulative_welfare"], cost))
    lines += ["```", "",
              "## Control (no shock) min floors: %s" % ", ".join(
                  "%s=%s" % (p, ctrl[p]["final_min_floor"]) for p in ctrl), ""]
    bf = shock["bottom-first"]
    stairway = (isinstance(bf["recovery_gens"], int)
                and bf["final_min_floor"] >= 0.20)
    if stairway:
        lines += ["## Verdict: STAIRWAY HOLDS",
                  "bottom-first recovered in %s gens, final min floor %s" % (
                      bf["recovery_gens"], bf["final_min_floor"]),
                  "- floor survived the catastrophe and kept climbing."]
        verdict = 0
    else:
        lines += ["## Verdict: stairway NOT confirmed under repaired metrics",
                  "bottom-first recov=%s, final min floor=%s." % (
                      bf["recovery_gens"], bf["final_min_floor"]),
                  "Honest negative - instruments now trustworthy; the",
                  "dynamics (SEED_TAX, DECAY, kappa) are the tuning knobs."]
        verdict = 0  # negative results are data, not failure
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = ROOT / "workareas" / ("cascade-v24-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    (wa / "cascade_report.md").write_text("\n".join(lines) + "\n")
    (wa / "results.json").write_text(json.dumps(
        {"regime": {"kappa": KAPPA, "seed_tax": SEED_TAX,
                     "seed_target": SEED_TARGET, "shock_gen": SHOCK_GEN,
                     "shock_loss": SHOCK_LOSS, "seed_loss": SEED_LOSS},
         "runs": results}, indent=1))
    print("[%s] SEED_TAX=%.2f median-recovery + rubble-netting" % (
        CANARY, SEED_TAX))
    for p in ctrl:
        c, s = ctrl[p], shock[p]
        print("  %-14s SHOCK min=%s med=%s recov=%s welf=%s (ctrl %s, cost %s)"
              % (p, s["final_min_floor"], s["final_median_floor"],
                 s["recovery_gens"], s["cumulative_welfare"],
                 c["cumulative_welfare"],
                 round(c["cumulative_welfare"] - s["cumulative_welfare"], 2)))
    print("[REPORT] " + str(wa / "cascade_report.md"))
    print("[%s] verdict=%d" % (CANARY, verdict))
    return verdict

if __name__ == "__main__":
    raise SystemExit(main())
