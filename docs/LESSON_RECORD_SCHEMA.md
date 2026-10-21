# Lesson Record Schema v1
CANARY: LESSON_SCHEMA_V1_20260924

Records: `data/lessons.jsonl` (append-only, JSONL, one record per line)

Fields:
- lesson_id: "LRN-YYYYMMDD-short-slug" (unique)
- created_at: ISO-8601
- status: draft | verified | superseded  (graduation to verified is human-gated)
- domain: shell | python | git | networking | hardware | research
- problem: what failed
- root_cause: why it failed
- solution: what corrected it
- verification: exact check proving the correction
- evidence: list of {type, reference} (commit hash, command, file, test witness)
- safety_notes: conditions and boundaries

License: CC-BY-SA-4.0 (documentation commons)
