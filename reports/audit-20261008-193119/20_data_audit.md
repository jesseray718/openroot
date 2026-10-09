
===== 13. SQLITE / FTS5 CAPABILITY (this python) =====
sqlite 3.45.1 | FTS5 compiled in: True

===== 14. DATABASE INVENTORY UNDER ~/openroot (read-only) =====
found 155 db files; profiling top 25 by size

- openroot/data/fts_index.db  (2116.9 MB, mtime 2026-10-08 18:32)
  * objects (4): table:compost_ledger, table:knowledge_fts, table:sqlite_sequence, table:workspace_lattice
  * row counts: compost_ledger=0; knowledge_fts=111862; sqlite_sequence=0; workspace_lattice=37250

- openroot/data/qa_corpus.db  (1510.4 MB, mtime 2026-09-20 21:16)
  * objects (8): table:answers, table:chunks, table:chunks_fts, table:chunks_fts_config, table:chunks_fts_content, table:chunks_fts_data, table:chunks_fts_docsize, table:chunks_fts_idx
  * FTS virtual tables: chunks_fts
  * row counts: answers=0; chunks=511705; chunks_fts=511705

- openroot/data/file_ledger.db  (410.9 MB, mtime 2026-10-08 04:02)
  * objects (1): table:files
  * row counts: files=888262

- openroot/data/hash_manifest_optiplex.db  (371.1 MB, mtime 2026-09-30 12:53)
  * objects (2): table:hash_manifest, table:manifest
  * row counts: hash_manifest=0; manifest=512755

- openroot/data/embeddings.db  (137.6 MB, mtime 2026-09-27 22:49)
  * SIDECAR: embeddings.db-wal  -> possible hot journal / live writer
  * SIDECAR: embeddings.db-shm  -> possible hot journal / live writer
  * objects (5): table:chunks, table:documents, table:embeddings, table:index_metadata, table:sqlite_sequence
  * row counts: chunks=11110; documents=1; embeddings=1; index_metadata=4; sqlite_sequence=2

- openroot/database/canonical_index.db  (109.4 MB, mtime 2026-10-04 22:56)
  * objects (3): table:canonical_files, table:file_embeddings, table:sqlite_sequence
  * row counts: canonical_files=74281; file_embeddings=0; sqlite_sequence=1

- openroot/openroot_vector.db  (91.7 MB, mtime 2026-10-04 23:13)
  * objects (3): table:canonical_files, table:file_embeddings, table:sqlite_sequence
  * row counts: canonical_files=62166; file_embeddings=41; sqlite_sequence=2

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/universal_index_1789712158.db  (28.1 MB, mtime 2026-09-18 02:27)
  * objects (4): table:audit_log, table:content_classes, table:files, table:qa_templates
  * row counts: audit_log=72; content_classes=6; files=40194; qa_templates=4

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/suggest.sqlite  (23.8 MB, mtime 2026-08-14 15:55)
  * SIDECAR: suggest.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: suggest.sqlite-shm  -> possible hot journal / live writer
  * objects (28): table:amo_custom_details, table:amp_custom_details, table:amp_fts, table:amp_fts_config, table:amp_fts_data, table:amp_fts_docsize, table:amp_fts_idx, table:dismissed_dynamic_suggestions, table:dismissed_suggestions, table:dynamic_custom_details, table:full_keywords, table:geonames, table:geonames_alternates, table:geonames_metrics, table:icons, table:ingested_records, table:keywords, table:keywords_i18n ...
  * FTS virtual tables: amp_fts
  * row counts: amo_custom_details=6; amp_custom_details=4570; amp_fts=0; dismissed_dynamic_suggestions=0; dismissed_suggestions=0; dynamic_custom_details=39; full_keywords=4570; geonames=2924; geonames_alternates=ERR(OperationalError); geonames_metrics=0; icons=204; ingested_records=306; keywords=110992; keywords_i18n=ERR(OperationalError); keywords_metrics=56; mdn_custom_details=20; meta=2; prefix_keywords=45

- openroot/knowledge_index.db  (22.3 MB, mtime 2026-10-05 06:41)
  * objects (7): table:ledger, table:ledger_fts, table:ledger_fts_config, table:ledger_fts_content, table:ledger_fts_data, table:ledger_fts_docsize, table:ledger_fts_idx
  * FTS virtual tables: ledger_fts
  * row counts: ledger=2934; ledger_fts=2934

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/storage/permanent/chrome/idb/3870112724rsegmnoittet-es.sqlite  (19.8 MB, mtime 2026-08-14 19:48)
  * SIDECAR: 3870112724rsegmnoittet-es.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: 3870112724rsegmnoittet-es.sqlite-shm  -> possible hot journal / live writer
  * objects (7): table:database, table:file, table:index_data, table:object_data, table:object_store, table:object_store_index, table:unique_index_data
  * row counts: database=1; file=21; object_store=4; object_store_index=2

- openroot/data/agapenet_kb_v2.db  (16.9 MB, mtime 2026-10-02 19:51)
  * objects (10): table:jobs, table:ledger, table:sqlite_sequence, table:tidbits, table:tidbits_config, table:tidbits_content, table:tidbits_data, table:tidbits_docsize, table:tidbits_idx, table:vectors
  * FTS virtual tables: tidbits
  * row counts: jobs=2; ledger=0; sqlite_sequence=1; tidbits=1534; vectors=0

- openroot/data/dedup_ledger.db  (12.7 MB, mtime 2026-09-27 23:47)
  * objects (1): table:files
  * row counts: files=23047

- openroot/data/ecosystem_v2.db  (9.9 MB, mtime 2026-10-08 06:44)
  * objects (2): table:gates, table:repairs
  * row counts: gates=30998; repairs=0

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/domain_to_categories.sqlite  (8.7 MB, mtime 2026-08-14 20:35)
  * SIDECAR: domain_to_categories.sqlite-journal  -> possible hot journal / live writer
  * objects (2): table:domain_to_categories, table:moz_meta
  * row counts: domain_to_categories=72939; moz_meta=1

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/places.sqlite  (5.2 MB, mtime 2026-08-14 20:40)
  * SIDECAR: places.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: places.sqlite-shm  -> possible hot journal / live writer
  * objects (21): table:moz_anno_attributes, table:moz_annos, table:moz_bookmarks, table:moz_bookmarks_deleted, table:moz_historyvisits, table:moz_historyvisits_extra, table:moz_inputhistory, table:moz_items_annos, table:moz_keywords, table:moz_meta, table:moz_newtab_shortcuts_interaction, table:moz_newtab_story_click, table:moz_newtab_story_impression, table:moz_origins, table:moz_places, table:moz_places_extra, table:moz_places_metadata, table:moz_places_metadata_search_queries ...
  * row counts: moz_anno_attributes=2; moz_annos=2; moz_bookmarks=12; moz_bookmarks_deleted=0; moz_historyvisits=614; moz_historyvisits_extra=0; moz_inputhistory=3; moz_items_annos=0; moz_keywords=0; moz_meta=1; moz_newtab_shortcuts_interaction=259; moz_newtab_story_click=0; moz_newtab_story_impression=653; moz_origins=41; moz_places=423; moz_places_extra=0; moz_places_metadata=532; moz_places_metadata_search_queries=0

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/favicons.sqlite  (5.2 MB, mtime 2026-08-14 20:40)
  * SIDECAR: favicons.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: favicons.sqlite-shm  -> possible hot journal / live writer
  * objects (4): table:moz_icons, table:moz_icons_to_pages, table:moz_pages_w_icons, table:sqlite_stat1
  * row counts: moz_icons=49; moz_icons_to_pages=663; moz_pages_w_icons=341; sqlite_stat1=3

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/termux-home-rescue/data/mesh_index.db  (2.8 MB, mtime 2026-09-13 12:28)
  * objects (1): table:files
  * row counts: files=7564

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/storage/default/https+++lumo.proton.me/idb/1066234074LDu3m%oADEBh_CdLC4I49.sqlite  (2.5 MB, mtime 2026-08-14 19:44)
  * SIDECAR: 1066234074LDu3m%oADEBh_CdLC4I49.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: 1066234074LDu3m%oADEBh_CdLC4I49.sqlite-shm  -> possible hot journal / live writer
  * objects (7): table:database, table:file, table:index_data, table:object_data, table:object_store, table:object_store_index, table:unique_index_data
  * row counts: database=1; file=0; object_store=7; object_store_index=5

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/agape_rag.db  (1.8 MB, mtime 2026-09-18 01:36)
  * objects (7): table:chunks, table:chunks_fts, table:chunks_fts_config, table:chunks_fts_content, table:chunks_fts_data, table:chunks_fts_docsize, table:chunks_fts_idx
  * FTS virtual tables: chunks_fts
  * row counts: chunks=267; chunks_fts=267

- openroot/data/newton_chain.db  (1.3 MB, mtime 2026-09-30 16:56)
  * objects (14): table:artifacts, table:audit_log, table:chain, table:edges, table:meta, table:node_fts, table:node_fts_config, table:node_fts_content, table:node_fts_data, table:node_fts_docsize, table:node_fts_idx, table:nodes, table:receipts, table:sqlite_sequence
  * FTS virtual tables: node_fts
  * row counts: artifacts=120; audit_log=369; chain=3; edges=233; meta=2; node_fts=135; nodes=135; receipts=1; sqlite_sequence=1

- openroot/context_bridge/lumo_inbox/ingested.sqlite  (1.0 MB, mtime 2026-09-30 02:09)
  * objects (6): table:msgs, table:msgs_fts, table:msgs_fts_config, table:msgs_fts_data, table:msgs_fts_docsize, table:msgs_fts_idx
  * FTS virtual tables: msgs_fts
  * row counts: msgs=579; msgs_fts=579

- openroot/consolidation-backups/untracked_collision_20260919-072429/logs/terminal_rag.sqlite  (0.9 MB, mtime 2026-09-12 05:31)
  * objects (1): table:chunks
  * row counts: chunks=50

- openroot/data/doc_index.db  (0.9 MB, mtime 2026-09-21 04:00)
  * objects (6): table:fts_docs, table:fts_docs_config, table:fts_docs_content, table:fts_docs_data, table:fts_docs_docsize, table:fts_docs_idx
  * FTS virtual tables: fts_docs
  * row counts: fts_docs=64

- openroot/data/sdcard-sync/kit/chunk_index.sqlite  (0.9 MB, mtime 2026-09-12 20:57)
  * objects (3): table:chunks, table:files, table:sqlite_sequence
  * row counts: chunks=1522; files=1342; sqlite_sequence=2

===== 15. NEWTON CHAIN LEDGER =====

- archives/openroot (1)/agape_kb/newton_chain.jsonl  (0.0 MB, mtime 2026-08-05 13:54)
  * lines=1  valid_json=1  malformed=0
  * key union (8): axiom, derived_from, eta_value, id, layer, statement, timestamp, verified
  * timestamps: first-seen=2026-08-05T18:54:56.398903+00:00  last-seen=2026-08-05T18:54:56.398903+00:00
  * NOTE: no explicit unit/energy keys in key union — schema may lack units.
  * first entry (trunc): {"id": "G00_be5fe075", "axiom": "LAYER1_GATE", "statement": "IF (DERIVATION) AND (R=1.0) THEN execute derivation at layer 1, targeting lowest η node", "layer": 1, "eta_value": 1.0, "verified": true, "derived_from": ["A1", "A2"], "timestamp"

- openroot/data/newton_chain.jsonl  (0.0 MB, mtime 2026-10-05 06:41)
  * lines=3  valid_json=3  malformed=0
  * key union (5): current_hash, index, payload, previous_hash, timestamp
  * timestamps: first-seen=2026-10-05T11:11:31.834243+00:00  last-seen=2026-10-05T11:41:27.903766+00:00
  * NOTE: no explicit unit/energy keys in key union — schema may lack units.
  * first entry (trunc): {"index": 0, "timestamp": "2026-10-05T11:11:31.834243+00:00", "payload": {"event": "GENESIS", "description": "Newton Chain Thermodynamic Ledger Initialized"}, "previous_hash": "000000000000000000000000000000000000000000000000000000000000000
  * last entry (trunc): {"index": 2, "timestamp": "2026-10-05T11:41:27.903766+00:00", "payload": {"work_type": "AERO_DISC_RUN", "joules_recorded": 1420.5, "node_id": "optiplex3060", "status": "VERIFIED"}, "previous_hash": "31bbc00f9c0ba1ccbdb7bae8322e3e84da99605d6

- snap/openroot (1)/agape_kb/newton_chain.jsonl  (0.0 MB, mtime 2026-08-05 13:54)
  * lines=1  valid_json=1  malformed=0
  * key union (8): axiom, derived_from, eta_value, id, layer, statement, timestamp, verified
  * timestamps: first-seen=2026-08-05T18:54:56.398903+00:00  last-seen=2026-08-05T18:54:56.398903+00:00
  * NOTE: no explicit unit/energy keys in key union — schema may lack units.
  * first entry (trunc): {"id": "G00_be5fe075", "axiom": "LAYER1_GATE", "statement": "IF (DERIVATION) AND (R=1.0) THEN execute derivation at layer 1, targeting lowest η node", "layer": 1, "eta_value": 1.0, "verified": true, "derived_from": ["A1", "A2"], "timestamp"

===== 16. ACRE-0001 / PoPW RECORD =====
- /home/jesse/archives/openroot (1)/acre/claims/ACRE-0001-seed-core-aero-disc.json (1088 bytes, mtime 2026-08-01 16:23)
  head: {   "claim_id": "ACRE-0001",   "type": "PoPW_contextual_absorption",   "timestamp": "2026-08-01T16:19:00-05:00",   "actor": "jesse@openroot.earth",   "work_description": "Absorption of Aero-Disc volumetric exchanger primitive + complete Seed Core (16 foundational optimization seeds) into durable inter-session lattice",   "physical_component": "Aero-Disc Path A cardboard disc design + porous_exchan
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_skills_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:16)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_github-repos_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:15)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:16)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_openroot-ecosystem_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:15)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:16)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/tokens/ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-17 05:39)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot-lattice/openroot/tokens/ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-08-14 00:21)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de

===== 17. LARGE FILES & DUPLICATE CANDIDATES (>= 20 MB) =====
Skipped reinstallable caches (.cache/.ollama/.npm/snap/.local/node_modules/venv/.git).
Top 40 largest files:
  140737471.6 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/core
   14537.1 MB  ~/archives/termux-full-backup-20260809-2143.tar.gz
   12978.4 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/archive.zip
    5477.2 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260819_221848.tar.xz
    5477.2 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260819_221848.tar.xz
    5476.5 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
    5476.5 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
    5200.6 MB  ~/wisdom-scaffold/data/optiplex_public.db
    5200.6 MB  ~/wisdom-recovery/20260904-024705/wisdom-scaffold/data/optiplex_public.db
    4920.7 MB  ~/optiplex-archive/New-folder/Alarms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    4920.7 MB  ~/optiplex-archive/New-folder/Alarms/Download/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    4295.0 MB  ~/archives/critical.tar.gz
    3996.7 MB  ~/optiplex-archive/New-folder/agape_recovery/critical_files/termux_backup_20260702_221906.tar.gz
    3996.7 MB  ~/optiplex-archive/New-folder/Alarms/termux_backup_20260702_221906.tar.gz
    3996.7 MB  ~/archives/termux_backup_20260702_221906.tar.gz
    3619.5 MB  ~/optiplex-archive/New-folder/Alarms/home_backup_20260724.tar.gz
    3619.5 MB  ~/archives/home_backup_20260724.tar.gz
    3186.2 MB  ~/optiplex-archive/New-folder/agape_recovery/critical_files/alchemy_archive_20260724_024327.tar.gz
    3186.2 MB  ~/optiplex-archive/New-folder/Alarms/openroot_usb_stage/openroot/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
    3186.2 MB  ~/optiplex-archive/New-folder/Alarms/openroot (2)/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
    2796.8 MB  ~/archives/home_backup_20260724.tar (1).gz
    2393.2 MB  ~/optiplex-archive/New-folder/Kai_Termux_Shared/phi-3-mini-q4.gguf
    2116.9 MB  ~/openroot/data/fts_index.db
    1890.3 MB  ~/archives/OpenRootArchives/20260810/openroot-pre-consolidation-backup-2148.tar.xz
    1758.9 MB  ~/kai_recovery/openroot/lumo_inbox/incoming/kai_extract_20260928_015017.tar.gz
    1758.9 MB  ~/harvest_hold/kai_import_20260928_015017.tar.gz
    1697.9 MB  ~/openroot/lumo_inbox/expanded/kai_extract_20260928_015017.bca6fe9a/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1697.9 MB  ~/kai_recovery/extracted/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1697.9 MB  ~/harvest_hold/kai_deep_harvest_20260928_024955/nested/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1510.4 MB  ~/openroot/data/qa_corpus.db
    1317.8 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260821_160013.tar.xz
    1317.8 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260821_160013.tar.xz
    1312.5 MB  ~/harvest_hold/a15_backup/termux_20260928_191232/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
    1312.5 MB  ~/harvest_hold/a15_backup/termux_20260928_190708/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
    1223.0 MB  ~/archives/OpenRootArchives/20260810/backups-2203.tar.xz
    1209.8 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/storage/emulated/0/Documents/old-downloads.tar.gz
    1209.8 MB  ~/archives/old-downloads.tar.gz
    1209.2 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/bc7527e5dc6cf30d/data/data/com.termux/files/home/downloads/termux_backup_20260702_221906.tar.gz
    1127.6 MB  ~/optiplex-archive/New-folder/Alarms/phone_backup/termux/termux_backup.tar.gz
    1118.9 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/auto_20260721_200420.log

Same-size duplicate groups (verify before deleting anything):
    5477.2 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260819_221848.tar.xz
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260819_221848.tar.xz
    5476.5 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
    5200.6 MB x2:
      ~/wisdom-scaffold/data/optiplex_public.db
      ~/wisdom-recovery/20260904-024705/wisdom-scaffold/data/optiplex_public.db
    4920.7 MB x2:
      ~/optiplex-archive/New-folder/Alarms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
      ~/optiplex-archive/New-folder/Alarms/Download/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    3996.7 MB x3:
      ~/optiplex-archive/New-folder/agape_recovery/critical_files/termux_backup_20260702_221906.tar.gz
      ~/optiplex-archive/New-folder/Alarms/termux_backup_20260702_221906.tar.gz
      ~/archives/termux_backup_20260702_221906.tar.gz
    3619.5 MB x2:
      ~/optiplex-archive/New-folder/Alarms/home_backup_20260724.tar.gz
      ~/archives/home_backup_20260724.tar.gz
    3186.2 MB x3:
      ~/optiplex-archive/New-folder/agape_recovery/critical_files/alchemy_archive_20260724_024327.tar.gz
      ~/optiplex-archive/New-folder/Alarms/openroot_usb_stage/openroot/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
      ~/optiplex-archive/New-folder/Alarms/openroot (2)/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
    1758.9 MB x2:
      ~/kai_recovery/openroot/lumo_inbox/incoming/kai_extract_20260928_015017.tar.gz
      ~/harvest_hold/kai_import_20260928_015017.tar.gz
    1697.9 MB x3:
      ~/openroot/lumo_inbox/expanded/kai_extract_20260928_015017.bca6fe9a/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
      ~/kai_recovery/extracted/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
      ~/harvest_hold/kai_deep_harvest_20260928_024955/nested/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1317.8 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260821_160013.tar.xz
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260821_160013.tar.xz
    1312.5 MB x2:
      ~/harvest_hold/a15_backup/termux_20260928_191232/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
      ~/harvest_hold/a15_backup/termux_20260928_190708/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
    1209.8 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/storage/emulated/0/Documents/old-downloads.tar.gz
      ~/archives/old-downloads.tar.gz
    1118.9 MB x3:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/auto_20260721_200420.log
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/storage/emulated/0/Documents/terminal-logs/auto_20260721_200420.log
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/auto_20260721_200420.log
    1117.3 MB x2:
      ~/optiplex-archive/New-folder/Alarms/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/5ed3729d0c9f1d85/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
    1117.3 MB x4:
      ~/optiplex-archive/New-folder/Kai_Termux_Shared/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
      ~/optiplex-archive/New-folder/Alarms/qwen2.5-1.5b-instruct-q4_k_m.gguf
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/5ed3729d0c9f1d85/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/5ed3729d0c9f1d85/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf

===== 18. SHELL-ESCAPE ARTIFACT FILENAMES (junk from unquoted heredocs) =====
Found 39 candidates (first 60). Some may be legit files; nothing is deleted:
  ' \\){DATA}'
  ' \\){ROOT}'
  ' \\){WISDOM}'
  'Android (1)'
  'Perplexity-AI-4.0.0-Linux(1).AppImage'
  'THEORETICAL_CLAIMS (1).jsonl'
  '[2600:6c40:2a3f:c289:dbf3:38bb:38ce:2787]:22000:'
  '[fd00:e4c0:e268:80ea:1cf3:192d:e6ab:e86c]:22000:'
  '[fd00:e4c0:e268:80ea:2cad:5610:355b:8c1a]:22000:'
  '[fd00:e4c0:e268:80ea:34d4:feff:fe16:a624]:22000:'
  '\\( HOME'
  '\\( {RAG}'
  '\\( {ROOT}'
  '\\( {WISDOM}'
  'archives/Download (1)'
  'archives/USB storage 1 (1).zip'
  'archives/USB storage 1 (2).zip'
  'archives/USB storage 1 (3).zip'
  'archives/USB storage 1 (4).zip'
  'archives/USB storage 1 (5).zip'
  'archives/USB storage 1 (6).zip'
  'archives/home_backup_20260724.tar (1).gz'
  'archives/kai9000-export-20260801_183632.tar (1).zip'
  'archives/kai9000-export-20260801_183632.tar (2).zip'
  'archives/kai9000-export-20260801_183632.tar (3).zip'
  'archives/kai9000-export-20260801_183632.tar (4).zip'
  'archives/kai9000-export-20260801_183632.tar (5).zip'
  'archives/openroot (1)'
  'archives/pack-b860d9de5ec23a303c96036761cffebcbd5c8292 (1).zip'
  'crowdfund-campaign (1)'
  'kai-settings (1).json'
  'snap/Download (1)'
  'snap/crowdfund-campaign (1)'
  'snap/openroot (1)'
  'une-push/{'
  'une-push/}'
  'une/{'
  'une/}'
  '{'

===== 19. BACKUP-FILE CHURN =====
20 backup files in ~/openroot/bin (iterative-repair history):
  a1_core_v1.py.pre_ledger_scan_repair.20260926T214957Z.bak
  a1_core_v1.py.pre_ledger_scan_repair.20260926T214851Z.bak
  handoff_manager.py.pre_session_id_collision_fix.20260926T220915Z.bak
  handoff_manager.py.pre_start_idempotency_fix.20260926T220804Z.bak
  bot_loop_v1.py.backup_20260923
  launch_ladder_v1.py.pre_mistake_runner_fix.20260926T210256Z.bak
  handoff_manager.py.pre_session_id_format_fix.20260926T221628Z.bak
  handoff_manager.py.pre_session_id_format_fix.20260926T221515Z.bak
  a1_core_v1.py.pre_bounded_roots.20260926T215133Z.bak
  handoff_manager.py.pre_session_id_collision_fix.20260926T220956Z.bak
  launch_ladder_v1.py.pre_registration_fix_v2.20260926T201522Z.bak
  handoff_manager.py.pre_single_session_repair.20260926T220226Z.bak
  handoff_manager.py.pre_end_session_tuple_fix.20260926T220321Z.bak
  launch_ladder_v1.py.pre_mistake_runner_fix_v2.20260926T210713Z.bak
  handoff_manager.py.pre_secrets_import.20260926T221131Z.bak
Recommendation: move .bak history into git history instead of sibling files.

===== 20. ACTIVE BOT STATE SNAPSHOT =====
- data_bot_state.json (mtime 2026-10-08 19:38):
  {
  "snapshots": {
    "/sdcard/openroot/thermo_ledger/eta_moves.jsonl": "missing",
    "/sdcard/openroot/parallel_analysis/ledger/ideas.jsonl": "missing",
    "/sdcard/openroot/ledger/experiments/linux_command_persistence.jsonl": "missing"
  },
  "cycles": 3223,
  "last_ts": 1791506286.2410588
}

- ~/.openroot_tap.tsv (mtime 2026-10-08 19:31), first 5 lines:
  20260925_050350	0	git push
  20260925_050401	0	cd openroot
  20260925_050411	1	gh stack checkout 61
  20260925_050434	1	gh stack rebase
  20260925_050442	1	gh stack push
