# Shell Scripts Inventory

**Generated:** 2026-09-21T22:40:08Z

## OptiPlex (Ubuntu)
| Script | Purpose | Canary |
|--------|---------|--------|
| `bin/stack_gate.sh v2` | Script validation | `STACK_GATE_V2` |
| `bin/agent.sh` | Model routing | `AGENT_MODEL` |
| `bin/onepass_v3.sh` | Weekly automation | `ONEPASS_V3` |
| `bin/push_guard_v2.sh` | Pre-push checks | `PUSH_GUARD_V2` |
| `bin/setup_restore_v1.sh` | GOALS.md rebuild | `SAFE` |

## Mobile (Termux/Android)
| Script | Location | Purpose |
|--------|----------|---------|
| `run_cycle.sh` | `/sdcard/openroot/` | Cycle counter |
| `run_core.sh` | `/sdcard/openroot/bin/` | Core launcher |
| `clip_send.sh` | `/sdcard/openroot/` | Clipboard buffer |
| `clip_read.sh` | `/sdcard/openroot/` | Clipboard reader |
| `hive.sh` | `/data/data/.../bin/` | Lattice query |
| `h003_ledger.sh` | `/sdcard/openroot/` | Thermal calc |
| `acre_ledger.sh` | `~/projects/openroot/` | Ledger init |
| `aegfrc_mix.sh` | `/sdcard/openroot/` | AE-GFRC mix |

**Status:** 50% have canary markers. Standardize needed.
