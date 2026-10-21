#!/usr/bin/env bash
# frp7_triage.sh — surface held-PR detail, owned-vs-fork branches, prune candidates, bin/ manifest
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
GH_USER=jesseray718
TS=$(date +%Y%m%d_%H%M%S)
RPT=$REPO/analysis/frp7_${TS}
mkdir -p "$RPT"
PLAN=$(ls -t "$REPO"/analysis/frp6_*/plan.json 2>/dev/null | head -1)
[ -z "$PLAN" ] && { echo "[gate] no frp6 plan.json found — run frp6 first"; exit 1; }
echo "[frp7] $TS — sourcing $PLAN"

# ---------- [stage:bin-manifest] ----------
echo "== tracked in bin/ ==" > "$RPT/bin_manifest.txt"
git -C "$REPO" ls-files bin/ | sort >> "$RPT/bin_manifest.txt"
echo "== on disk but untracked ==" >> "$RPT/bin_manifest.txt"
comm -13 <(git -C "$REPO" ls-files bin/ | sort) <(ls "$REPO/bin/" | sed 's|^|bin/|' | sort) \
  >> "$RPT/bin_manifest.txt" || true
echo "[stage:bin-manifest] $(wc -l < "$RPT/bin_manifest.txt") lines -> bin_manifest.txt"

# ---------- [stage:pr-triage] ----------
python3 - "$PLAN" "$RPT" <<'PYEOF'
import json, subprocess, sys, pathlib
plan = json.load(open(sys.argv[1])); rpt = pathlib.Path(sys.argv[2]); USER = "jesseray718"
fork_names = {a["repo"].split("/")[-1] for a in plan["actions"] if a["tag"] == "sync-fork"}

def gh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0: return {}
    try: return json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return {}

out = {"held_prs": [], "owned_branches": {}, "fork_branch_counts": {}, "prune_candidates": []}
for a in plan["actions"]:
    if a["tag"] != "merge-held": continue
    repo, num = a["repo"], str(a["pr"])
    det = gh("gh", "pr", "view", num, "-R", repo, "--json",
             "number,title,state,isDraft,mergeable,mergeStateStatus,body,author,createdAt,files")
    det["why_held"] = a.get("why"); det["draft"] = a.get("draft")
    out["held_prs"].append(det)
    print(f"[pr-triage] #{det.get('number')} {repo}: {det.get('mergeStateStatus')} "
          f"draft={det.get('isDraft')} '{(det.get('title') or '')[:60]}'")

for rec in plan["repos"]:
    name = rec["name"]
    if name in fork_names:
        out["fork_branch_counts"][name] = len(rec["extra_branches"])
        continue
    if not rec["extra_branches"]:
        continue
    branches = []
    for b in rec["extra_branches"]:
        info = gh("gh", "api", f"repos/{USER}/{name}/commits/{b}", "--jq",
                  "{sha: .sha, date: .commit.committer.date, msg: (.commit.message | split(\"\\n\")[0])}")
        branches.append({"branch": b, "sha": info.get("sha"), "last_commit": info.get("date"),
                         "subject": info.get("msg")})
    out["owned_branches"][name] = {"default": rec["default_branch"], "branches": branches}
    for b in branches:
        print(f"[owned-branch] {name}:{b['branch']} last={b['last_commit']} '{b['subject']}'")

json.dump(out, open(rpt / "triage.json", "w"), indent=2)
print(f"[stage:pr-triage] fork branches (leave alone): {sum(out['fork_branch_counts'].values())}")
print(f"[stage:pr-triage] owned repos with extra branches: {len(out['owned_branches'])}")
PYEOF

# ---------- [stage:report] ----------
echo "[held] review: $RPT/triage.json + $RPT/bin_manifest.txt"
echo "[held] NO mutations performed — triage only"
tail -1 "$0" | grep -q "# \[canary\] frp7 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp7 paste intact
