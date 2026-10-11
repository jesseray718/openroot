#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Read-only Aerocement evidence compiler.

Reads a Kai sandbox corpus, ranks Aerocement-relevant documents, optionally
embeds selected evidence through local Ollama, and writes a disposable review
bundle. It never writes to the source corpus or Git worktree and never invokes
GitHub, git commit, git push, or a PR mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import textwrap
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOPIC = "aerocement"
SOURCE_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".rst"}
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".cache",
    "data",
    "logs",
    "quarantine",
}
MAX_FILE_BYTES = 2_000_000
MAX_SOURCE_CHARS = 180_000
EMBED_CHUNK_CHARS = 5_000
EMBED_BATCH_SIZE = 12
PREVIEW_CHARS = 500

TERM_WEIGHTS = {
    "aerocement": 16,
    "aero cement": 16,
    "aircrete": 12,
    "air-crete": 12,
    "foam concrete": 12,
    "foamed concrete": 12,
    "cellular concrete": 10,
    "cementitious foam": 10,
    "lightweight concrete": 8,
    "ferrocement": 5,
    "cement": 2,
    "mortar": 3,
    "aggregate": 3,
    "sand": 2,
    "water-cement": 4,
    "water cement": 4,
    "mix ratio": 5,
    "mixing": 3,
    "foaming": 5,
    "foam": 3,
    "surfactant": 5,
    "curing": 4,
    "density": 4,
    "compressive strength": 5,
    "test": 2,
    "specimen": 3,
    "batch": 3,
    "mold": 2,
    "reinforcement": 3,
    "mesh": 2,
    "fiber": 3,
    "safety": 3,
    "hazard": 3,
    "silica": 4,
    "dust": 3,
    "structural": 3,
}

CLAIM_PATTERNS = {
    "measured_or_observed": re.compile(
        r"\b(measured|observed|recorded|tested|result(?:s)?|"
        r"compressive strength|density was|batch \w+)\b",
        re.IGNORECASE,
    ),
    "target_or_design_intent": re.compile(
        r"\b(target|goal|aim|objective|should|intended|design(?:ed)? to)\b",
        re.IGNORECASE,
    ),
    "hypothesis_or_uncertainty": re.compile(
        r"\b(hypothesis|may|might|could|potentially|possibly|"
        r"unknown|uncertain|to be tested|needs testing)\b",
        re.IGNORECASE,
    ),
    "safety_or_limitation": re.compile(
        r"\b(safety|hazard|warning|respirator|silica|dust|caustic|"
        r"not structural|do not|limitation|risk)\b",
        re.IGNORECASE,
    ),
}

README_SECTIONS = [
    ("Project status", "Experimental open documentation. This draft distinguishes sourced observations, design targets, and hypotheses. It does not establish structural suitability or safety certification."),
    ("What this repository contains", "A provenance-backed compilation of Aerocement-related notes, white papers, process references, and documentation candidates recovered from the approved local corpus."),
    ("Evidence-first scope", "Every substantive statement should be traceable to a source record. Unverified ideas remain labeled as hypotheses or targets rather than being promoted to performance claims."),
    ("Safety boundary", "Cementitious materials, dust, alkalinity, tooling, curing conditions, and any load-bearing use require appropriate safety procedures, material-specific review, and testing. This repository is not a substitute for engineering review or applicable building requirements."),
    ("Reproducibility path", "The intended workflow is: source evidence → documented mix/process proposal → controlled batch record → measurements → reviewable claim update."),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    return raw[:MAX_SOURCE_CHARS].decode("utf-8", errors="replace")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def score_document(path: Path, text: str) -> tuple[int, dict[str, int]]:
    haystack = f"{path.as_posix().lower()}\n{text.lower()}"
    hits: dict[str, int] = {}
    score = 0

    for term, weight in TERM_WEIGHTS.items():
        count = haystack.count(term)
        if count:
            capped = min(count, 20)
            hits[term] = capped
            score += capped * weight

    parts = {p.lower() for p in path.parts}
    if "aerocement" in parts:
        score += 80
    if path.name.lower() in {"readme.md", "white_paper.md", "whitepaper_v1.0.md"}:
        score += 20
    if "license" in path.name.lower():
        score += 5
    if path.suffix.lower() in {".md", ".txt"}:
        score += 3

    return score, hits


def find_candidates(source_root: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(source_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        for name in names:
            path = root_path / name
            try:
                if path.suffix.lower() not in SOURCE_EXTENSIONS:
                    continue
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
                files.append(path)
            except OSError:
                continue
    return sorted(files)


def chunk_text(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= EMBED_CHUNK_CHARS:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + EMBED_CHUNK_CHARS, len(text))
        if end < len(text):
            split = max(
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(". ", start, end),
            )
            if split > start + EMBED_CHUNK_CHARS // 2:
                end = split + 1
        chunks.append(text[start:end].strip())
        start = end
    return [chunk for chunk in chunks if chunk]


def l2_normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude == 0:
        return vector
    return [x / magnitude for x in vector]


def ollama_embed(url: str, model: str, inputs: list[str]) -> list[list[float]]:
    payload = json.dumps(
        {
            "model": model,
            "input": inputs,
            "truncate": True,
            "keep_alive": "10m",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{url.rstrip('/')}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama HTTP {exc.code}: {body[:2000]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    try:
        data = json.loads(body)
        vectors = data["embeddings"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError(f"Unexpected Ollama response: {body[:2000]}") from exc

    if not isinstance(vectors, list) or len(vectors) != len(inputs):
        raise RuntimeError(
            f"Ollama returned {len(vectors) if isinstance(vectors, list) else 'non-list'} "
            f"vectors for {len(inputs)} inputs."
        )

    normalized: list[list[float]] = []
    for vector in vectors:
        if not isinstance(vector, list) or not vector:
            raise RuntimeError("Ollama returned an empty or invalid embedding vector.")
        normalized.append(l2_normalize([float(value) for value in vector]))
    return normalized


def collect_claim_signals(text: str) -> Counter[str]:
    signals: Counter[str] = Counter()
    for label, pattern in CLAIM_PATTERNS.items():
        signals[label] += len(pattern.findall(text))
    return signals


def to_markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_No qualifying evidence documents were found._\n"

    header = "| Rank | Score | Source | Why it ranked |\n|---:|---:|---|---|\n"
    body = []
    for idx, row in enumerate(rows, 1):
        terms = ", ".join(
            f"{term}×{count}" for term, count in sorted(
                row["term_hits"].items(),
                key=lambda item: (-item[1], item[0]),
            )[:8]
        )
        body.append(
            f"| {idx} | {row['score']} | `{row['relative_path']}` | {terms or 'path/topic match'} |"
        )
    return header + "\n".join(body) + "\n"


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_readme(top_docs: list[dict[str, Any]], report: dict[str, Any]) -> str:
    lines = [
        "# Aerocement",
        "",
        "> **Status: generated review draft — not yet published or validated as an engineering specification.**",
        "",
        "## Purpose",
        "",
        "This repository is a provenance-backed open documentation package for the Aerocement material and process concept. It is generated from a local evidence corpus so that future contributors can distinguish original notes, source-linked observations, targets, and unresolved questions.",
        "",
    ]

    for heading, paragraph in README_SECTIONS:
        lines.extend([f"## {heading}", "", paragraph, ""])

    lines.extend(
        [
            "## Current evidence basis",
            "",
            f"This draft was compiled from {report['selected_documents']} Aerocement-relevant documents selected from {report['documents_scanned']} readable local documents. The generated source manifest records hashes and excerpts for review.",
            "",
            "### Highest-ranked source documents",
            "",
            to_markdown_table(top_docs[:10]).rstrip(),
            "",
            "## Claim discipline",
            "",
            "- **Observed or measured statements** require a source record and, where applicable, raw test data.",
            "- **Targets** describe intended performance or design direction and are not results.",
            "- **Hypotheses** are plausible ideas requiring testing.",
            "- **Safety and structural suitability** are explicitly unresolved unless supported by an applicable test record and review.",
            "",
            "## Suggested repository path",
            "",
            "1. Review `provenance/source_manifest.json` and remove irrelevant, private, or uncertain source material.",
            "2. Review `claims/claim_signals.json`; convert only traceable observations into documented claims.",
            "3. Add controlled batch records and measurements before making material-performance statements.",
            "4. Move this reviewed draft into a Git worktree only after the evidence and licensing review is complete.",
            "",
            "## Generated artifacts",
            "",
            "- `provenance/source_manifest.json` — source inventory, hashes, relevance, and excerpts.",
            "- `provenance/excluded_documents.json` — files considered but excluded from the selected set.",
            "- `embeddings/aerocement_embeddings.jsonl` — optional local semantic index.",
            "- `claims/claim_signals.json` — conservative keyword-level claim/safety signals.",
            "- `REVIEW.md` — one-page operator review packet.",
            "- `gate_report.json` — machine-readable pipeline result.",
            "",
            "## License and publication status",
            "",
            "This draft does not select or assert a final license. Each source document must be reviewed for ownership, licensing, and publication intent before any public release.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--model", default="nomic-embed-text:latest")
    parser.add_argument("--max-documents", type=int, default=80)
    parser.add_argument("--embed-top", type=int, default=40)
    parser.add_argument("--no-embed", action="store_true")
    args = parser.parse_args()

    source_root = args.source_root.expanduser().resolve()
    output_root = args.output_root.expanduser().resolve()

    if not source_root.is_dir():
        print(f"[held] source root does not exist: {source_root}", file=sys.stderr)
        return 2

    if output_root.exists():
        print(f"[held] output root already exists: {output_root}", file=sys.stderr)
        return 2

    output_root.mkdir(parents=True)
    for name in ("provenance", "embeddings", "claims", "reports"):
        (output_root / name).mkdir()

    print(f"[stage] source_root={source_root}", flush=True)
    print(f"[stage] output_root={output_root}", flush=True)

    documents: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for path in find_candidates(source_root):
        try:
            text = read_text(path)
            score, term_hits = score_document(path, text)
            relative = path.relative_to(source_root).as_posix()
            documents.append(
                {
                    "relative_path": relative,
                    "absolute_path": str(path),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                    "score": score,
                    "term_hits": term_hits,
                    "preview": normalize_text(text)[:PREVIEW_CHARS],
                    "claim_signals": dict(collect_claim_signals(text)),
                    "_text": text,
                }
            )
        except Exception as exc:
            skipped.append({"path": str(path), "reason": str(exc)})

    documents.sort(key=lambda item: (-item["score"], item["relative_path"]))
    selected = [item for item in documents if item["score"] > 0][:args.max_documents]
    excluded = [
        {
            key: value
            for key, value in item.items()
            if key != "_text"
        }
        for item in documents
        if item not in selected
    ]

    print(
        f"[gate] scanned={len(documents)} selected={len(selected)} "
        f"excluded={len(excluded)} unreadable={len(skipped)}",
        flush=True,
    )

    if not selected:
        print("[held] No Aerocement-relevant documents selected; no draft generated.", file=sys.stderr)
        return 1

    vectors_written = 0
    embedding_errors: list[str] = []
    embedding_dims: set[int] = set()
    index_path = output_root / "embeddings" / "aerocement_embeddings.jsonl"

    if not args.no_embed:
        try:
            probe = ollama_embed(args.ollama_url, args.model, ["Aerocement embedding health check."])
            embedding_dims.add(len(probe[0]))
            print(
                f"[gate] ollama_probe=passed model={args.model} dim={len(probe[0])}",
                flush=True,
            )

            with index_path.open("w", encoding="utf-8") as handle:
                for document in selected[:args.embed_top]:
                    chunks = chunk_text(document["_text"])
                    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
                        batch = chunks[start:start + EMBED_BATCH_SIZE]
                        vectors = ollama_embed(args.ollama_url, args.model, batch)
                        for chunk_number, (chunk, vector) in enumerate(
                            zip(batch, vectors),
                            start=start + 1,
                        ):
                            embedding_dims.add(len(vector))
                            record = {
                                "source_root": str(source_root),
                                "file": document["relative_path"],
                                "sha256": document["sha256"],
                                "chunk": chunk_number,
                                "preview": normalize_text(chunk)[:PREVIEW_CHARS],
                                "embedding": vector,
                            }
                            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
                            vectors_written += 1
                print(
                    f"[gate] embeddings=passed records={vectors_written} dims={sorted(embedding_dims)}",
                    flush=True,
                )
        except Exception as exc:
            embedding_errors.append(str(exc))
            if index_path.exists():
                index_path.unlink()
            print(f"[held] embeddings=unavailable reason={exc}", flush=True)
    else:
        print("[stage] embeddings=skipped by --no-embed", flush=True)

    source_manifest = {
        "schema_version": "1.0",
        "topic": TOPIC,
        "generated_at": now_utc(),
        "source_root": str(source_root),
        "selection_policy": {
            "extensions": sorted(SOURCE_EXTENSIONS),
            "max_file_bytes": MAX_FILE_BYTES,
            "ranking_terms": TERM_WEIGHTS,
            "selected_documents": len(selected),
        },
        "documents": [
            {key: value for key, value in item.items() if key != "_text"}
            for item in selected
        ],
    }

    all_signals: Counter[str] = Counter()
    for document in selected:
        all_signals.update(document["claim_signals"])

    claim_report = {
        "schema_version": "1.0",
        "topic": TOPIC,
        "generated_at": now_utc(),
        "method": "keyword-level signals only; not a factual claim extractor",
        "aggregate_signals": dict(all_signals),
        "documents": [
            {
                "file": document["relative_path"],
                "score": document["score"],
                "signals": document["claim_signals"],
            }
            for document in selected
        ],
        "required_human_review": [
            "Confirm which material/process statements are original observations.",
            "Attach raw data before publishing quantitative performance claims.",
            "Review safety language against actual SDSs, tooling, and local conditions.",
            "Review ownership and licensing before public release.",
            "Do not represent generated prose as independently verified engineering guidance.",
        ],
    }

    gate_report = {
        "check_id": "aerocement-evidence-compiler",
        "status": "ready_for_review" if not embedding_errors else "ready_for_review_with_embedding_warning",
        "topic": TOPIC,
        "generated_at": now_utc(),
        "source_root": str(source_root),
        "output_root": str(output_root),
        "documents_scanned": len(documents),
        "selected_documents": len(selected),
        "excluded_documents": len(excluded),
        "unreadable_documents": len(skipped),
        "embedding_records": vectors_written,
        "embedding_dimensions": sorted(embedding_dims),
        "embedding_errors": embedding_errors,
        "remote_mutation": False,
        "git_mutation": False,
        "source_mutation": False,
        "required_next_gate": "human evidence and licensing review before Git worktree generation",
    }

    write_json(output_root / "provenance" / "source_manifest.json", source_manifest)
    write_json(output_root / "provenance" / "excluded_documents.json", excluded)
    write_json(output_root / "provenance" / "unreadable_documents.json", skipped)
    write_json(output_root / "claims" / "claim_signals.json", claim_report)
    write_json(output_root / "gate_report.json", gate_report)

    top_docs = [
        {key: value for key, value in document.items() if key != "_text"}
        for document in selected
    ]
    (output_root / "README_DRAFT.md").write_text(
        build_readme(top_docs, gate_report),
        encoding="utf-8",
    )

    review = f"""# Aerocement compilation review

## Gate result

```text
{gate_report["status"]}
```

## Source scope

- Source root: `{source_root}`
- Readable text documents scanned: {len(documents)}
- Aerocement-relevant documents selected: {len(selected)}
- Excluded documents: {len(excluded)}
- Unreadable documents: {len(skipped)}
- Semantic index records: {vectors_written}
- Embedding dimensions: {sorted(embedding_dims) or "not generated"}

## Evidence ranking

{to_markdown_table(top_docs[:20])}

## Claim and safety signals

```json
{json.dumps(dict(all_signals), indent=2, sort_keys=True)}
```

## Required human review

- Confirm source ownership, licenses, privacy, and publication intent.
- Check that generated summaries preserve uncertainty and do not invent results.
- Connect only accepted sources to a Git worktree.
- Add controlled batch and test evidence before publishing material-performance or structural claims.
- Make the next Git/PR action only after reviewing this bundle.

## Mutation boundary

This run did not modify the source corpus, a Git repository, a Git index, a branch, GitHub, or any remote.
"""
    (output_root / "REVIEW.md").write_text(review, encoding="utf-8")

    print(f"[banked] manifest={output_root / 'provenance' / 'source_manifest.json'}")
    print(f"[banked] readme_draft={output_root / 'README_DRAFT.md'}")
    print(f"[banked] review={output_root / 'REVIEW.md'}")
    print(f"[banked] gate_report={output_root / 'gate_report.json'}")
    print(f"[gate] AEROCEMENT_EVIDENCE_COMPILATION_READY_FOR_REVIEW")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
