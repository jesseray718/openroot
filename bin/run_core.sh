#!/bin/bash
# Quick runner for core_atomic.py
# Usage: ./run_core.sh f1 jesse "Lead_Architect"

SCRIPT="/sdcard/openroot/bin/core_atomic.py"
if [ ! -f "$SCRIPT" ]; then
    echo "Error: core_atomic.py not found at $SCRIPT"
    exit 1
fi

python3 "$SCRIPT" "$@"
