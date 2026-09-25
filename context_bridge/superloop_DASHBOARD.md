# SuperLoop Composite Dashboard — 2026-09-25 11:00 UTC
Auto-pulsed every 15 min via cron | Canary: [SUPERLOOPV3]

## Command Flow Health
- Commands analyzed: 250
- Dominant bucket: `other`
- Top transitions: other->other, other->system, system->other, exec->other, other->author

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
| other | lumo | max |

## Drift Detection
- Status: ALERTS
- 'other' ratio alert threshold: 50%
- [intent_unclear] over half of commands are 'other' — buckets need refinement

## Live Stack State
- Ollama: UP | Models: deepseek-r1:1.5b, llama3.2:1b, openroot-coder:latest, qwen2.5:3b, nomic-embed-text:latest, qwen2.5-coder:7b, openroot-assistant:latest
- bot_loop daemon: ALIVE (1 proc)

---
*Dashboard SHA256 prefix: 02d8124d27ab612b*
[exit=0]