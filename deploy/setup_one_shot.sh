#!/usr/bin/env bash
set -eu
command -v git >/dev/null || { echo "Install git first"; exit 1; }
command -v docker >/dev/null || { echo "Install Docker first"; exit 1; }
cd ~
git clone https://github.com/jesseray718/openroot.git
cd openroot
docker build -t openroot -f deploy/docker/Dockerfile .
docker run -it --rm -v "$(pwd)":/openroot \
  -v "$(pwd)/data":/openroot/data -v "$(pwd)/logs":/openroot/logs openroot
echo "[banked] OpenRoot Superlinear Spine Active"
echo "Next: read context_bridge/RIDE_ALONG_STATE.md"
