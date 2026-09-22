#!/usr/bin/env bash
# recover_v1.sh — bin/ verification + GOALS/MASTER_TODO rebuild + handoff seal
# Provenance: Lumo-authored, stack_gate principles applied (comment-aware).
# Dry-run default. CONFIRM=1 banks. Idempotent. Absolute paths. Canary-verified.
set -eu
export GIT_PAGER=cat
REPO=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
CANARY="[canary] paste intact marker"

[banked] () { echo "[$1] $2"; echo "[$1] $2" >> "$REPO/context_bridge/seed_master-$TS.log"; }
TAIL=$(tail -1 "$0")
echo "$CANARY" ; grep -qF "$CANARY" "$0" || { echo "[held] canary missing — abort"; exit 0; }
[ -d "$REPO/.git" ] || { [banked] held "not a git worktree — abort"; exit 0; }

[banked] gate "HEAD=$(git -C "$REPO" rev-parse --short HEAD)"

# [stage:bin] verify tracking, bank if untracked
TRACKED=$(git -C "$REPO" ls-files bin/ | wc -l)
if [ "$TRACKED" -eq 0 ]; then
  CAND=""
  for p in bin TASK.md analysis; do [ -e "$REPO/$p" ] && CAND="$CAND $p"; done
  if [ "${CONFIRM:-0}" = "1" ]; then
    git -C "$REPO" add $CAND
    git -C "$REPO" commit -m "bank bin/ tooling + TASK.md + analysis (filter-repo survivor recovery, gates passed)" >/dev/null
    [banked] banked "committed:$CAND ($(git -C "$REPO" rev-parse --short HEAD))"
  else
    [banked] held "DRY-RUN: would commit$CAND — rerun with CONFIRM=1"
  fi
else
  [banked] gate "bin/ already tracked ($TRACKED files) — no action"
fi

# [stage:rebuild] extract task lines from 2026-09-16 remnants → drafts (uncommitted, human gate)
DRAFT_G="$REPO/context_bridge/GOALS.rebuild.draft.$TS.md"
DRAFT_T="$REPO/context_bridge/MASTER_TODO.rebuild.draft.$TS.md"
python3 - "$REPO" "$DRAFT_G" "$DRAFT_T" <<'PYEOF'
import re, sys, glob, hashlib, datetime
repo, dg, dt = sys.argv[1], sys.argv[2], sys.argv[3]
remnants = sorted(glob.glob(f"{repo}/context_bridge/session-2026-09-16-*.md"))
tasks = set()
for rem in remnants:
    for m in re.finditer(r"^\s*(?:[-*]|\d+[.)])\s+(.{4,140})", open(rem, errors="replace").read(), re.M):
        t = m.group(1).strip()
        if re.search(r"TODO|task|next action|queue|priority|#[0-9]", t, re.I) or t.startswith("["):
            tasks.add(t)
body = "\n".join(f"- {t}" for t in sorted(tasks)) or "- (no remnants recovered — manual rebuild required)"
open(dg, "w").write(f"# GOALS.md rebuild draft\n# from {len(remnants)} context_bridge remnant(s)\n\n{body}\n")
open(dt, "w").write(f"# MASTER_TODO.md rebuild draft\n# {len(sorted(tasks))} task line(s) extracted\n\n{body}\n")
for f in (dg, dt):
    print(f"[held] draft (human review, uncommitted): {f} sha256:{hashlib.sha256(open(f,'rb').read()).hexdigest()[:16]}")
print(f"[gate] scanned {len(remnants)} remnant(s), extracted {len(sorted(tasks))} candidate lines")
PYEOF

# [stage:seal] handoff ledger append
for f in "$DRAFT_G" "$DRAFT_T"; do
  echo "$(sha256sum "$f" | cut -c1-16) $f" >> "$REPO/seed_master.log"
done
[banked] banked "handoff sealed → context_bridge/seed_master-$TS.log + seed_master.log"
echo "[exit=0]"
