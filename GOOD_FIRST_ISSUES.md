# Good First Issues — Welcome, Builder

OpenRoot is a radical-credit, open-door project: **everyone who contributes gets named.**
Claim any task by commenting on it or opening a PR referencing the task ID.
Simple tasks ship in ~30 minutes. No gatekeeping, no CLA maze — GPL-3.0 code / CC-BY-SA-4.0 docs.

| ID | Task | Difficulty | Location |
|----|------|-----------|----------|
| id|title|difficulty|source_path |
| 1|echo "[stage-3] mine TODO/FIXME debt into candidate issues"|easy|bin/mesh_recruit_v1.sh:41 |
| 2|  done < <(grep -rn --include='*.py' --include='*.sh' -iE 'TODO|FIXME|XXX:' bin/ 2>/dev/null | head -40)|easy|bin/mesh_recruit_v1.sh:49 |
| 3|    VALUES ('Rebuild GOALS.md + MASTER_TODO.md','Restore 18-task restructure from context_bridge/session-20260918_015240.md remnant','context_bridge/session-20260918_015240.md','medium');"|easy|bin/mesh_recruit_v1.sh:54 |
| 4|"""OpenRoot Master Todo Automation Engine v2.0 — one-shot, idempotent."""|easy|bin/todo_processor.py:2 |
| 5|TODO_PATH = ROOT / "MASTER_TODO.md"|easy|bin/todo_processor.py:12 |
| 6|REPORT_PATH = ROOT / "reports" / "todo_automation_report.json"|easy|bin/todo_processor.py:15 |
| 7|def parse_todos()|easy|bin/todo_processor.py:31 |
| 8|    if not TODO_PATH.exists()|easy|bin/todo_processor.py:32 |
| 9|        print("[held] MASTER_TODO.md missing")|easy|bin/todo_processor.py:33 |
| 10|    items = re.findall(r"- \[ \] (\d+)/10\s+(.+?)\s*->", TODO_PATH.read_text())|easy|bin/todo_processor.py:35 |
| 11|    print(f"[parse] {len(items)} todo items extracted")|easy|bin/todo_processor.py:36 |
| 12|Execute MASTER_TODO automation to resolve markdown clarity/engineering items.|easy|bin/todo_processor.py:43 |
| 13|- [ ] Re-run watchdog_once.py to refresh MASTER_TODO|easy|bin/todo_processor.py:51 |
| 14|    python3 -m py_compile bin/todo_processor.py|easy|bin/todo_processor.py:56 |
| 15|    todos = parse_todos()|easy|bin/todo_processor.py:130 |
| 16|    # Fix 3: MASTER_TODO.md — assign unique IDs and dedupe duplicates|easy|bin/todo_processor.py:142 |
| 17|    if TODO_PATH.exists()|easy|bin/todo_processor.py:143 |
| 18|        raw = TODO_PATH.read_text()|easy|bin/todo_processor.py:144 |
| 19|        new = "# MASTER TODO (auto-refreshed by watchdog_once.py)\n\n" + "\n".join(lines) + "\n"|easy|bin/todo_processor.py:156 |
| 20|        write(TODO_PATH, new)|easy|bin/todo_processor.py:157 |
| 21|        print(f"[write] MASTER_TODO.md: {uid} unique tasks, IDs assigned")|easy|bin/todo_processor.py:158 |
| 22|        "todos_parsed": len(todos),|easy|bin/todo_processor.py:164 |
| 23|    expected = {str(p) for p in (GOALS_PATH, HANDBOOK_PATH, TODO_PATH)}|easy|bin/todo_processor.py:172 |
| 24|        run_git(["add", str(GOALS_PATH), str(HANDBOOK_PATH), str(TODO_PATH), str(REPORT_PATH)])|easy|bin/todo_processor.py:177 |
| 25|                 "docs: todo automation v2.0 - restructured GOALS/USER_GUIDE, "|easy|bin/todo_processor.py:179 |
| 26|                 "unique task IDs in MASTER_TODO (py_compile + report verified)"])|easy|bin/todo_processor.py:180 |
| 27|    print("[done] todo_automation v2.0 complete")|easy|bin/todo_processor.py:186 |
| 28|    todo = [p for p in files if p not in done_paths]|easy|bin/agape_qa_engine.py:107 |
| 29|    print(f"[observe] embedded already: {len(done_paths)} | to embed: {len(todo)}")|easy|bin/agape_qa_engine.py:108 |
| 30|    for p in todo|easy|bin/agape_qa_engine.py:110 |
| 31|Wire canonical_index embeddings|medium|enable_vector_embeddings.py |
| 32|Rebuild GOALS.md + MASTER_TODO.md|medium|context_bridge/session-20260918_015240.md |
| 33|Fix OpenCell contact placeholder + license decision|easy|OpenCell-Thermal-System README |
| 34|Build pyranometer measurement rig|medium|OpenCell-Thermal-System |

## Permaculture Operating Principles (how we work)
1. Observe & interact — consult lessons.db before every task
2. Catch & store energy — bank every insight into a ledger
3. Obtain a yield — measure useful output per joule invested
4. Self-regulate & accept feedback — every change is graded before merge
5. Value renewables — local models, solar-powered hardware
6. Produce no waste — mistakes become lessons, lessons become docs
7. Patterns to details — canon locked, spokes free
8. Integrate, don't segregate — builders, graders, rememberers, humans
9. Small & slow — atomic edits only
10. Value diversity — your build, your data, your name in CREDITS.md
11. Edges are productive — mobile/Termux contributions welcome
12. Respond to change — lessons verified, workflow mutates

**Credit:** every merged PR adds a line to CREDITS.md. Attribution is sacred here.
