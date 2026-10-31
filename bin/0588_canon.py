#!/usr/bin/env python3
"""
OpenRoot Canon — locked names and algorithms.
Newton chain: match a postulate, skip the essay.
Need-gate: a new word is expensive.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

K_BOLTZMANN = 1.380649e-23
ROOT = Path(__file__).resolve().parents[1]
CANON_PATH = ROOT / "canon" / "CANON.json"
NOM_PATH = ROOT / "canon" / "NOMENCLATURE.json"
ALG_PATH = ROOT / "canon" / "ALGORITHMS.json"
CANDIDATE_PATH = ROOT / "canon" / "CANDIDATES.json"
REG_PATH = ROOT / "canon" / "REGULATION.json"
FEEDBACK_PATH = ROOT / "canon" / "FEEDBACK.jsonl"
STATE_PATH = ROOT / "canon" / "STATE.json"
KINDS = ("confirm", "correct", "reject", "overclaim", "missing", "confuse")


def load() -> tuple[dict, dict, dict]:
    canon = json.loads(CANON_PATH.read_text(encoding="utf-8"))
    nom = json.loads(NOM_PATH.read_text(encoding="utf-8"))
    alg = json.loads(ALG_PATH.read_text(encoding="utf-8"))
    return canon, nom, alg


def candidates() -> dict:
    if not CANDIDATE_PATH.exists():
        return {"version": "1.0.0", "items": {}}
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def save_candidates(obj: dict) -> None:
    tmp = CANDIDATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(CANDIDATE_PATH)


def coord(N: float, T: float, R: float) -> float:
    if R >= 1.0 and T >= 1:
        return 0.0
    return N * 0.001 * (1 + 0.1 * T) * ((1 - R) ** T)


def synergy(N: float, R: float, B: float = 6.0) -> float:
    if N <= 0 or B <= 1:
        raise ValueError("N>0 and B>1")
    return 1.0 + (R * 0.5 * (math.log(N) / math.log(B)))


def eta(useful_joules: float, human_joules: float) -> float | None:
    if human_joules <= 0:
        return None
    return useful_joules / human_joules


def gamma(Y: float, L: float, P: float, F: float, Jh: float, Je: float, C: float) -> float | None:
    den = Jh + Je + C
    if den <= 0:
        return None
    return (Y * L * P * F) / den


def landauer(bits: float, T_kelvin: float = 300.0) -> float:
    return bits * T_kelvin * K_BOLTZMANN * math.log(2)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _postulate(canon: dict, pid: str) -> dict | None:
    for p in canon["postulates"]:
        if p["id"] == pid or p["name"] == pid:
            return {"id": p["id"], "name": p["name"], "lock": p["lock"]}
    return None


def newton(query: str, canon: dict, nom: dict) -> list[dict]:
    q = _norm(query)
    hits = []
    for word in q.split():
        target = nom.get("redirects", {}).get(word)
        if target:
            if target.startswith("N"):
                h = _postulate(canon, target)
                if h:
                    hits.append(h)
            elif target in nom["tokens"]:
                hits.append({"id": "NOM", "name": target, "lock": nom["tokens"][target]})
    for p in canon["postulates"]:
        blob = _norm(p["id"] + " " + p["name"] + " " + p.get("symbol", "") + " " + p["lock"])
        keys = {p["id"].lower(), p["name"].lower(), p.get("symbol", "").lower()}
        if any(k and k in q.split() for k in keys) or any(tok in q for tok in keys if len(tok) > 2):
            hits.append({"id": p["id"], "name": p["name"], "lock": p["lock"]})
            continue
        # light overlap on distinctive words from the lock
        if p["name"] in q or p["id"].lower() in q:
            hits.append({"id": p["id"], "name": p["name"], "lock": p["lock"]})
    for token, meaning in nom["tokens"].items():
        tl = token.lower()
        if tl in q.split() or f" {tl} " in f" {q} ":
            already = {h["name"] for h in hits} | {h["id"] for h in hits}
            if token not in already and tl not in {h["name"].lower() for h in hits}:
                hits.append({"id": "NOM", "name": token, "lock": meaning})
    # unique by lock text
    seen = set()
    out = []
    for h in hits:
        if h["lock"] in seen:
            continue
        seen.add(h["lock"])
        out.append(h)
    return out


def need_gate(proposed: str, meaning: str, canon: dict, nom: dict) -> dict:
    prop = proposed.strip()
    key = _norm(prop)
    meaning_n = _norm(meaning)
    for p in canon["postulates"]:
        if key in _norm(p["name"] + " " + p.get("symbol", "") + " " + p["lock"]) or meaning_n in _norm(p["lock"]):
            return {"decision": "reuse", "cite": p["id"], "lock": p["lock"]}
    for token, m in nom["tokens"].items():
        if key == _norm(token) or key in _norm(m) or meaning_n in _norm(m):
            return {"decision": "reuse", "cite": token, "lock": m}
    for phrase in nom["forbidden_paraphrase"]:
        if _norm(phrase) in meaning_n or meaning_n in _norm(phrase):
            return {"decision": "reject", "reason": "forbidden_paraphrase", "phrase": phrase}
    c = candidates()
    item = c["items"].setdefault(
        prop,
        {"token": prop, "meaning": meaning, "uses": 0, "status": "candidate"},
    )
    item["uses"] = int(item.get("uses", 0)) + 1
    if item["uses"] >= 3:
        item["status"] = "ready_to_lock"
    c["items"][prop] = item
    save_candidates(c)
    return {
        "decision": "candidate",
        "token": prop,
        "uses": item["uses"],
        "status": item["status"],
        "rule": "3 real uses then lock into NOMENCLATURE.json by hand. Canon files stay small.",
    }


def _reg() -> dict:
    return json.loads(REG_PATH.read_text(encoding="utf-8"))


def _state() -> dict:
    if not STATE_PATH.exists():
        return {"version": "1.0.0", "targets": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(obj: dict) -> None:
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE_PATH)


def _today_heat_events(target: str) -> int:
    if not FEEDBACK_PATH.exists():
        return 0
    day = time.strftime("%Y-%m-%d", time.gmtime())
    n = 0
    with FEEDBACK_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("target") == target and row.get("time_iso", "").startswith(day):
                if row.get("kind") != "confirm":
                    n += 1
    return n


def _append_feedback(row: dict) -> None:
    with FEEDBACK_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def _resolve_target(target: str, canon: dict, nom: dict) -> dict:
    t = target.strip()
    p = _postulate(canon, t)
    if p:
        return {"class": "postulate", "id": p["id"], "name": p["name"], "lock": p["lock"]}
    if t in nom["tokens"]:
        return {"class": "token", "id": t, "name": t, "lock": nom["tokens"][t]}
    c = candidates()["items"]
    if t in c:
        return {"class": "candidate", "id": t, "name": t, "lock": c[t].get("meaning", ""), "record": c[t]}
    return {"class": "unknown", "id": t, "name": t, "lock": None}


def feedback(target: str, kind: str, note: str, source: str, canon: dict, nom: dict) -> dict:
    if kind not in KINDS:
        return {"ok": False, "error": f"kind must be one of {KINDS}"}
    spec = _reg()
    resolved = _resolve_target(target, canon, nom)
    if resolved["class"] == "unknown":
        return {
            "ok": False,
            "error": "unknown target",
            "target": target,
            "next": "cite an N-id, a token, or a candidate. need_gate first if it does not exist.",
        }
    th = spec["thresholds"]
    if kind != "confirm" and _today_heat_events(resolved["id"]) >= th["max_heat_events_per_target_per_day"]:
        return {
            "ok": False,
            "action": "rate_limited",
            "cite": "N16",
            "target": resolved["id"],
            "note": "self-regulation applies to feedback itself. wait until tomorrow or confirm instead.",
        }
    now = time.time()
    row = {
        "time_unix": int(now),
        "time_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "target": resolved["id"],
        "class": resolved["class"],
        "kind": kind,
        "note": note,
        "source": source,
        "canon_text_changed": False,
    }
    _append_feedback(row)

    state = _state()
    slot = state["targets"].setdefault(
        resolved["id"],
        {"heat": 0.0, "confirms": 0, "corrects": 0, "rejects": 0, "status": "cool", "draft": None},
    )
    action = "logged"
    if kind == "confirm":
        slot["confirms"] += 1
        slot["heat"] = max(0.0, float(slot["heat"]) - th["cool_per_confirm"])
        action = "cooled"
        if resolved["class"] == "candidate":
            c = candidates()
            if resolved["id"] in c["items"]:
                c["items"][resolved["id"]]["confirms"] = int(c["items"][resolved["id"]].get("confirms", 0)) + 1
                if c["items"][resolved["id"]].get("status") == "killed":
                    c["items"][resolved["id"]]["status"] = "candidate"
                    slot["status"] = "cool"
                    action = "candidate_revived"
                save_candidates(c)
    elif kind == "correct":
        slot["corrects"] += 1
        slot["heat"] = float(slot["heat"]) + th["heat_correct"]
        slot["draft"] = note
        action = "successor_drafted_not_applied"
    elif kind == "reject":
        slot["rejects"] += 1
        slot["heat"] = float(slot["heat"]) + th["heat_reject"]
        action = "heat_added"
        if resolved["class"] == "candidate" and slot["heat"] >= th["kill_candidate_heat"]:
            c = candidates()
            if resolved["id"] in c["items"]:
                c["items"][resolved["id"]]["status"] = "killed"
                save_candidates(c)
            slot["status"] = "killed"
            action = "candidate_killed"
    elif kind == "overclaim":
        slot["heat"] = float(slot["heat"]) + th["heat_overclaim"]
        action = "overclaim_flagged_N14"
        slot["draft"] = note or "N14"
    elif kind == "missing":
        slot["heat"] = float(slot["heat"]) + th["heat_missing"]
        action = "gap_flagged"
    elif kind == "confuse":
        slot["heat"] = float(slot["heat"]) + th["heat_confuse"]
        action = "compress_flagged"

    if resolved["class"] == "postulate" and slot["heat"] >= th["review_heat"]:
        slot["status"] = "review"
        action = "review_opened_lock_unchanged"
    elif resolved["class"] != "candidate" and slot["heat"] < th["review_heat"] and slot["status"] != "killed":
        slot["status"] = "cool" if slot["heat"] == 0 else "warm"

    state["targets"][resolved["id"]] = slot
    _save_state(state)
    return {
        "ok": True,
        "cite": "N16",
        "action": action,
        "target": resolved["id"],
        "class": resolved["class"],
        "heat": slot["heat"],
        "status": slot["status"],
        "draft": slot.get("draft"),
        "canon_text_changed": False,
        "lock": resolved["lock"],
    }


def regulate_status() -> dict:
    spec = _reg()
    state = _state()
    review = [k for k, v in state.get("targets", {}).items() if v.get("status") in ("review", "killed")]
    return {
        "cite": "N16",
        "thresholds": spec["thresholds"],
        "review_or_killed": review,
        "targets": state.get("targets", {}),
        "feedback_lines": sum(1 for _ in FEEDBACK_PATH.open()) if FEEDBACK_PATH.exists() else 0,
        "rule": "high heat opens review. you still edit CANON.json by hand and hang it.",
    }


def derive(utterance: str, canon: dict, nom: dict) -> dict:
    hits = newton(utterance, canon, nom)
    if hits:
        return {"operator": "A1", "path": "Newton", "hits": hits}
    return {
        "operator": "A1",
        "path": "underived",
        "utterance": utterance,
        "next": "need_gate if this must become a token, else speak an existing one",
    }


def cmd_eval(args: argparse.Namespace) -> int:
    if args.fn == "coord":
        print(coord(args.N, args.T, args.R))
    elif args.fn == "synergy":
        print(synergy(args.N, args.R, args.B))
    elif args.fn == "eta":
        print(eta(args.useful, args.human))
    elif args.fn == "gamma":
        print(gamma(args.Y, args.L, args.P, args.F, args.Jh, args.Je, args.C))
    elif args.fn == "landauer":
        print(landauer(args.bits, args.Tkelvin))
    else:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    canon, nom, _alg = load()
    p = argparse.ArgumentParser(description="OpenRoot canon")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("newton", help="match locked postulates, skip the essay")
    n.add_argument("query")

    d = sub.add_parser("derive", help="A1: Newton first")
    d.add_argument("utterance")

    g = sub.add_parser("need", help="propose a new token")
    g.add_argument("token")
    g.add_argument("meaning")

    sub.add_parser("list", help="print locked ids")
    sub.add_parser("tokens", help="print nomenclature tokens")

    e = sub.add_parser("eval", help="run a locked algorithm")
    e.add_argument("fn", choices=["coord", "synergy", "eta", "gamma", "landauer"])
    e.add_argument("--N", type=float, default=6)
    e.add_argument("--T", type=float, default=1)
    e.add_argument("--R", type=float, default=1.0)
    e.add_argument("--B", type=float, default=6)
    e.add_argument("--useful", type=float, default=0)
    e.add_argument("--human", type=float, default=0)
    e.add_argument("--Y", type=float, default=0)
    e.add_argument("--L", type=float, default=1)
    e.add_argument("--P", type=float, default=1)
    e.add_argument("--F", type=float, default=1)
    e.add_argument("--Jh", type=float, default=0)
    e.add_argument("--Je", type=float, default=0)
    e.add_argument("--C", type=float, default=0)
    e.add_argument("--bits", type=float, default=1)
    e.add_argument("--Tkelvin", type=float, default=300.0)

    fb = sub.add_parser("feedback", help="accept heat or cool without rewriting locks")
    fb.add_argument("target", help="N-id, token, or candidate")
    fb.add_argument("kind", choices=list(KINDS))
    fb.add_argument("note")
    fb.add_argument("--source", default="jesse")

    sub.add_parser("regulate", help="show heat, review flags, killed candidates")

    args = p.parse_args(argv)
    if args.cmd == "newton":
        print(json.dumps(newton(args.query, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "derive":
        print(json.dumps(derive(args.utterance, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "need":
        print(json.dumps(need_gate(args.token, args.meaning, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "list":
        print(json.dumps([{k: p[k] for k in ("id", "name") if k in p} | {"symbol": p.get("symbol")} for p in canon["postulates"]], indent=2))
        return 0
    if args.cmd == "tokens":
        print(json.dumps(nom["tokens"], indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "eval":
        return cmd_eval(args)
    if args.cmd == "feedback":
        print(json.dumps(feedback(args.target, args.kind, args.note, args.source, canon, nom), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "regulate":
        print(json.dumps(regulate_status(), indent=2, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
