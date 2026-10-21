#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
PY="/home/jesse/openroot/bin/openroot_knowledge_intake_v1.py"
ROOT="/home/jesse/openroot/data/openroot_knowledge"
DB="/home/jesse/openroot/data/openroot_knowledge/openroot_knowledge.db"

cd "$REPO"
mkdir -p "$ROOT"/{sources,claims,case_studies,pattern_blockers,blueprints,exports}

cat <<'PY' >"$PY"
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
OpenRoot evidence-first knowledge intake.

Stores auditable source metadata, falsifiable claims, case studies, and
nonviolent defensive pattern blockers. It intentionally does not treat any
political, historical, financial, or religious assertion as settled merely
because it is added to the database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO = Path("/home/jesse/openroot")
ROOT = REPO / "data" / "openroot_knowledge"
DB = ROOT / "openroot_knowledge.db"
TAG = "[OPENROOTKNOWLEDGEV1]"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS documents (
    sha256 TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    local_path TEXT,
    source_url TEXT,
    author TEXT,
    publisher TEXT,
    publication_year INTEGER,
    source_type TEXT NOT NULL,
    license_note TEXT,
    acquired_at TEXT NOT NULL,
    added_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    document_sha256 TEXT,
    statement TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    confidence TEXT NOT NULL,
    evidence_locator TEXT,
    falsification_test TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unreviewed',
    created_at TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(document_sha256) REFERENCES documents(sha256)
);

CREATE TABLE IF NOT EXISTS case_studies (
    case_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    system_domain TEXT NOT NULL,
    period TEXT,
    summary TEXT NOT NULL,
    alleged_mechanism TEXT NOT NULL,
    measurable_harm TEXT,
    evidence_standard TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'research_queue',
    created_at TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS pattern_blockers (
    blocker_id TEXT PRIMARY KEY,
    pattern_name TEXT NOT NULL,
    threat_model TEXT NOT NULL,
    early_signals TEXT NOT NULL,
    nonviolent_response TEXT NOT NULL,
    verification TEXT NOT NULL,
    owner_control TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS knowledge_nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    path_or_uri TEXT NOT NULL,
    parent_id TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_case_studies_status ON case_studies(status);
CREATE INDEX IF NOT EXISTS idx_pattern_blockers_status ON pattern_blockers(status);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON knowledge_nodes(node_type);
"""


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def node_id(kind: str, label: str) -> str:
    return f"{kind}:{digest(label.encode('utf-8'))[:20]}"


def connect() -> sqlite3.Connection:
    ROOT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.commit()
    return con


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def register_document(
    con: sqlite3.Connection,
    name: str,
    source_url: str,
    author: str,
    publisher: str,
    year: int | None,
    source_type: str,
    license_note: str,
    metadata: dict,
) -> str:
    payload = canonical_json(
        {
            "name": name,
            "source_url": source_url,
            "author": author,
            "publisher": publisher,
            "year": year,
            "source_type": source_type,
            "license_note": license_note,
            "metadata": metadata,
        }
    ).encode("utf-8")
    sha = digest(payload)
    timestamp = now()
    con.execute(
        """
        INSERT INTO documents(
            sha256, canonical_name, local_path, source_url, author, publisher,
            publication_year, source_type, license_note, acquired_at, added_at,
            metadata_json
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(sha256) DO UPDATE SET
            canonical_name=excluded.canonical_name,
            source_url=excluded.source_url,
            author=excluded.author,
            publisher=excluded.publisher,
            publication_year=excluded.publication_year,
            source_type=excluded.source_type,
            license_note=excluded.license_note,
            metadata_json=excluded.metadata_json
        """,
        (
            sha,
            name,
            "",
            source_url,
            author,
            publisher,
            year,
            source_type,
            license_note,
            timestamp,
            timestamp,
            canonical_json(metadata),
        ),
    )
    con.execute(
        """
        INSERT INTO knowledge_nodes(
            node_id,node_type,label,sha256,path_or_uri,parent_id,created_at,metadata_json
        ) VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(node_id) DO UPDATE SET
            sha256=excluded.sha256,
            path_or_uri=excluded.path_or_uri,
            metadata_json=excluded.metadata_json
        """,
        (
            node_id("document", name),
            "document",
            name,
            sha,
            source_url,
            None,
            timestamp,
            canonical_json({"source_type": source_type}),
        ),
    )
    return sha


def seed(con: sqlite3.Connection) -> None:
    docs = [
        {
            "name": "A People's History of the United States",
            "url": "https://www.zinnedproject.org/materials/peoples-history-of-the-united-states/",
            "author": "Howard Zinn",
            "publisher": "HarperCollins / Zinn Education Project reference",
            "year": 1980,
            "source_type": "book_reference",
            "license": "Citation and metadata only; obtain text lawfully.",
            "metadata": {
                "scope": "bottom-up U.S. social history",
                "use": "research starting point, not sole authority",
                "verification": "cross-check claims against primary sources and independent scholarship",
            },
        },
        {
            "name": "The Emperor Wears No Clothes",
            "url": "https://reason.com/1993/06/01/selling-pot/",
            "author": "Jack Herer",
            "publisher": "Book reference / contemporary review source",
            "year": 1985,
            "source_type": "book_reference",
            "license": "Citation and metadata only; obtain text lawfully.",
            "metadata": {
                "scope": "hemp and cannabis history, industrial uses, drug-policy critique",
                "use": "claim discovery only",
                "verification": "separate documented fact, interpretation, and advocacy",
            },
        },
        {
            "name": "War Is a Racket",
            "url": "https://archive.org/stream/WarIsARacket/WarIsARacket_djvu.txt",
            "author": "Smedley D. Butler",
            "publisher": "Round Table Press",
            "year": 1935,
            "source_type": "primary_text",
            "license": "Verify jurisdictional public-domain status before redistribution.",
            "metadata": {
                "scope": "antiwar political critique",
                "use": "historical primary-source analysis",
                "verification": "distinguish Butler's argument from independently established facts",
            },
        },
        {
            "name": "The Art of War",
            "url": "https://en.wikisource.org/wiki/The_Art_of_War_(Sun)",
            "author": "Sun Tzu",
            "publisher": "Public-domain translation reference",
            "year": None,
            "source_type": "classical_text",
            "license": "Verify edition and translation rights before copying.",
            "metadata": {
                "scope": "strategy",
                "use": "nonviolent resilience, preparation, and conflict de-escalation only",
                "prohibited_use": "harm, coercion, evasion of law, or targeting people",
            },
        },
    ]
    by_name: dict[str, str] = {}
    for d in docs:
        by_name[d["name"]] = register_document(
            con,
            d["name"],
            d["url"],
            d["author"],
            d["publisher"],
            d["year"],
            d["source_type"],
            d["license"],
            d["metadata"],
        )

    claims = [
        (
            "claim:research-standard",
            None,
            "Historical, political, financial, and policy claims require attributable evidence, a confidence label, and a stated falsification test before being promoted beyond research status.",
            "methodological",
            "high",
            "Database inspection must show source linkage or explicit absence, confidence, and falsification criteria.",
            "A counterexample is any promoted claim lacking those fields.",
            "accepted",
            "Core OpenRoot epistemic guardrail.",
        ),
        (
            "claim:drug-policy-market-comparison",
            by_name["The Emperor Wears No Clothes"],
            "Claims about drug prohibition, regulated markets, public health, taxation, purity, or criminal-market effects must be separated into measurable policy outcomes and evaluated with jurisdiction-specific evidence.",
            "policy_hypothesis",
            "medium",
            "Compare mortality, contamination, treatment access, arrests, price, tax receipts, and illicit-market indicators across specified jurisdictions and periods.",
            "Credible comparative evidence showing no relationship, reverse relationship, or a different causal mechanism weakens or falsifies the stated hypothesis.",
            "research_queue",
            "No universal legalization conclusion is stored as fact.",
        ),
        (
            "claim:war-profit-incentives",
            by_name["War Is a Racket"],
            "War-related procurement and financing can create concentrated economic incentives; each asserted causal pathway requires contracts, budgets, ownership records, and counterfactual analysis.",
            "historical_economic_hypothesis",
            "medium",
            "Trace dated procurement, financing, beneficiary, and decision records for a defined conflict.",
            "If records do not support the claimed pathway or show stronger alternative explanations, revise or reject the claim.",
            "research_queue",
            "Butler is stored as an argument and primary text, not conclusive proof.",
        ),
        (
            "claim:bitcoin-governance",
            None,
            "Bitcoin's design goals, governance, adoption, regulation, custodial concentration, and market structure should be analyzed as distinct, time-bounded claims rather than as a single intentional-control narrative.",
            "technology_governance_hypothesis",
            "medium",
            "Use protocol history, public repositories, regulatory records, custody concentration data, and dated market-structure evidence.",
            "Claims of coordinated manipulation require direct, independently corroborated evidence of coordination.",
            "research_queue",
            "Avoids converting suspicion into an untestable assertion.",
        ),
        (
            "claim:open-verifiable-knowledge",
            None,
            "A content-addressed ledger can improve auditability and deduplication when records preserve SHA-256, provenance, licenses, timestamps, and falsifiable claim links.",
            "systems_design",
            "medium",
            "Measure duplicate detection, retrieval accuracy, provenance completeness, and reproducible verification rates against a baseline.",
            "If the system cannot reproduce hashes or provenance links, the claim fails operationally.",
            "accepted",
            "Aligns with A1 ledger and future public verification work.",
        ),
    ]
    for cid, sha, statement, kind, confidence, evidence, falsification, status, notes in claims:
        con.execute(
            """
            INSERT INTO claims(
                claim_id,document_sha256,statement,claim_type,confidence,
                evidence_locator,falsification_test,status,created_at,notes
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(claim_id) DO UPDATE SET
                document_sha256=excluded.document_sha256,
                statement=excluded.statement,
                claim_type=excluded.claim_type,
                confidence=excluded.confidence,
                evidence_locator=excluded.evidence_locator,
                falsification_test=excluded.falsification_test,
                status=excluded.status,
                notes=excluded.notes
            """,
            (cid, sha, statement, kind, confidence, evidence, falsification, status, now(), notes),
        )

    studies = [
        (
            "case:prohibition-policy",
            "Alcohol prohibition and policy externalities",
            "public_policy",
            "United States, 1920-1933",
            "Research how a legal prohibition changed enforcement burdens, illicit supply, violence, product safety, and post-repeal regulation.",
            "Policy restrictions can displace activity into unregulated markets; magnitude and causality require data.",
            "Use dated public-health, enforcement, economic, and legislative records.",
            "primary_sources_plus_peer_review",
            "research_queue",
            "Do not generalize automatically to all substances or all jurisdictions.",
        ),
        (
            "case:knowledge-extraction",
            "Community knowledge extraction through closed platforms",
            "digital_commons",
            "Contemporary",
            "Research how user-generated knowledge can become locked behind proprietary interfaces, changing access, governance, and value distribution.",
            "Centralized control of storage, ranking, identity, and terms can create dependency and extraction risk.",
            "Terms of service, exportability tests, governance records, and user-impact measures.",
            "mixed_methods",
            "research_queue",
            "OpenRoot response: portable formats, local-first copies, hashes, explicit licenses, and human review.",
        ),
        (
            "case:public-accountability",
            "Public authority transparency and accountability failures",
            "governance",
            "Jurisdiction-specific",
            "Build case studies only from named jurisdictions, dated public records, court filings, audits, and independently corroborated reporting.",
            "Opaque authority and weak oversight can increase abuse risk and reduce correction capacity.",
            "Public records, inspector reports, court records, and reproducible data.",
            "primary_records_required",
            "research_queue",
            "Never create blanket accusations about groups of people.",
        ),
    ]
    for row in studies:
        con.execute(
            """
            INSERT INTO case_studies(
                case_id,title,system_domain,period,summary,alleged_mechanism,
                measurable_harm,evidence_standard,status,created_at,notes
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(case_id) DO UPDATE SET
                title=excluded.title,
                system_domain=excluded.system_domain,
                period=excluded.period,
                summary=excluded.summary,
                alleged_mechanism=excluded.alleged_mechanism,
                measurable_harm=excluded.measurable_harm,
                evidence_standard=excluded.evidence_standard,
                status=excluded.status,
                notes=excluded.notes
            """,
            (*row[:-1], now(), row[-1]),
        )

    blockers = [
        (
            "blocker:single-point-of-failure",
            "Single point of failure",
            "A service, database, identity provider, maintainer, or vendor can halt access or alter terms unilaterally.",
            "No export path; one credential controls all data; undocumented manual recovery; centralized hosting only.",
            "Maintain local-first copies, open formats, content hashes, tested backups, multiple maintainers, and documented recovery drills.",
            "Quarterly restore test proves a new machine can verify and use a complete exported corpus.",
            "Users retain local copies and can independently verify hashes.",
            "draft",
            "Applies to knowledge, automation, and community infrastructure.",
        ),
        (
            "blocker:opaque-claims",
            "Opaque or unfalsifiable claims",
            "High-impact narratives spread without sources, timestamps, definitions, or disconfirming conditions.",
            "Anonymous screenshots; missing primary records; claims that cannot specify what evidence would change the conclusion.",
            "Require claim/source separation, confidence labels, dates, direct quotations with locator fields, competing hypotheses, and falsification tests.",
            "Random audit samples must resolve to sources and clearly state uncertainty.",
            "Any contributor can inspect, challenge, and improve evidence records.",
            "draft",
            "Defends against misinformation without censorship architecture.",
        ),
        (
            "blocker:knowledge-enclosure",
            "Knowledge enclosure",
            "Useful public knowledge becomes inaccessible through paywalls, proprietary formats, unexportable platforms, or unclear rights.",
            "Terms prohibit export; data cannot be opened offline; no license metadata; access depends on a single service.",
            "Store lawful metadata and user-owned notes in open formats; retain SHA-256 provenance; publish original work under clear licenses; respect copyright.",
            "Independent user can export, hash-check, search, and read all locally created OpenRoot records offline.",
            "No claim of ownership over third-party copyrighted texts; use citations and lawful acquisition.",
            "draft",
            "Promotes access without infringement.",
        ),
        (
            "blocker:automation-without-consent",
            "Automation without consent",
            "Automated tools can overwrite work, publish claims, spend resources, or make consequential judgments without review.",
            "Hidden writes; no dry run; no logs; no human gate; unclear rollback.",
            "Use explicit human approval for commits, pushes, deletes, public posting, and consequential external actions; preserve dry-run defaults.",
            "Audit logs show each state-changing action, actor, input hash, and approval event.",
            "Operators retain final control of outputs and external actions.",
            "draft",
            "Matches current OpenRoot commit-gate doctrine.",
        ),
    ]
    for row in blockers:
        con.execute(
            """
            INSERT INTO pattern_blockers(
                blocker_id,pattern_name,threat_model,early_signals,nonviolent_response,
                verification,owner_control,status,created_at,notes
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(blocker_id) DO UPDATE SET
                pattern_name=excluded.pattern_name,
                threat_model=excluded.threat_model,
                early_signals=excluded.early_signals,
                nonviolent_response=excluded.nonviolent_response,
                verification=excluded.verification,
                owner_control=excluded.owner_control,
                status=excluded.status,
                notes=excluded.notes
            """,
            (*row[:-1], now(), row[-1]),
        )
    con.commit()


def status(con: sqlite3.Connection) -> int:
    rows = [
        ("documents", "SELECT COUNT(*) FROM documents"),
        ("claims", "SELECT COUNT(*) FROM claims"),
        ("case_studies", "SELECT COUNT(*) FROM case_studies"),
        ("pattern_blockers", "SELECT COUNT(*) FROM pattern_blockers"),
        ("knowledge_nodes", "SELECT COUNT(*) FROM knowledge_nodes"),
    ]
    for label, sql in rows:
        print(f"{label}={con.execute(sql).fetchone()[0]}")
    return 0


def export_markdown(con: sqlite3.Connection, out: Path) -> int:
    lines = [
        "# OpenRoot evidence-first knowledge map",
        "",
        "Generated from a local SQLite ledger. Entries are research objects, not automatic proof.",
        "",
        "## Sources",
        "",
    ]
    for row in con.execute(
        "SELECT canonical_name,author,publication_year,source_url,source_type,license_note FROM documents ORDER BY canonical_name"
    ):
        name, author, year, url, kind, license_note = row
        lines.append(f"- {name} — {author or 'Unknown'} ({year or 'n.d.'}); {kind}; {url}; {license_note}")
    lines.extend(["", "## Claims", ""])
    for row in con.execute(
        "SELECT claim_id,statement,confidence,status,falsification_test FROM claims ORDER BY claim_id"
    ):
        cid, statement, confidence, state, test = row
        lines.append(f"- `{cid}` [{state}, confidence={confidence}]: {statement} Falsification: {test}")
    lines.extend(["", "## Case studies", ""])
    for row in con.execute(
        "SELECT case_id,title,status,summary,evidence_standard FROM case_studies ORDER BY case_id"
    ):
        cid, title, state, summary, standard = row
        lines.append(f"- `{cid}` [{state}]: {title}. {summary} Evidence standard: {standard}.")
    lines.extend(["", "## Nonviolent pattern blockers", ""])
    for row in con.execute(
        "SELECT blocker_id,pattern_name,threat_model,nonviolent_response,verification FROM pattern_blockers ORDER BY blocker_id"
    ):
        bid, name, threat, response, verification = row
        lines.append(f"- `{bid}`: {name}. Threat: {threat} Response: {response} Verify: {verification}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[banked] exported={out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("init", "status", "export"))
    args = parser.parse_args()
    con = connect()
    if args.command == "init":
        seed(con)
        print(f"[banked] database={DB}")
        return status(con)
    if args.command == "status":
        return status(con)
    return export_markdown(con, ROOT / "exports" / "openroot_evidence_map.md")


if __name__ == "__main__":
    raise SystemExit(main())
PY

chmod 0755 "$PY"
python3 -m py_compile "$PY"
echo "[banked] py_compile PASS: $PY"

python3 "$PY" init
python3 "$PY" export
python3 "$PY" status

test -s "$DB"
test -s "$ROOT/exports/openroot_evidence_map.md"
grep -Fq "claim:research-standard" "$ROOT/exports/openroot_evidence_map.md"
grep -Fq "blocker:automation-without-consent" "$ROOT/exports/openroot_evidence_map.md"

echo "[banked] knowledge intake ledger and evidence map verified"
echo "# [OPENROOTKNOWLEDGEV1]"
echo "[exit=0]"
