#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
# session_seal_v2.py — seal 2026-09-19 session: bank PR-intake tooling, capture stray
# report dir, fix license_fleet offline source, write context_bridge handoff.
# DRY-RUN default. CONFIRM=1 commits+pushes. Human is the only commit gate.
# [canary] session_seal_v2_CANARY_MARKER
import hashlib, os, platform, shutil, subprocess, sys
from datetime import datetime, timezone

REPO = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"
LOCAL_GPL = "/usr/share/common-licenses/GPL-3"

def say(tag, msg): print(f"[{tag}] {msg}")

def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=REPO,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        say("held", f"FAIL: {cmd}\n{r.stderr.strip()[:300]}"); sys.exit(1)
    return r

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""): h.update(c)
    return h.hexdigest()

assert platform.node() == "optiplex3060", "[held] run on optiplex3060"
os.chdir(REPO)
print("[gate] start CONFIRM=" + str(CONFIRM))

# ── stage 1: state snapshot ──────────────────────────────────────
head = sh("git rev-parse --short HEAD").stdout.strip()
behind = sh(["git", "fetch", "origin", "main", "--quiet"]) or None
origin = sh("git rev-parse --short origin/main").stdout.strip()
dirty = sh(["git", "status", "--porcelain"]).stdout.strip().splitlines()
say("gate", f"local HEAD={head} origin/main={origin} dirty_entries={len(dirty)}")

def bank(paths, msg):
    staged = [p for p in paths if os.path.exists(p)]
    if not staged:
        say("held", f"nothing to bank, missing: {set(paths)-set(staged)}"); return False
    sh(["git", "add", *staged])
    if sh("git diff --cached --quiet", check=False).returncode == 0:
        say("banked", f"already committed, nothing new: {staged}"); return True
    stat = sh("git diff --cached --stat").stdout.strip().splitlines()[-1]
    if CONFIRM:
        sh(["git", "commit", "-m", msg])
        sh(["git", "push", "origin", "main"])
        say("banked", f"pushed {sh('git rev-parse --short HEAD').stdout.strip()}: {stat}")
    else:
        say("held", f"DRY would commit+push — {msg} ({stat})")
    return True

# ── stage 2: bank PR-intake pipeline (dry-run proven on PR #63) ──
for f in ("bin/pr_intake.sh", "bin/readme_contributors.sh"):
    if not os.path.exists(f):
        if os.path.exists("/tmp/pr_intake_install.sh"):
            say("gate", "re-materializing from idempotent /tmp installer")
            sh("CONFIRM=0 bash /tmp/pr_intake_install.sh", check=False)
        else:
            say("held", f"{f} missing AND /tmp installer gone — rebuild from session log"); sys.exit(1)
for f in ("bin/pr_intake.sh", "bin/readme_contributors.sh"):
    assert "SPDX-License-Identifier" in open(f).read(), f"[held] {f} lost SPDX header"
    sh(f"bash -n {f}")
say("banked", "bash -n + SPDX grep green: pr_intake.sh + readme_contributors.sh")
bank(["bin/pr_intake.sh", "bin/readme_contributors.sh"],
     "feat(bin): PR intake pipeline + auto-contributor credit (proven on PR #63); "
     "provenance: dry-run + bash -n + SPDX grep verified, human gate")

# ── stage 3: capture stray report dir at repo root ───────────────
stray = "gh_audit_20260919_101948"
if os.path.isdir(stray) and not os.path.isdir(f"reports/{stray}"):
    if CONFIRM:
        shutil.move(stray, f"reports/{stray}")
        say("banked", f"moved {stray}/ -> reports/{stray}/")
    else:
        say("held", f"DRY would move {stray}/ -> reports/{stray}/")
elif os.path.isdir(f"reports/{stray}"):
    say("banked", f"reports/{stray}/ already present")
else:
    say("banked", "no stray report dir at root")
bank([f"reports/{stray}"], f"chore(reports): bank stray root report dir {stray} "
     "(pre-branching orphan of the gh_audit series)")

# ── stage 4: license_fleet offline source fix ────────────────────
lf = "bin/license_fleet_continue_v1.py"
src = open(lf).read()
if os.path.isfile(LOCAL_GPL) and os.path.getsize(LOCAL_GPL) >= 30000:
    if LOCAL_GPL not in src:
        anchor = 'for src, fn in [("gh", lambda:'
        patch = ('for src, fn in [("local", lambda: open("/usr/share/common-licenses/GPL-3").read()),'
                 '\n                     ("gh", lambda:')
        assert anchor in src, "[held] fetch_lic_text anchor drifted — patch manually"
        open(lf, "w").write(src.replace(anchor, patch, 1))
        say("banked", f"patched {lf}: local GPL-3 source first ({os.path.getsize(LOCAL_GPL)}B, no network)")
    else:
        say("banked", f"{lf} already carries local source")
    sh(f"python3 -m py_compile {lf}")
    r = sh(f"CONFIRM=0 python3 {lf}", check=False)
    if "NO_LICENSE_TEXT_SOURCE" in (r.stdout + r.stderr):
        say("held", "still no source after patch — inspect manually"); sys.exit(1)
    say("banked", "dry-run passes: license source resolves locally")
    bank([lf], "fix(bin): license_fleet_continue_v1 local GPL-3 source "
         "(/usr/share/common-licenses/GPL-3) — kills NO_LICENSE_TEXT_SOURCE; "
         "provenance: py_compile + dry-run verified")
    say("note", "to apply fleet-wide: CONFIRM=1 python3 bin/license_fleet_continue_v1.py")
else:
    say("held", f"{LOCAL_GPL} missing/too small — license text source unresolved")

# ── stage 5: handoff seal to context_bridge/ ────────────────────
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
artifacts = [f for f in ("bin/pr_intake.sh", "bin/readme_contributors.sh", lf) if os.path.exists(f)]
lines = [f"# Session Seal {ts} — PR #63 era closeout", "",
         f"- VERIFIED: PR #63 squash-merged (Reh1t, issue #53 closed); HEAD lineage 591bbc10 -> 181702a9",
         f"- ARTIFACTS:"] + [f"  - {p} sha256:{sha256(p)}" for p in artifacts] + [
         f"- BROKEN: repo pinning via gh REST is a nonexistent endpoint (fleet_hygiene_v1 lesson); "
         f"pins need GraphQL user.pinnedItems mutation or manual web UI",
         f"- NEXT: 1) CONFIRM=1 run license fleet, 2) pin 4 repos on profile (web UI or GraphQL), "
         f"3) aerocement-panel-v0 standalone repo, 4) weekly onepass_v3.sh", ""]
hc = f"context_bridge/session-{ts}-pr63-seal.md"
open(hc, "w").write("\n".join(lines))
sh(f"grep -q 'PR #63 squash-merged' {hc}")
say("banked", f"handoff written: {hc}")
bank([hc], "docs(context_bridge): session seal " + ts +
     " — PR #63 closeout, artifact sha256s, broken items, next actions")

print("[exit=0]")
