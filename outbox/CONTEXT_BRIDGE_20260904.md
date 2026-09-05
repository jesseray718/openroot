# CONTEXT_BRIDGE 2026-09-04T09:56-05:00
operator: Jesse Ray / jesseray718
panes: A15 Termux WD53PPW | optiplex3060 JW5PQXV folder 9wa5l-2o8fl
sync: /storage/emulated/0/openroot <-> /home/jesse/openroot
outbox bus: /home/jesse/openroot/outbox  (gitignored)

## Live sockets
- sqlite skip: /home/jesse/wisdom-scaffold/data/optiplex_public.db
  theorem_registry 3 | geodesic_dome_specs 50 | V6=1080 struts 7.21/7.11/7.02 in
  THM-001 TRI_RIGIDITY skips FEA | THM-002 R=L/sqrt(pi) | THM-003 Kepler 0.74048
  fuller stubs 2x59 words (titles only)
  codebase_fts 2,585,375 rows | tight MATCH \~1.1 ms | loose "fuller" is noise
- nomic tables: /home/jesse/wisdom-scaffold/data/optiplex_index.db
  github_repos 42 | nomic_embeddings 42 | file_chunks 53942 | file_chunk_embeddings 12450
- operator_memory.db events 10603 embeddings 600
- file_map_safe.sqlite 79936
- or_coder: /home/jesse/knowledge/or_coder.py  LAN :11434 qwen2.5-coder:7b  NO CLOUD
  ask/review = /api/generate  STALLS (killed at 18s). health may still say ONLINE
  orq alias: /home/jesse/bin/orq -> that file (made this morning, not historic)
- aider: /home/jesse/.local/bin/aider  cache Aug 19 / WAL touched 2026-09-04
- palm.py: /home/jesse/openroot/bin/palm.py  Find over phone-terminal-logs
- ingest (DO NOT RUN): /home/jesse/wisdom-scaffold/scripts/ingestion/ingest_fuller_v3.py
  archive.org Synergetics djvu + Everything_I_Know_1975 djvu
  DROP TABLE on synergetics_fuller_corpus — would wipe stubs
- dead: une/bin/nomic_embed.py (state_utils missing, cloud Nomic API, Termux paths)
- agape_engine.py exists; postulates.json MISSING on this share
- popw: /home/jesse/openroot/data/popw_ledger.jsonl UNTRACKED keep

## Git
- repo /home/jesse/openroot
- branch pin/20260904-palm @ f4c0c1c
- PR https://github.com/jesseray718/openroot/pull/38
  files: bin/palm.py bin/bootstrap_openroot_stack.sh docs/SESSION_20260904_MIX.md
- local still dirty-untracked; tracked edits in stash@{0} 20260904-openroot-dirty-tracked
- do not git add -A | pull | clean -fd | reset --hard
- outbox/ gitignored; pin also at docs/SESSION_20260904_MIX.md

## Mix you built (not orq)
ms path = sqlite theorems + codebase_fts
file 7B = aider
chat 7B = or_coder generate (sick)
cloud = Gemini/OpenRouter/Grok apps + keys, not in or_coder.py
geometry working set = 50 dome rows + 3 theorems
Fuller books = not ingested

## Next / do-not
- test pipeline commands in prior turn
- do not ingest_fuller_v3 (copyright + DROP)
- do not orq ask until generate returns
- do not review *.db
- merge PR 38 only if those 3 files should hit main
