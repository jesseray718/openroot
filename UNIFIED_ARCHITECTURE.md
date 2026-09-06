# UNIFIED_ARCHITECTURE.md
## OpenRoot + UNE + Aerocement — Core Unified Project

**Version:** 1.1  
**Author:** Jesse Ray McMillen (OpenRoot)  
**License:** Documentation CC-BY-SA 4.0 | Code GPL v3  

## Executive Summary

Three repositories form one coherent system:

| Repository          | Role                     | Function                                      |
|---------------------|--------------------------|-----------------------------------------------|
| openroot            | Physical infrastructure  | Credit → Property → Energy → Food stack       |
| une                 | Computational substrate  | Thermodynamic ledgers, η tracking, Agape      |
| black-locust-rmh    | Living systems           | Black Locust permaculture + thermal cascade   |

Every dollar routed correctly becomes credit-building.  
Every concrete panel captures sunlight while serving as structure.  
Every computation tracks useful joules vs human joules (η).  
Every node serves the lowest node first. R=1.0 is the only coordination state that scales.

## Layer Stack (Bottom → Top)

1. Hardware (A15 + OptiPlex + future thin clients)
2. Syncthing mesh (folder nodes)
3. Session state + context_bridge
4. Knowledge Compression Engine + Agape Oracle
5. or-* CLI control plane
6. Physical PoPW / Aerocement / RMH

## Canonical Paths (never tilde)

- $HOME/openroot
- $HOME/une/computational_flow
- $HOME/black-locust-rmh
- /sdcard/openroot/context_bridge
- /sdcard/openroot/ledger
- /sdcard/openroot/session_seeds
- /sdcard/openroot/agape_kb
- $HOME/bin/or-*

## Daily η loop

or-status → or-sync → or-learn / or-oracle → physical action → ledger write
