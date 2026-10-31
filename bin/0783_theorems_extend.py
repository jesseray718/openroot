#!/usr/bin/env python3
"""theorems_extend.py - theorem kernel with flag-memoized proofs. Part 1/3 appended via sh."""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")
CHAIN = STORE / "chain.jsonl"
CACHE = STORE / "proof_cache.json"

def dumps(o): return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def content_hash(o): return hashlib.sha256(dumps(o).encode("utf-8")).hexdigest()
def flag_of(tag, digest): return f"FLAG-{tag}-{digest[:16]}"

def load_kind(kind):
    p = STORE / f"{kind}.jsonl"
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r.get("id")] = r
    return out

def load_all():
    idx = {}
    for k in ("axioms", "definitions", "postulates", "theorems"):
        idx[k] = load_kind(k)
    return idx

def load_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {"version": "1.0", "memo": {}}

def save_cache(c):
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(CACHE)

KERNEL_RULES = ("assume", "unfold_def", "modus_ponens", "eval_c", "eq_refl", "need_gate")

def resolve(fid, idx, seen=None, trace=None):
    """Trace a premise id to axiom ground. Returns proof suffix or None."""
    seen = seen or set()
    trace = trace or []
    if fid in seen:
        return None
    seen.add(fid)
    for layer, tag in (("axioms", "AX"), ("definitions", "DF"), ("theorems", "TH"), ("postulates", "PO")):
        if fid in idx[layer]:
            rec = idx[layer][fid]
            pres = list(rec.get("premises") or [])
            sub = []
            for p in pres:
                deeper = resolve(p, idx, seen, trace)
                if deeper is None:
                    return None
                sub.extend(deeper)
            rule = "assume" if layer == "axioms" else ("unfold_def" if layer == "definitions" else "modus_ponens")
            sub.append({"rule": rule, "from": [str(p) for p in pres], "conclude": fid})
            return sub
    return None

def prove(goal_id, idx, cache):
    gh = content_hash({"goal": goal_id})
    memo = cache["memo"].get(goal_id)
    if memo:
        return {"status": "CACHED", "flag": memo["flag"], "hash": memo["hash"], "replays_skipped": True}
    chain = resolve(goal_id, idx)
    if chain is None:
        return {"status": "REJECTED", "reason": "premise chain does not terminate at axioms/known theorems"}
    digest = content_hash({"kind": "theorem", "id": goal_id, "statement": idx.get("_goal_statement", ""), "premises": [goal_id], "proof": chain})
    rec = {"kind": "theorem", "id": goal_id, "flag": flag_of("TH", digest), "hash": digest,
           "statement": idx.get("_goal_statement", ""), "premises": [goal_id], "proof": chain, "ts": time.time()}
    with (STORE / "theorems.jsonl").open("a", encoding="utf-8") as f:
        f.write(dumps(rec) + "\n")
    with CHAIN.open("a", encoding="utf-8") as f:
        f.write(dumps({"flag": rec["flag"], "hash": digest, "id": rec["id"], "kind": "theorem", "ts": rec["ts"]}) + "\n")
    cache["memo"][goal_id] = {"flag": rec["flag"], "hash": digest}
    save_cache(cache)
    return {"status": "PROVED", "flag": rec["flag"], "steps": len(chain), "proof": chain}

def checkflag(token, idx):
    for layer in idx.values():
        for rec in layer.values():
            if token in (rec.get("flag"), rec.get("hash"), rec.get("id")):
                return rec
    return None

if __name__ == "__main__":
    cmd, arg = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else (sys.argv[1] if sys.argv else "", None)
    idx = load_all()
    if cmd == "prove":
        idx["_goal_statement"] = arg
        print(json.dumps(prove(arg, idx, load_cache()), indent=2))
    elif cmd == "checkflag":
        hit = checkflag(arg, idx)
        print(json.dumps(hit, indent=2) if hit else json.dumps({"status": "NOT_FOUND", "flag": arg}))
    elif cmd == "audit":
        print(f"axioms={len(idx['axioms'])} definitions={len(idx['definitions'])} postulates={len(idx['postulates'])} theorems={len(idx['theorems'])}")
    else:
        print("usage: theorems_extend.py prove|checkflag <arg> | prove <GOAL-ID>")

def export_for_sync():
    """Return bundle for mesh transfer."""
    return {"cache": load_cache(), "chain_tail": None}
