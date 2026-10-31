# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
# CANARY:OPENROOT-PHI-ROUTER-HARNESS-V3
"""Structured-output routing + semantic gate: tool must be manifest-exact, model must match specialty."""
import json, os, urllib.request, hashlib, datetime

ROOT = "/home/jesse/openroot"
MODEL = "phi4-router"
API = "http://localhost:11434/api/chat"

def ls(p, exts):
    return sorted(f for f in os.listdir(p) if f.endswith(exts)) if os.path.isdir(p) else []

SCRIPTS = ls(f"{ROOT}/bin", (".sh", ".py"))
MODELS = ["qwen2.5-coder:7b", "openroot-instruct:7b", "qwen2.5:3b",
          "llama3.2:3b", "deepseek-r1:1.5b", "nomic-embed-text"]
SYSTEM = (
    "You are the OpenRoot router. Given a task, select the tool and model. "
    "tool MUST be exactly one of these names from the manifest: "
    + ", ".join(SCRIPTS + MODELS) + ". "
    "If no listed tool fits, set tool to \"MISSING\". "
    "Embedding/search tasks use model nomic-embed-text. "
    "Code editing/generation tasks use model qwen2.5-coder:7b. "
    "If no model applies, use null."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "tool": {"type": "string"},
        "model": {"type": ["string", "null"]},
        "args_hint": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["tool", "model", "args_hint", "confidence"],
}

def call(q):
    payload = json.dumps({"model": MODEL, "stream": False,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": q}],
        "format": SCHEMA,                                  # runtime-enforced JSON
        "options": {"temperature": 0.1}}).encode()
    req = urllib.request.Request(API, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(json.load(r)["message"]["content"])   # schema guarantees parse

def semantically_ok(d, expect):
    """Format is guaranteed by schema; this checks SEMANTICS only."""
    tool, model = d["tool"], d["model"]
    if expect == "MISSING":
        return tool == "MISSING", f"wanted MISSING, got {tool}"
    if tool == "MISSING":
        return False, "routed MISSING for a task the estate can do"
    if tool not in SCRIPTS and tool not in MODELS:
        return False, f"invented tool {tool!r} not in manifest"
    if expect == "EMBED" and model != "nomic-embed-text":
        return False, f"embedding must route to nomic-embed-text, got {model}"
    if expect == "CODE" and model != "qwen2.5-coder:7b":
        return False, f"code must route to qwen2.5-coder:7b, got {model}"
    return True, None

TESTS = [
    ("Route: summarize a seed file in the context bridge and log a receipt", "SUMMARY"),
    ("Route: edit a Python script that fails py_compile", "CODE"),
    ("Route: embed a document for semantic search against the goal index", "EMBED"),
    ("Route: deploy the Kubernetes Helm chart to production", "MISSING"),
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
rp = f"{ROOT}/data/phi_router_receipts_v3_{ts}.jsonl"
open(rp, "w").write("\n".join(json.dumps(r) for r in receipts))
print(f"[{'banked' if passed == len(TESTS) else 'held'}] {passed}/{len(TESTS)} semantic passes | receipts: {rp}")
