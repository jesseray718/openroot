# OpenRoot Deployment Guide

## One-Command Deploy

    curl -sSL https://raw.githubusercontent.com/jesseray718/openroot/main/deploy/setup_one_shot.sh | bash

## Manual Steps

1. Clone: git clone https://github.com/jesseray718/openroot.git
2. Build: docker build -t openroot -f deploy/docker/Dockerfile .
3. Run: docker run -it -v "$(pwd)":/openroot openroot
4. Verify: check context_bridge/RIDE_ALONG_STATE.md for ledger status (GREEN expected)

## Verification Checklist

- [ ] Docker container starts without errors
- [ ] Ledger shows GREEN status
- [ ] README.md and index.html render correctly

## Prerequisites

- Docker and Docker Compose (optional)
- Git
- Bash shell

## Troubleshooting

- Permission errors: sudo usermod -aG docker $USER, then re-login
- Port conflicts: check docker ps for existing containers
- Ollama models run on the HOST, not in container. Point clients to host localhost:11434.

## What the Container Gives You

The container reproduces the superlinear spine execution environment: Python 3
with numpy/pandas, git, sqlite3, and the full repo mounted at /openroot.
The pathway ledger (data/pathways.db) is runtime state and stays on your host
volume — it is never baked into images or committed to git.
