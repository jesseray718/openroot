#!/usr/bin/env python3
"""7B coder loop. Flag first. Numeric C/S hang in-kernel. Never mint axioms."""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import axiom_engine as ax

DEFAULT_URL = os.environ.get("OPENROOT_LLM_URL", "http://127.0.0.1:8080/v1/chat/completions")
DEFAULT_MODEL = os.environ.get("OPENROOT_LLM_MODEL", "qwen2.5-coder-7b-instruct")
PROMPT = Path(__file__).resolve().parent / "prompts" / "SYSTEM.txt"
PLACEHOLDER_MODELS = {"", "PASTE_ID_FROM_CURL", "PASTE_ID", "REPLACE_ME"}

C_RE = re.compile(
    r"C\s*\(\s*N\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*T\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*R\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*\)\s*=\s*([0-9]+(?:\.[0-9]+)?)",
    re.I,
)
S_RE = re.compile(
    r"S\s*\(\s*N\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*R\s*=\s*([0-9]+(?:\.[0-9]+)?)(?:\s*,\s*B\s*=\s*([0-9]+(?:\.[0-9]+)?))?\s*\)\s*=\s*([0-9]+(?:\.[0-9]+)?)",
    re.I,
)


def load_system() -> str:
    if PROMPT.exists():
        return PROMPT.read_text(encoding="utf-8")
    return "You are the OpenRoot 7B coder. JSON only. Never invent axioms. Flag first."


def catalog_brief(limit: int = 40) -> str:
    rows = []
    for kind in ("axiom", "definition", "postulate", "theorem"):
        for rec in ax.load_jsonl(kind):
            rows.append(f"{rec['flag']} {rec['id']} {rec['statement'][:120]}")
            if len(rows) >= limit:
                return "\n".join(rows)
    return "\n".join(rows)


def model_id() -> str:
    mid = DEFAULT_MODEL
    if mid not in PLACEHOLDER_MODELS:
        return mid
    try:
        req = urllib.request.Request("http://127.0.0.1:8080/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["data"][0]["id"]
    except Exception:
        return "qwen2.5-coder-7b-instruct"


def chat(messages: list[dict], temperature: float = 0.1) -> str:
    body = json.dumps(
        {
            "model": model_id(),
            "temperature": temperature,
            "max_tokens": 800,
            "messages": messages,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        DEFAULT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return json.dumps({"error": "llm_unreachable", "detail": str(e), "url": DEFAULT_URL})
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps({"error": "bad_llm_shape", "raw": data})


def extract_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        return {"error": "no_json", "raw": text[:500]}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        return {"error": "json_decode", "detail": str(e), "raw": text[:500]}


def exact_record(query: str):
    q = (query or "").strip()
    hit = ax.lookup(q)
    if not hit.get("hit"):
        return None
    rec = hit["record"]
    keys = {str(rec.get("flag") or ""), str(rec.get("hash") or ""), str(rec.get("id") or ""), str(rec.get("statement") or "")}
    if q in keys:
        return rec
    return None


def hang_c(query: str):
    m = C_RE.search(query.replace(" ", "")) or C_RE.search(query)
    if not m:
        return None
    N, T, R, expect = map(float, m.groups())
    val = ax.eval_c(N, T, R)
    stmt = f"C(N={N:g},T={T:g},R={R:g}) = {val:g}"
    if abs(val - expect) > 1e-12:
        return {"hit": False, "valid": False, "reason": f"eval_c_mismatch:{val}!={expect}", "C": val}
    spec = {
        "id": f"TH-C-N{N:g}-T{T:g}-R{R:g}",
        "statement": stmt,
        "keys": ["c instance", stmt],
        "premises": ["N03", "B2"],
        "conclude": stmt,
        "proof": [
            {"rule": "assume", "from": [], "conclude": "B2"},
            {"rule": "eval_c", "N": N, "T": T, "R": R, "expect": val, "conclude": stmt},
        ],
    }
    return ax.prove_and_flag(spec)


def hang_s(query: str):
    m = S_RE.search(query)
    if not m:
        return None
    N = float(m.group(1))
    R = float(m.group(2))
    B = float(m.group(3) or 6.0)
    expect = float(m.group(4))
    val = ax.eval_s(N, R, B)
    stmt = f"S(N={N:g},R={R:g},B={B:g}) = {val}"
    if abs(val - expect) > 1e-6:
        return {"hit": False, "valid": False, "reason": f"eval_s_mismatch:{val}!={expect}", "S": val}
    spec = {
        "id": f"TH-S-N{N:g}-R{R:g}-B{B:g}",
        "statement": stmt,
        "premises": ["N05"],
        "conclude": stmt,
        "proof": [
            {"rule": "assume", "from": [], "conclude": "N05"},
            {"rule": "eval_s", "N": N, "R": R, "B": B, "expect": val, "conclude": stmt},
        ],
    }
    return ax.prove_and_flag(spec)


def same_claim(rec, query: str) -> bool:
    q = query.strip()
    return q in {
        str(rec.get("flag") or ""),
        str(rec.get("hash") or ""),
        str(rec.get("id") or ""),
        str(rec.get("statement") or ""),
    }


def run_query(query: str, use_llm: bool = True) -> dict:
    ax.seed_all(False)
    rec = exact_record(query)
    if rec:
        return {
            "hit": True,
            "recomputed": False,
            "flag": rec.get("flag"),
            "hash": rec.get("hash"),
            "id": rec.get("id"),
            "kind": rec.get("kind"),
            "statement": rec.get("statement"),
        }
    numeric = hang_c(query) or hang_s(query)
    if numeric is not None:
        return numeric
    if not use_llm:
        return {"hit": False, "flag": None, "advice": "not exact and not C/S", "near": ax.retrieve(query)}
    raw = chat(
        [
            {"role": "system", "content": load_system() + "\n\nKNOWN FLAGS\n" + catalog_brief()},
            {"role": "user", "content": "Query: " + query + "\nProof spec for THIS statement only. Do not return an axiom flag unless the query is that axiom."},
        ]
    )
    spec = extract_json(raw)
    if spec.get("flag") and not spec.get("proof"):
        again = ax.lookup(spec["flag"])
        if again.get("hit") and same_claim(again["record"], query):
            rec = again["record"]
            return {"hit": True, "recomputed": False, "flag": rec.get("flag"), "hash": rec.get("hash"), "id": rec.get("id")}
        return {"hit": False, "valid": False, "reason": "llm_cited_unrelated_flag", "cited": spec.get("flag")}
    if spec.get("error"):
        return {"hit": False, "valid": False, "reason": spec}
    if "statement" not in spec:
        return {"hit": False, "valid": False, "reason": "llm_missing_statement", "raw": spec}
    return ax.prove_and_flag(spec)


def main(argv) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.stdout.write("coder_loop.py ask <query> [--llm|--no-llm]\n")
        return 0
    if argv[1] == "catalog":
        sys.stdout.write(catalog_brief(200) + "\n")
        return 0
    if argv[1] == "ask":
        args = argv[2:]
        use_llm = "--no-llm" not in args
        q = " ".join(a for a in args if a not in ("--llm", "--no-llm"))
        print(ax.dumps(run_query(q, use_llm=use_llm)))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
