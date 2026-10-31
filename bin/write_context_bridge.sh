# SPDX-License-Identifier: GPL-3.0
#!/bin/bash
# write_context_bridge.sh — session close-out bridge, sealed with SHA256
set -eu
TS=$(date +%Y%m%d_%H%M%S)
DIR=/home/${OPENROOT_USER}/openroot/context_bridge
SEED=$DIR/session-$TS.md
mkdir -p "$DIR"

cat > "$SEED" << 'SEED_EOF'
# CONTEXT BRIDGE — OpenRoot Session Seed
author: Jesse McMillen Ray (${OPENROOT_USER}, OpenRoot) | node: optiplex3060 | written: SESSION_CLOSE

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
- /home/${OPENROOT_USER}/openroot/bin/universal_index_pipeline.py     (v1.1 clean rewrite, compiles, EXECUTED)
- /home/${OPENROOT_USER}/openroot/bin/universal_unpack.py             (v1.0, ran, partial — interrupted?)
- /home/${OPENROOT_USER}/openroot/bin/agape_qa_engine.py             (RAG QA: embed/ask/chat/templates; route_template 2-layer patched; source_files extension-filter patched; compiles)
- /home/${OPENROOT_USER}/openroot/bin/model_symposium.py             (3B<->7B synergy miner, compiles)
- /home/${OPENROOT_USER}/openroot/bin/build_core_view.py              (259 docs -> 969KB index.html, WORKS)
- /home/${OPENROOT_USER}/openroot/bin/core_view_server.sh             (BUGGY: cd-before-dir + no set -e ordering)
- /home/${OPENROOT_USER}/openroot/data/universal_index/universal_index_1789712158.db  (289 archives scanned: 76 unique, 213 byte-dupes)
- /home/${OPENROOT_USER}/openroot/data/universal_index/unpack_list_1789712158.json
- /home/${OPENROOT_USER}/openroot/data/universal_index/agape_rag.db  (chunks accumulate via embedder)
- /home/${OPENROOT_USER}/openroot/data/core_view/index.html          (generated, 259 docs)

## VERIFIED STATE
- Universal index built: [stage-1..7] all green, qa_router.sh emitted
- Stage-B unpack ran: ~8317 unique files indexed, ~9841 dupe merges observed across banked archives
- Dedup finding: 213/289 archives byte-identical (73% redundancy) — consolidation confirmed
- asset_preclassify_v2.py: never completed a promoted run (interrupted + grader-down history);
  shelf = 217 items, prior seal bcbca1e8726a9746c98e7a44aee0175dc309b19c960005edef42a812de64847d
- Model fleet (Ollama): 12 models live incl qwen2.5-coder:7b, qwen2.5:3b, nomic-embed-text

## BROKEN / INCOMPLETE
1. core_view_server.sh: verify=000. Fix: kill pgrep -f "http.server 8088"; cd /home/${OPENROOT_USER}/openroot/data/core_view THEN nohup python3 -m http.server 8088 --bind 0.0.0.0; re-curl want 200
2. model_symposium: job EXITED 1 — READ /home/${OPENROOT_USER}/openroot/logs/symposium.log first action
3. Embedder not relaunched after extension-filter patch — resume (idempotent, skips committed paths)
4. Salvage loop ^C'd mid-run: two truncated tarballs at /home/${OPENROOT_USER}/openroot/data/usb128-import-20260913/home_full_2026082{1_160013,9_221848}.tar.xz — xz -dc | tar -xf salvage incomplete
5. Whether stage-B finished all 76 archives: UNKNOWN — check audit_log table in the index DB
6. preclassify 217-item shelf: still unpromoted

## NEXT ACTIONS (priority order, exact commands)
1. bash: tail -50 /home/${OPENROOT_USER}/openroot/logs/symposium.log           # diagnose death
2. bash: sqlite3 /home/${OPENROOT_USER}/openroot/data/universal_index/universal_index_1789712158.db 'SELECT COUNT(*) FROM audit_log WHERE action="unpack"'   # how many of 76 done
3. Relaunch embedder: OLLAMA_HOST=http://localhost:11434 nohup python3 /home/${OPENROOT_USER}/openroot/bin/agape_qa_engine.py embed > /home/${OPENROOT_USER}/openroot/logs/agape_embed.log 2>&1 &
4. Fix core view server (item 1 above), then A15: Chrome http://192.168.1.193:8088 -> Add to Home screen
5. START HWCHAIN: create /home/${OPENROOT_USER}/openroot/bin/hwchain.py per MISSION spec —
   genesis records = outputs of dome_bom_truth, aerocement-calc, OpenCell-Thermal-System
6. After corpus embeds: rerun model_symposium.py (should now ground in real RAG chunks)
7. Smoke test: python3 agape_qa_engine.py ask "where is the dome strut BOM calculator"

## BOOT PROTOCOL FOR NEXT WINDOW
This file is state. Read it, verify artifacts exist (ls paths above), run fleet audit:
pgrep -af "agape_qa_engine|model_symposium|universal_index_pipeline|http.server"
Then execute NEXT ACTIONS in order. Highest-eta move: hwchain.py genesis build.
SEED_EOF

H=$(sha256sum "$SEED" | awk '{print $1}')
echo "$H  $SEED" >> /home/${OPENROOT_USER}/openroot/context_bridge/seed_master.log
echo "[sealed] $SEED"
echo "  sha256 $H"
echo "[gate] paste to next window: cat $SEED"
