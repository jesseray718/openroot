#!/usr/bin/env bash
# frp9_tree_dedupe.sh — collapse ACTIVE branches by tree-SHA duplication from frp8 plan.
# Duplicate-tree siblings are prune candidates; newest per tree kept. Duplicates carry ZERO unique work vs sibling.
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
GH_USER=jesseray718
TS=$(date +%Y%m%d_%H%M%S)
RPT=$REPO/analysis/frp9_${TS}
mkdir -p "$RPT"
PLAN=$(ls -t "$REPO"/analysis/frp8_*/prune_plan.json 2>/dev/null | head -1)
[ -z "$PLAN" ] && { echo "[gate] no frp8 prune_plan.json — run frp8 first"; exit 1; }
echo "[frp9] $TS — sourcing $PLAN"

python3 - "$PLAN" "$RPT" "$GH_USER" <<'PYEOF'
import json, subprocess, sys, pathlib, datetime
plan = json.load(open(sys.argv[1])); rpt = pathlib.Path(sys.argv[2]); USER = sys.argv[3]
now = datetime.datetime.now(datetime.timezone.utc)

def gh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0: return None
    return r.stdout.strip()

entries = []
for e in plan.get("ACTIVE", []):
    sha = gh("gh", "api", f"repos/{USER}/{e['repo']}/commits/{e['branch']}",
             "--jq", ".commit.tree.sha")
    if not sha:
        print(f"[error-branch] {e['repo']}:{e['branch']} — tree lookup failed, left alone")
        entries.append({**e, "tree": None}); continue
    try: age = (now - datetime.datetime.fromisoformat(e["last_commit"].replace("Z","+00:00"))).total_seconds()
    except Exception: age = 0
    entries.append({**e, "tree": sha, "_age_sec": age})

groups = {}
for e in entries:
    if e["tree"]: groups.setdefault((e["repo"], e["tree"]), []).append(e)

dupes, singles, kept = [], [], 0
for (repo, tree), members in groups.items():
    members.sort(key=lambda m: -m["_age_sec"])   # newest first
    keeper = members[0]; kept += 1
    for m in members[1:]:
        dupes.append({"repo": m["repo"], "branch": m["branch"], "kept_sibling": keeper["branch"],
                      "tree": tree[:12], "subject": m.get("subject")})
    if len(members) == 1: singles.append(members[0])

out = {"kept_trees": kept, "duplicate_prune_candidates": dupes,
       "unique_active": [ {k: v for k, v in e.items() if k != "_age_sec"} for e in singles ]}
json.dump(out, open(rpt / "dedupe_plan.json", "w"), indent=2)

by_repo = {}
for d in dupes: by_repo[d["repo"]] = by_repo.get(d["repo"], 0) + 1
print(f"[dedupe] trees_kept={kept} duplicate_candidates={len(dupes)} unique_active={len(singles)}")
print("[dupe-by-repo] " + json.dumps(by_repo))
for d in dupes[:15]:
    print(f"[dupe] {d['repo']}:{d['branch']} == tree {d['tree']} (keep {d['kept_sibling']}) '{(d['subject'] or '')[:40]}'")
print(f"[held] review {rpt}/dedupe_plan.json — CONFIRM-gated deletion wired in next pass after you approve")
PYEOF

tail -1 "$0" | grep -q "# \[canary] frp9 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp9 paste intact
