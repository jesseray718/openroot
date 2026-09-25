#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# goals_rebuild_v1_20260920.py — recover/rebuild GOALS.md + MASTER_TODO from remnants.
# Stage A: hunt for setup_restore_v1.sh (boot-seed claimed it exists; VERDICT BY SEARCH).
# Stage B: ingest all 3 salvaged_tasks files, dedupe, diff v2 runs to find newest additions.
# Stage C: emit GOALS.rebuild + MASTER_TODO.rebuild DRAFTS (verbatim tasks, no invention) —
#          human reviews; nothing auto-committed (human is the only commit gate).
import pathlib, datetime, hashlib
OPENROOT = "/home/jesse/openroot"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
print("[canary] OPENROOT-goals-rebuild-v1-20260920 paste intact")
report = []
def say(m):
    print(m); report.append(m)

say("== STAGE A [hunt] setup_restore_v1.sh ==")
hits = []
for root in [OPENROOT, "/home/jesse/src/openroot", "/home/jesse"]:
    p = pathlib.Path(root)
    if p.is_dir():
        for f in p.rglob("setup_restore*"):
            hits.append(str(f))
            say("[banked] FOUND: %s" % f)
    cb = pathlib.Path(root, "context_bridge")
    if cb.is_dir():
        for f in cb.glob("session-*"):
            try:
                if "setup_restore_v1" in f.read_text(errors="ignore"):
                    hits.append(str(f)); say("[banked] script REFERENCED in: %s" % f)
            except Exception:
                pass
if not hits:
    say("[held] no copy of setup_restore_v1.sh anywhere — purged with filter-repo; rebuilding from salvage instead")

say("== STAGE B [ingest] 3 salvaged task dumps ==")
files = ["data/salvaged_tasks_20260920_014329.txt",
         "data/salvaged_tasks_v2_20260920_015234.txt",
         "data/salvaged_tasks_v2_20260920_015411.txt"]
raw = {}
for rel in files:
    p = pathlib.Path(OPENROOT, rel)
    if p.exists():
        raw[rel] = [l.rstrip() for l in p.read_text(errors="ignore").splitlines()]
        say("[banked] %s :: %d lines" % (rel, len(raw[rel])))
    else:
        say("[held] %s :: MISSING" % rel)

# dedupe task lines (non-empty), preserve latest-known ordering (later file wins position)
tasks = []
seen = set()
for rel in reversed(files):  # oldest first so newest order dominates? -> actually iterate oldest->newest, later appends override position
    pass
ordered = []
for rel in files:  # chronological; v2_15411 last
    for l in raw.get(rel, []):
        t = l.strip()
        if not t or t.startswith("#"):
            continue
        if t.lower() in seen:
            continue
        seen.add(t.lower()); ordered.append(l)

added_late = [l for l in ordered
              if any(l not in raw.get(files[0], []) and l not in raw.get(files[1], []) for _ in [0])]
say("[banked] unique task lines: %d (v2-final adds vs first two: %d)" % (len(ordered), len(added_late)))

say("== STAGE C [draft] GOALS.rebuild + MASTER_TODO.rebuild (NOT committed) ==")
g = pathlib.Path(OPENROOT, "GOALS.rebuild.%s.md" % STAMP)
g.write_text(
    "# GOALS.md — REBUILD DRAFT %s\n\n"
    "> Reconstructed from data/salvaged_tasks* remnants after filter-repo loss of\n"
    "> 'todo automation v2.0' commit (GOALS/MASTER_TODO 18-task restructure).\n"
    "> Status: DRAFT — human review required before commit. Original script lost\n"
    "> (setup_restore_v1.sh purged); this rebuild is task-verbatim, structure best-effort.\n\n"
    "## Unique tasks recovered (%d)\n" % (STAMP, len(ordered))
    + "\n".join("- %s" % t for t in ordered) + "\n")

mt = pathlib.Path(OPENROOT, "context_bridge", "MASTER_TODO.rebuild.%s.md" % STAMP)
mt.write_text(
    "# MASTER_TODO — REBUILD DRAFT %s\n\n"
    "## Immediate queue (per boot seed, live as of this rebuild)\n"
    "1. ~~verify/commit bin/~~ DONE: 97397e58 + pushed\n"
    "2. THIS FILE: rebuild GOALS.md + MASTER_TODO (approve, then mv over originals)\n"
    "3. Support Reh1t PR #53 (RAG ingestion) — force-pushed history, clone is stale\n"
    "4. Pin 4 repos on profile + [PHOTO] slot in openroot README\n"
    "5. aerocement-panel-v0 standalone repo w/ build evidence\n"
    "6. SARE grant framing\n"
    "7. Weekly onepass_v3.sh\n\n"
    "## Recovered tasks (%d, verbatim from salvage)\n" % len(ordered)
    + "\n".join("- [ ] %s" % t for t in ordered) + "\n\n"
    "## Salvage provenance\n"
    + "\n".join("- %s (%d lines, sha256 %s)" % (r, len(raw[r]), hashlib.sha256(pathlib.Path(OPENROOT, r).read_bytes()).hexdigest()[:16]) for r in files if r in raw) + "\n")

say("[banked] GOALS draft: %s" % g)
say("[banked] MASTER_TODO draft: %s" % mt)
rep = pathlib.Path(OPENROOT, "context_bridge", "report-goals-rebuild-%s.md" % STAMP)
rep.write_text("\n".join(report) + "\n\n## Handoff %s\ndrafts written, NOTHING committed (human gate)\nnext: review both .rebuild files; if structure ok, mv over GOALS.md + MASTER_TODO.md, then commit\n" % STAMP)
say("[banked] report sealed: %s" % rep)
print("[exit=0]")
