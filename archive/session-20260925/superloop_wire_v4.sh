#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# superloop_wire_v4.sh — consume model_registry.json in smart_router + CI gate
# Canary: [SUPERLOOPV4]  Human gate: commit held; push only after inspect
set -euo pipefail
export GIT_PAGER=cat
OR=/home/jesse/openroot
cd "$OR"

# ============================================================
# PIECE 1: REGISTRY CONSUMER — patch smart_router.py (guarded)
# ============================================================
if [ ! -f bin/smart_router.py ]; then
  echo "[held] bin/smart_router.py not found — registry consumer not wired"
else
  cp bin/smart_router.py "bin/smart_router.py.bak.$(date +%Y%m%d_%H%M%S)"
  if grep -q 'SUPERLOOPV4-REGISTRY-HOOK' bin/smart_router.py; then
    echo "[held] registry hook already present in smart_router.py (idempotent)"
  else
    python3 - <<'HOOK_EOF'
from pathlib import Path
P = Path("/home/jesse/openroot/bin/smart_router.py")
src = P.read_text()

HOOK = '''

# --- SUPERLOOPV4-REGISTRY-HOOK (mined routing weights, auto-managed) ---
import json as _json
from pathlib import Path as _Path
_REGISTRY = _Path("/home/jesse/openroot/data/model_registry.json")

def _registry_bucket_for(task_hint):
    """Map a task hint to the superloop bucket vocabulary, then to registry routing."""
    import re
    BUCKETS = [
        ("bridge",   r"\\b(ssh|scp)\\b"), ("gitops", r"\\b(git|gh|commit|pr)\\b"),
        ("model",    r"(ollama|11434|qwen|infer)"), ("author", r"(heredoc|write|draft|generate doc)"),
        ("exec",     r"(execute|run|compile|smoke)"), ("gate", r"(gate|verify|grade|test)"),
        ("system",   r"(process|daemon|memory|disk)"), ("net", r"(curl|fetch|network)"),
    ]
    for name, pat in BUCKETS:
        if re.search(pat, task_hint, re.I):
            return name
    return "other"

def route_by_registry(task_hint, fallback=None):
    """Return mined routing decision for a task, from data/model_registry.json.
    Falls back to caller-provided default if registry unreadable."""
    try:
        reg = _json.loads(_REGISTRY.read_text())
        bucket = _registry_bucket_for(task_hint)
        rw = reg.get("routing_weights", {}).get(bucket, {})
        return {"bucket": bucket,
                "route_to": rw.get("route_to", fallback or "lumo"),
                "pref_model": rw.get("pref_model", ""),
                "source": "registry",
                "generated": reg.get("generated")}
    except Exception:
        return {"bucket": "unknown", "route_to": fallback or "lumo",
                "pref_model": "", "source": "fallback"}
# --- END SUPERLOOPV4-REGISTRY-HOOK ---
'''

if "def route_by_registry" not in src:
    src = src.rstrip("\n") + "\n" + HOOK
    P.write_text(src)
    print("[banked] registry hook appended to smart_router.py")
else:
    print("[held] route_by_registry already defined")
HOOK_EOF

  python3 -m py_compile bin/smart_router.py && echo "[gate:py_compile] smart_router PASS"

  # Smoke: call the hook from outside
  python3 - <<'SMOKE_EOF'
import importlib.util
spec = importlib.util.spec_from_file_location("sr", "/home/jesse/openroot/bin/smart_router.py")
sr = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(sr)
except SystemExit:
    pass  # routers often define main-guard arg parsing
d = sr.route_by_registry("verify this commit with the gate")
print("[smoke] gitops task ->", d)
assert d["bucket"] == "gitops", "bucket mismatch: " + str(d)
assert d["source"] in ("registry", "fallback")
print("[smoke] registry routing VERIFIED")
SMOKE_EOF
fi

# ============================================================
# PIECE 2: CI GATE — .github/workflows/superloop_ci.yml
# ============================================================
mkdir -p .github/workflows
cat > .github/workflows/superloop_ci.yml <<'YMLEOF'
# CI gate for the superloop layer — blocks merges that break the loop itself.
# Canary: [SUPERLOOPV4]  provenance: AI-assisted, human-gated
name: superloop-ci
on:
  pull_request:
    paths:
      - 'bin/superloop_*.py'
      - 'bin/smart_router.py'
      - 'data/model_registry.json'
      - '.github/workflows/superloop_ci.yml'
  push:
    branches: [main]
    paths:
      - 'bin/superloop_*.py'
      - 'bin/smart_router.py'
      - 'data/model_registry.json'

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: py_compile every superloop module
        run: |
          set -e
          STATUS=0
          for f in bin/superloop_*.py bin/smart_router.py; do
            [ -f "$f" ] || continue
            python3 -m py_compile "$f" && echo "[PASS] $f" || { echo "[FAIL] $f"; STATUS=1; }
          done
          exit $STATUS

      - name: registry JSON sanity
        run: |
          python3 - <<'PY'
          import json, sys
          try:
              reg = json.load(open("data/model_registry.json"))
          except FileNotFoundError:
              print("[PASS] no registry committed (runtime-state artifact) — skipping")
              sys.exit(0)
          except json.JSONDecodeError as e:
              print(f"[FAIL] model_registry.json invalid JSON: {e}"); sys.exit(1)
          assert "routing_weights" in reg, "registry missing routing_weights"
          print("[PASS] registry parses:", len(reg["routing_weights"]), "buckets")
          PY

      - name: SPDX license header check
        run: |
          STATUS=0
          for f in bin/superloop_*.py; do
            [ -f "$f" ] || continue
            grep -q "SPDX-License-Identifier: GPL-3.0" "$f" && echo "[PASS] $f" || { echo "[FAIL] no SPDX header: $f"; STATUS=1; }
          done
          exit $STATUS

      - name: shell syntax gate (bash -n)
        run: |
          STATUS=0
          for f in $(git ls-files '*.sh' 2>/dev/null); do
            bash -n "$f" && echo "[PASS] $f" || { echo "[FAIL] $f"; STATUS=1; }
          done
          exit $STATUS
YMLEOF
echo "[banked] CI gate written: .github/workflows/superloop_ci.yml"

# ============================================================
# PIECE 3: verify + stage (commit is the human gate)
# ============================================================
echo ""
echo "=== LOCAL PRE-FLIGHT (mirror of CI) ==="
bash -n .github/workflows/superloop_ci.yml 2>/dev/null || echo "[info] yaml not bash — expected"
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/superloop_ci.yml')); print('[gate:yaml] PASS')" \
  || echo "[gate:yaml] pyyaml unavailable — CI itself will validate on GitHub"

git add bin/smart_router.py .github/workflows/superloop_ci.yml
git status --short

echo ""
echo "=== HELD FOR HUMAN GATE ==="
echo "inspect: git diff --cached --stat"
echo "commit:  git commit -m '[ADD][SUPERLOOP] wire mined registry into smart_router routing + CI gate (py_compile, registry sanity, SPDX, bash -n); AI-assisted, human-gated'"
echo "push:    git push origin main"
echo "[exit=0]"
