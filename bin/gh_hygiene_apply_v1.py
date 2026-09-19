#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# gh_hygiene_apply_v1.py — fleet hygiene from per-repo GROUND TRUTH (fixes 3 shell bugs:
# empty-licenseInfo column, ghost repo names, 0-byte license text).
# Forks/archived skipped. Dry-run default, CONFIRM=1 applies. Idempotent.
# [canary] gh_hygiene_apply_v1_CANARY_MARKER
import base64, json, os, socket, subprocess, sys, urllib.request
from datetime import datetime, timezone

OWNER = "jesseray718"; REPO_DIR = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"
MIN_LIC_BYTES = 30000

DESCRIPTIONS = {  # from boot-seed knowledge; empty = held for human draft
    "aerocement-calc": "Aerocement structural calculators — geodesic dome + opencell panel engineering math",
    "jesseray718": "OpenRoot ecosystem index — pinned project hub",
    "jesseray718-archive": "Archive: legacy firmware (nrf52/nrf54l15/stm32) and historical work",
    "kai9000": "KAI-9000 agent workspace — sessions and sync-from-kai source material",
    "kai-memory": "Persistent memory store for KAI agent lineage",
    "etaledger": "",
}

def say(t, m): print(f"[{t}] {m}")
def gh(args, ok=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if ok and r.returncode != 0:
        raise RuntimeError(f"gh rc={r.returncode}: {r.stderr.strip()[:200]} :: {' '.join(args[:4])}")
    return r

def main():
    assert socket.gethostname() == "optiplex3060", "[held] run on optiplex3060"
    gh(["auth", "status"])  # implicit check
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    rep = f"{REPO_DIR}/reports/gh_hygiene_apply_{ts}"; os.makedirs(rep, exist_ok=True)
    say("gate", f"start CONFIRM={CONFIRM} -> {rep}")

    inv = json.loads(gh(["repo", "list", OWNER, "--limit", "200",
        "--json", "name,isArchived,isFork,description"]).stdout)
    live = {r["name"] for r in inv}
    say("banked", f"live repos: {len(live)}")

    def fetch_lic_text():
        r = gh(["api", "/licenses/gpl-3.0", "--jq", ".content"], ok=False)
        if r.returncode == 0 and r.stdout.strip():
            try:
                t = base64.b64decode(r.stdout).decode("utf-8", "replace")
                if len(t.encode()) >= MIN_LIC_BYTES: return t, "gh /licenses api"
            except Exception: pass
        try:
            t = urllib.request.urlopen("https://www.gnu.org/licenses/gpl-3.0.txt", timeout=30).read().decode("utf-8", "replace")
            if len(t.encode()) >= MIN_LIC_BYTES: return t, "gnu.org direct"
        except Exception as e: say("held", f"gnu.org fetch failed: {e}")
        return None, "NO SOURCE"

    lic_txt = None; lic_src = None; applied, held = [], []
    for r in sorted(inv, key=lambda x: x["name"]):
        n = r["name"]
        if n not in live or not n or not all(c.isalnum() or c in "._-" for c in n):
            held.append(f"{n}|GHOST_NAME"); continue
        if r["isFork"]: held.append(f"{n}|FORK_SKIPPED"); continue
        if r["isArchived"]: held.append(f"{n}|ARCHIVED"); continue
        meta = json.loads(gh(["api", f"repos/{OWNER}/{n}"]).stdout)
        lic = (meta.get("license") or {}).get("spdx_id") or ""
        desc = meta.get("description") or ""

        if not lic:  # license ground truth: per-repo GET, not repo-list column
            if lic_txt is None:
                lic_txt, lic_src = fetch_lic_text()
                if lic_txt is None:
                    held.append(f"{n}|NO_LIC_TEXT_SOURCE"); continue
                say("gate", f"license text: {len(lic_txt.encode())}B via {lic_src}")
            if CONFIRM:
                try:
                    gh(["api", "-X", "PUT", f"repos/{OWNER}/{n}/contents/LICENSE",
                        "-f", "message=Add GPL-3.0 (SPDX) — gh_hygiene_apply_v1",
                        "-f", "content=" + base64.b64encode(lic_txt.encode()).decode()])
                    applied.append(f"{n}|LICENSE_GPL-3.0"); say("banked", f"licensed {n}")
                except RuntimeError as e: held.append(f"{n}|LIC_PUSH_FAIL"); say("held", f"{n}: {e}")
            else:
                say("held", f"DRY: would push GPL-3.0 ({len(lic_txt.encode())}B) -> {n}/LICENSE")

        if not desc:
            d = DESCRIPTIONS.get(n, "")
            if not d: held.append(f"{n}|NO_DESC_DRAFTED"); say("held", f"no desc drafted: {n}")
            elif CONFIRM:
                gh(["repo", "edit", "-R", f"{OWNER}/{n}", "--description", d])
                applied.append(f"{n}|DESC_SET"); say("banked", f"described {n}: {d[:50]}")
            else: say("held", f"DRY: would set desc on {n}: {d[:60]}")

    for f, rows in (("applied.tsv", applied), ("held.tsv", held)):
        with open(f"{rep}/{f}", "w") as fh: fh.write("\n".join(rows) + "\n")
    say("banked", f"report: {rep}/ applied={len(applied)} held={len(held)}")

    # queue item 1: bin/ tracking state (report only — human is commit gate)
    tr = subprocess.run(["git", "-C", REPO_DIR, "ls-files", "bin/"], capture_output=True, text=True).stdout.split()
    st = subprocess.run(["git", "-C", REPO_DIR, "status", "--porcelain", "bin/"], capture_output=True, text=True).stdout.strip().splitlines()
    say("banked" if tr else "held", f"bin/ tracked={len(tr)} files, working-tree changes={len(st)}")
    for line in st: say("held", f"bin drift: {line}")
    if not tr: say("held", "bin/ UNTRACKED — git add bin/ analysis/ then human-verified commit")
    print("[exit=0]")

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"[held] FATAL: {e}"); sys.exit(1)
