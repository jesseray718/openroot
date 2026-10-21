# JSON Configuration Files

**Generated:** 2026-09-21T22:40:08Z

## Active Configs
| File | Purpose | Status |
|------|---------|--------|
| `une/code_registry.jsonl` | H-003 UNE axioms | Dynamic load |
| `data/env_map.json` | Env variables | Generated |
| `analysis/grle_weights.json` | GRLE scoring | Verified |
| `agape_setup_config.json` | Setup template | Markor |
| `context_bridge/*.json` | Session seeds | Rotating |

## Ledgers (Blockchain)
| File | Type | Genesis |
|------|------|---------|
| `acre/LEDGER.jsonl` | ACRE PoPW | `1bba5f46...` |
| `h003_ledger.log` | Thermal CSV | `2026-07-02` |

## Runtime DBs (GitIgnored)
- `data/team_gate.db`
- `data/repo_drift.db`
- `data/canonical_index.db`

**Action:** Verify `.gitignore` excludes `*.db`
