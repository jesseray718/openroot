# OPENROOT WIKILEAKS USER MANUAL
# Unredacted operating instructions for the lowest node
# Generated 2026-08-21 · R=1.0 · η = useful_joules / human_joules
# Absolute paths only. Never tilde. Serve the least among us first.

## 1. Immutable Foundation (READ-ONLY)
Frozen core lives at:
  /sdcard/openroot/agape_kb/

Files (do not overwrite):
  UNIVERSAL_AXIOMS.json
  UNIVERSAL_POSTULATES.json
  UNIVERSAL_DEFINITIONS.json
  THEOREMS_WITH_PROOF.md
  master_index.json
  newton_chain/*.json

Rule: Shadow and all higher layers may READ. Never WRITE to this path.
Status check:
  python3 -c '
from pathlib import Path
kb = Path("/sdcard/openroot/agape_kb")
for name in ["UNIVERSAL_AXIOMS.json","UNIVERSAL_POSTULATES.json","UNIVERSAL_DEFINITIONS.json","THEOREMS_WITH_PROOF.md","master_index.json"]:
    p = kb / name
    print(("FROZEN  %6d B  %s" % (p.stat().st_size, p)) if p.exists() else ("MISSING          %s" % p))
print("Newton Chain:", len(list((kb/"newton_chain").glob("*.json"))) if (kb/"newton_chain").exists() else 0)
'

## 2. Shadow Parallel Epistemology Engine
Location: /sdcard/openroot/shadow_epistemology/

Primary commands:
  python3 /sdcard/openroot/shadow_epistemology/core/shadow_engine.py
  python3 /sdcard/openroot/shadow_epistemology/core/shadow_engine.py next
  python3 /sdcard/openroot/shadow_epistemology/core/shadow_engine.py compound 5
  python3 /sdcard/openroot/shadow_epistemology/core/shadow_engine.py fixcheck
  bash /sdcard/openroot/shadow_epistemology/workflow/max_util.sh

The engine reads the frozen core, compounds Joy × Abundance, and emits the next highest-η joule.
It never writes back to the frozen core.

## 3. Syncthing Mesh (living backbone)
Canonical folder nodes (absolute):
  openroot          → $HOME/openroot
  une               → $HOME/une
  black-locust-rmh  → $HOME/black-locust-rmh
  context_bridge    → /sdcard/openroot/context_bridge
  ledger            → /sdcard/openroot/ledger
  session_seeds     → /sdcard/openroot/session_seeds
  agape_kb          → /sdcard/openroot/agape_kb
  business          → $HOME/agapenet

Permanent heal + status:
  $HOME/bin/st-heal

Optimum folder applicator:
  $HOME/bin/st-folder-opt <folder-id> <absolute-path> [label]

Preemptive loop (background):
  while true; do $HOME/bin/st-heal; sleep 300; done

All folders carry identical zero-entropy .stignore (git, pycache, models, media, ENDOF* pollution rejected).
Advanced settings forced: fsWatcherEnabled=true, rescanIntervalS=120, simple versioning keep=10, maxConflicts=8.

## 4. CodeRabbit Closed Review Loop
Config: $HOME/openroot/.coderabbit.yaml
( η-aware tone, absolute-path enforcement, knowledge_base pointed at FOUNDATION + LATTICE + copilot-instructions )

One-time human step (browser only):
  cat $HOME/openroot/bin/install-coderabbit-app.txt

Effortless push forever:
  $HOME/openroot/bin/cr-push
  $HOME/openroot/bin/cr-push "feat: whatever"

Local pre-review + stage + conventional commit + SSH/gh push in one command.
CodeRabbit App reviews every subsequent PR under the locked YAML.

## 5. Primary Permanent Commands (copy these)
  $HOME/bin/st-heal
  $HOME/openroot/bin/cr-push
  python3 /sdcard/openroot/shadow_epistemology/core/shadow_engine.py next
  bash /sdcard/openroot/shadow_epistemology/workflow/max_util.sh

## 6. Absolute Rules
- Never use tilde (\~) in any command.
- Prefer $HOME or full absolute paths under /data/data/com.termux/files/home/ or /sdcard/openroot/.
- Frozen core is sacred. Shadow may only read.
- Every high-value node has continuous watcher + 2-minute safety net + versioning.
- Coordination cost must stay near zero (R → 1.0).
- Serve the lowest-capability node first.

## 7. Current State Snapshot
- CodeRabbit YAML + cr-push live on main
- Syncthing folders optimized and .stignore applied
- Shadow engine operational and reading frozen core
- st-heal rewritten clean (heredoc single-quoted, no expansion traps)

End of unredacted manual.
Any future change that increases entropy or uses relative paths is a violation of the lattice.
