#!/usr/bin/env python3
"""window_fuse_v1.py - window extraction + isolated fresh-mind fusion workarea
+ Matthew 25:40 floor-lift optimizer. WINFUSEV1 canary.

Three stages, one run:
  [extract] scan window (24h) of context_bridge/ bin/ data/ analysis/
            digests only, no bodies: the fresh mind gets a MINIMAL seed,
            proving the fusion converges from compressed context, not cargo.
  [fuse]    build isolated workarea workareas/fuse-<ts>/ containing ONLY:
            window digest, lesson chain seal, node model, fused path.
            No inherited runtime state. Fresh mind = digest in, decision out.
  [matthew] MT25:40 optimizer: w_i = 1/(f_i + eps); score actions as
            verified-bottom-decile benefit / cost, subject to hard
            non-regression floor guard. Writes fused_path.md for human gate.

Doctrine: human gates graduation of the fused path into GOALS/MASTER_TODO.
Nothing here commits, pushes, or writes outside workareas/.
Transport doctrine: this file must be deployed via stdin heredoc (bash -s)
or base64 - never inline through the ssh single-quote eval layer.
"""
import hashlib, json, os, statistics, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DB = ROOT / "data/lessons.db"
WORKROOT = ROOT / "workareas"
CANARY = "WINFUSEV1"
EPS = 1e-6

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def extract_window(hours=24):
    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    digest = {}
    for sub in ("context_bridge", "bin", "data", "analysis"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.stat().st_mtime >= cutoff:
                try:
                    h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                except OSError:
                    continue
                rel = str(p.relative_to(ROOT))
                digest[rel] = {"mtime": int(p.stat().st_mtime),
                               "sha16": h,
                               "bytes": p.stat().st_size}
    return digest

def lesson_shas():
    if not DB.exists():
        return []
    c = sqlite3.connect(str(DB))
    try:
        return [r[0] for r in c.execute(
            "SELECT link_sha FROM lessons ORDER BY id").fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        c.close()

def load_nodes(wa):
    """Node model: floor f_i in [0,1], capacity. Live model wins;
    demo seed proves the math end-to-end with zero external state."""
    live = ROOT / "data" / "matthew_nodes.json"
    if live.exists():
        nodes = json.loads(live.read_text())["nodes"]
        src = "live:data/matthew_nodes.json"
    else:
        nodes = [
            {"id": "demo-floor",  "floor": 0.05, "capacity_w": 100},
            {"id": "demo-lower",  "floor": 0.30, "capacity_w": 100},
            {"id": "demo-middle", "floor": 0.60, "capacity_w": 100},
            {"id": "demo-top",    "floor": 0.90, "capacity_w": 100},
        ]
        src = "DEMO SEED - replace data/matthew_nodes.json for live runs"
    (wa / "node_model_source.txt").write_text(src)
    return nodes

def mt2540_weight(f):
    """Matt 25:40 identity mapping: done to the least == done to Him.
    Coefficient diverges as floor -> 0. Harm to the least cannot be
    compensated anywhere - the floor guard enforces that clause."""
    return 1.0 / (f + EPS)

def evaluate(nodes, alloc_j):
    gains, floors, wscores = {}, {}, {}
    for n in nodes:
        a = alloc_j.get(n["id"], 0.0)
        gain = a * (1.0 - n["floor"])
        gains[n["id"]] = gain
        floors[n["id"]] = n["floor"] + gain
        wscores[n["id"]] = gain * mt2540_weight(n["floor"])
    old_min = min(n["floor"] for n in nodes)
    new_min = min(floors.values())
    old_base = {n["id"]: n["floor"] for n in nodes}
    regressed = [i for i, f in floors.items() if f < old_base[i] - EPS]
    old_med = statistics.median(list(old_base.values()))
    new_med = statistics.median(list(floors.values()))
    return {
        "floor_lift": new_min - old_min,
        "gap_compression": (old_med - old_min) - (new_med - new_min),
        "weight_score": sum(wscores.values()),
        "regressions": regressed,
    }

def fuse(nodes, candidates):
    ranked = []
    for cand in candidates:
        verdict = evaluate(nodes, cand["alloc"])
        if verdict["regressions"]:
            cand["verdict"] = "REJECTED - floor regression, Mt 25:40 violation"
            ranked.append((None, cand, verdict))
            continue
        score = verdict["floor_lift"] / max(cand.get("cost_j", 1.0), EPS)
        cand["verdict"] = "VALID"
        ranked.append((score, cand, verdict))
    valid = [r for r in ranked if r[0] is not None]
    valid.sort(key=lambda r: -r[0])
    return ranked, (valid[0][1] if valid else None)

def candidate_sets(ids):
    lo, ml, mi, hi = ids[0], ids[1], ids[2], ids[3]
    return [
        {"name": "equal-spread", "cost_j": 1.0,
         "alloc": {lo: 0.25, ml: 0.25, mi: 0.25, hi: 0.25}},
        {"name": "bottom-first (Mt 25:40)", "cost_j": 1.0,
         "alloc": {lo: 0.60, ml: 0.25, mi: 0.10, hi: 0.05}},
        {"name": "merit-top (beast-pattern control)", "cost_j": 1.0,
         "alloc": {lo: 0.05, ml: 0.10, mi: 0.25, hi: 0.60}},
    ]

def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa = WORKROOT / ("fuse-" + ts)
    wa.mkdir(parents=True, exist_ok=True)
    print("[" + CANARY + "] canary intact, workarea:", wa.name)

    digest = extract_window()
    (wa / "window_digest.json").write_text(json.dumps(
        {"generated": now(), "window_hours": 24,
         "files": digest, "count": len(digest)}, indent=1))
    shas = lesson_shas()
    (wa / "lesson_chain_seal.json").write_text(json.dumps(
        {"chain_length": len(shas),
         "tip_link_sha": shas[-1] if shas else None,
         "all_link_shas": shas}, indent=1))
    print("[EXTRACT] window files:", len(digest),
          "| lesson chain:", len(shas))

    nodes = load_nodes(wa)
    if len(nodes) < 4:
        print("[WARN] node model has fewer than 4 nodes - "
              "candidate allocator expects 4+; aborting safely")
        return 1
    candidates = candidate_sets([n["id"] for n in nodes[:4]])
    ranked, best = fuse(nodes, candidates)

    report = ["# Fused Path - " + ts, "",
              "Fresh mind = window digest + chain seal ONLY.",
              "Source: " + (wa / "node_model_source.txt").read_text(), "",
              "## Matthew 25:40 objective",
              "maximize delta(min floor) per joule, subject to",
              "zero-regression on any node floor.",
              "w_i = 1/(f_i + eps) - done to the least == done to Him.", ""]
    for score, cand, v in ranked:
        line = "- **{}**: {} | floor_lift {:+.4f} | gap_comp {:+.4f} | weight {:.4f}".format(
            cand["name"], cand["verdict"],
            v["floor_lift"], v["gap_compression"], v["weight_score"])
        if score is not None:
            line += " | lift/joule {:.4f}".format(score)
        report.append(line)
    if best:
        report += ["", "**SELECTED PATH: " + best["name"] + "**",
                   "allocation: " + json.dumps(best["alloc"]), "",
                   "Human gate: review, then graduate allocation policy",
                   "into GOALS.md / matthew_nodes.json updates."]
    (wa / "fused_path.md").write_text("\n".join(report) + "\n")
    (wa / "matthew_verdicts.json").write_text(json.dumps(
        [{"candidate": c["name"], "verdict": c["verdict"],
          "metrics": v} for _, c, v in ranked], indent=1))
    print("[FUSE] selected:", best["name"] if best else "NONE VALID")
    print("[MATTHEW] report:", wa / "fused_path.md")
    print("[" + CANARY + "] complete - nothing committed; human gate holds.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
