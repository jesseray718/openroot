#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
# license_fleet_continue_v1.py — fleet licensing from per-repo ground truth
# [canary] license_fleet_continue_v1_CANARY_MARKER
import base64, json, os, socket, subprocess, sys, urllib.request
from datetime import datetime, timezone

OWNER = "jesseray718"; REPO_DIR = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"
MIN_LIC_BYTES = 30000

def say(t, m): print(f"[{t}] {m}")

def gh(args, ok=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if ok and r.returncode != 0:
        raise RuntimeError(f"gh rc={r.returncode}: {r.stderr.strip()[:200]}")
    return r

def fetch_lic_text():
    for src, fn in [("local", lambda: open("/usr/share/common-licenses/GPL-3").read()),
                     ("gh", lambda: gh(["api", "/licenses/gpl-3.0", "--jq", ".content"])),
                    ("gnu", lambda: urllib.request.urlopen("https://www.gnu.org/licenses/gpl-3.0.txt", timeout=30).read().decode())]:
        try:
            raw = fn()
            if isinstance(raw, subprocess.CompletedProcess):
                if raw.returncode != 0 or not raw.stdout.strip(): continue
                t = base64.b64decode(raw.stdout).decode("utf-8", "replace")
            else:
                t = raw
            if len(t.encode()) >= MIN_LIC_BYTES: return t, src
        except Exception: continue
    return None, "NO_SOURCE"

def main():
    assert socket.gethostname() == "optiplex3060", "[held] run on optiplex3060"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    rep = f"{REPO_DIR}/reports/license_fleet_{ts}"; os.makedirs(rep, exist_ok=True)
    say("gate", f"start CONFIRM={CONFIRM} -> {rep}")

    inv = json.loads(gh(["repo", "list", OWNER, "--limit", "200", "--json", "name,isArchived,isFork"]).stdout)
    live = {r["name"] for r in inv}
    lic_text, lic_src = fetch_lic_text()
    if lic_text is None:
        say("held", "NO_LICENSE_TEXT_SOURCE"); print("[exit=0]"); return

    applied, held = [], []
    for r in sorted(inv, key=lambda x: x["name"]):
        n = r["name"]
        if n not in live or r["isFork"] or r["isArchived"]: continue
        meta = json.loads(gh(["api", f"repos/{OWNER}/{n}"]).stdout)
        lic = (meta.get("license") or {}).get("spdx_id") or ""

        if not lic:
            if CONFIRM:
                try:
                    gh(["api", "-X", "PUT", f"repos/{OWNER}/{n}/contents/LICENSE",
                        "-f", "message=Add GPL-3.0 — license_fleet_continue_v1",
                        "-f", f"content={base64.b64encode(lic_text.encode()).decode()}"])
                    applied.append(n); say("banked", f"licensed {n}")
                except RuntimeError as e:
                    held.append(f"{n}|FAIL"); say("held", f"{n}: {e}")
            else:
                say("held", f"DRY: {n} ({len(lic_text.encode())}B)")

    with open(f"{rep}/applied.tsv", "w") as f: f.write("\n".join(applied) + "\n")
    with open(f"{rep}/held.tsv", "w") as f: f.write("\n".join(held) + "\n")
    say("banked", f"applied={len(applied)} held={len(held)} report={rep}/")
    print("[exit=0]")

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"[held] FATAL: {e}"); sys.exit(1)
