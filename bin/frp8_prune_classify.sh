#!/usr/bin/env bash
# frp8_prune_classify.sh — branch containment classifier from frp7 triage
# CONTAINED (ahead_by=0) = safe-prune candidate | STALE-UNMERGED (>45d, ahead) | ACTIVE (recent, ahead)
# Dry-run default. CONFIRM=1 deletes CONTAINED branches only, per-branch, logged.
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
GH_USER=jesseray718
TS=$(date +%Y%m%d_%H%M%S)
RPT=$REPO/analysis/frp8_${TS}
mkdir -p "$RPT"
TRIAGE=$(ls -t "$REPO"/analysis/frp7_*/triage.json 2>/dev/null | head -1)
[ -z "$TRIAGE" ] && { echo "[gate] no frp7 triage.json — run frp7 first"; exit 1; }
echo "[frp8] $TS — mode: $([ "${CONFIRM:-0}" = "1" ] && echo EXECUTE-PRUNE || echo DRY-RUN)"

python3 - "$TRIAGE" "$RPT" "$GH_USER" "${CONFIRM:-0}" <<'PYEOF'
import json, subprocess, sys, pathlib, datetime, time
triage = json.load(open(sys.argv[1])); rpt = pathlib.Path(sys.argv[2])
USER = sys.argv[3]; EXECUTE = sys.argv[4] == "1"
now = datetime.datetime.now(datetime.timezone.utc)

def gh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0: return {}
    try: return json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return {}

buckets = {"CONTAINED": [], "STALE-UNMERGED": [], "ACTIVE": [], "ERROR": []}
for name, rec in triage["owned_branches"].items():
    base = rec["default"]
    for b in rec["branches"]:
        br = b["branch"]
        cmp_ = gh("gh", "api", f"repos/{USER}/{name}/compare/{base}...{br}")
        if "ahead_by" not in cmp_:
            buckets["ERROR"].append({"repo": name, "branch": br}); continue
        entry = {"repo": name, "branch": br, "ahead": cmp_["ahead_by"],
                 "behind": cmp_["behind_by"], "last_commit": b.get("last_commit"),
                 "subject": b.get("subject"), "url": cmp_.get("html_url")}
        if cmp_["ahead_by"] == 0:
            buckets["CONTAINED"].append(entry)
        else:
            try:
                age = (now - datetime.datetime.fromisoformat(b["last_commit"].replace("Z","+00:00"))).days
            except Exception:
                age = -1
            entry["age_days"] = age
            buckets["STALE-UNMERGED" if age > 45 else "ACTIVE"].append(entry)

plan = {k: v for k, v in buckets.items()}
json.dump(plan, open(rpt / "prune_plan.json", "w"), indent=2)

print(f"[classify] CONTAINED={len(buckets['CONTAINED'])} STALE-UNMERGED={len(buckets['STALE-UNMERGED'])} "
      f"ACTIVE={len(buckets['ACTIVE'])} ERROR={len(buckets['ERROR'])}")
by_repo = {}
for e in buckets["CONTAINED"]: by_repo[e["repo"]] = by_repo.get(e["repo"], 0) + 1
print("[contained-by-repo] " + json.dumps(by_repo))
st = sorted(buckets["STALE-UNMERGED"], key=lambda e: e.get("age_days") or 999, reverse=True)[:10]
for e in st:
    print(f"[stale-top10] {e['repo']}:{e['branch']} ahead={e['ahead']} age={e.get('age_days')}d '{e['subject'][:50]}'")

deleted = 0
if EXECUTE:
    for e in buckets["CONTAINED"]:
        r = subprocess.run(["gh", "api", "-X", "DELETE",
                            f"repos/{USER}/{e['repo']}/git/refs/heads/{e['branch']}"],
                           capture_output=True, text=True)
        ok = r.returncode == 0
        deleted += int(ok)
        print(f"[{'banked' if ok else 'held'}] delete {e['repo']}:{e['branch']}")
    print(f"[banked] pruned {deleted}/{len(buckets['CONTAINED'])} contained branches")
else:
    print(f"[held] DRY-RUN — {len(buckets['CONTAINED'])} contained branches proposed for deletion")
    print(f"[held] review: {rpt}/prune_plan.json; re-run CONFIRM=1 to execute")
PYEOF

tail -1 "$0" | grep -q "# \[canary\] frp8 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp8 paste intact
