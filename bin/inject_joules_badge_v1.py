#!/usr/bin/env python3
"""Inject live joules-saved counter into README/profile/landing pages.
Reads data/joules_saved.json, finds/inserts badge line in three targets."""
import json
from pathlib import Path

REPO = "/home/jesse/openroot"
COUNTER = Path(REPO + "/data/joules_saved.json")
TARGETS = [
    Path(REPO + "/README.md"),
    Path(REPO + "/profile/README.md"),
    Path(REPO + "/site/index.html"),
]

BADGE_LINE = "## 💡 Energy Efficiency: **{saved}J saved** by skipping cached pathways ({fresh} fresh, {cached} cached)"
ALT_BADGE = "<!-- 💡 Energy: **{saved}J saved** by cached pathways -->"

def read_counter():
    if not COUNTER.exists():
        return None
    return json.loads(COUNTER.read_text())

def inject_md(path: Path, data):
    if not path.exists():
        print(f"[held] absent: {path}")
        return False
    content = path.read_text()
    badge = BADGE_LINE.format(**data)
    # Check if already present
    for line in content.splitlines():
        if "Energy Efficiency" in line or "Energy: **" in line:
            if badge in line:
                print(f"[banked] already present: {path}")
                return True
            # Replace old line
            lines = content.splitlines()
            new_lines = []
            for l in lines:
                if "Energy Efficiency" in l or "Energy: **" in l:
                    new_lines.append(badge)
                else:
                    new_lines.append(l)
            path.write_text("\n".join(new_lines) + "\n")
            print(f"[banked] replaced in: {path}")
            return True
    # Append near top (after first heading)
    lines = content.splitlines()
    insert_idx = 1
    for i, l in enumerate(lines):
        if l.startswith("#"):
            insert_idx = i + 1
            break
    lines.insert(insert_idx, badge)
    path.write_text("\n".join(lines) + "\n")
    print(f"[banked] inserted in: {path}")
    return True

def inject_html(path: Path, data):
    if not path.exists():
        print(f"[held] absent: {path}")
        return False
    content = path.read_text()
    alt = ALT_BADGE.format(**data)
    # Replace existing comment
    if "Energy: **" in content:
        import re
        content = re.sub(r'<!--\s*💡 Energy:.*?-->', alt, content, flags=re.DOTALL)
        path.write_text(content)
        print(f"[banked] replaced in: {path}")
        return True
    # Insert after <body> or title
    if "<body>" in content:
        content = content.replace("<body>", f"<body>\n{alt}")
    path.write_text(content)
    print(f"[banked] inserted in: {path}")
    return True

def main():
    data = read_counter()
    if not data:
        print("[held] no counter data — run joules_saved_counter_v1.py first")
        return
    saved = data.get("saved_joules", 0)
    fresh = data.get("runs_fresh", 0)
    cached = data.get("runs_cached", 0)
    payload = {"saved": f"{saved:.3f}", "fresh": fresh, "cached": cached}
    for t in TARGETS:
        if t.suffix == ".html":
            inject_html(t, payload)
        else:
            inject_md(t, payload)

if __name__ == "__main__":
    main()
    print("[banked] joules badge injected")
    print("[exit=0]")
