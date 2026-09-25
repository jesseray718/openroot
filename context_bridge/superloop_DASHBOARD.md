# SuperLoop — PROMPT-ANCHORED (v3p4)
**Canary:** [SUPERLOOPV3P4] | Auto-pulsed every 15 min via cron

## Command Classification Health
- Commands analyzed: 250
- Dominant bucket: `other`
- Clean 'other' ratio: **TARGET <20%** (current depends on sample size)

## Routing Weights (Auto-Learned)
| Trigger | Route | Model |
|---------|-------|-------|
| bridge | smart_router | 7b |
| gitops | smart_router | 7b |
| model | qwen2.5-coder:7b | 7b |
| author | 7b | 7b |
| exec | 3b | 3b |
| gate | team_gate | 3b |
| system | local_shell | none |
| net | smart_router | 7b |
| files | local_shell | none |
| nav | local_shell | none |
| vars | local_shell | none |
| builtin | local_shell | none |
| other | lumo | max |

---
*Dashboard SHA256 prefix: 02d8124d27ab612b*
[exit=0]