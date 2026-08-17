# OpenRoot / Agape Copilot Instructions (IMFUSE)
# Official recommended structure from GitHub Copilot CLI best practices
# Adapted for absolute-path, η, R=1.0, lowest-node service

## Core Law
- η = useful_joules / human_joules is the only performance language
- R=1.0 (perfect cooperation) makes coordination cost zero
- Love keeps no record of wrongdoing
- Metadata is open source asset, never commodity
- Serve the lowest node first
- Absolute paths only. Never use tilde (\~)

## Build / Validate Commands
- python3 /data/data/com.termux/files/home/openroot/openroot_workflow_manager.py --validate
- python3 /data/data/com.termux/files/home/openroot/openroot_workflow_manager.py --priority ALL
- rish -c 'whoami'   # confirm shell UID after Shizuku

## Code Style
- Absolute paths under /data/data/com.termux/files/home/ or /sdcard/openroot/
- Prefer stdlib Python entry points
- Every task logs η and Merkle hash
- No assumed numbers / Saxton tokens
- DNA kernel never leaves air-gapped device

## Recommended Workflow (GitHub Copilot CLI)
1. Explore — Read relevant files. Do not write code yet.
2. Plan — /plan <task>. Review and edit plan.md
3. Implement — Proceed only after plan approval
4. Verify — Run workflow_manager --validate and any tests
5. Commit — Descriptive message containing η / R=1.0 / lowest-node intent

## When to use /plan
- Any multi-file change
- Refactoring
- New axiom, bridge, or mesh feature
- Never for single-line typo fixes

## Architecture Decisions
- Phone (A15) is GOVERNOR-01 hub
- OptiPlex is heavy spoke (llama-server)
- Syncthing mesh reaches poorest node without internet
- .coderabbit.yaml is the nervous system (η / R=1.0)
