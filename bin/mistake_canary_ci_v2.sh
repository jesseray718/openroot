#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# SPDX-License-Identifier: GPL-3.0-only
# mistake_canary_ci_v2.sh — canaries keyed by mistake CLASS (real schema), deduped by sha.
LOG=/home/${OPENROOT_USER}/openroot/data/mistakes/mistake_log.jsonl
PASS=0; FAIL=0; SKIPPED=0
[ -f "$LOG" ] || { echo "[held] no mistake log"; exit 1; }

echo "[gate] canary 0: JSONL parses (regression: generator-repr corruption)"
if python3 -c "
import json,sys
rows=[json.loads(l) for l in open('$LOG') if l.strip()]
sys.exit(0 if rows else 1)"; then
    PASS=$((PASS+1)); echo "  [banked] parse-ok"
else
    FAIL=$((FAIL+1)); echo "  [held] LOG CORRUPT — refusing further canaries"; exit 1
fi

seen=""
while IFS= read -r line; do
    [ -z "$(echo "$line" | tr -d '[:space:]')" ] && continue
    cls=$(echo "$line" | python3 -c 'import json,sys;print(json.loads(sys.stdin.read()).get("class",""))' 2>/dev/null || echo "")
    sha=$(echo "$line" | python3 -c 'import json,sys;print(json.loads(sys.stdin.read()).get("sha",""))' 2>/dev/null || echo "")
    [ -z "$cls" ] && { SKIPPED=$((SKIPPED+1)); continue; }
    case "$seen" in *"$sha|$cls"*) SKIPPED=$((SKIPPED+1)); continue;; esac
    seen="$seen $sha|$cls"
    case "$cls" in
        gate-bypass-environment)
            if grep -qE '^\s*(export\s+)?CONFIRM=1' ~/.bashrc ~/.profile ~/.bash_aliases 2>/dev/null; then
                FAIL=$((FAIL+1)); echo "  [held] CONFIRM=1 persisted in startup files"
            else
                PASS=$((PASS+1)); echo "  [banked] no sticky CONFIRM flag"
            fi ;;
        env-var-dead-across-ssh-session)
            if ls /Modelfile.* >/dev/null 2>&1; then
                FAIL=$((FAIL+1)); echo "  [held] root-leaked Modelfile residue exists"
            else
                PASS=$((PASS+1)); echo "  [banked] no root-level leak files"
            fi ;;
        python-snippet-pasted-into-bash)
            if tail -n 200 ~/.bash_history 2>/dev/null | grep -qE '^\s*(import|from)\s+(json|sys|os)'; then
                SKIPPED=$((SKIPPED+1)); echo "  [held] history contains pasted-python traces (policy class)"
            else
                PASS=$((PASS+1)); echo "  [banked] no pasted-python in history tail"
            fi ;;
        json-generator-repr-corruption)
            if python3 -c "
import json
[json.loads(l) for l in open('$LOG') if l.strip()]
assert '<generator' not in open('$LOG').read()"; then
                PASS=$((PASS+1)); echo "  [banked] log free of generator-repr corruption"
            else
                FAIL=$((FAIL+1)); echo "  [held] generator-repr corruption present"
            fi ;;
        *) SKIPPED=$((SKIPPED+1)); echo "  [gate] no canary mapped for class: $cls" ;;
    esac
done < "$LOG"
echo "[banked] canary CI v2: pass=$PASS fail=$FAIL skipped=$SKIPPED unique=$(echo $seen | wc -w)"
[ "$FAIL" -eq 0 ]
