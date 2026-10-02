#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# superloop_patch_v3p2.sh — filter code-line noise from recall, add cd/var buckets,
#                            re-classify existing log, verify gist publish end-to-end
# Canary: [SUPERLOOPV3P2]  Human gate: commit held until you inspect log
set -euo pipefail
OR=/home/jesse/openroot

cat > "$OR/bin/superloop_noise_filter.py" <<'PYEOF'
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Re-classify data/superloop_commands.jsonl with: noise filter + new buckets.
Idempotent: rewrites bucket field on every entry; adds [noise] flag but keeps
the row (audit trail preserved, analysis can exclude flagged rows)."""
import json, re
from pathlib import Path

CMDLOG = Path("/home/jesse/openroot/data/superloop_commands.jsonl")

# Lines that are CODE, not shell commands (heredoc bodies, python REPL, arithmetic)
NOISE_PATTERNS = [
    r"^\s*(print|def |class |import |from .* import|return |if |elif |else|try:|except|for |while |with |assert )\s*\(?.*",
    r"^\s*[a-zA-Z_]\w*\s*=\s*(me\.|self\.|[\"'])",          # c = me.shape_of(...)
    r"^\s*[A-Z_]+\$?\s*=.*grep|cut|sed",                     # K=$(python3 ...
    r"^\s*PYE?OF$",
    r"^\s*(rm|cp|mv|echo|sed|grep|mkdir|ls)\b.*(\\\s*$)",    # wrapped continuation lines
    r"^\s*\.py\b|^\s+\w",                                    # starts with whitespace = likely wrapped body
]

BUCKETS = [
    ("bridge",   r"\b(ssh|scp)\b"),
    ("gitops",   r"\b(git|gh)\b"),
    ("model",    r"(ollama|localhost:11434|qwen)"),
    ("author",   r"cat\s*<<|heredoc|PYE?OF"),
    ("exec",     r"^(python3?|bash|sh)\b|py_compile"),
    ("assistant",r"\b(lumo|hive\.sh|nanobot|smart_router|bot_loop|mistake_engine)\b"),
    ("gate",     r"(stack_gate|team_gate|push_guard|grep\s+-q)"),
    ("system",   r"\b(ps|pgrep|kill|nohup|crontab|df|free)\b"),
    ("net",      r"\b(curl|wget|tailscale)\b"),
    ("files",    r"^(ls|cat|grep|tail|head|sed|mv|cp|mkdir|find|wc|rm)\b"),
    ("nav",      r"^cd\b|^pushd\b|^pwd$"),
    ("vars",     r"^[A-Za-z_]\w*=.*"),
]

def classify(cmd):
    for name, pat in BUCKETS:
        if re.search(pat, cmd):
            return name
    return "other"

def is_noise(cmd):
    for pat in NOISE_PATTERNS:
        if re.search(pat, cmd):
            return True
    return False

rows = []
if CMDLOG.exists():
    for ln in CMDLOG.read_text(errors="replace").splitlines():
        try:
            e = json.loads(ln)
        except Exception:
            continue
        e["noise"] = bool(is_noise(e["cmd"]))
        e["bucket"] = classify(e["cmd"])
        rows.append(e)

with CMDLOG.open("w") as f:
    for e in rows:
        f.write(json.dumps(e)+"\n")

clean = [e for e in rows if not e["noise"]]
from collections import Counter
bc = Counter(e["bucket"] for e in clean)
total_clean = len(clean)
print("[RECLASS] rows=%d clean=%d noise=%d" % (len(rows), total_clean, len(rows)-total_clean))
print("[RECLASS] clean buckets: %s" % json.dumps(dict(bc)))
if total_clean:
    print("[RECLASS] 'other' ratio now: %.1f%%" % (100*bc.get("other",0)/total_clean))
print("[exit=0]")
PYEOF

python3 -m py_compile "$OR/bin/superloop_noise_filter.py" && echo "[gate:py_compile] PASS"
python3 "$OR/bin/superloop_noise_filter.py"

echo "=== FINAL VERIFICATION RUN ==="
python3 "$OR/bin/superloop_composite_v3.py" --recall 250 --confirm 1
echo "[exit=0]"
