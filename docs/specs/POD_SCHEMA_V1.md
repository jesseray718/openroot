# OPENROOT POD SCHEMA v1
status: SPEC-STAGE — LOCKED FOR HUMAN RATIFICATION. No builder code until ratified.
schema_version: 1
author: jesse (OpenRoot LLC, jesseray718)
license: code GPL-3.0-only / docs CC-BY-SA-4.0
date: 2026-10-13

## PURPOSE
One pod = one domain corpus = one SQLite file + manifest.json + seal.jsonl.
Pods are sovereign, offline-capable, hash-addressed, federatable on shared schema.
Query across pods = UNION over identical schema. No external services inside a pod.

## POD BUNDLE LAYOUT
    mypod/
      pod.db           # everything below (SQLite, WAL)
      manifest.json    # identity, license, model provenance, schema_version
      seal.jsonl       # merkle root chain over doc sha256 set (append-only)

## SQLITE SCHEMA (DDL — normative)

    PRAGMA journal_mode=WAL;

    CREATE TABLE ledger (
      doc_id INTEGER PRIMARY KEY,
      sha256 TEXT UNIQUE NOT NULL,     -- sha256 of raw doc bytes (identity)
      path TEXT NOT NULL,              -- origin path/URI at ingest
      size INTEGER, mtime REAL,
      media_type TEXT,                 -- text|pdf|html|zim-entry|...
      ingested_at TEXT,
      origin_pod TEXT                  -- provenance on federated merge
    );

    CREATE TABLE chunks (
      chunk_id INTEGER PRIMARY KEY,
      doc_sha256 TEXT NOT NULL REFERENCES ledger(sha256),
      ordinal INTEGER,
      section_path TEXT,               -- heading breadcrumb "Math>Calc>Limits"
      text TEXT NOT NULL,
      char_start INTEGER, char_end INTEGER
    );
    CREATE INDEX idx_chunks_doc ON chunks(doc_sha256);

    CREATE VIRTUAL TABLE chunks_fts USING fts5(
      text, section_path,
      content='chunks', content_rowid='chunk_id',
      tokenize='porter unicode61');

    CREATE VIRTUAL TABLE chunk_vec USING vec0(    -- sqlite-vec extension
      chunk_id INTEGER PRIMARY KEY,
      embedding float[768]);                       -- nomic-embed-text dims

    CREATE TABLE embed_cache (
      chunk_sha256 TEXT PRIMARY KEY,   -- sha256(chunk utf-8 text); model-independent
      model TEXT NOT NULL,             -- e.g. nomic-embed-text:v1.5
      embedded_at TEXT);

    CREATE TABLE facets (
      doc_sha256 TEXT NOT NULL,
      key TEXT NOT NULL,
      value TEXT NOT NULL,
      PRIMARY KEY (doc_sha256, key, value));

    CREATE TABLE contributions (
      contrib_id INTEGER PRIMARY KEY,
      doc_sha256 TEXT NOT NULL,
      payload TEXT NOT NULL,            -- JSON observation body
      observer_sig TEXT,                -- optional key fingerprint
      evidence_sha256 TEXT,             -- hash of photo/scan backing claim
      state TEXT NOT NULL DEFAULT 'pending',  -- pending|reviewed|merged|rejected
      reviewed_by TEXT, reviewed_at TEXT);

    CREATE TABLE seals (
      seal_id INTEGER PRIMARY KEY,
      merkle_root TEXT NOT NULL,        -- over sorted ledger.sha256 leaves
      prev_seal TEXT,                   -- hash chain
      sealed_at TEXT, note TEXT);

## RESERVED FACET KEYS (recommend, don't require)
category, geo_bbox, lat, lon, season_start, season_end, altitude_min_m,
altitude_max_m, time_of_day, difficulty, source_license. Pods may add keys freely;
union queries only guarantee the reserved set.

## CHUNKING RULES
1. Split at heading/section boundaries first (section_path records the breadcrumb).
2. Hard cap 500 words per chunk, floor 40. Oversized sections split at paragraph seams.
3. No overlap (sections are disjoint). No word-level chunks — rejected: token matching
   destroys context semantics and explodes index size.
4. Chunk identity = sha256(chunk utf-8 text), independent of model and pod.

## DEDUP HIERARCHY (strict order — never skip)
file sha256 (skip known docs) -> chunk sha256 (skip known chunks) -> embed_cache
(chunk_sha256+model). Identical text appearing in 10 pods = ONE embedding anywhere.

## HYBRID QUERY CONTRACT
INPUT : {q, filters:{facet:value,...}, top_k, mode:auto|keyword|semantic}
PIPE  : FTS5 bm25 over chunks_fts joined to facets (filtered) -> top 50 chunk_ids
        embed(q) -> cosine vs chunk_vec restricted to candidates
        fuse: score = 0.6*bm25_norm + 0.4*cosine
OUTPUT: {chunks:[{chunk_id, doc_sha256, text, section_path, score,
        provenance:{path, origin_pod}}]}   -- every answer cites its hashes

## CONTRIBUTION PROTOCOL
Observations enter as contributions (state=pending). A human or trusted reviewer
moves state to reviewed -> merged (payload inserted into chunks/facets) or rejected.
Observer sig + evidence_sha256 optional but recorded. Merges append a new seal.
Truthfulness is procedural (review), not cryptographic — hashes prove integrity,
not correctness. Never conflate the two in marketing or code.

## SEAL PROTOCOL
Sealing = merkle root over sorted ledger.sha256, chained (prev_seal), appended to
seal.jsonl. Any consumer recomputes and compares. Mismatch = tombstone, never delete.

## INVARIANTS
- Idempotent ingest: re-running the builder on unchanged sources yields byte-identical pod.db.
- Qdrant is FORBIDDEN inside a pod; federation layer only, threshold ~5M vectors.
- Single-writer ingest (owner); readers unlimited (WAL).
- schema_version in manifest.json; migrations append-only, never mutate existing columns.

## NON-GOALS (v1)
Word-level granularity. Live scraping (dumps only). Multi-writer concurrency.
Distributed consensus (contributions are reviewed centrally per pod).

## RATIFICATION
Human reads, amends or approves. Approval = commit with message referencing
sha256 of this file. Only then does builder code begin.
