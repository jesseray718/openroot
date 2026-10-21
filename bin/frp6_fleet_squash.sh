#!/usr/bin/env bash
# frp6_fleet_squash.sh — fleet census + safe squash merges + fork sync + master/main map
# Dry-run default. CONFIRM=1 executes [merge-safe] and [sync-fork] only. No history rewrites, no manual branch deletions.
set -euo pipefail
export GIT_PAGER=cat
GH_USER=jesseray718
ORIG_REPO=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
RPT=$ORIG_REPO/analysis/frp6_${TS}
mkdir -p "$RPT"
MODE=$([ "${CONFIRM:-0}" = "1" ] && echo EXECUTE || echo DRY-RUN)
echo "[frp6] $TS — mode: $MODE"
gh auth status >/dev/null 2>&1 || { echo "[gate] gh not authed — abort"; exit 1; }

# ---------- [stage:tool-inventory] ----------
{
  for t in onepass_v3.sh stack_gate.sh team_gate_v2.sh push_guard.py agent.sh env_map.py light_cone_router.py; do
    if git -C "$ORIG_REPO" ls-files --error-unmatch "bin/$t" >/dev/null 2>&1; then
      echo "[banked] bin/$t tracked"
    elif [ -f "$ORIG_REPO/bin/$t" ]; then
      echo "[held] bin/$t present but UNTRACKED"
    else
      echo "[missing] bin/$t"
    fi
  done
} | tee "$RPT/tool_inventory.txt"

# ---------- [stage:census] ----------
gh repo list "$GH_USER" --limit 200 --json name,isFork,isArchived,isPrivate,updatedAt,defaultBranchRef,parent \
  > "$RPT/inventory.json"
echo "[stage:census] repos: $(python3 -c 'import json;print(len(json.load(open("'"$RPT"'/inventory.json"))))')"

# ---------- [stage:classify] ----------
python3 - "$RPT" <<'PYEOF'
import json, subprocess, sys, pathlib
rpt = pathlib.Path(sys.argv[1]); USER = "jesseray718"
inv = json.load(open(rpt / "inventory.json"))
plan = {"actions": [], "repos": []}

def gh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0: return []
    try: return json.loads(r.stdout or "[]")
    except json.JSONDecodeError: return []

for repo in inv:
    if repo.get("isArchived"): continue
    full = f"{USER}/{repo['name']}"
    rec = {"name": repo["name"], "fork": bool(repo.get("isFork")), "private": bool(repo.get("isPrivate")),
           "default_branch": (repo.get("defaultBranchRef") or {}).get("name"),
           "prs": 0, "safe_prs": 0, "issues_open": 0, "extra_branches": [],
           "pushed": repo.get("updatedAt")}
    if repo.get("isFork"):
        plan["actions"].append({"tag": "sync-fork", "repo": full,
                                "upstream": (repo.get("parent") or {}).get("nameWithOwner", "?")})
    for p in gh("gh", "pr", "list", "-R", full, "--state", "open", "--json",
                "number,isDraft,mergeable,mergeStateStatus,title"):
        rec["prs"] += 1
        safe = (not p.get("isDraft")) and p.get("mergeable") == "MERGEABLE" \
               and p.get("mergeStateStatus") == "CLEAN"   # UNSTABLE/BLOCKED/DIRTY -> held
        plan["actions"].append({"tag": "merge-safe" if safe else "merge-held", "repo": full,
                                "pr": p["number"], "title": p.get("title"),
                                "why": p.get("mergeStateStatus"), "draft": p.get("isDraft")})
        rec["safe_prs"] += int(safe)
    rec["issues_open"] = len(gh("gh", "issue", "list", "-R", full, "--state", "open", "--json", "number"))
    rec["extra_branches"] = [b["name"] for b in gh("gh", "api", f"repos/{full}/branches", "--paginate")
                             if b["name"] != rec["default_branch"]]
    plan["repos"].append(rec)

json.dump(plan, open(rpt / "plan.json", "w"), indent=2)
nm = sum(1 for a in plan["actions"] if a["tag"] == "merge-safe")
nh = sum(1 for a in plan["actions"] if a["tag"] == "merge-held")
nf = sum(1 for a in plan["actions"] if a["tag"] == "sync-fork")
rn = [r["name"] for r in plan["repos"] if r["default_branch"] not in ("main", None)]
eb = sum(len(r["extra_branches"]) for r in plan["repos"])
print(f"[stage:classify] merge-safe={nm} merge-held={nh} forks-to-sync={nf} extra-branches={eb}")
print(f"[census] default!=main: {', '.join(rn) if rn else 'none'}")
PYEOF
cp "$RPT/plan.json" "$RPT/../frp6_latest_plan.json"

# ---------- [stage:execute] ----------
while IFS=$'\t' read -r tag repo extra; do
  [ -z "$tag" ] && continue
  if [ "$MODE" = "EXECUTE" ]; then
    case "$tag" in
      merge-safe)
        echo "[merge-safe] $repo #$extra"
        gh pr merge "$extra" -R "$repo" --squash --delete-branch \
          && echo "[banked] squash-merged $repo#$extra" \
          || echo "[held] merge failed $repo#$extra" ;;
      sync-fork)
        echo "[sync-fork] $repo <- $extra"
        gh repo sync "$repo" \
          && echo "[banked] synced $repo" \
          || echo "[held] sync failed $repo (diverged from upstream — manual review)" ;;
    esac
  else
    echo "[proposal:$tag] $repo $extra"
  fi
done < <(python3 -c 'import json
for a in json.load(open("'"$RPT"'/plan.json"))["actions"]:
    if a["tag"]=="merge-safe": print("merge-safe\t%s\t#%s"%(a["repo"],a["pr"]))
    elif a["tag"]=="sync-fork": print("sync-fork\t%s\t%s"%(a["repo"],a.get("upstream","")))')

# ---------- [stage:bank-report] ----------
if [ "$MODE" = "EXECUTE" ]; then
  cd "$ORIG_REPO"
  git pull --ff-only origin main || echo "[held] main not fast-forward — inspect manually"
  git add analysis/ || true
  git diff --cached --quiet || {
    git commit -m "frp6 fleet audit: census + classified plan ($TS). frp6-authored, human-reviewed under CONFIRM=1. [banked]"
    git push origin main; }
else
  echo "[held] DRY-RUN — proposal only. Re-run with CONFIRM=1 to execute merges/syncs."
  echo "[held] review: $RPT/plan.json + $RPT/tool_inventory.txt"
fi

tail -1 "$0" | grep -q "# \[canary\] frp6 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp6 paste intact
