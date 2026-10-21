#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — routing weights v1: write model_registry.json, patch smart_router.py to read it
# eta = useful_joules / human_joules
import json, os, sys, datetime, glob, subprocess

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
CANARY = "WEIGHTS1"
REGISTRY = "/home/jesse/openroot/data/model_registry.json"
ROUTER = "/home/jesse/openroot/bin/smart_router.py"
LOG = f"/home/jesse/openroot/logs/routing_weights_{STAMP}.log"

print(f"[{CANARY}] START {STAMP}")

# ============================================================
# VERIFIED MODEL STATE FROM BENCH OUTPUT
# ============================================================
registry = {
    "version": "v1",
    "generated_at": STAMP,
    "doctrine_notes": [
        "Instruments audited before builders (bench --bench passed).",
        "Custom openroot-* models FAIL py_compile — NOT ROUTED for authoring.",
        "nomic-embed-text never co-loaded with 7B+indexer (RAM constraint on OptiPlex 16GB)."
    ],
    "models": {
        "qwen2.5-coder:7b": {
            "role": "AUTHOR",
            "size_gb": 4,
            "grade": "PASS",
            "lineage": "known-good 5-for-5 (session 2026-09-18 onward)",
            "latency_s": None,  # populate via warm-pool probe if desired
            "usage_policy": "primary author, no exceptions until re-bench",
            "co_load_rules": "ok with 3B, forbidden with nomic+indexer"
        },
        "openroot-coder:latest": {
            "role": "UNVERIFIED_AUTHOR",
            "size_gb": 4,
            "grade": "FAIL",
            "lineage": "custom, py_compile=FAIL at 51.7s (bench 2026-09-24 162648)",
            "latency_s": 51.7,
            "usage_policy": "DO NOT ROUTE authoring work — can produce non-compiling output",
            "co_load_rules": "none"
        },
        "qwen2.5:3b": {
            "role": "GRADER",
            "size_gb": 1,
            "grade": "PASS",
            "lineage": "known-good grader",
            "latency_s": 0.4,  # from probe
            "usage_policy": "grading/validation only",
            "co_load_rules": "ok with 7B author, ok with nomic"
        },
        "openroot-assistant:latest": {
            "role": "UNVERIFIED_GRADE",
            "size_gb": 4,
            "grade": "FAIL",
            "lineage": "custom, py_compile=FAIL at 122.4s (bench 2026-09-24 162648)",
            "latency_s": 122.4,
            "usage_policy": "DO NOT ROUTE grading work — unreliable",
            "co_load_rules": "none"
        },
        "deepseek-r1:1.5b": {
            "role": "THINK",
            "size_gb": 1,
            "grade": "OPEN",
            "lineage": "chain-of-thought specialist, not yet bench-tested",
            "latency_s": None,
            "usage_policy": "reasoning-chain drafts only, never code authoring",
            "co_load_rules": "ok with anyone"
        },
        "llama3.2:1b": {
            "role": "TINY",
            "size_gb": 1,
            "grade": "OPEN",
            "lineage": "keyword routing / pinger only",
            "latency_s": None,
            "usage_policy": "routing/pinging, never authoring or grading",
            "co_load_rules": "ok with anyone"
        },
        "nomic-embed-text:latest": {
            "role": "EMBED",
            "size_gb": 0,
            "grade": "PASS",
            "lineage": "FTS5 pair, required for RAG",
            "latency_s": None,
            "usage_policy": "embedding service only",
            "co_load_rules": "FORBIDDEN with 7B author + indexer active (RAM overflow risk)"
        }
    },
    "routing_table": {
        "AUTHOR": ["qwen2.5-coder:7b"],
        "GRADE": ["qwen2.5:3b"],
        "THINK": ["deepseek-r1:1.5b"],
        "TINY": ["llama3.2:1b"],
        "EMBED": ["nomic-embed-text:latest"],
        "UNVERIFIED": ["openroot-coder:latest", "openroot-assistant:latest"]  # never auto-route
    }
}

# write registry atomically (write then rename)
tmp_reg = REGISTRY + ".tmp"
os.makedirs(os.path.dirname(REGISTRY), exist_ok=True)
with open(tmp_reg, "w") as f:
    json.dump(registry, f, indent=2)
os.rename(tmp_reg, REGISTRY)
print(f"[banked] wrote {REGISTRY} ({os.path.getsize(REGISTRY)} bytes)")

# ============================================================
# PATCH smart_router.py TO READ THIS REGISTRY
# ============================================================
if os.path.exists(ROUTER):
    router_src = open(ROUTER).read()
    
    # add import and registry load if missing
    if "from data.model_registry import" not in router_src and "model_registry" not in router_src:
        router_src = router_src.replace(
            "#!/usr/bin/env python3",
            "#!/usr/bin/env python3\nimport json\nfrom pathlib import Path"
        )
        
        # inject registry loading near top of main() or module scope
        if "MODEL_REGISTRY =" not in router_src:
            injection = '''
# Routing weights — read from model_registry.json (audited bench state)
MODEL_REGISTRY_PATH = Path("/home/jesse/openroot/data/model_registry.json")
MODEL_REGISTRY = json.load(open(MODEL_REGISTRY_PATH)) if MODEL_REGISTRY_PATH.exists() else None

def get_model_for_role(role: str):
    """Route role → model name from verified weights. Returns None if no model graded PASS."""
    if not MODEL_REGISTRY:
        return None
    candidates = MODEL_REGISTRY.get("routing_table", {}).get(role, [])
    for m in candidates:
        if MODEL_REGISTRY["models"].get(m, {}).get("grade") == "PASS":
            return m
    return None  # no eligible model
'''
            # insert after imports
            lines = router_src.split("\n")
            insert_idx = len(lines)
            for i, l in enumerate(lines):
                if l.startswith("def "):
                    insert_idx = i
                    break
            router_src = "\n".join(lines[:insert_idx]) + injection + "\n" + "\n".join(lines[insert_idx:])
            open(ROUTER, "w").write(router_src)
            print(f"[banked] patched {ROUTER} (added MODEL_REGISTRY + get_model_for_role)")
        else:
            print(f"[status] {ROUTER} already contains model_registry logic — skip patch")
    else:
        print(f"[status] {ROUTER} already references model_registry — skip patch")
else:
    print(f"[status] {ROUTER} not found — create routing_weights stub or defer patch")

# ============================================================
# HANDOFF
# ============================================================
hp = f"/home/jesse/openroot/context_bridge/routing_weights_handoff_{STAMP}.md"
os.makedirs(os.path.dirname(hp), exist_ok=True)
with open(hp, "w") as f:
    f.write(f"# Routing Weights Handoff {STAMP}\n")
    f.write(f"- Registry: {REGISTRY} ({os.path.getsize(REGISTRY)} bytes)\n")
    f.write(f"- Models rated: {len(registry['models'])}\n")
    f.write(f"- Auth-pass: {[m for m,d in registry['models'].items() if d['role']=='AUTHOR' and d['grade']=='PASS']}\n")
    f.write(f"- Graders-pass: {[m for m,d in registry['models'].items() if d['role']=='GRADER' and d['grade']=='PASS']}\n")
    f.write(f"- Customs-failed: {[m for m,d in registry['models'].items() if d['role'].startswith('UNVERIFIED')]}\n")
    f.write(f"- Smart-router patched: {os.path.exists(ROUTER) and 'MODEL_REGISTRY' in open(ROUTER).read()}\\n")
    f.write(f"- Next action: git add data/model_registry.json && commit, then audit smart_router.py routes\\n")
h = __import__("hashlib").sha256(open(hp, "rb").read()).hexdigest()
print(f"sha256 {h}  {hp}")
print(f"[{CANARY}] END {STAMP} [exit=0]")
