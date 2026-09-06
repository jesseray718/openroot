#!/bin/bash
# SSH / OptiPlex only.
set -eu
case "$(pwd)" in
  /data/data/com.termux*|/storage/emulated*|/sdcard*) echo "REFUSE: A15 pane."; exit 2 ;;
esac
ROOT=/home/jesse/openroot
KIT=$ROOT/kit
MODELS=/home/jesse/models
mkdir -p "$KIT/bin" "$KIT/sql" "$KIT/data" "$KIT/docs" "$KIT/manual" "$MODELS"
echo "SSH kit root $KIT"
python3 "$KIT/bin/kit_init.py"
python3 "$KIT/bin/rounds_sim.py"
python3 "$KIT/bin/tidbit.py" module coder
echo "MODELS dir $MODELS"
ls -lh "$MODELS" || true
echo "NEXT: start llama-server on a real GGUF from that listing"
echo "NEXT: curl -s http://127.0.0.1:8080/v1/models"
