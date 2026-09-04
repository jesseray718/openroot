# 2026-09-04 mix pin
- public db: /home/jesse/wisdom-scaffold/data/optiplex_public.db
- codebase_fts rows: 2585375  (tight MATCH \~1.1 ms)
- theorems + V6 cut-list live (THM-001 skips FEA; V6=1080 struts)
- fuller stubs: 2 x 59 words (ingest reserved titles, payload missing)
- ingest live: /home/jesse/wisdom-scaffold/scripts/ingestion/ingest_fuller_v3.py
  sources: archive.org Synergetics djvu.txt + Everything_I_Know_1975_djvu.txt
  DB_PATH relative: optiplex_public.db  (run only from data/ dir if ever)
- nomic tables: /home/jesse/wisdom-scaffold/data/optiplex_index.db
- operator_memory.db events: 10603
- or_coder: LAN Ollama only, no cloud, generate stalling
- aider: /home/jesse/.local/bin/aider
- orq alias: /home/jesse/bin/orq -> knowledge/or_coder.py
- palm.py: /home/jesse/openroot/bin/palm.py
- do not run ingest_fuller_* until copyright/disk call
- do not git add *.db
