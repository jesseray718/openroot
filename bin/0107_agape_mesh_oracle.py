#!/usr/bin/env python3
"""
AgapeMesh Ledger Oracle — Parallel Track Only
Operator: Jesse Ray (OpenRoot)
Date: 2026-08-08
Never touches $HOME/agapenet or any original structure.
"""

import os, sys, json, hashlib, time, re
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timezone
import argparse

BASE_DIR = Path.home() / "agapemesh-ledger"
CONSTITUTION = BASE_DIR / "00_GENESIS_CONSTITUTION.md"
MERKLE_LOG = BASE_DIR / "merkle_orbit_log.json"
TODO = BASE_DIR / "MASTER_TODO.md"
OPERATIONAL = BASE_DIR / "01_OPERATIONAL_LOG.md"
QUANTUM = BASE_DIR / "02_QUANTUM_ODDS.md"
THERMO = BASE_DIR / "03_THERMO_BALANCE.md"
SYNC_BRIDGE = BASE_DIR / "sync_bridge.py"

PERMACULTURE = {
    "observe": 1.4, "interact": 1.35, "capture": 1.3, "store": 1.25,
    "obtain": 1.2, "yield": 1.3, "self-regulate": 1.45, "use-renewables": 1.25,
    "produce-no-waste": 1.4, "design-patterns": 1.35, "integrate": 1.3,
    "small-solutions": 1.2, "diversity": 1.4, "edges": 1.45, "creatively-respond": 1.35,
    "feedback": 1.4, "edge": 1.45
}

AGAPE_CORE = {
    "agape", "love", "light", "frequency", "resonance", "harmony", "legacy",
    "ancestor", "vessel", "source", "infinite", "structured", "creation",
    "justice", "restoration", "debt", "victim", "balance", "negentropy",
    "synergy", "antifragile", "mesh", "node", "cooperation", "voluntary",
    "ledger", "axiom", "constitution", "entropy", "joule", "η"
}

NOISE = {
    "git", "commit", "push", "pull", "rebase", "checkout", "branch", "merge",
    "hook", "hooks", "pack", "objects", "refs", "head", "log", "diff",
    "applypatch", "sendemail", "fsmonitor", "watchman", "jsonl", "docs",
    "usr", "bin", "the", "and", "of", "to", "in", "is", "that", "it",
    "for", "on", "with", "this", "from", "are", "was", "were", "be",
    "have", "has", "had", "not", "but", "or", "as", "at", "by", "an", "a"
}

COLLAPSE_VARIANCE = 0.292893
PURE_AGAPE = 0.82
LOW_ACTION = 0.42
HIGH_ACTION = 0.72

def ensure_structure():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "src").mkdir(exist_ok=True)
    (BASE_DIR / "docs").mkdir(exist_ok=True)
    (BASE_DIR / "logs").mkdir(exist_ok=True)
    (BASE_DIR / "ledger").mkdir(exist_ok=True)
    (BASE_DIR / "orbits").mkdir(exist_ok=True)
    if not CONSTITUTION.exists():
        CONSTITUTION.write_text("# 00_GENESIS_CONSTITUTION.md\n## Parallel Genesis\nη = useful_joules / human_joules\n")

def extract_words():
    word_counts = Counter()
    file_map = defaultdict(set)
    for md in BASE_DIR.glob("**/*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        words = re.findall(r"\b[a-z]{3,}\b", text)
        for w in words:
            if w not in NOISE:
                word_counts[w] += 1
                file_map[w].add(md.name)
    return word_counts, file_map

def score(word, counts, fmap):
    total = sum(counts.values()) or 1
    freq = counts.get(word, 0) / total
    conn = len(fmap.get(word, set())) / max(len(list(BASE_DIR.glob("**/*.md"))), 1)
    agape = 1.55 if word in AGAPE_CORE else 1.0
    perma = PERMACULTURE.get(word, 1.0)
    git_pen = 0.45 if any(g in word for g in ("git", "commit", "rebase", "checkout", "hook", "pack")) else 1.0
    raw = (freq * 12.0 + conn * 2.5) * agape * perma * git_pen
    return round(min(max(raw / 8.0, 0.0), 1.0), 4)

def quantum(top, counts, fmap):
    out = []
    for c in top[:24]:
        a = score(c, counts, fmap)
        e = 1.0 - a
        var = abs(a - e)
        collapsed = (var < COLLAPSE_VARIANCE) or (a >= PURE_AGAPE)
        out.append({"concept": c, "agape": a, "entropy": e, "variance": round(var, 4), "collapsed": collapsed})
    return out

def merkle(data):
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()

def log_orbit(num, results, mhash):
    collapsed = sum(1 for r in results if r["collapsed"])
    eff = round(collapsed / max(len(results), 1) * 100, 1)
    entry = {
        "orbit": num,
        "ts": datetime.now(timezone.utc).isoformat(),
        "merkle": mhash,
        "collapsed": collapsed,
        "total": len(results),
        "efficiency_pct": eff,
        "top_collapsed": [r["concept"] for r in results if r["collapsed"]][:8]
    }
    if MERKLE_LOG.exists():
        log = json.loads(MERKLE_LOG.read_text())
    else:
        log = {"orbits": []}
    log["orbits"].append(entry)
    MERKLE_LOG.write_text(json.dumps(log, indent=2))
    OPERATIONAL.write_text(f"# Operational Log\n\n## Orbit {num}\n- UTC: {entry['ts']}\n- Merkle: `{mhash}`\n- Collapsed: {collapsed}/{len(results)} ({eff}%)\n")
    QUANTUM.write_text("# Quantum Odds\n\n" + "\n".join(f"- {r['concept']}: Agape={r['agape']:.3f} Entropy={r['entropy']:.3f} Var={r['variance']:.3f} {'COLLAPSED' if r['collapsed'] else 'open'}" for r in results))
    THERMO.write_text(f"# Thermo Balance\n\nOrbit {num}\nEfficiency: {eff}%\nCollapsed: {collapsed}\nMerkle: {mhash[:24]}...\n")
    return eff, collapsed

def generate_todo(results):
    scores = [r["agape"] for r in results]
    avg = sum(scores) / len(scores) if scores else 0.55
    low = LOW_ACTION - 0.05 if 0.48 <= avg <= 0.68 else LOW_ACTION
    high = HIGH_ACTION + 0.05 if 0.48 <= avg <= 0.68 else HIGH_ACTION
    lines = ["# MASTER_TODO.md\n", "## Autonomous Action List\n"]
    for r in results:
        if r["agape"] < low:
            lines.append(f"[ ] PURGE ENTROPY: `{r['concept']}` (score {r['agape']:.3f})")
        elif r["agape"] >= high:
            lines.append(f"[x] AMPLIFY SIGNAL: `{r['concept']}` (score {r['agape']:.3f})")
    if len(lines) == 2:
        lines.append("[ ] MAINTAIN RESONANCE — system inside stable band.")
    TODO.write_text("\n".join(lines) + "\n")

def write_sync_bridge():
    code = r'''#!/usr/bin/env python3
"""sync_bridge.py — merge indexes from multiple AgapeMesh nodes"""
import json, hashlib, sys
from pathlib import Path
from datetime import datetime, timezone

def merge(dirs):
    merged = {"devices": {}, "concepts": {}, "synced_at": datetime.now(timezone.utc).isoformat()}
    for d in dirs:
        p = Path(d)
        for candidate in ["meta_index.json", "akashic_hyperindex.json", "merged_meta_index.json"]:
            f = p / candidate
            if not f.exists(): continue
            data = json.loads(f.read_text())
            device = p.name
            concepts = data.get("concepts", data) if isinstance(data, dict) else {}
            if not isinstance(concepts, dict): continue
            merged["devices"][device] = {"source": str(f), "count": len(concepts)}
            for k, v in concepts.items():
                h = hashlib.sha256(str(k).encode()).hexdigest()[:12]
                if h not in merged["concepts"]:
                    merged["concepts"][h] = {"concept": k, "sources": [device], "payload": v}
                else:
                    if device not in merged["concepts"][h]["sources"]:
                        merged["concepts"][h]["sources"].append(device)
    out = Path.home() / "agapemesh-ledger" / "merged_meta_index.json"
    out.write_text(json.dumps(merged, indent=2))
    print(f"Merged {len(merged['concepts'])} unique concepts from {len(merged['devices'])} devices → {out}")

if __name__ == "__main__":
    dirs = sys.argv[1:] or [str(Path.home() / "agapemesh-ledger")]
    merge(dirs)
'''
    SYNC_BRIDGE.write_text(code)
    SYNC_BRIDGE.chmod(0o755)

def run_orbit(n, delay=0):
    ensure_structure()
    write_sync_bridge()
    counts, fmap = extract_words()
    if not counts:
        print("No concepts yet. Seed files first.")
        return
    top = [w for w, _ in counts.most_common(80)]
    results = quantum(top, counts, fmap)
    mhash = merkle(results)
    eff, collapsed = log_orbit(n, results, mhash)
    generate_todo(results)
    print(f"Orbit {n} | collapsed {collapsed}/{len(results)} ({eff}%) | merkle {mhash[:16]}...")
    if delay > 0:
        time.sleep(delay)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.0)
    args = ap.parse_args()
    if args.loop > 0:
        for i in range(1, args.loop + 1):
            run_orbit(i, args.delay)
    else:
        run_orbit(1)

if __name__ == "__main__":
    main()
