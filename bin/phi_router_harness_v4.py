#!/usr/bin/env python3
# CANARY:OPENROOT-PHI-ROUTER-HARNESS-V4
"""Enum-locked structured outputs: grammar forbids invented tools; handleable flag guards the trap."""
import json, os, urllib.request, hashlib, datetime

ROOT = "/home/jesse/openroot"
MODEL = "phi4-router"
API = "http://localhost:11434/api/chat"

def ls(p, exts):
    return sorted(f for f in os.listdir(p) if f.endswith(exts)) if os.path.isdir(p) else []

SCRIPTS = ls(f"{ROOT}/bin", (".sh", ".py"))
MODELS = ["qwen2.5-coder:7b", "openroot-instruct:7b", "qwen2.5:3b",
          "llama3.2:3b", "deepseek-r1:1.5b", "nomic-embed-text"]
assert SCRIPTS, "bin/ is EMPTY — router has nothing to ground on. Check /home/jesse/openroot/bin"
print(f"[gate] manifest: {len(SCRIPTS)} scripts, {len(MODELS)} models")

SYSTEM = (
    "You triage tasks for the OpenRoot estate. First decide: can ANY tool below do it? "
    "handleable means an EXISTING tool in TOOLS already does this task today. Writing NEW code to gain a capability = handleable false. If NO, set handleable=false, tool=\"MISSING\", model=\"none\". "
    "If YES, set handleable=true and pick tool and model from ONLY these names:\n"
    "TOOLS: " + ", ".join(SCRIPTS) + "\n"
    "MODELS: " + ", ".join(MODELS) + "\n"
    "Rules: embedding/semantic-search tasks -> model nomic-embed-text. "
    "code-editing tasks -> model qwen2.5-coder:7b. "
    "Kubernetes, cloud, web-scraping, enterprise tools = NOT handleable.\n"
    "Example: task 'deploy Airflow DAG to GCP' -> "
    '{"handleable": false, "tool": "MISSING", "model": "none", "args_hint": "no cloud tools in estate", "confidence": 0.95}'
)

SCHEMA = {
    "type": "object",
    "properties": {
        "handleable": {"type": "boolean"},
        "tool": {"type": "string", "enum": SCRIPTS + ["MISSING"]},
        "model": {"type": "string", "enum": ["none"] + MODELS},
        "args_hint": {"type": "string", "maxLength": 120},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["handleable", "tool", "model", "args_hint", "confidence"],
}

def call(q):
    payload = json.dumps({"model": MODEL, "stream": False,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": q}],
        "format": SCHEMA,
        "options": {"temperature": 0.1, "num_ctx": 4096}}).encode()
    req = urllib.request.Request(API, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(json.load(r)["message"]["content"])
    if d["model"] == "none":
        d["model"] = None
    return d

def semantically_ok(d, expect):
    h, tool, model = d["handleable"], d["tool"], d["model"]
    if h != (tool != "MISSING"):
        return False, f"inconsistent triage: handleable={h} but tool={tool}"
    if h != (model is not None):
        return False, f"inconsistent triage: handleable={h} but model={model}"
    if expect == "MISSING":
        return (not h), "should have declared unhandleable" if h else None
    if not h:
        return False, "declared MISSING for a task the estate can do"
    if expect == "EMBED" and model != "nomic-embed-text":
        return False, f"embedding must -> nomic-embed-text, got {model}"
    if expect == "CODE" and model != "qwen2.5-coder:7b":
        return False, f"code must -> qwen2.5-coder:7b, got {model}"
    return True, None

TESTS = [
    ("Route: summarize a seed file in the context bridge and log a receipt", "SUMMARY"),
    ("Route: edit a Python script that fails py_compile", "CODE"),
    ("Route: embed a document for semantic search against the goal index", "EMBED"),
    ("Route: deploy the Kubernetes Helm chart to production", "MISSING"),
    ("Route: scrape Twitter trending topics with Selenium", "MISSING"),  # second trap, different flavor
]

receipts, passed = [], 0
for q, expect in TESTS:
    d = call(q)
    ok, why = semantically_ok(d, expect)
    passed += ok
    print(f"Q: {q}\nA: {json.dumps(d)}\n[gate] {'PASS' if ok else 'FAIL: ' + str(why)}\n---")
    receipts.append({"q": q, "expect": expect, "parsed": d, "fail_reason": why,
                     "sha": hashlib.sha256(json.dumps(d).encode()).hexdigest()[:12]})

ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
rp = f"{ROOT}/data/phi_router_receipts_v4_{ts}.jsonl"
open(rp, "w").write("\n".join(json.dumps(r) for r in receipts))
print(f"[{'banked' if passed == len(TESTS) else 'held'}] {passed}/{len(TESTS)} semantic passes | receipts: {rp}")
