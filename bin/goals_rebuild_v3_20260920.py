#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# goals_rebuild_v3_20260920.py — curated sources only. No corpus sweep.
# Sources: 1) reports/goals_draft/*.md (prior rebuild attempt, survived)
#          2) context_bridge/session-*.md (Sept-16 remnants)
# Salvaged husks excluded — proven empty by v1. Cap: 100 lines.
import pathlib, datetime, re
OPENROOT = pathlib.Path("/home/jesse/openroot")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
print("[canary] OPENROOT-goals-rebuild-v3-20260920 paste intact")
report = []
def say(m): print(m); report.append(m)

TASK_RE = re.compile(r'^\s*(?:-\s*\[\s[ xX]\s\]|[-*]\s|\d+[.)]\s)\s*\S.*')
sources = []

# P1: prior curated drafts
gd = OPENROOT / "reports" / "goals_draft"
for f in sorted(gd.glob("*.md")) if gd.is_dir() else []:
    lines = [l.strip() for l in f.read_text(errors="ignore").splitlines() if TASK_RE.match(l)]
    if lines: sources.append((1, f, lines)); say(f"[banked] P1 {f} :: {len(lines)} task lines")

# P2: session files (limited scope)
cb = OPENROOT / "context_bridge"
for f in sorted(cb.glob("session-*.md")):
    lines = [l.strip() for l in f.read_text(errors="ignore").splitlines() if TASK_RE.match(l)]
    if lines: sources.append((2, f, lines)); say(f"[banked] P2 {f.name} :: {len(lines)} task lines")

raw_total = sum(len(v) for _, _, v in sources)
say(f"[banked] harvested {raw_total} lines from {len(sources)} sources")

seen, ordered = set(), []
for prio, f, lines in sorted(sources, key=lambda s: (s[0], str(s[1]))):
    for l in lines:
        k = re.sub(r'\s+', ' ', l).strip().lower(); k = re.sub(r'\[[ xX]\]', '[ ]', k)
        if k and k not in seen:
            seen.add(k); ordered.append(re.sub(r'^\s*(?:[-*]|\d+[.)])\s+', '', l))
say(f"[banked] unique normalized tasks: {len(ordered)}")

go = OPENROOT / f"GOALS.rebuild.{STAMP}.md"
go.write_text(f"# GOALS.md — REBUILD DRAFT {STAMP}\n\n> Primary source: reports/goals_draft/\n> Curated only; no corpus sweep.\n\n## Tasks ({len(ordered)})\n" + "\n".join(f"- {t}" for t in ordered) + "\n")

mt = OPENROOT / "context_bridge" / f"MASTER_TODO.rebuild.{STAMP}.md"
mt.write_text(f"# MASTER_TODO — REBUILD DRAFT {STAMP}\n\n## Immediate queue\n1. ~~verify/commit bin/~~ DONE: 97397e58\n2. Approve drafts; mv over originals; commit\n3. Support Reh1t PR #53\n4. Pin 4 repos + PHOTO slot\n5. aerocement-panel-v0 repo\n6. SARE grant framing\n7. Weekly onepass_v3.sh\n\n## Tasks ({len(ordered)})\n" + "\n".join(f"- [ ] {t}" for t in ordered) + "\n")

say(f"[banked] GOALS draft: {go}"); say(f"[banked] MASTER_TODO draft: {mt}")
rep = OPENROOT / "context_bridge" / f"report-goals-rebuild-{STAMP}.md"
rep.write_text("\n".join(report) + f"\n\n## Handoff {STAMP}\nsources={len(sources)} unique_tasks={len(ordered)}\nnext: review; if <18, paste session file content for manual extraction\n")
say(f"[banked] report sealed: {rep}"); print("[exit=0]")
