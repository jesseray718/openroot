# OpenRoot

**Verifiable local autonomy. Sealed evidence, measured energy, auditable actions, physical work receipts.**

OpenRoot is a decentralized, open-source framework for civilizational regeneration based on permaculture principles, fractal mesh geometry, contribution economics, and direct work attestation.

## Receipt chain

```
v1.0 (genesis):      a5a988e5879eb4f2ce14aadc0c72ae29eded0987b0c3ca9fcf4eeb9cacf5a889
  sealed:            2026-10-18T09:21:54Z
  documents:         14 founding docs
  signed by:         Ed25519 (genesis/genesis_ed25519.pub)

v1.1 (theorem reg):    11f7934c5c1e42ca9303e939bae26425b905c186aa634190d63304092a5bfc57
  sealed:            2026-10-18T11:49:28Z
  parent:            a5a988e5... (v1.0)
  theorems registered: 3
  formal proofs:     pending v1.2
```

## Pod Loader Tool — Make Your Own Pods

OpenRoot ships a pod loader that converts any text into a sealed SQLite3 pod with dual-hash content addressing, FTS5 indexing, and optional nomic embeddings.

### Quick start

```bash
# Ingest a file or directory
python3 bin/pod_loader_v1.py ingest my_pod ./my_docs/

# Optional: generate nomic embeddings
python3 bin/pod_loader_v1.py embed my_pod

# Seal the pod
python3 bin/pod_loader_v1.py seal my_pod

# Query the pod
python3 bin/pod_loader_v1.py query my_pod "your search query"
```

### Pod architecture

- **documents** table: file identity (sha256), path, size, mtime, metadata
- **chunks** table: chunk identity (blake3), doc reference, text, char count
- **chunks_fts** virtual table: FTS5 full-text index with BM25 ranking
- **vectors** table: per-chunk nomic embeddings (blob of floats)
- **pod_meta** table: merkle_root, sealed_at, chunk_count

## Founding corpus (14 documents)

| # | Document | Layer |
|---|---|---|
| 01 | Trillion Dollar Redirect | Economics |
| 02 | Full Systemic Reallocation Model | Economics |
| 03 | Combined Telecom-Energy Reallocation | Economics |
| 04 | Global Fractal Mesh Framework | Mesh |
| 05 | Societal Transformation | Vision |
| 06 | Aerocement Whitepaper v1.0 | Energy |
| 07 | Aerocement Defensive Publication | IP |
| 08 | Human Continuity Master v1.0 | Resilience |
| 09 | OpenRoot Lumo Context Bridge | Project |
| 10 | Axioms (Euclidean taxonomy) | Foundation |
| 11 | AX-039 Absolute Protection | Governance |
| 12 | Newton Chain Kingdom Engine | Governance |
| 13 | 12 Agape Formalized | Governance |
| 14 | ACRE Specification | Token economics |

## License
- Documentation: CC-BY-SA 4.0
- Code: GPL v3
