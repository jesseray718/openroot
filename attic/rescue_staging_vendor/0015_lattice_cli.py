#!/usr/bin/env python3
"""
OpenRoot Lattice CLI — persistent deep reasoner
JSON in → multi-depth proof → merkle → ACRE mint
Now with: persistent NP- memory + --from seeding
"""
import json, hashlib, os, sys, time, uuid
from copy import deepcopy
from datetime import datetime, timezone
from collections import defaultdict

TERMUX = "/data/data/com.termux/files/home"
ROOT = os.path.join(TERMUX, "projects/openroot") if os.path.exists(TERMUX) else os.path.expanduser("$HOME/openroot")
LEDGER = os.path.join(ROOT, "acre/ledger.jsonl")
LEARNINGS = os.path.join(ROOT, "learnings/lattice.json")
os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
os.makedirs(os.path.dirname(LEARNINGS), exist_ok=True)

AXIOMS = {
    "AX-001": {"s": "Energy is neither created nor destroyed", "c": "physics"},
    "AX-002": {"s": "Entropy of an isolated system never decreases", "c": "physics"},
    "AX-003": {"s": "Every action has equal and opposite reaction", "c": "physics"},
    "AX-018": {"s": "Every bit erased costs ≥ kT ln(2) joules", "c": "computation"},
    "AX-019": {"s": "Computation is a physical process", "c": "computation"},
    "AX-022": {"s": "Observe before acting", "c": "permaculture"},
    "AX-023": {"s": "Capture and store energy when abundant", "c": "permaculture"},
    "AX-024": {"s": "Obtain a yield", "c": "permaculture"},
    "AX-025": {"s": "Apply self-regulation and accept feedback", "c": "permaculture"},
    "AX-027": {"s": "Produce no waste", "c": "permaculture"},
    "AX-040": {"s": "Proof requires witness; truth demands verification", "c": "consensus"},
    "AX-041": {"s": "Immutability preserves truth across time", "c": "consensus"},
}

def P(rule, from_, cond, effect, depth=1):
    return {"rule": rule, "from": from_, "cond": cond, "effect": effect, "depth": depth}

BASE_POSTULATES = {
    "P-001": P("Insufficient observation reduces quality",
               ["AX-022"], lambda p: p.get("observation_days",0)<7,
               lambda p: p.update({"η_penalty": p.get("η_penalty",0)+6}), 1),
    "P-002": P("Finite energy sources carry systemic debt",
               ["AX-002","AX-023"], lambda p: p.get("energy","grid") not in ("solar","wind","hydro","biomass"),
               lambda p: p.update({"η_penalty": p.get("η_penalty",0)+10}), 2),
    "P-003": P("No feedback → fragile system",
               ["AX-025"], lambda p: not p.get("feedback"),
               lambda p: p.update({"η_penalty": p.get("η_penalty",0)+8}), 2),
    "P-004": P("Waste outputs = incomplete design",
               ["AX-027"], lambda p: any(o.get("disp")=="waste" for o in p.get("outputs",[])),
               lambda p: p.update({"η_penalty": p.get("η_penalty",0)+8}), 2),
    "P-005": P("High human input violates least-effort",
               ["AX-024"], lambda p: p.get("human_input",1)>8,
               lambda p: p.update({"η_penalty": p.get("η_penalty",0)+6}), 2),
    "P-020": P("Unobserved high-effort is ethically questionable",
               ["AX-022","AX-024","P-001","P-005"],
               lambda p: p.get("observation_days",0)==0 and p.get("human_input",0)>5,
               lambda p: p.update({"η_penalty":p.get("η_penalty",0)+8, "recommendations":p.get("recommendations",[])+["HALT-level: restart with observation"]}), 4),
    "P-024": P("Compute without joule accounting is incomplete",
               ["AX-018","AX-019"], lambda p: p.get("compute_joules",0)==0 and p.get("involves_compute"),
               lambda p: p.update({"η_penalty": p.get("η_penalty",0)+6}), 3),
}

class Lattice:
    def __init__(self):
        self.axioms = AXIOMS
        self.post = dict(BASE_POSTULATES)
        self.new = []
        self.proof = []
        self._load_persistent()

    def _load_persistent(self):
        """Load every previously generated NP- postulate so knowledge accumulates"""
        if not os.path.exists(LEARNINGS):
            return
        try:
            with open(LEARNINGS) as f:
                data = json.load(f)
            for key, meta in data.get("generated_postulates", {}).items():
                if key in self.post:
                    continue
                # Reconstruct a safe compound postulate
                combines = meta.get("combines", [])
                if not combines:
                    continue
                self.post[key] = {
                    "rule": meta.get("rule", f"Compound {key}"),
                    "from": meta.get("from", []),
                    "combines": combines,
                    "cond": lambda p, c=set(combines): all(
                        (k in self.post and self.post[k]["cond"](p)) for k in c
                    ),
                    "effect": lambda p: p.update({"η_bonus": p.get("η_bonus",0)+8}),
                    "depth": meta.get("depth", 5),
                    "auto": True
                }
            print(f"  loaded {len(data.get('generated_postulates',{}))} persistent NP- postulates")
        except Exception as e:
            print(f"  (learnings load skipped: {e})")

    def _save_persistent(self):
        data = {"generated_postulates": {}, "sessions": []}
        if os.path.exists(LEARNINGS):
            try:
                with open(LEARNINGS) as f:
                    data = json.load(f)
            except: pass
        for k in self.new:
            if k in self.post:
                d = self.post[k]
                data["generated_postulates"][k] = {
                    "rule": d["rule"],
                    "from": d.get("from", []),
                    "combines": d.get("combines", []),
                    "depth": d.get("depth", 5),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
        data["sessions"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "new": self.new,
            "proof_len": len(self.proof)
        })
        with open(LEARNINGS, "w") as f:
            json.dump(data, f, indent=2)

    def apply(self, problem, depth_limit=99):
        p = deepcopy(problem)
        p.setdefault("η_penalty", 0)
        p.setdefault("η_bonus", 0)
        p.setdefault("acre_eligible", True)
        p.setdefault("recommendations", [])
        fired = []
        for k, d in list(self.post.items()):
            if d["depth"] > depth_limit: continue
            try:
                if d["cond"](p):
                    d["effect"](p)
                    self.proof.append({"post":k, "rule":d["rule"], "from":d.get("from",[]), "depth":d["depth"]})
                    fired.append(k)
            except: pass
        return p, fired

    def deepen(self, history):
        counts = defaultdict(int)
        for fired in history:
            if len(fired) >= 2:
                counts[tuple(sorted(fired))] += 1
        for combo, n in counts.items():
            if n < 2: continue
            if any(set(d.get("combines",[])) == set(combo) for d in self.post.values()): continue
            key = f"NP-{len([k for k in self.post if k.startswith('NP-')])+1:03d}"
            derives = list({a for k in combo for a in self.post.get(k,{}).get("from",[])})
            self.post[key] = {
                "rule": f"Compound: {'+'.join(combo)} co-fire",
                "from": derives, "combines": list(combo),
                "cond": lambda p, c=set(combo): all(k in self.post and self.post[k]["cond"](p) for k in c),
                "effect": lambda p: p.update({"η_bonus": p.get("η_bonus",0)+8}),
                "depth": max(self.post[k]["depth"] for k in combo)+1,
                "auto": True
            }
            self.new.append(key)
        return self.new

    def η(self, p):
        base = p.get("base_η", 55.0)
        return max(0.0, min(100.0, base + p.get("η_bonus",0) - p.get("η_penalty",0)))

    def merkle(self, nodes):
        if not nodes: return hashlib.sha256(b"empty").hexdigest()
        layer = [hashlib.sha256(json.dumps(n, sort_keys=True).encode()).hexdigest() for n in nodes]
        while len(layer) > 1:
            if len(layer) % 2: layer.append(layer[-1])
            layer = [hashlib.sha256((layer[i]+layer[i+1]).encode()).hexdigest() for i in range(0,len(layer),2)]
        return layer[0]

    def run(self, problem, max_loops=8):
        self.proof = []
        self.new = []
        hist = []
        cur = deepcopy(problem)
        results = []
        for i in range(max_loops):
            depth = (i+1)*2
            cur, fired = self.apply(cur, depth)
            score = self.η(cur)
            hist.append(fired)
            results.append({"loop":i+1, "depth":depth, "fired":len(fired), "η":round(score,2)})
            if i>0 and abs(results[-1]["η"]-results[-2]["η"])<0.3 and len(fired)==results[-2]["fired"]:
                break
        new = self.deepen(hist)
        if new:
            cur, _ = self.apply(cur, 99)
            results.append({"loop":len(results)+1, "depth":99, "fired":0, "η":round(self.η(cur),2), "new":new})
        final_η = self.η(cur)
        root = self.merkle(self.proof + results)
        claim = None
        if cur.get("acre_eligible") and final_η >= 40.0 and self.proof:
            claim = self.mint(problem, final_η, root)
        self._save_persistent()
        return {
            "η": final_η,
            "loops": len(results),
            "proof_len": len(self.proof),
            "new_postulates": self.new,
            "merkle_root": root,
            "acre_claim": claim,
            "recommendations": cur.get("recommendations", []),
            "history": results,
            "final_state": cur
        }

    def mint(self, problem, η, root):
        prev = "genesis"
        if os.path.exists(LEDGER):
            with open(LEDGER) as f:
                lines = [l.strip() for l in f if l.strip()]
                if lines: prev = json.loads(lines[-1]).get("hash","genesis")
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": "acre_claim",
            "task": problem.get("name","unnamed")[:80],
            "η": η,
            "proof_len": len(self.proof),
            "merkle": root,
            "prev": prev,
            "verified": False
        }
        entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        with open(LEDGER, "a") as f: f.write(json.dumps(entry)+"\n")
        return entry

    def load_from_claim(self, claim_hash):
        """Seed reasoning from a previous ACRE claim"""
        if not os.path.exists(LEDGER):
            return None
        with open(LEDGER) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get("hash","").startswith(claim_hash) or e.get("merkle","").startswith(claim_hash):
                        return {
                            "name": f"continue:{e.get('task','prior')}",
                            "base_η": e.get("η", 55),
                            "observation_days": 14,   # already observed
                            "feedback": True,
                            "human_input": 3,
                            "prior_merkle": e.get("merkle"),
                            "prior_hash": e.get("hash"),
                            "seeded": True
                        }
                except: continue
        return None

def parse_task(item):
    if isinstance(item, str): item = {"name": item}
    q = str(item.get("name", item.get("task",""))).lower()
    return {
        "name": item.get("name", item.get("task","task")),
        "base_η": item.get("base_η", 70 if "solar" in q or "thermal" in q else 55),
        "energy": item.get("energy", "solar" if any(x in q for x in ("solar","thermal","heat")) else "grid"),
        "observation_days": item.get("observation_days", 0),
        "feedback": item.get("feedback", False) or "auto" in q,
        "human_input": item.get("human_input", 6),
        "involves_compute": item.get("involves_compute", "compute" in q or "code" in q or "lattice" in q),
        "compute_joules": item.get("compute_joules", 0),
        "outputs": item.get("outputs", []),
        "recommendations": item.get("recommendations", []),
        "seeded": item.get("seeded", False)
    }

def load_h003_from_ledger():
    """AX-019: Dynamic yield from ledger, no hardcoded values."""
    import json, os
    ledger_path = os.path.expanduser("~/projects/openroot/acre/ledger.jsonl")
    if not os.path.exists(ledger_path):
        return None
    entries = []
    with open(ledger_path) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                if d.get("work_type") == "thermal_generation_h003":
                    entries.append(d)
            except:
                pass
    if not entries:
        return None
    # Latest entry by timestamp
    e = max(entries, key=lambda x: x.get("timestamp", ""))
    return {
        "name": "H-003 solar thermal capture Saxton (live)",
        "observation_days": 0,
        "human_input": e.get("energy_joules", 0) / 1e6,
        "energy": "thermal",
        "ledger_entry": e,
        "area_m2": e.get("area_m2", 0),
        "nightly_kwh": e.get("nightly_kwh", 0),
        "7n_kwh": e.get("7n_kwh", 0),
    }


def main():
    import sys
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python3 lattice_cli.py --demo")
        print("  python3 lattice_cli.py tasks.json")
        print("  python3 lattice_cli.py --from <claim_hash_or_merkle>")
        sys.exit(1)

    eng = Lattice()
    print(f"\n{'='*64}")
    print(f"  LATTICE  ·  {len(AXIOMS)} axioms  ·  {len(eng.post)} postulates (live)")
    print(f"{'='*64}")

    if args[0] == "--from":
        if len(args) < 2:
            print("Need claim hash or merkle prefix")
            sys.exit(1)
        seed = eng.load_from_claim(args[1])
        if not seed:
            print(f"No claim matching {args[1][:16]}...")
            sys.exit(1)
        print(f"  seeded from prior claim -> {seed.get('name','')}")
        tasks = [seed]

    elif args[0] == "--demo":
        h003 = load_h003_from_ledger()
        if h003:
            tasks = [h003]
            print(f"  loaded H-003 from ledger: {h003.get('area_m2', '?')} m2")
        else:
            tasks = [
                {"name": "Black Locust RMH with feedback sensors",
                 "observation_days": 12, "feedback": True, "energy": "biomass"},
                {"name": "AeroCement PoPW lattice compute",
                 "involves_compute": True, "compute_joules": 0}
            ]

    else:
        with open(args[0]) as f:
            raw = json.load(f)
        tasks = raw if isinstance(raw, list) else raw.get("tasks", [raw])

    for t in tasks:
        prob = parse_task(t)
        r = eng.run(prob)
        eta = float(r.get("eta", r.get("η", r.get("eta_score", 0.0))))
        loops = r.get("loops", r.get("loop_count", 0))
        proof = r.get("proof_len", r.get("proof", r.get("proof_steps", 0)))
        merkle = str(r.get("merkle_root", r.get("merkle", r.get("root", ""))))[:16]
        print(f"\n> {prob.get('name','')[:60]}")
        print(f"  η={eta:.1f}  loops={loops}  proof={proof}  merkle={merkle}…")
        np = r.get("new_postulates", [])
        if np:
            print(f"  NEW deep postulates: {np}")
        claim = r.get("acre_claim")
        if claim:
            h = claim.get("hash", "")[:20] if isinstance(claim, dict) else str(claim)[:20]
            print(f"  ACRE MINTED  hash={h}...")
        else:
            print("  (no ACRE - threshold not met)")
        if prob.get("seeded"):
            print(f"  continued from prior -> {str(prob.get('prior_hash',''))[:16]}...")
    print()

if __name__ == "__main__":
    main()
