#!/usr/bin/env bash
# restore_staging.sh — recover vanished bin scripts INTO A STAGING DIR.
# Never writes to live paths. Review, then install manually.
set -u
M="$HOME/.openroot_gh_audit/mirror-openroot.git"
STAGE="$HOME/openroot/restore_bin_$(date +%Y%m%d-%H%M%S)"
SRC2="$HOME/openroot/reports/reasoning_kernel_audit_20260929T050213Z/sources"
mkdir -p "$STAGE"

NAMES="newton_daemon.py bot_loop_v1.py watchdog_once.py lumo_ingest.py \
superloop_composite_v3.py measure_thermal_v1.py task_dispatch_v1.sh \
ws_auto_sync.sh file_ledger_v2.py file_ledger_parallel_v1.py ecosystem_v2.py \
openroot_rapl_sampler_v1.py openai_relay_9999.py 1349_bottom_tier.py \
a1_core_v1.py handoff_manager.py launch_ladder_v1.py"

for n in $NAMES; do
  c=$(git -C "$M" log --all --format=%H -1 -- "bin/$n" 2>/dev/null)
  if [ -n "$c" ] && git -C "$M" rev-parse -q --verify "$c:bin/$n" >/dev/null 2>&1; then
    git -C "$M" show "$c:bin/$n" > "$STAGE/$n"
    echo "MIRROR   : $n   (as of commit ${c:0:10})"
    continue
  fi
  hit=$(ls "$SRC2" 2>/dev/null | grep -F "${n%.py}" | grep '\.py$' | head -1)
  if [ -n "$hit" ]; then
    cp "$SRC2/$hit" "$STAGE/$n"
    echo "AUDITSRC : $n   (from $hit — Sep 29 vintage)"
    continue
  fi
  echo "MISSING  : $n   (not on remote, not in audit sources)"
done
echo
echo "staging dir: $STAGE   (nothing installed yet)"
