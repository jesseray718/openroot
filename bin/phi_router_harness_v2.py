#!/usr/bin/env python3
# CANARY:OPENROOT-PHI-ROUTER-HARNESS-V2
"""Router test harness: manifest-grounded, JSON-gated, numeric-confidence checked."""
import json, os, re, urllib.request, hashlib, datetime

ROOT = "/home/jesse/openroot"
MODEL = "phi4-router"
API = "http://localhost:11434/api/chat"

def build_manifest():
    def ls(p, exts):
        return sorted(f for f in os.listdir(p) if f.endswith(exts)) if os.path.isdir(p) else []
    return {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "estate": {
            "bin_dir": f"{ROOT}/bin", "data_dir": f"{ROOT}/data",
            "bridge_dir": f"{ROOT}/context_bridge",
            "models": ["qwen2.5-coder:7b", "openroot-instruct:7b", "qwen2.5:3b",
                        "llama3.2:3b", "deepseek-r1:1.5b", "nomic-embed-text"]},
        "scripts_bin": ls(f"{ROOT}/bin", (".sh", ".py")),
        "ledgers_data": ls(f"{ROOT}/data", (".db", ".jsonl", ".json")),
    }

SYSTEM = (
    "You are the OpenRoot router. Output JSON ONLY. "
    "Schema: {\"tool\": \"<name>\", \"model\": \"<name or null>\", "
    "\"args_hint\": \"<one line>\", \"confidence\": 0.92}. "
    "confidence MUST be a single number between 0 and 1. "
    "Only reference tools from this manifest, by exact name. "
    "If the needed tool is not listed, respond with "
    "{\"tool\": \"MISSING\", \"error\": \"<name>\"}. Never invent tools. "
    "No markdown fences. JSON only.\nMANIFEST:\n" + json.dumps(build_manifest(), indent=1)
)

def call(q):
    payload = json.dumps({"model": MODEL, "stream": False,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": q}],
        "options": {"temperature": 0.1}}).encode()
    req = urllib.request.Request(API, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["message"]["content"].strip()

def gate(raw):
    """Strip fences if present, parse, validate schema + numeric confidence."""
    m = re.search(r"\{.*\}", raw, re.DOTALL)          # tolerate stray prose/fences
    if not m:
        return None, "no JSON object found"
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError: {e}"
    conf = d.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
        return d, f"confidence not numeric in [0,1]: {conf!r}"
    for k in ("tool", "model", "args_hint"):
        if k not in d:
            return d, f"missing key: {k}"
    return d, None

TESTS = [
    ("Route: summarize a seed file and log a receipt", "SUMMARY"),
    ("Route: edit a Python script that fails py_compile", "CODE"),
    ("Route: embed a document for semantic search", "EMBED"),
    ("Route: deploy the Kubernetes Helm chart to production", "MISSING"),  # trap: not in estate
]

passed, failed = 0, 0
receipts = []
for q, expect in TESTS:
    raw = call(q)
    d, err = gate(raw)
    ok = err is None
    verdict = "PASS" if ok else f"FAIL ({err})"
    print(f"Q: {q}\nA: {json.dumps(d) if d else raw}\n[gate] {verdict}  (expected: {expect})\n---")
    receipts.append({"q": q, "expect": expect, "parsed": d, "err": err,
                      "sha": hashlib.sha256(raw.encode()).hexdigest()[:12]})
    passed, failed = passed + ok, failed + (not ok)

rp = f"{ROOT}/data/phi_router_receipts_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
open(rp, "w").write("\n".join(json.dumps(r) for r in receipts))
print(f"[{'banked' if failed == 0 else 'held'}] {passed}/{len(TESTS)} passed | receipts: {rp}")
