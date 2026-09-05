#!/data/data/com.termux/files/usr/bin/bash
# Absolute paths only. Offline first.
export OPENROOT=/data/data/com.termux/files/home/openroot
export UNE=/data/data/com.termux/files/home/une
mkdir -p $OPENROOT/mesh/chicken-wire/nodes
python3 $OPENROOT/computational_flow/und_gate.py
echo "Spoke ready. R target 1.0. Serve lowest node."
