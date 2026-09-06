# Nanobot Swarm Toolkit — kai9000 + Termux

**Path:** `docs/kai9000/NANOBOT-SWARM-TOOLKIT.md`
**License:** CC-BY-SA 4.0 (docs) | GPL v3 (code)
**Author:** Jesse Ray (jesseray718)

## Concept

Small, single-purpose AI-powered shell scripts that chain together into swarms — Unix "small tools that compose," applied to a phone. Each nanobot does one thing (transcribe, diagnose, publish, route) and takes input/output via clipboard, so any nanobot can feed any other. `swarm` is the meta-bot: it listens to a spoken intent and dispatches to the right nanobot(s).

kai9000 (Alpine Linux sandbox, real `apk` package management) is the heavy-compute node; Termux is the orchestrator handling mic/clipboard/TTS/Android integration. The optimal split: Termux drives, kai9000 crunches.

## kai9000 Bridge Setup

Run inside the kai9000 Alpine shell to stand up a local inference bridge Termux can call over HTTP:

```bash
# Inside kai9000 Alpine sandbox
apk update && apk add curl jq python3 py3-pip openssh git

# Install Groq CLI
pip install groq --break-system-packages

# Shared config (synced via Syncthing or shared storage)
mkdir -p ~/.config/aiq
# copy API keys over from Termux

# Lightweight bridge server
pip install flask --break-system-packages

cat > ~/bridge.py << 'PY'
from flask import Flask, request, jsonify
import subprocess, json
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data.get('prompt','')
    provider = data.get('provider','groq')
    model = data.get('model','llama-3.3-70b-versatile')
    result = subprocess.run(
        ['python3', '-c', f"""
import groq, os, sys
c = groq.Groq(api_key=os.environ.get('GROQ_API_KEY'))
r = c.chat.completions.create(
    model='{model}',
    messages=[{{'role':'user','content':''' + repr(prompt) + '''}}]
)
print(r.choices[0].message.content)
"""],
        capture_output=True, text=True
    )
    return jsonify({'response': result.stdout.strip()})

@app.route('/health')
def health():
    return jsonify({'status':'alive'})

app.run(host='0.0.0.0', port=9999, debug=False)
PY

python3 ~/bridge.py &
```

From Termux:

```bash
curl -s http://localhost:9999/health
```

## The 10 Nanobots

Ranked by daily impact. `vs` and `vai` already exist on-device; the remaining eight are checked into `bin/` in this repo (see table).

| # | Bot | What | Repo path |
|---|-----|------|-----------|
| 1 | `vs` | Speak → Groq Whisper → clipboard | on-device (Termux), not yet checked in |
| 2 | `vai` | Speak → Groq Whisper → LLM → clipboard + TTS | on-device (Termux), not yet checked in |
| 3 | `git-fix` | Diagnoses and repairs common git issues (missing upstream, diverged branches) | [`bin/git-fix`](../../bin/git-fix) |
| 4 | `deepdive` | Scans a directory → tree + file inventory + word freq → clipboard | [`bin/deepdive`](../../bin/deepdive) |
| 5 | `publish` | One command: GitHub tag+push, IPFS pin, Zenodo queue | [`bin/publish`](../../bin/publish) |
| 6 | `une-scribe` | Voice → transcript → saved as a UNE-named markdown doc | [`bin/une-scribe`](../../bin/une-scribe) |
| 7 | `fix-it` | Clipboard error → AI diagnosis → fix command in clipboard | [`bin/fix-it`](../../bin/fix-it) |
| 8 | `ctx-bridge` | Generates a session-handoff summary for a new chat window | [`bin/ctx-bridge`](../../bin/ctx-bridge) |
| 9 | `therm-calc` | Voice → thermal-cascade physics calculation → clipboard + TTS | [`bin/therm-calc`](../../bin/therm-calc) |
| 10 | `swarm` | Voice intent → routes to the matching nanobot(s) | [`bin/swarm`](../../bin/swarm) |

All scripts assume a Termux environment (`#!/data/data/com.termux/files/usr/bin/bash`), the `aiq` multi-provider CLI, and `GROQ_API_KEY` sourced from `~/.config/aiq/config.sh`. Install to `~/bin` on-device and `chmod +x`.

### How they swarm together

```
              ┌─────────┐
   YOU ──→   │ swarm   │ ← voice router, picks the right bot(s)
              └────┬────┘
                   │
     ┌─────┬───────┼───────┬──────┬────────┐
     ▼     ▼       ▼       ▼      ▼        ▼
  vs    vai   deepdive  publish git-fix  therm-calc
  │      │       │       │       │         │
  └──┐   │       │       │       │         │
     ▼   │       │       │       │         ▼
  une-scribe    fix-it   IPFS   GitHub   clipboard
     │           │       │       │
     ▼           ▼       ▼       ▼
 ~/docs/une  clipboard  Zenodo  GitHub
```

Chained example: say "swarm", then "audit openroot and publish everything" → detects both keywords → runs `deepdive` → runs `publish` → repo scanned, tagged, pushed to GitHub + IPFS + Zenodo in one flow.

Solo examples:

```
vs 10                          # talk → text in clipboard
vai 10                         # talk → AI answers aloud + clipboard
git-fix                        # heals git state
deepdive ~/projects/openroot   # full audit in clipboard
publish ~/projects/openroot    # blasts everywhere
une-scribe AX.KNW.SYS          # speak axiom → saved as markdown
fix-it                         # paste error → get fix in clipboard
ctx-bridge                     # session handoff for new chat window
therm-calc 20                  # speak thermal question → get calculation
swarm                          # speak intent → routes to correct bot(s)
```

## Ten Capability Upgrades (non-nanobot)

Not scripts — infrastructure moves that raise the ceiling on the whole stack:

1. Build `whisper.cpp` locally — offline voice transcription when WiFi drops
2. Wire kai9000 as a persistent compute daemon — models survive Termux restarts
3. Auto-publish on git tag — GitHub Actions triggers IPFS+Zenodo upload on tag push
4. Configure FUTO Voice Input continuous mode — hands-free dictation in any app
5. Syncthing sync between Termux `~/projects` and kai9000 — shared workspace across sandboxes
6. Termux widget per nanobot — one-tap home-screen icons for `vs`, `vai`, `swarm`
7. Proton Pass CLI — auto-fill API keys across Termux/kai9000/Alpine sessions
8. Local RAG index of all OpenRoot docs — `or-rag` + `nomic-embed` feeding `vai` queries
9. Persistent lumo-bridge daemon — clipboard → LLM → clipboard without app switching
10. Cron-like scheduler in Termux (`crond` / `termux-job-scheduler`) — automated deepdives, backups, periodic publishes
