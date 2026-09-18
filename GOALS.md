# GOALS.md — OpenRoot

> Rebuilt 2026-09-18 from context_bridge/session-20260918_015240.md mission brief
> (original todo-automation v2.0 restructure lost to filter-repo rewrite; intent preserved below)

## MISSION (carry forward — this is the next build)
BUILD "HWCHAIN": a content-addressable blockchain of open-source hardware tech knowledge.
Units = hardware artifacts: tech docs, BOMs, cutlists, g-codes, calculation scripts,
parameter tables, thermal/aerocement/dome data. Not money — provenance + verification.
Design (extends existing synthesis engine + knowledge_ledger.py concept):
  1. Every artifact hashed (SHA256) -> content-addressable ID (CAS pattern, FLAG-AX-* style)
  2. Append-only SQLite ledger: each record fields =
     id, sha256, artifact_type(doc|bom|cutlist|gcode|calc|dataset), path, title,
     license(GPL-3.0/CC-BY-SA-4.0), tags, prev_hash -> chain integrity like synthesis.py
  3. Merkle root per batch -> seal to manifest_index.txt (pattern already proven GREEN)
  4. Graduation gate: a record only becomes canonical after py_compile/smoke-test/
     numeric-check passes (borrow 7B-author + 3B-grade verification pattern)
  5. Query layer: agape_qa_engine templates (bom_query, file_locator) against the
     chain DB; core view renders canonical chain as browsable HTML
  6. Publish: gh push to a hardware-chain repo (dome_bom_truth, aerocement-calc,
     OpenCell-Thermal-System outputs become genesis records)

## ARTIFACTS BUILT THIS SESSION (absolute paths)
- /home/jesse/openroot/bin/universal_index_pipeline.py     (v1.1 clean rewrite, compiles, EXECUTED)
- /home/jesse/openroot/bin/universal_unpack.py             (v1.0, ran, partial — interrupted?)
- /home/jesse/openroot/bin/agape_qa_engine.py             (RAG QA: embed/ask/chat/templates; route_template 2-layer patched; source_files extension-filter patched; compiles)
- /home/jesse/openroot/bin/model_symposium.py             (3B<->7B synergy miner, compiles)
- /home/jesse/openroot/bin/build_core_view.py              (259 docs -> 969KB index.html, WORKS)
- /home/jesse/openroot/bin/core_view_server.sh             (BUGGY: cd-before-dir + no set -e ordering)
- /home/jesse/openroot/data/universal_index/universal_index_1789712158.db  (289 archives scanned: 76 unique, 213 byte-dupes)
- /home/jesse/openroot/data/universal_index/unpack_list_1789712158.json
- /home/jesse/openroot/data/universal_index/agape_rag.db  (chunks accumulate via embedder)
- /home/jesse/openroot/data/core_view/index.html          (generated, 259 docs)

## VERIFIED STATE
- Universal index built: [stage-1..7] all green, qa_router.sh emitted
- Stage-B unpack ran: ~8317 unique files indexed, ~9841 dupe merges observed across banked archives
- Dedup finding: 213/289 archives byte-identical (73% redundancy) — consolidation confirmed
- asset_preclassify_v2.py: never completed a promoted run (interrupted + grader-down history);
  shelf = 217 items, prior seal bcbca1e8726a9746c98e7a44aee0175dc309b19c960005edef42a812de64847d
- Model fleet (Ollama): 12 models live incl qwen2.5-coder:7b, qwen2.5:3b, nomic-embed-text

## BROKEN / INCOMPLETE
1. core_view_server.sh: verify=000. Fix: kill pgrep -f "http.server 8088"; cd /home/jesse/openroot/data/core_view THEN nohup python3 -m http.server 8088 --bind 0.0.0.0; re-curl want 200
2. model_symposium: job EXITED 1 — READ /home/jesse/openroot/logs/symposium.log first action
3. Embedder not relaunched after extension-filter patch — resume (idempotent, skips committed paths)
4. Salvage loop ^C'd mid-run: two truncated tarballs at /home/jesse/openroot/data/usb128-import-20260913/home_full_2026082{1_160013,9_221848}.tar.xz — xz -dc | tar -xf salvage incomplete
5. Whether stage-B finished all 76 archives: UNKNOWN — check audit_log table in the index DB
6. preclassify 217-item shelf: still unpromoted

## NEXT ACTIONS (priority order, exact commands)

## NEXT ACTIONS (priority order, exact commands)
1. bash: tail -50 /home/jesse/openroot/logs/symposium.log           # diagnose death
2. bash: sqlite3 /home/jesse/openroot/data/universal_index/universal_index_1789712158.db 'SELECT COUNT(*) FROM audit_log WHERE action="unpack"'   # how many of 76 done
3. Relaunch embedder: OLLAMA_HOST=http://localhost:11434 nohup python3 /home/jesse/openroot/bin/agape_qa_engine.py embed > /home/jesse/openroot/logs/agape_embed.log 2>&1 &
4. Fix core view server (item 1 above), then A15: Chrome http://192.168.1.193:8088 -> Add to Home screen
5. START HWCHAIN: create /home/jesse/openroot/bin/hwchain.py per MISSION spec —
   genesis records = outputs of dome_bom_truth, aerocement-calc, OpenCell-Thermal-System
6. After corpus embeds: rerun model_symposium.py (should now ground in real RAG chunks)
7. Smoke test: python3 agape_qa_engine.py ask "where is the dome strut BOM calculator"

## BOOT PROTOCOL FOR NEXT WINDOW

## ACTIVE QUEUE (from mesh session, 2026-09-18)
1. Wire canonical_index embeddings (34,265 files, 0 embedded) — issue live on GitHub
2. Support Reh1t PR #53 (RAG ingestion) — clone predates force-push, be gentle
3. hwchain.py genesis build (highest-eta per mission brief)
4. aerocement-panel-v0 standalone repo with build evidence
5. SARE grant framing (COP-boundary language only — never >100% thermo)
6. Weekly onepass_v3.sh cadence

## BOOT PROTOCOL FOR NEXT WINDOW
This file is state. Read it, verify artifacts exist (ls paths above), run fleet audit:
pgrep -af "agape_qa_engine|model_symposium|universal_index_pipeline|http.server"
Then execute NEXT ACTIONS in order. Highest-eta move: hwchain.py genesis build.

## STANDING DOCTRINE
- eta = J_useful/J_human is the only efficiency metric
- Commit messages assert; grep verifies
- Human is the only commit gate
- Mistakes become lessons in data/lessons.db (currently 3)
