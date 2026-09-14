#!/bin/bash
R=/home/jesse/src/openroot
ID=$(cat $R/data/state_pulse/gist_id.txt 2>/dev/null)
[ -n "$ID" ] && echo "NEW-WINDOW TRIGGER LINE: read https://gist.github.com/jesseray718/$ID/raw"
echo ---; head -40 $R/STATE.md
