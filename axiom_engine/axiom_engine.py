#!/usr/bin/env python3
"""OpenRoot axiom kernel — hash flags, no second compute.

7B proposes. Kernel verifies. Flag is the only thing you keep.
Axioms never rewrite themselves (N16). New axioms require human hang.

Live roots (two-pane):
  SSH  /home/jesse/openroot/axiom_engine
  A15  /data/data/com.termux/files/home/openroot/axiom_engine
  mesh /storage/emulated/0/openroot/axiom_engine
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = (
    Path(os.environ["OPENROOT_AXIOM_ROOT"]).resolve()
    if os.environ.get("OPENROOT_AXIOM_ROOT")
    else Path(__file__).resolve().parent
)
STORE = ROOT / "store"
SEEDS = ROOT / "seeds"
PROMPTS = ROOT / "prompts"
KINDS = ("axiom", "definition", "postulate", "theorem", "flag")
HARD_RULES = ("assume", "eval_c", "eval_s", "eq_refl", "need_gate")
SOFT_RULES = (
    "modus_ponens",
    "modus_tollens",
    "hypothetical_syllogism",
    "disjunctive_syllogism",
    "and_intro",
    "and_elim",
    "or_intro",
    "contrapositive",
    "eq_sym",
    "eq_trans",
    "eq_subst",
)
RULES = HARD_RULES + SOFT_RULES
N03_C = "C(N,T,R) = N * 0.001 * (1 + 0.1*T) * (1 - R)**T"
N05_S = "S = 1.0 + (R * 0.5 * log_B(N))"


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(obj: Any) -> str:
    return sha256_hex(dumps(obj).encode("utf-8"))


def flag_name(kind: str, digest: str) -> str:
    tag = {"axiom": "AX", "definition": "DF", "postulate": "PO", "theorem": "TH", "flag": "FL"}[kind]
    return f"FLAG-{tag}-{digest[:16]}"


def now() -> float:
    return time.time()


def _ensure() -> None:
    for d in (STORE, SEEDS, PROMPTS):
        d.mkdir(parents=True, exist_ok=True)


def jsonl_path(kind: str) -> Path:
    return STORE / f"{kind}s.jsonl"


def flags_index_path() -> Path:
    return STORE / "checkflags.json"


def chain_path() -> Path:
    return STORE / "chain.jsonl"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def load_jsonl(kind: str) -> list[dict]:
    p = jsonl_path(kind)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def rewrite_jsonl(kind: str, rows: list[dict]) -> None:
    text = "".join(dumps(r) + "\n" for r in rows)
    atomic_write(jsonl_path(kind), text)


def load_flags() -> dict:
    p = flags_index_path()
    if not p.exists():
        return {"version": "2.0", "algo": "sha256", "flags": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_flags(idx: dict) -> None:
    atomic_write(flags_index_path(), json.dumps(idx, indent=2, ensure_ascii=False) + "\n")


def hang_chain(rec: dict) -> None:
    line = dumps({"ts": now(), "hash": rec.get("hash"), "flag": rec.get("flag"), "kind": rec.get("kind"), "id": rec.get("id")}) + "\n"
    p = chain_path()
    if p.exists():
        p.write_text(p.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        atomic_write(p, line)


def index_by_hash() -> dict[str, dict]:
    m: dict[str, dict] = {}
    for kind in ("axiom", "definition", "postulate", "theorem"):
        for rec in load_jsonl(kind):
            m[rec["hash"]] = rec
            m[rec["flag"]] = rec
            if rec.get("id"):
                m[rec["id"]] = rec
            if rec.get("name"):
                m[str(rec["name"])] = rec
            for k in rec.get("keys") or []:
                m[str(k)] = rec
    for fl in load_flags().get("flags", []):
        m[fl["flag"]] = fl
        m[fl["hash"]] = fl
        if fl.get("name"):
            m[fl["name"]] = fl
        if fl.get("id"):
            m[fl["id"]] = fl
    return m


def body_for_hash(kind: str, rec: dict) -> dict:
    return {
        "kind": kind,
        "id": rec.get("id"),
        "statement": (rec.get("statement") or "").strip(),
        "premises": list(rec.get("premises") or []),
        "proof": rec.get("proof") or [],
    }


def make_record(kind: str, rec: dict) -> dict:
    body = body_for_hash(kind, rec)
    digest = content_hash(body)
    return {
        "kind": kind,
        "id": rec.get("id") or flag_name(kind, digest),
        "name": rec.get("name") or rec.get("id") or flag_name(kind, digest),
        "statement": body["statement"],
        "keys": list(rec.get("keys") or []),
        "premises": body["premises"],
        "proof": body["proof"],
        "category": rec.get("category") or "",
        "source": rec.get("source") or "",
        "irreducible": bool(rec.get("irreducible", kind == "axiom")),
        "grade": rec.get("grade") or ("LOCK" if kind == "axiom" else "OPEN"),
        "hash": digest,
        "flag": flag_name(kind, digest),
        "ts": rec.get("ts") or now(),
    }


def upsert(kind: str, rec: dict) -> dict:
    if kind not in KINDS:
        raise ValueError(kind)
    if kind == "axiom" and load_jsonl("axiom"):
        built = make_record(kind, rec)
        existing = index_by_hash()
        if built["hash"] in existing or built.get("id") in existing:
            hit = existing.get(built["hash"]) or existing.get(built["id"])
            return {"hit": True, "recomputed": False, "flag": hit.get("flag"), "hash": hit.get("hash"), "record": hit}
        return {
            "hit": False,
            "recomputed": False,
            "valid": False,
            "reason": "N16_axioms_do_not_rewrite. Human hang required. Use hang-axiom --confirm.",
            "flag": None,
        }
    built = make_record(kind, rec)
    existing = index_by_hash()
    if built["hash"] in existing or built["flag"] in existing:
        hit = existing.get(built["hash"]) or existing.get(built["flag"])
        return {"hit": True, "recomputed": False, "flag": hit.get("flag", built["flag"]), "hash": hit.get("hash", built["hash"]), "record": hit}
    rows = load_jsonl(kind)
    rows.append(built)
    rewrite_jsonl(kind, rows)
    idx = load_flags()
    idx["flags"].append(
        {
            "flag": built["flag"],
            "kind": kind,
            "hash": built["hash"],
            "name": built["name"],
            "id": built["id"],
            "statement": built["statement"],
            "premises": built["premises"],
            "proof_hash": content_hash(built["proof"]),
            "ts": built["ts"],
        }
    )
    save_flags(idx)
    hang_chain(built)
    return {"hit": False, "recomputed": True, "flag": built["flag"], "hash": built["hash"], "record": built}


def hang_axiom(rec: dict, confirm: bool = False) -> dict:
    if not confirm:
        return {"valid": False, "reason": "human hang required: hang-axiom --confirm"}
    built = make_record("axiom", rec)
    existing = index_by_hash()
    if built["hash"] in existing or built.get("id") in existing:
        hit = existing.get(built["hash"]) or existing.get(built["id"])
        return {"hit": True, "recomputed": False, "flag": hit.get("flag"), "hash": hit.get("hash"), "record": hit}
    rows = load_jsonl("axiom")
    rows.append(built)
    rewrite_jsonl("axiom", rows)
    idx = load_flags()
    idx["flags"].append(
        {
            "flag": built["flag"],
            "kind": "axiom",
            "hash": built["hash"],
            "name": built["name"],
            "id": built["id"],
            "statement": built["statement"],
            "premises": built["premises"],
            "proof_hash": content_hash(built["proof"]),
            "ts": built["ts"],
        }
    )
    save_flags(idx)
    hang_chain(built)
    return {"hit": False, "recomputed": True, "flag": built["flag"], "hash": built["hash"], "record": built}


def lookup(token: str) -> dict:
    token = (token or "").strip()
    if not token:
        return {"hit": False}
    idx = index_by_hash()
    if token in idx:
        rec = idx[token]
        return {"hit": True, "recomputed": False, "flag": rec.get("flag"), "hash": rec.get("hash"), "record": rec}
    low = token.lower()
    for rec in (*load_jsonl("axiom"), *load_jsonl("definition"), *load_jsonl("postulate"), *load_jsonl("theorem")):
        keys = [k.lower() for k in rec.get("keys") or []]
        if low == str(rec.get("id", "")).lower() or low == str(rec.get("name", "")).lower() or low in keys:
            return {"hit": True, "recomputed": False, "flag": rec["flag"], "hash": rec["hash"], "record": rec}
        if rec["statement"].lower() == low:
            return {"hit": True, "recomputed": False, "flag": rec["flag"], "hash": rec["hash"], "record": rec}
        if rec.get("flag", "").lower() == low or rec.get("hash", "").lower() == low:
            return {"hit": True, "recomputed": False, "flag": rec["flag"], "hash": rec["hash"], "record": rec}
    return {"hit": False, "token": token}


def eval_c(N: float, T: float, R: float) -> float:
    if R >= 1.0 and T >= 1.0:
        return 0.0
    return float(N) * 0.001 * (1.0 + 0.1 * float(T)) * ((1.0 - float(R)) ** float(T))


def eval_s(N: float, R: float, B: float = 6.0) -> float:
    if N <= 0 or B <= 1:
        raise ValueError("N>0 and B>1 required")
    return 1.0 + (float(R) * 0.5 * math.log(float(N), float(B)))


def _facts(premises: list[str], store: dict[str, dict]) -> set[str]:
    facts = set()
    for p in premises:
        rec = store.get(p)
        if rec:
            facts.add(rec.get("id") or p)
            facts.add(rec.get("flag") or "")
            facts.add(rec.get("statement") or "")
            facts.add(p)
        else:
            facts.add(p)
    return {f for f in facts if f}


def verify_proof(premises: list[str], proof: list[dict], conclude: str) -> dict:
    store = index_by_hash()
    known = _facts(premises, store)
    derived: list[str] = []
    used_soft = False
    for i, step in enumerate(proof):
        rule = step.get("rule")
        if rule not in RULES:
            return {"valid": False, "at": i, "reason": f"unknown_rule:{rule}"}
        if rule in SOFT_RULES:
            used_soft = True
        frm = list(step.get("from") or [])
        out = (step.get("conclude") or "").strip()
        if not out:
            return {"valid": False, "at": i, "reason": "empty_conclude"}
        if rule == "assume":
            if out not in known and out not in premises and out not in store:
                return {"valid": False, "at": i, "reason": f"assume_not_in_premises:{out}"}
            derived.append(out)
            known.add(out)
            continue
        if rule == "eval_c":
            try:
                N = float(step["N"])
                T = float(step["T"])
                R = float(step["R"])
            except Exception as e:
                return {"valid": False, "at": i, "reason": f"eval_c_bad_args:{e}"}
            val = eval_c(N, T, R)
            expect = step.get("expect")
            if expect is not None and abs(val - float(expect)) > 1e-12:
                return {"valid": False, "at": i, "reason": f"eval_c_mismatch:{val}!={expect}"}
            derived.append(out)
            known.add(out)
            continue
        if rule == "eval_s":
            try:
                N = float(step["N"])
                R = float(step["R"])
                B = float(step.get("B", 6.0))
            except Exception as e:
                return {"valid": False, "at": i, "reason": f"eval_s_bad_args:{e}"}
            val = eval_s(N, R, B)
            expect = step.get("expect")
            if expect is not None and abs(val - float(expect)) > 1e-9:
                return {"valid": False, "at": i, "reason": f"eval_s_mismatch:{val}!={expect}"}
            derived.append(out)
            known.add(out)
            continue
        if rule == "eq_refl":
            if "=" not in out:
                return {"valid": False, "at": i, "reason": "eq_refl_needs_equality"}
            left, right = [x.strip() for x in out.split("=", 1)]
            if left != right:
                return {"valid": False, "at": i, "reason": f"eq_refl_mismatch:{left}!={right}"}
            derived.append(out)
            known.add(out)
            continue
        if rule == "need_gate":
            blob = " ".join(known).lower()
            if "n11" not in blob and "need_gate" not in blob:
                return {"valid": False, "at": i, "reason": "need_gate_without_N11"}
            derived.append(out)
            known.add(out)
            continue
        missing = [x for x in frm if x not in known and x not in store]
        if missing and rule not in ("or_intro",):
            return {"valid": False, "at": i, "reason": f"missing_premises:{missing}"}
        derived.append(out)
        known.add(out)
    if conclude not in known and conclude not in derived:
        return {"valid": False, "at": len(proof), "reason": "conclusion_not_derived", "derived": derived}
    return {"valid": True, "derived": derived, "conclude": conclude, "soft": used_soft}


def prove_and_flag(spec: dict) -> dict:
    token_body = body_for_hash("theorem", spec)
    digest = content_hash(token_body)
    flag = flag_name("theorem", digest)
    hit = lookup(flag)
    if hit.get("hit"):
        return {"hit": True, "recomputed": False, "flag": flag, "hash": digest, "valid": True}
    check = verify_proof(
        list(spec.get("premises") or []),
        list(spec.get("proof") or []),
        spec.get("conclude") or spec.get("statement") or "",
    )
    if not check["valid"]:
        return {"hit": False, "recomputed": True, "valid": False, "reason": check, "flag": None}
    if check.get("soft"):
        rec = dict(spec)
        rec["kind"] = "postulate"
        rec["grade"] = "SOFT"
        rec["id"] = spec.get("id") or flag_name("postulate", digest)
        out = upsert("postulate", rec)
        out["valid"] = True
        out["grade"] = "SOFT"
        out["note"] = "soft rules used. hung as postulate not theorem. human hang to promote."
        return out
    rec = dict(spec)
    rec["kind"] = "theorem"
    rec["grade"] = "HARD"
    return upsert("theorem", rec) | {"valid": True, "grade": "HARD"}


def retrieve(query: str, limit: int = 8) -> list[dict]:
    q = query.lower().split()
    scored = []
    for kind in ("axiom", "definition", "postulate", "theorem"):
        for rec in load_jsonl(kind):
            blob = " ".join([rec.get("id", ""), rec.get("name", ""), rec.get("statement", ""), " ".join(rec.get("keys") or [])]).lower()
            score = sum(1 for w in q if w and w in blob)
            if score:
                scored.append((score, rec))
    scored.sort(key=lambda x: -x[0])
    return [r for _, r in scored[:limit]]


SEED = [
    {"kind": "axiom", "id": "N00", "name": "source", "category": "canon", "irreducible": True,
     "statement": "N00 source. Claims begin at a named source, not at a generated paragraph.",
     "keys": ["n00", "source"]},
    {"kind": "axiom", "id": "N01", "name": "eta", "category": "canon", "irreducible": True,
     "statement": "eta = useful_joules / human_joules. This is the only performance language allowed.",
     "keys": ["n01", "eta", "useful joules"]},
    {"kind": "axiom", "id": "N02", "name": "gamma", "category": "canon", "irreducible": True,
     "statement": "N02 gamma. Waste and coordination leakage are first-class, not footnotes.",
     "keys": ["n02", "gamma"]},
    {"kind": "axiom", "id": "N03", "name": "C", "category": "canon", "irreducible": True,
     "statement": N03_C,
     "keys": ["n03", "coordination cost", "c(n,t,r)"]},
    {"kind": "axiom", "id": "N04", "name": "R", "category": "canon", "irreducible": True,
     "statement": "N04 R. Resonance R is in [0,1]. R=1.0 is perfect cooperation.",
     "keys": ["n04", "resonance", "r=1.0"]},
    {"kind": "axiom", "id": "N05", "name": "S", "category": "canon", "irreducible": True,
     "statement": N05_S,
     "keys": ["n05", "synergy"]},
    {"kind": "axiom", "id": "N06", "name": "landauer_floor", "category": "physics", "irreducible": True,
     "statement": "Landauer floor at 300 K is approximately 2.85e-21 J per bit erasure. Computation is physical.",
     "keys": ["n06", "landauer", "bit erasure"]},
    {"kind": "axiom", "id": "N07", "name": "least_first", "category": "canon", "irreducible": True,
     "statement": "N07 L least-first. Serve the lowest-capability node first.",
     "keys": ["n07", "least first"]},
    {"kind": "axiom", "id": "N08", "name": "hang", "category": "canon", "irreducible": True,
     "statement": "N08 hang. A claim hangs on an immutable blob, not on a live rotating file.",
     "keys": ["n08", "hang"]},
    {"kind": "axiom", "id": "N09", "name": "PoPW", "category": "canon", "irreducible": True,
     "statement": "N09 Proof of Physical Work. Monetizable claims rest on measured joules or mass-or-photo hang.",
     "keys": ["n09", "popw"]},
    {"kind": "axiom", "id": "N10", "name": "cas", "category": "canon", "irreducible": True,
     "statement": "N10 chain.jsonl + content-addressed store. Not a public-chain host as existence.",
     "keys": ["n10", "chain.jsonl", "cas"]},
    {"kind": "axiom", "id": "N11", "name": "need_gate", "category": "canon", "irreducible": True,
     "statement": "N11 need_gate. Do not add a module while the live canon path is empty.",
     "keys": ["n11", "need gate"]},
    {"kind": "axiom", "id": "N12", "name": "edges", "category": "canon", "irreducible": True,
     "statement": "N12 edges. Use edges and value the marginal.",
     "keys": ["n12", "edges"]},
    {"kind": "axiom", "id": "N13", "name": "cure_21d", "category": "canon", "irreducible": True,
     "statement": "N13 21-day cure. Field claims wait for a real soak, not a demo reject revival.",
     "keys": ["n13", "21-day"]},
    {"kind": "axiom", "id": "N14", "name": "efficiency_cap", "category": "canon", "irreducible": True,
     "statement": "N14 efficiency cap. Do not mix heat-engine eta, act eta, EROI, and sim score in one sentence.",
     "keys": ["n14", "efficiency cap"]},
    {"kind": "axiom", "id": "N15", "name": "licenses", "category": "canon", "irreducible": True,
     "statement": "N15 licenses. CC-BY-SA-4.0 docs / GPL-3.0 code unless a file says otherwise.",
     "keys": ["n15", "license"]},
    {"kind": "axiom", "id": "N16", "name": "regulate", "category": "canon", "irreducible": True,
     "statement": "N16 regulate. Feedback is heat. Locks do not rewrite themselves.",
     "keys": ["n16", "regulate"]},
    {"kind": "axiom", "id": "B1", "name": "computation_physical", "category": "physics", "irreducible": True,
     "statement": "Computation is physical. Every bit has energy cost at or above the Landauer limit.",
     "keys": ["b1", "physical computation"]},
    {"kind": "axiom", "id": "B2", "name": "zero_coord", "category": "agape", "irreducible": True,
     "statement": "When R = 1.0 and T >= 1, C(N,T,R) = 0 for all N.",
     "keys": ["b2", "zero coordination", "agape coordination"]},
    {"kind": "axiom", "id": "B3", "name": "useful_work", "category": "une", "irreducible": True,
     "statement": "Useful work is measured in joules that produce lasting physical or informational structure.",
     "keys": ["b3", "useful work"]},
    {"kind": "axiom", "id": "B4", "name": "monetize_after_chain", "category": "une", "irreducible": True,
     "statement": "A claim is only monetizable after an unbroken chain of verified postulates ending in measured joules or R=1.0 with proof.",
     "keys": ["b4", "flag-0", "monetizable"]},
    {"kind": "axiom", "id": "LNC", "name": "noncontradiction", "category": "logic", "irreducible": True,
     "statement": "Nothing can both be and not be at the same time in the same respect. not (P and not P).",
     "keys": ["noncontradiction", "lnc"]},
    {"kind": "axiom", "id": "LEM", "name": "excluded_middle", "category": "logic", "irreducible": True,
     "statement": "For any proposition P, P or not P.",
     "keys": ["excluded middle", "lem"]},
    {"kind": "axiom", "id": "ID", "name": "identity", "category": "logic", "irreducible": True,
     "statement": "Everything is identical to itself. A = A.",
     "keys": ["identity", "a is a"]},
    {"kind": "axiom", "id": "AX-ALIGN", "name": "total_alignment", "category": "agape", "irreducible": True,
     "statement": "Total alignment of a node with the root is R approaching 1.0. Partial alignment leaves residual coordination cost.",
     "keys": ["alignment", "axiom 1"]},
    {"kind": "axiom", "id": "AX-COOP", "name": "node_cooperation", "category": "agape", "irreducible": True,
     "statement": "Cooperation between nodes is the same relation as alignment with the root, applied laterally.",
     "keys": ["cooperation", "axiom 2"]},
    {"kind": "definition", "id": "DEF-FLAG", "name": "checkflag", "category": "cas",
     "statement": "A checkflag is FLAG-<AX|DF|PO|TH|FL>-<sha256[:16]> over the canonical body {kind,id,statement,premises,proof}. Lookup by flag or full hash skips replay.",
     "keys": ["checkflag", "flag name", "hash"]},
    {"kind": "definition", "id": "DEF-PROOF", "name": "proof_object", "category": "cas",
     "statement": "A proof is a list of {rule, from, conclude} using only kernel RULES. The 7B may propose steps. The kernel accepts or rejects. Rejected steps never hang.",
     "keys": ["proof object", "rule"]},
    {"kind": "definition", "id": "DEF-HARD", "name": "hard_theorem", "category": "cas",
     "statement": "A HARD theorem uses only assume, eval_c, eval_s, eq_refl, need_gate. Soft-rule proofs hang as postulates.",
     "keys": ["hard", "soft"]},
    {"kind": "definition", "id": "DEF-R", "name": "resonance", "category": "agape",
     "statement": "R in [0,1] is the cooperation coefficient. R=1.0 zeros (1-R)^T for T>=1.",
     "keys": ["resonance definition"]},
    {"kind": "definition", "id": "DEF-ETA", "name": "eta_ratio", "category": "une",
     "statement": "eta is useful_joules divided by human_joules. Not heat-engine efficiency, not EROI, not a sim score.",
     "keys": ["eta definition"]},
    {"kind": "definition", "id": "DEF-SWARM", "name": "base6_swarm", "category": "agape",
     "statement": "Atomic functions are translate, orchestrate, retrieve, process, synthesize, verify. Recursion replaces each with a 6-unit sub-swarm. Units at tier T equal 6^T.",
     "keys": ["swarm", "base-6", "6^T"]},
    {"kind": "definition", "id": "P01", "name": "observe_interact", "category": "permaculture",
     "statement": "Observe and interact before acting.", "keys": ["p01"]},
    {"kind": "definition", "id": "P02", "name": "catch_store", "category": "permaculture",
     "statement": "Catch and store energy.", "keys": ["p02"]},
    {"kind": "definition", "id": "P03", "name": "obtain_yield", "category": "permaculture",
     "statement": "Obtain a yield.", "keys": ["p03"]},
    {"kind": "definition", "id": "P04", "name": "self_regulate", "category": "permaculture",
     "statement": "Apply self-regulation and accept feedback.", "keys": ["p04"]},
    {"kind": "definition", "id": "P05", "name": "renewable", "category": "permaculture",
     "statement": "Use and value renewable resources and services.", "keys": ["p05"]},
    {"kind": "definition", "id": "P06", "name": "no_waste", "category": "permaculture",
     "statement": "Produce no waste.", "keys": ["p06"]},
    {"kind": "definition", "id": "P07", "name": "patterns", "category": "permaculture",
     "statement": "Design from patterns to details.", "keys": ["p07"]},
    {"kind": "definition", "id": "P08", "name": "integrate", "category": "permaculture",
     "statement": "Integrate rather than segregate.", "keys": ["p08"]},
    {"kind": "definition", "id": "P09", "name": "small_slow", "category": "permaculture",
     "statement": "Use small and slow solutions.", "keys": ["p09"]},
    {"kind": "definition", "id": "P10", "name": "diversity", "category": "permaculture",
     "statement": "Use and value diversity.", "keys": ["p10"]},
    {"kind": "definition", "id": "P11", "name": "respond_change", "category": "permaculture",
     "statement": "Use edges and value the marginal. Creatively respond to change.", "keys": ["p11", "twelfth axiom edge"]},
    {"kind": "postulate", "id": "PO-MP", "name": "modus_ponens", "category": "logic",
     "statement": "From P implies Q and P, infer Q.",
     "keys": ["modus ponens"], "premises": ["ID"]},
]


HARD_THEOREMS = [
    {
        "id": "TH-C0",
        "name": "C_zero_at_R1",
        "statement": "C(N=6,T=1,R=1.0) = 0.0",
        "keys": ["c=0", "eval coord", "zero coordination theorem"],
        "premises": ["N03", "N04", "B2"],
        "conclude": "C(N=6,T=1,R=1.0) = 0.0",
        "proof": [
            {"rule": "assume", "from": [], "conclude": "N03"},
            {"rule": "assume", "from": [], "conclude": "B2"},
            {"rule": "eval_c", "N": 6, "T": 1, "R": 1.0, "expect": 0.0, "conclude": "C(N=6,T=1,R=1.0) = 0.0"},
        ],
    },
    {
        "id": "TH-C0-SCALE",
        "name": "C_zero_any_N",
        "statement": "C(N=1296,T=4,R=1.0) = 0.0",
        "keys": ["c=0 scale", "6^4"],
        "premises": ["N03", "B2"],
        "conclude": "C(N=1296,T=4,R=1.0) = 0.0",
        "proof": [
            {"rule": "assume", "from": [], "conclude": "B2"},
            {"rule": "eval_c", "N": 1296, "T": 4, "R": 1.0, "expect": 0.0, "conclude": "C(N=1296,T=4,R=1.0) = 0.0"},
        ],
    },
    {
        "id": "TH-ID",
        "name": "identity_inst",
        "statement": "N03 = N03",
        "keys": ["identity instance"],
        "premises": ["ID", "N03"],
        "conclude": "N03 = N03",
        "proof": [
            {"rule": "assume", "from": [], "conclude": "ID"},
            {"rule": "eq_refl", "from": ["ID"], "conclude": "N03 = N03"},
        ],
    },
]


def seed_all(force: bool = False) -> dict:
    _ensure()
    if load_jsonl("axiom") and not force:
        return {"seeded": False, "axioms": len(load_jsonl("axiom")), "flags": len(load_flags().get("flags", []))}
    if force:
        for kind in ("axiom", "definition", "postulate", "theorem"):
            rewrite_jsonl(kind, [])
        atomic_write(flags_index_path(), dumps({"version": "2.0", "algo": "sha256", "flags": []}) + "\n")
        atomic_write(chain_path(), "")
    n = 0
    for rec in SEED:
        if rec["kind"] == "axiom":
            hang_axiom(rec, confirm=True)
        else:
            upsert(rec["kind"], rec)
        n += 1
    proofs = []
    for spec in HARD_THEOREMS:
        proofs.append(prove_and_flag(spec))
    return {"seeded": True, "wrote": n, "flags": len(load_flags().get("flags", [])), "proofs": [{"id": p.get("record", {}).get("id"), "flag": p.get("flag"), "hit": p.get("hit")} for p in proofs]}


def stats() -> dict:
    idx = load_flags()
    return {
        "root": str(ROOT),
        "axioms": len(load_jsonl("axiom")),
        "definitions": len(load_jsonl("definition")),
        "postulates": len(load_jsonl("postulate")),
        "theorems": len(load_jsonl("theorem")),
        "flags": len(idx.get("flags", [])),
        "chain": str(chain_path()),
    }


def ask(query: str) -> dict:
    hit = lookup(query)
    if hit.get("hit"):
        rec = hit["record"]
        return {
            "hit": True,
            "recomputed": False,
            "flag": rec.get("flag"),
            "hash": rec.get("hash"),
            "kind": rec.get("kind"),
            "id": rec.get("id"),
            "statement": rec.get("statement"),
        }
    found = retrieve(query)
    if not found:
        return {
            "hit": False,
            "recomputed": False,
            "flag": None,
            "reason": "no_match",
            "advice": "Do not mint an axiom. File a postulate. Kernel must verify before hang.",
        }
    top = found[0]
    return {
        "hit": True,
        "recomputed": False,
        "flag": top["flag"],
        "hash": top["hash"],
        "kind": top["kind"],
        "id": top["id"],
        "statement": top["statement"],
        "also": [{"flag": r["flag"], "id": r["id"]} for r in found[1:6]],
    }


def dump_universal() -> dict:
    return {
        "axioms": load_jsonl("axiom"),
        "definitions": load_jsonl("definition"),
        "postulates": load_jsonl("postulate"),
        "theorems": load_jsonl("theorem"),
        "flags": load_flags().get("flags", []),
    }


USAGE = """axiom_engine.py seed|seed-force|stats|ask <q>|lookup <token>|retrieve <q>|prove <json>|eval_c N T R|eval_s N R [B]|dump|hang-postulate|hang-axiom --confirm
"""


def main(argv: list[str]) -> int:
    _ensure()
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.stdout.write(USAGE)
        return 0
    cmd = argv[1]
    if cmd == "seed":
        print(dumps(seed_all(False)))
        return 0
    if cmd == "seed-force":
        print(dumps(seed_all(True)))
        return 0
    if cmd == "stats":
        print(dumps(stats()))
        return 0
    if cmd == "ask":
        print(dumps(ask(" ".join(argv[2:]) or "")))
        return 0
    if cmd == "lookup":
        print(dumps(lookup(" ".join(argv[2:]) or "")))
        return 0
    if cmd == "retrieve":
        print(dumps(retrieve(" ".join(argv[2:]) or "")))
        return 0
    if cmd == "dump":
        print(dumps(dump_universal()))
        return 0
    if cmd == "eval_c":
        N, T, R = map(float, argv[2:5])
        print(dumps({"C": eval_c(N, T, R), "N": N, "T": T, "R": R}))
        return 0
    if cmd == "eval_s":
        N, R = float(argv[2]), float(argv[3])
        B = float(argv[4]) if len(argv) > 4 else 6.0
        print(dumps({"S": eval_s(N, R, B), "N": N, "R": R, "B": B}))
        return 0
    if cmd == "prove":
        spec = json.loads(argv[2] if len(argv) > 2 else sys.stdin.read())
        print(dumps(prove_and_flag(spec)))
        return 0
    if cmd == "hang-postulate":
        spec = json.loads(argv[2] if len(argv) > 2 else sys.stdin.read())
        spec["kind"] = "postulate"
        spec["irreducible"] = False
        print(dumps(upsert("postulate", spec)))
        return 0
    if cmd == "hang-axiom":
        rest = argv[2:]
        confirm = "--confirm" in rest
        raw = [x for x in rest if x != "--confirm"]
        spec = json.loads(raw[0] if raw else sys.stdin.read())
        print(dumps(hang_axiom(spec, confirm=confirm)))
        return 0
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
