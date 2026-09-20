#!/usr/bin/env python3
# goals_rebuild_v2_20260920.py — v1 crashed (format-string bug) AND salvage dumps are EMPTY.
# New source of truth: context_bridge/session-2026-09-16-*.md (boot-seed-verified remnants)
# plus a repo-wide sweep for task-checklist lines. f-strings throughout (bug-class fix).
# DRAFTS ONLY — nothing committed, human is the gate.
import pathlib, datetime, re, hashlib
OPENROOT = pathlib.Path("/home/jesse/openroot")
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
print("[canary] OPENROOT-goals-rebuild-v2-20260920 paste intact")
report = []
def say(m):
    print(m); report.append(m)

# ---- Stage A: confirm salvage husks, then harvest session files ----
say("== STAGE A [harvest] source sweep ==")
sources = {}  # path -> list of matched lines (verbatim)
TASK_RE = re.compile(r'^\s*(?:-\s*\[\s[ xX]\s\]|[-*]\s|\d+[.)]\s)\s*\S.*')

for rel in ["data/salvaged_tasks_20260920_014329.txt",
            "data/salvaged_tasks_v2_20260920_015234.txt",
            "data/salvaged_tasks_v2_20260920_015411.txt"]:
    p = OPENROOT / rel
    txt = p.read_text(errors="ignore") if p.exists() else ""
    say(f"[{'banked' if txt.strip() else 'held'}] {rel} :: {len(txt.splitlines())} lines" +
        (" (EMPTY HUSK)" if not txt.strip() else ""))
    if txt.strip():
        sources[str(p)] = [l for l in txt.splitlines() if TASK_RE.match(l)]

cb = OPENROOT / "context_bridge"
sess = sorted(cb.glob("session-2026-09-16-*.md")) if cb.is_dir() else []
say(f"[banked] Sept-16 session files found: {len(sess)}")
for f in sess:
    lines = [l for l in f.read_text(errors="ignore").splitlines() if TASK_RE.match(l)]
    if lines:
        sources[str(f)] = lines
        say(f"[banked] {f.name} :: {len(lines)} task-pattern lines")

# ---- Stage B: deep sweep of remaining md/txt (skip context_bridge duplicates, data dirs) ----
if not sources:
    say("[held] session files empty/absent — widening sweep")
    for p in OPENROOT.rglob("*"):
        if p.suffix not in (".md", ".txt") or not p.is_file():
            continue
        s = str(p)
        if "/context_bridge/" in s or "/.git/" in s or "salvaged_tasks" in s or "/venv/" in s:
            continue
        try:
            lines = [l for l in p.read_text(errors="ignore").splitlines() if TASK_RE.match(l)]
        except Exception:
            continue
        if len(lines) >= 3:  # only files with real task clusters
            sources[s] = lines
            say(f"[banked] {s} :: {len(lines)} task-pattern lines")

# ---- Stage C: dedupe verbatim, preserve first-seen order ----
seen, ordered = set(), []
for path in sorted(sources, key=str):
    for l in sources[path]:
        k = re.sub(r'\s+', ' ', l).strip().lower()
        if k and k not in seen:
            seen.add(k); ordered.append(re.sub(r'^\s*', '', l))
say(f"[banked] unique verbatim task lines: {len(ordered)}")

# ---- Stage D: drafts ----
go = OPENROOT / f"GOALS.rebuild.{STAMP}.md"
go.write_text(f"""# GOALS.md — REBUILD DRAFT {STAMP}

> Reconstructed from context_bridge/session-2026-09-16-*.md remnants (+ sweep).
> Salvage dumps proved EMPTY (0 lines) — v1 source was dead on arrival.
> DRAFT — human review required before commit; lines verbatim, no invention.

## Recovered tasks ({len(ordered)})
""" + "\n".join(f"- {t}" for t in ordered) + "\n")

mt = OPENROOT / "context_bridge" / f"MASTER_TODO.rebuild.{STAMP}.md"
mt.write_text(f"""# MASTER_TODO — REBUILD DRAFT {STAMP}

## Immediate queue
1. ~~verify/commit bin/~~ DONE: 97397e58, pushed
2. THIS: approve rebuild drafts, mv over GOALS.md + MASTER_TODO.md, commit
3. Support Reh1t PR #53 (RAG ingestion) — force-pushed history, clone stale
4. Pin 4 repos on profile + [PHOTO] slot in openroot README
5. aerocement-panel-v0 standalone repo w/ build evidence
6. SARE grant framing
7. Weekly onepass_v3.sh

## Recovered tasks ({len(ordered)}, verbatim)
""" + "\n".join(f"- [ ] {t}" for t in ordered) + """

## Provenance
""" + ("\n".join(f"- {pathlib.Path(s).name} ({len(v)} lines, sha256 {hashlib.sha256(pathlib.Path(s).read_bytes()).hexdigest()[:16]})" for s, v in sorted(sources.items())) if sources else "- NO SOURCES FOUND — sweep came up empty") + "\n")

say(f"[banked] GOALS draft: {go}")
say(f"[banked] MASTER_TODO draft: {mt}")

rep = OPENROOT / "context_bridge" / f"report-goals-rebuild-{STAMP}.md"
rep.write_text("\n".join(report) + f"""

## Handoff {STAMP}
sources={len(sources)} unique_tasks={len(ordered)}
drafts written, NOTHING committed (human gate)
note: v1 crash root-caused (implicit-concat + %-precedence); v2 uses f-strings
next: review both .rebuild drafts; if {len(ordered)} < 18 expected tasks, hunt diff in session files manually
""")
say(f"[banked] report sealed: {rep}")
print("[exit=0]")
