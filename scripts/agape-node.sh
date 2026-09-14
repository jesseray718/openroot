#!/data/data/com.termux/files/usr/bin/bash
set -e
cd /sdcard/openroot
python src/nodes/agape-node/agape_node.py "$@"
