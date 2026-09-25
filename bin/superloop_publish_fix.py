#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Patch superloop_composite_v3.py: gh api PATCH gist publish + --sample mode.
Edits the file in place via targeted line surgery; safe to re-run (idempotent)."""
import json, re
from pathlib import Path

TARGET = Path("/home/jesse/openroot/bin/superloop_composite_v3.py")
src = TARGET.read_text()

# --- FIX 1: replace publish() body — gh gist edit can't read '-' as content.
# Use gh api PATCH with JSON input, built safely (no shell quoting hazards). ---
old_pub_start = src.index("def publish(confirm):")
old_pub_end = src.index("def main():")
new_pub = '''def publish(confirm):
    if not confirm:
        return "[held] dashboard written locally; CONFIRM=1 publishes gist"
    import subprocess as sp
    try:
        payload = json.dumps({
            "description": "OpenRoot SUPERLOOP dashboard (auto-pulsed)",
            "files": {"STATE.md": {"content": DASHBOARD.read_text()}},
        })
        r = sp.run(["gh","api","-X","PATCH","gists/"+GIST_ID,"--input","-"],
                   input=payload, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return "[banked] gist published via gh api PATCH"
        return "[FAIL] gist: " + r.stderr[:200]
    except Exception as e:
        return "[FAIL] gist error: " + str(e)[:200]

'''
src = src[:old_pub_start] + new_pub + src[old_pub_end:]

# --- FIX 2: add --sample mode: dump top 'other' commands for regex tuning ---
if "--sample" not in src:
    src = src.replace(
        '    ap.add_argument("--confirm", type=int, default=0)',
        '    ap.add_argument("--confirm", type=int, default=0)\n'
        '    ap.add_argument("--sample", type=int, default=0)')
    src = src.replace(
        "if __name__ == \"__main__\":\n    main()",
        '''def sample_other(top_n=20):
    """Evidence-based bucket tuning: show most-repeated 'other' commands."""
    counts = {}
    if CMDLOG.exists():
        for ln in CMDLOG.read_text(errors="replace").splitlines():
            try:
                e = json.loads(ln)
                if e["bucket"] == "other":
                    counts[e["cmd"]] = counts.get(e["cmd"], 0) + 1
            except Exception:
                pass
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    print("[SAMPLE] top %d 'other' commands (freq):" % len(ranked))
    for cmd, n in ranked:
        print("  %3dx  %s" % (n, cmd[:140]))
    print("[SAMPLE] paste these back to Lumo -> we write bucket regexes from evidence")

if __name__ == "__main__":
    import sys as _sys
    if "--sample" in _sys.argv:
        sample_other()
    else:
        main()''')

TARGET.write_text(src)
print("[banked] patched:", TARGET)
