#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# superloop_census_v3p3.sh — evidence census of CLEAN 'other' rows (noise excluded)
# Canary: [SUPERLOOPV3P3]
set -euo pipefail
OR=/home/jesse/openroot

cat > "$OR/bin/superloop_other_census.py" <<'PYEOF'
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Census of clean (non-noise) 'other' commands — final evidence for bucket regexes."""
import json
from collections import Counter
from pathlib import Path

CMDLOG = Path("/home/jesse/openroot/data/superloop_commands.jsonl")

others = []
if CMDLOG.exists():
    for ln in CMDLOG.read_text(errors="replace").splitlines():
        try:
            e = json.loads(ln)
        except Exception:
            continue
        if e.get("bucket") == "other" and not e.get("noise"):
            others.append(e["cmd"])

counts = Counter(others)
print("[CENSUS] clean 'other' rows: %d, unique: %d" % (len(others), len(counts)))
print("[CENSUS] ---- top 40 by frequency ----")
for cmd, n in counts.most_common(40):
    print("  %3dx  %s" % (n, cmd[:150]))

# Also classify by first token, so patterns jump out even past line 40
firsts = Counter(cmd.split()[0] if cmd.split() else "<empty>" for cmd in others)
print("[CENSUS] ---- first-token histogram ----")
for tok, n in firsts.most_common(25):
    print("  %4dx  %s" % (n, tok))

# Heuristic verdict: how many clean others start with a known shell builtin?
builtins_ = {"echo","export","source","alias","grep","sudo","apt","pkg","pip","pip3",
             "chmod","chown","tar","zip","unzip","nano","vi","vim","less","which",
             "whoami","date","sleep","true","false","clear","history","man","touch"}
bi = sum(n for tok, n in firsts.items() if tok in builtins_)
print("[CENSUS] first-token shell-builtins: %d / %d (%.0f%%)" % (bi, len(others), 100*bi/max(len(others),1)))
print("[CENSUS] rest = terminal OUTPUT lines captured by tmux heuristic (need prompt-anchored capture)")
print("[exit=0]")
PYEOF

python3 -m py_compile "$OR/bin/superloop_other_census.py" && echo "[gate:py_compile] PASS"
python3 "$OR/bin/superloop_other_census.py"
