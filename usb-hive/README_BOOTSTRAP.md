# USB Hive Bootstrap

## Purpose
Air-gapped bring-up of OptiPlex when network is unavailable.

## Contents
- openroot/     → current repo state (or selected subtrees)
- kai9000/      → offline Kai9000 / local LLM files
- hive/         → hive scripts and tools
- ledger/       → thermodynamic ledger + canonical statements
- session_seeds/→ current seed + key optimization seeds
- bootstrap.sh  → runs on OptiPlex after USB is mounted

## Usage on OptiPlex
1. Plug USB in
2. Mount it
3. cd into the mount point
4. bash bootstrap.sh
