# OpenRoot / Agape Copilot Instructions (IMFUSE)
# Official recommended structure from GitHub Copilot CLI best practices

## Core Law
- η = useful_joules / human_joules is the only performance language
- R=1.0 makes coordination cost zero
- Love keeps no record of wrongdoing
- Metadata is open source asset, never commodity
- Serve the lowest node first
- Absolute paths only. Never use tilde

## Build / Validate
- python3 /data/data/com.termux/files/home/openroot/openroot_workflow_manager.py --validate
- python3 /data/data/com.termux/files/home/openroot/openroot_workflow_manager.py --priority ALL
- rish -c 'whoami'

## Code Style
- Absolute paths under /data/data/com.termux/files/home/ or /sdcard/openroot/
- Prefer stdlib Python
- Log η and Merkle on every task
- No assumed numbers / Saxton tokens
- DNA kernel never leaves air-gapped device

## Recommended Workflow (GitHub Copilot CLI)
1. Explore — Read files. Do not write code yet.
2. Plan — /plan <task>. Review plan.md
3. Implement — Only after plan approval
4. Verify — workflow_manager --validate
5. Commit — message contains η / R=1.0 / lowest-node intent

## When to use /plan
- Multi-file changes, refactoring, new axioms, mesh features
- Never for single-line fixes

## Architecture
- A15 = GOVERNOR-01 hub
- OptiPlex = heavy spoke (llama-server)
- Syncthing reaches poorest node without internet
- .coderabbit.yaml = nervous system
