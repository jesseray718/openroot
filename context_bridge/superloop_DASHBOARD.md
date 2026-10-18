# SuperLoop Composite Dashboard — 2026-10-18 08:00 UTC
Auto-pulsed every 15 min via cron | Canary: [SUPERLOOPV3]

## Command Flow Health
- Commands analyzed: 250
- Dominant bucket: `other`
- Top transitions: other->other

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
- Ollama: UP | Models: smollm2:1.7b, qwen2.5-coder:3b, gemma3:1b, granite3.3:2b, qwen3:1.7b, qwen3:0.6b, qwen2.5-coder:1.5b, qwen2.5:1.5b, phi4-router:latest, nomic-embed-text:latest, openroot-instruct:7b, qwen2.5:7b-instruct, phi4-mini:latest, llama3.2:3b, qwen2.5-coder:7b, deepseek-r1:1.5b, llama3.2:1b, openroot-coder:latest, qwen2.5:3b, openroot-assistant:latest
- bot_loop daemon: ALIVE (1 proc)

---
*Dashboard SHA256 prefix: 02d8124d27ab612b*
[exit=0]