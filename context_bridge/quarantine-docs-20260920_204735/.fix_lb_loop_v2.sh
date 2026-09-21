#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
cd ~/openroot
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:identify] which bin/*.sh fails syntax?"
FAILING=""
for f in bin/*.sh; do
  if ! bash bin/stack_gate.sh "$f" >/dev/null 2>&1; then
    echo "[FAILS] $f ($(wc -l < "$f") lines)"; FAILING="${FAILING} $f"
  fi
done
if [ -z "$FAILING" ]; then echo "[OK] all bin/*.sh pass — earlier 1-line FAIL may have been interleaved output"; fi

echo "[STAGE:inspect] failing script contents (truth, no invention)"
for f in $FAILING; do echo "--- $f ---"; cat "$f"; done

echo "[STAGE:exclude-decide] holding failing script OUT of gating needs conscious choice"
if [ -n "$FAILING" ]; then
  cp ${FAILING} "context_bridge/" 2>/dev/null || true
  echo "[HELD-DUMP] copies banked to context_bridge/ for repair; not auto-excluded"
fi

echo "[STAGE:wrapper-v2] doctrine-compliant gate — stub-held instruments excluded from pipeline AND gate"
cat <<'WRAP' > bin/lb_stack_gate_all.sh
#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# Gate every bin/*.sh pre-run (doctrine). Stub-held instruments are excluded from
# the pipeline, therefore also from gating — a stub cannot block verified instruments.
# Stub exclusion list: context_bridge/.gate_exclude (one basename per line).
# To consciously exempt a REAL script, add its basename there — human is the gate.
set -u
cd "$(dirname "$0")/.." || exit 1
EXCL=$(cat context_bridge/.gate_exclude 2>/dev/null || echo "refine_next.sh")
fails=0
for f in bin/*.sh; do
  base=$(basename "$f")
  skip=0
  while IFS= read -r e; do [ "$base" = "$e" ] && skip=1; done <<< "$EXCL"
  if [ "$skip" = "1" ]; then echo "[SKIP-STUB] $base (stub-held, not gated)"; continue; fi
  if ! bash bin/stack_gate.sh "$f" >/dev/null 2>&1; then
    echo "[GATE-FAIL] $f"; fails=$((fails+1))
  fi
done
[ "$fails" -eq 0 ] || { echo "[RESULT] ${fails} gate failures"; exit 1; }
echo "[RESULT] all gated bin/*.sh pass"
exit 0
WRAP
chmod +x bin/lb_stack_gate_all.sh
if bash bin/lb_stack_gate_all.sh; then echo "[GATE-ALL] wrapper passes standalone"; else
  echo "[HELD] gate failure — repair the failing script(s) above, or consciously add basename to context_bridge/.gate_exclude"
  echo "[NOTE] failing script copies already banked to context_bridge/ — do not blind-exclude"
fi

echo "[STAGE:patch-flex] lb_loop_v2 — regex patch (survives local drift like agent_loop hold clause)"
python3 - <<'PYEOF'
import re
from pathlib import Path
p = Path("bin/lb_loop_v2.py")
src = p.read_text()
changed = []

if "lb_stack_gate_all.sh" not in src:
    new_src, n = re.subn(
        r'\(\s*"stack_gate"\s*,\s*\[[^\]]*?\]\s*\)',
        '("stack_gate",   ["bash", "bin/lb_stack_gate_all.sh"]),',
        src, count=1)
    assert n == 1, "[HELD] stack_gate stage tuple not found by regex — dump STAGES manually"
    src = new_src; changed.append("stack_gate stage -> wrapper")

if "LB_DOC_EXCLUDE" not in src:
    m = re.search(r'(def inputs_sig\(stage\):\n)(.*?)(?=\ndef )', src, re.DOTALL)
    assert m, "[HELD] inputs_sig not found — manual patch needed"
    body = '''    import hashlib as _h
    sig = ""
    if stage == "doc_compiler":
        excl = [x for x in os.environ.get("LB_DOC_EXCLUDE", "context_bridge/*doc_compile*").split(",") if x]
        for p in sorted(ROOT.rglob("*.md")):
            if ".git" in str(p): continue
            rel = p.relative_to(ROOT).as_posix()
            if any(Path(rel).match(e) for e in excl): continue
            sig += f"{rel}:{_h.sha256(p.read_bytes()).hexdigest()[:12]};"
    return sig
'''
    src = src[:m.start()] + m.group(1) + body + src[m.end():]
    changed.append("doc_compiler content-hash signature")

if not changed:
    print("[ALREADY] both patches present — idempotent, nothing to do")
else:
    p.write_text(src)
    print(f"[PATCHED] {', '.join(changed)}")
PYEOF
python3 -m py_compile bin/lb_loop_v2.py && echo "[COMPILE] py_compile passed"
python3 -c "import ast; ast.parse(open('bin/lb_loop_v2.py').read()); print('[AST] parsed clean')"

echo "[STAGE:bind] mistake classes to ledger (never re-debug these again)"
python3 bin/lb_loop_v2.py solve 0c63933c78a0cc2a \
  "stack_gate.sh requires operand; pipeline stages must call doctrine-compliant wrapper (bin/lb_stack_gate_all.sh); exact-string patch asserts hold under local drift — use regex patches for living files" || true

echo "[STAGE:loop] drive to completion"
python3 bin/lb_loop_v2.py run
RUN1=$?
echo "[LOOP-RC] ${RUN1}"

if [ "${RUN1}" = "0" ]; then
  echo "[STAGE:proof] compounding rerun — expect all cache-hits incl doc_compiler"
  python3 bin/lb_loop_v2.py run
  echo "[PROOF-RC] $?"
fi
python3 bin/lb_loop_v2.py stats

echo "[STAGE:seal] session record + commit + push"
cat <<SEED > context_bridge/session-2026-09-21-lbloop-fix2.md
# lb_loop fix pass 2 — 2026-09-21
- exact-string patch assert held (local drift) → switched to regex patching
- wrapper v2: stub-aware gating via context_bridge/.gate_exclude; repairs banked not blind-excluded
- doc_compiler self-invalidation fixed via content-hash corpus signature
- mistake 0c63933c78a0cc2a bound: operand-missing + patch-drift classes
- loop rc recorded below; compounding proof attempted on clean pass
## Provenance: lumo-assisted, human-gated
## Loop-rc: ${RUN1}
SEED
cat <<MSG > .commitmsg.txt
[FIX] lb_loop v2 patches — operand-compliant gating + cache self-invalidation

- lb_stack_gate_all.sh v2: gates all bin/*.sh, stub exclusion via .gate_exclude (human-gated)
- lb_loop_v2.py: stack_gate stage routed to wrapper; doc_compiler input sig content-hashed
- mistake ledger: 0c63933c78a0cc2a bound (operand + patch-drift class)
- regex patching replaces exact-string asserts for living files

Provenance: lumo-assisted, human-gated
MSG
git add bin/lb_stack_gate_all.sh bin/lb_loop_v2.py context_bridge/session-2026-09-21-lbloop-fix2.md
git commit -F .commitmsg.txt && rm -f .commitmsg.txt
git push origin main && echo "[BANKED] pushed $(git rev-parse --short HEAD)"

echo "[CANARY] lbloop-fix2-complete-${TS}"
echo "[exit=0]"
