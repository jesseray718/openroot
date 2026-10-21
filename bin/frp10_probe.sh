#!/usr/bin/env bash
# frp10_probe.sh — failed-check detail for 5 held PRs + default-branch truth map for 12 non-main repos
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
GH_USER=jesseray718
TS=$(date +%Y%m%d_%H%M%S)
RPT=$REPO/analysis/frp10_${TS}
mkdir -p "$RPT"
PLAN=$(ls -t "$REPO"/analysis/frp6_*/plan.json 2>/dev/null | head -1)
[ -z "$PLAN" ] && { echo "[gate] no frp6 plan.json — run frp6 first"; exit 1; }
echo "[frp10] $TS — probe only, zero mutations"

# ---------- [stage:pr-checks] ----------
{
  for spec in "OpenCell-Thermal-System 18" "OpenCell-Thermal-System 16" \
              "OpenCell-Thermal-System 15" "OpenCell-Thermal-System 12" \
              "openroot-thesis 5"; do
    set -- $spec
    echo "== $1 PR#$2 =="
    gh pr view "$2" -R "$GH_USER/$1" --json title,author,mergeable,mergeStateStatus,statusCheckRollup \
      --template '{{.title}} | {{.author.login}} | {{.mergeStateStatus}}{{range .statusCheckRollup}}
  {{.name}}: {{.conclusion}}{{end}}' || echo "(pr view failed)"
  done
} | tee "$RPT/pr_checks.txt"

# ---------- [stage:default-map] ----------
python3 - "$PLAN" "$GH_USER" <<'PYEOF' | tee /dev/stderr > "$RPT/default_map.txt"
import json, subprocess, sys
plan = json.load(open(sys.argv[1])); USER = sys.argv[2]
def gh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None

non_main = [r for r in plan["repos"] if r["default_branch"] not in ("main", None)]
print(f"[default-map] {len(non_main)} repos with non-main default:")
for r in non_main:
    full = f"{USER}/{r['name']}"
    has_main = any(b == "main" for b in r["extra_branches"])
    def_date = gh("gh", "api", f"repos/{full}/commits/{r['default_branch']}", "--jq", ".commit.committer.date")
    main_date = gh("gh", "api", f"repos/{full}/commits/main", "--jq", ".commit.committer.date") if has_main else None
    verdict = ("RETARGET main->default (main newer)" if main_date and def_date and main_date > def_date
               else "main stale vs default — keep default" if main_date and def_date
               else "no main branch exists")
    print(f"  {r['name']}: default='{r['default_branch']}'({def_date}) main={main_date or 'absent'} => {verdict}")
PYEOF

echo "[held] review: $RPT/pr_checks.txt + $RPT/default_map.txt"
tail -1 "$0" | grep -q "# \[canary\] frp10 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp10 paste intact
