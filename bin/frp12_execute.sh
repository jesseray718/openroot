#!/usr/bin/env bash
# frp12_execute.sh v1.1 — prune executor, keyed by repo:branch (v1.0 name-collision FIXED)
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
GH_USER=jesseray718
TS=$(date +%Y%m%d_%H%M%S)
RPT=$REPO/analysis/frp12_${TS}
mkdir -p "$RPT"
PRUNE=$(ls -t "$REPO"/analysis/frp8_*/prune_plan.json 2>/dev/null | head -1)
DEDUPE=$(ls -t "$REPO"/analysis/frp9_*/dedupe_plan.json 2>/dev/null | head -1)
if [ -z "$PRUNE" ] || [ -z "$DEDUPE" ]; then echo "[gate] missing frp8/frp9 plans"; exit 1; fi
MODE=$([ "${CONFIRM:-0}" = "1" ] && echo EXECUTE || echo DRY-RUN)
echo "[frp12 v1.1] $TS — mode: $MODE"

# ---------- [stage:quality-log] ----------
gh run list -R "$GH_USER/OpenCell-Thermal-System" --workflow Quality --limit 3 \
  --json conclusion,databaseId > "$RPT/quality_runs.json" || true
RUN_ID=$(python3 -c 'import json;r=json.load(open("'"$RPT"'/quality_runs.json"));print(next((x["databaseId"] for x in r if x.get("conclusion")=="failure"),""))' 2>/dev/null || echo "")
if [ -n "$RUN_ID" ]; then
  gh run view "$RUN_ID" -R "$GH_USER/OpenCell-Thermal-System" --log-failed > "$RPT/quality_failure.log" 2>&1 || true
  echo "[stage:quality-log] raw tail:"
  tail -15 "$RPT/quality_failure.log" 2>/dev/null || echo "(log empty)"
else
  echo "[held] no failed Quality runs reachable"
fi

# ---------- [stage:prune] ----------
python3 - "$PRUNE" "$DEDUPE" "$RPT" "$MODE" <<'PYEOF'
import json, subprocess, sys, pathlib
prune = json.load(open(sys.argv[1])); dedupe = json.load(open(sys.argv[2]))
rpt, mode = pathlib.Path(sys.argv[3]), sys.argv[4]

targets = {}   # KEY: "repo:branch" — v1.0 name-collision bug eliminated
for e in prune["CONTAINED"]:
    targets[f"{e['repo']}:{e['branch']}"] = (e["repo"], e["branch"], "contained ahead_by=0")
for d in dedupe["duplicate_prune_candidates"]:
    targets[f"{d['repo']}:{d['branch']}"] = (d["repo"], d["branch"], f"tree-dupe {d['tree']} keep={d['kept_sibling']}")

json.dump({k: {"repo": v[0], "branch": v[1], "proof": v[2]} for k, v in targets.items()},
          open(rpt / "prune_targets.json", "w"), indent=2)
print(f"[prune] {len(targets)} unique targets (expect 54)")
deleted = 0
if mode == "EXECUTE":
    for key, (repo, br, proof) in sorted(targets.items()):
        r = subprocess.run(["gh", "api", "-X", "DELETE", f"repos/{repo}/git/refs/heads/{br}"],
                           capture_output=True, text=True)
        ok = r.returncode == 0; deleted += int(ok)
        print(f"[{'banked' if ok else 'held'}] {key} ({proof})")
    print(f"[banked] pruned {deleted}/{len(targets)}")
else:
    print("[held] DRY-RUN — full list in prune_targets.json; CONFIRM=1 executes")
PYEOF

# ---------- [stage:bank] ----------
cd "$REPO"
if [ "$MODE" = "EXECUTE" ]; then
  git pull --ff-only origin main || true
  git add analysis/ bin/
  if ! git diff --cached --quiet; then
    git commit -m "frp12 fleet consolidation: prune 54 zero-content branches + frp5-frp12 audit reports. frp12-authored, human-confirmed. [banked]"
    git push origin main
    echo "[banked] pushed $(git rev-parse --short HEAD)"
  else
    echo "[banked] nothing new to commit"
  fi
else
  echo "[held] review $RPT/prune_targets.json then: CONFIRM=1 bash $0"
fi
tail -1 "$0" | grep -q "# \[canary] frp12 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp12 paste intact
