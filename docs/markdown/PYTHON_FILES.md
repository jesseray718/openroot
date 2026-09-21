# Python Files Inventory (Active Only)

**Generated:** 2026-09-21T22:40:08Z  
**Focus:** Production scripts (excludes venv, deep archives)

## Core Scripts
| File | Location | Purpose |
|------|----------|---------|
| `openroot_public_readiness.py` | `bin/` | GitHub issue automation |
| `acre_tagger.py` | root | ACRE PoPW claim tagging |
| `rad_cooling.py` | root | Radiative cooling calc |
| `secure_and_commit_v4_*.py` | `bin/` | Git commit helper |
| `efficiency_coefficient.py` | `bin/` | Energy ETA calculator |
| `env_map.py` | `bin/` | Env var mapping |
| `push_guard.py` | `bin/` | Pre-push validation |
| `team_gate_v2.sh` | `bin/` | Multi-model gate |

## Mobile (Termux)
| File | Location | Purpose |
|------|----------|---------|
| `core_atomic.py` | `/sdcard/openroot/bin/` | Atomic function runner |

## Referenced (Verify Existence)
- `nanobot_lattice.py` - Called by `hive.sh`
- `light_cone_router.py` - Router script
- `agape_qa_engine.py` - QA scoring
- `terminal_log_rag.py` - Log indexing
- `doc_compile.py` - Doc consolidation

**Note:** Deep finds return 50k+ files (archives/logs). Focus on `bin/` and root.
