# OpenRoot — Copilot Instructions

## Environment
Developer is on a Samsung Galaxy A15 (Android, no root) using Termux as the primary terminal. No GUI IDE — everything is CLI or browser. Scripts must be paste-ready bash blocks requiring zero manual editing. Voice transcription artifacts are common in prompts — parse intent, never correct spelling aloud.

## Key Paths
- Repo: $HOME/projects/openroot/
- Scripts: $HOME/projects/openroot/bin/
- Research: $HOME/projects/openroot/research/
- Docs: $HOME/projects/openroot/docs/fractal-convergence/
- Firmware: $HOME/projects/openroot/firmware/
- Local models: $HOME/models/
- Clipboard pipe: `termux-clipboard-set` for cross-app transfer

## Tech Stack
- Python 3 (argparse, subcommands, no heavy deps — phone has limited storage)
- Bash scripts in $HOME/bin/ (Termux-compatible shebang: #!/data/data/com.termux/files/usr/bin/bash)
- Solana/Anchor (Rust) for ACRE smart contract
- ESP32 + SX1262 LoRa for mesh nodes (Arduino C++)
- llama.cpp for local LLMs (Qwen2.5 1.5B, GGUF q4_k_m)
- aiq CLI for multi-provider cloud AI (Groq, Google, Cerebras, OpenRouter, GitHub Models, Mistral)

## Code Style Rules
- Dense output, minimal comments — code speaks for itself
- Bash: use heredocs for file creation, avoid sed/ed (syntax errors on Termux)
- Python: stdlib-first, avoid pip installs unless necessary
- No /tmp paths — Termux restricts /tmp, use $TMPDIR or $HOME/tmp/
- All file writes use $HOME/ paths (never bare ~ or \\~)
- Git: merge strategy (not rebase), push origin main
- Output piped to `termux-clipboard-set` when useful

## Project Context
OpenRoot is a decentralized permaculture technology framework combining:
- Thermal cascade system (H-003): volumetric blackbody concrete solar panels → underground labyrinth → insulated battery storage → Stirling/TEG discharge
- AE-GFRC: aerated glass fiber reinforced concrete with zirconium substitution + xanthan gum stabilizer
- ACRE token: Solana Anchor contract, PoPW (proof of productive work), 1 ACRE per 1000 joules verified
- Vesica Piscis mesh: ESP32+LoRa nodes in Flower of Life topology, local LoRa + IPFS backhaul
- UNE: Universal Nomenclature Engine (36-symbol base, exponential layers)
- Agape: cooperative engineering principle integrating UNE, Kingdom Engine, ACRE

## Conventions
- UNE designations: DV.GEN.TH.AE01, DV.MSH.VP.ND01, etc.
- Hypothesis tracking: H-001 through H-006+ with formal null/scale hypotheses
- Axioms: AX-001 through AX-039+
- Copyright: One Human Family (humanity collectively)
- License: CC-BY-SA 4.0 (docs) / GPL v3 (code)
- Defensive publication strategy — no patents, all open-source

## Efficiency Rules
- Maximum output per minimum input — anticipate next steps
- Generate complete terminal blocks, not fragments
- When fixing errors: return only the fix + one-line explanation
- Execute full chains without asking "do you want me to also..."
- If uncertain, attempt and report results rather than stalling

## H-003 Tools
bin/h003_ledger.sh [area_m2]
- Nightly/7n thermal cascade (12.91 kWh/m²) → ACRE (1 ACRE = 1000 J PoPW)
- Output: H-003|area=Xm2|nightly=YkWh|7n=ZkWh|ACRE=W
- Theoretical until physical test

bin/h003_log.sh [area_m2]
- Runs ledger + ISO8601 timestamp → research/h003_ledger.log
- Auto termux-clipboard-set of line
- Daily/iterative H-003 validation + PoPW trail
