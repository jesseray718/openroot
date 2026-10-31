#!/usr/bin/env python3
"""Agape universal 3-symbol nomenclature.

Address space
  Alphabet  : 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ   (36)
  1-symbol  : 36
  2-symbol  : 1 296
  3-symbol  : 46 656
  Reserved  : first 1 010 cells (system / axioms / Newton Chain / Godpan poles)
  Usable    : 45 646   ← the number you remembered

Root
  A         = Agape (the whole semantic field collapsed into one letter)
  cell 000  = hash-address of the root (encode_triple(0))
  cell AAA  = letter-axis Agape/Agape/Agape (pure Godpan pole)

Godpan
  God  = Source / Agape / R=1.0 / C=0
  Pan  = the All that can still align with Source
  Godpan score in [-1, +1] : +1 identical with root field, -1 pure extraction

Embeddings
  Deterministic 64-d hashed projection. No torch. Phone-native.
  Cosine vs AGAPE_ROOT_TEXT is the Godpan alignment number.

Storage
  SQLite WAL + FTS5 + BLOB vectors. One file. Offline forever.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import struct
import time
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional, Sequence, Tuple

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
assert len(ALPHABET) == 36
BASE = 36
SPACE = BASE ** 3          # 46656
RESERVED = 1010
USABLE = SPACE - RESERVED  # 45646
DIM = 64
ROOT_SYMBOL = "A"

AGAPE_ROOT_TEXT = (
    "Agape is unconditional, self-giving, non-reciprocal love that seeks the good "
    "of the other regardless of worthiness. It is the love that originates in the "
    "Source, flows outward, and returns nothing for itself. It is the force that "
    "makes coordination cost zero. Greek agape, Latin caritas when purified, "
    "Hebrew hesed as covenant loyalty beyond contract, Arabic mahabba in its "
    "highest form, Sanskrit prem stripped of attachment, Chinese ren when it "
    "becomes universal. The gap between beings is closed by this force. When "
    "R=1.0 the coordination term (1-R)^T vanishes. A is the symbol that carries "
    "the entire field. Negative Agape is extraction, zero-sum, the force that "
    "opens the gap."
)

AXIOMS = {
    "A0": "Source exists and is generative (Agape).",
    "A1": "Beings are distinct yet capable of perfect cooperation (R=1.0).",
    "A2": "C(N,T,R)=N*0.001*(1+0.1*T)*(1-R)^T ; at R=1.0, C=0.",
    "A3": "Synergy multiplies with depth under perfect Agape.",
    "A4": "Every irreversible bit has a measurable Landauer cost.",
    "A5": "The gap between nodes is the measurable absence of Agape.",
    "A6": "Verified postulates are flagged once and never recomputed.",
}

# Position-1 = domain (what kind of thing). A is Agape/Source.
# 36 slots so every first symbol has a human-universal category.
DOMAIN = {
    "0": "void/unassigned",
    "1": "number/measure",
    "2": "relation/graph",
    "3": "time/process",
    "4": "space/place",
    "5": "energy/joule",
    "6": "matter/material",
    "7": "life/biology",
    "8": "mind/cognition",
    "9": "language/sign",
    "A": "agape/source",          # ROOT
    "B": "being/person",
    "C": "catch-store-energy",
    "D": "diversity/variety",
    "E": "edge/marginal",
    "F": "food/yield",
    "G": "governance/law",
    "H": "habitat/shelter",
    "I": "integrate/not-segregate",
    "J": "justice/repair",
    "K": "knowledge/postulate",
    "L": "labor/work",
    "M": "mesh/network",
    "N": "node/least-among-us",
    "O": "observe/interact",
    "P": "produce-no-waste",
    "Q": "query/question",
    "R": "resonance/R",
    "S": "self-regulate",
    "T": "thermal/heat",
    "U": "use-renewable",
    "V": "value-diversity",
    "W": "water/cycle",
    "X": "creatively-respond",
    "Y": "yield/obtain",
    "Z": "zero-cost-coordination",
}

# Position-2 = relation (how it binds)
RELATION = {
    "0": "null",
    "1": "identity",
    "2": "part-of",
    "3": "causes",
    "4": "enables",
    "5": "measures",
    "6": "stores",
    "7": "transforms",
    "8": "transmits",
    "9": "bounds",
    "A": "loves/serves",
    "B": "belongs-with",
    "C": "cooperates",
    "D": "distributes",
    "E": "exchanges",
    "F": "feeds",
    "G": "governs",
    "H": "heals",
    "I": "inhabits",
    "J": "joins",
    "K": "knows",
    "L": "learns",
    "M": "mirrors",
    "N": "nourishes",
    "O": "observes",
    "P": "protects",
    "Q": "questions",
    "R": "resonates",
    "S": "shares",
    "T": "teaches",
    "U": "unifies",
    "V": "verifies",
    "W": "witnesses",
    "X": "crosses/edge",
    "Y": "yields-to",
    "Z": "zeros-gap",
}

# Position-3 = polarity / state toward Godpan
POLARITY = {
    "0": "unformed",
    "1": "seed",
    "2": "growing",
    "3": "stable",
    "4": "yielding",
    "5": "compounding",
    "6": "teaching",
    "7": "systemized",
    "8": "fractal",
    "9": "eternal",
    "A": "pure-agape",           # Godpan pole
    "B": "benevolent",
    "C": "coherent",
    "D": "diluted",
    "E": "extractive",
    "F": "fragmented",
    "G": "generous",
    "H": "hostile",
    "I": "integrating",
    "J": "just",
    "K": "known-verified",
    "L": "lost/gap",
    "M": "mutual",
    "N": "negentropic",
    "O": "open",
    "P": "predatory",
    "Q": "questioning",
    "R": "R=1.0",
    "S": "selfish",
    "T": "true",
    "U": "unconditional",
    "V": "verified",
    "W": "wasteful",
    "X": "adversarial",
    "Y": "yes/aligned",
    "Z": "zero-resonance",
}

# Signed polarity used for Godpan prior before embedding cosine
POLARITY_PRIOR = {
    "A": 1.00, "R": 1.00, "U": 0.98, "N": 0.95, "V": 0.94, "K": 0.92,
    "Y": 0.90, "G": 0.88, "J": 0.86, "C": 0.84, "M": 0.82, "T": 0.80,
    "I": 0.78, "B": 0.75, "O": 0.70, "9": 0.68, "8": 0.64, "7": 0.60,
    "6": 0.55, "5": 0.50, "4": 0.40, "3": 0.30, "2": 0.20, "1": 0.10,
    "0": 0.00, "Q": 0.05, "D": -0.25, "L": -0.40, "F": -0.55,
    "W": -0.65, "S": -0.75, "E": -0.85, "H": -0.90, "P": -0.95,
    "X": -0.98, "Z": -1.00,
}


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


AGAPE_ROOT_HASH = sha256(AGAPE_ROOT_TEXT)


def symbol_to_int(sym: str) -> int:
    return ALPHABET.index(sym.upper())


def int_to_symbol(i: int) -> str:
    return ALPHABET[i % BASE]


def encode_triple(n: int) -> str:
    if not 0 <= n < SPACE:
        raise ValueError("out of 36^3 range")
    a = n // (BASE * BASE)
    b = (n // BASE) % BASE
    c = n % BASE
    return int_to_symbol(a) + int_to_symbol(b) + int_to_symbol(c)


def decode_triple(s: str) -> int:
    s = s.upper()
    if len(s) != 3:
        raise ValueError("need exactly 3 symbols")
    return symbol_to_int(s[0]) * 1296 + symbol_to_int(s[1]) * 36 + symbol_to_int(s[2])


def is_reserved(n: int) -> bool:
    return 0 <= n < RESERVED


def decode_meaning(cell: str) -> dict:
    cell = cell.upper()
    if len(cell) != 3:
        raise ValueError("need 3 symbols")
    d, r, p = cell[0], cell[1], cell[2]
    return {
        "cell": cell,
        "index": decode_triple(cell),
        "reserved": is_reserved(decode_triple(cell)),
        "domain": DOMAIN.get(d, "?"),
        "relation": RELATION.get(r, "?"),
        "polarity": POLARITY.get(p, "?"),
        "prior": POLARITY_PRIOR.get(p, 0.0),
        "phrase": f"{DOMAIN.get(d,'?')} that {RELATION.get(r,'?')} in state {POLARITY.get(p,'?')}",
    }


def hash_address(text: str, salt: str = AGAPE_ROOT_HASH) -> str:
    h = sha256(salt + "|" + text.strip().lower())
    return encode_triple(int(h[:8], 16) % SPACE)


def embed(text: str, dim: int = DIM) -> List[float]:
    """Deterministic hashed embedding. Stable across devices. No model weights."""
    vec = [0.0] * dim
    blob = text.strip().lower().encode("utf-8")
    if not blob:
        return vec
    # multi-hash projection + trigram features
    for i in range(8):
        digest = hashlib.sha256(blob + bytes([i])).digest()
        for j in range(0, 32, 4):
            idx = (digest[j] + 256 * (i % 2)) % dim
            signed = struct.unpack(">i", digest[j:j + 4])[0]
            vec[idx] += signed / 2147483648.0
    toks = [t for t in "".join(ch if ch.isalnum() else " " for ch in text.lower()).split() if t]
    for t in toks:
        d = hashlib.sha256(t.encode()).digest()
        idx = d[0] % dim
        vec[idx] += 0.35
        if len(t) >= 3:
            for k in range(len(t) - 2):
                tri = t[k:k + 3]
                td = hashlib.sha256(tri.encode()).digest()
                vec[td[0] % dim] += 0.12
    # L2 normalize
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / n for x in vec]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


ROOT_VEC = embed(AGAPE_ROOT_TEXT)

POS_PROTOS = [
    AGAPE_ROOT_TEXT,
    "unconditional self-giving love serve the least among us close the gap zero coordination cost",
    "cooperation resonance R=1.0 produce no waste raise eta for the lowest node",
    "repair heal nourish protect share unify verify without extraction",
]
NEG_PROTOS = [
    "extract labor from the poor to buy status domination predation",
    "zero-sum selfish hostile wasteful adversarial fragmentation",
    "open the gap punish the lowest node harvest people as means",
    "coordination cost as weapon status theater hoarding",
]
POS_VECS = [embed(p) for p in POS_PROTOS]
NEG_VECS = [embed(p) for p in NEG_PROTOS]


def _max_cos(v, proto_vecs):
    return max(cosine(v, p) for p in proto_vecs)


def godpan_score(text: str, polarity_symbol: Optional[str] = None) -> float:
    """Contrastive Godpan: Source prototypes minus anti-prototypes.

    Hashed embeddings share tokens across antonyms; contrast cancels that.
    Returns signed score in [-1, +1].
    """
    v = embed(text)
    contrast = _max_cos(v, POS_VECS) - _max_cos(v, NEG_VECS)
    c = max(-1.0, min(1.0, contrast * 2.2))
    if polarity_symbol is None:
        return c
    prior = POLARITY_PRIOR.get(polarity_symbol.upper(), 0.0)
    return max(-1.0, min(1.0, 0.65 * c + 0.35 * prior))


def pack_vec(v: Sequence[float]) -> bytes:
    return struct.pack(f"{len(v)}f", *v)


def unpack_vec(b: bytes) -> List[float]:
    n = len(b) // 4
    return list(struct.unpack(f"{n}f", b))


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS cells (
    cell        TEXT PRIMARY KEY,
    idx         INTEGER UNIQUE NOT NULL,
    reserved    INTEGER NOT NULL,
    domain      TEXT,
    relation    TEXT,
    polarity    TEXT,
    phrase      TEXT,
    label       TEXT,
    category    TEXT,
    godpan      REAL,
    vec         BLOB,
    source      TEXT,
    created_ts  REAL
);
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY,
    text        TEXT NOT NULL,
    cell        TEXT NOT NULL,
    category    TEXT,
    godpan      REAL,
    vec         BLOB,
    meta_json   TEXT,
    created_ts  REAL,
    FOREIGN KEY(cell) REFERENCES cells(cell)
);
CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
    text, category, cell, content='entries', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
  INSERT INTO entries_fts(rowid, text, category, cell)
  VALUES (new.id, new.text, new.category, new.cell);
END;
CREATE INDEX IF NOT EXISTS idx_entries_cell ON entries(cell);
CREATE INDEX IF NOT EXISTS idx_entries_godpan ON entries(godpan);
CREATE INDEX IF NOT EXISTS idx_cells_godpan ON cells(godpan);
CREATE TABLE IF NOT EXISTS meta (
    k TEXT PRIMARY KEY,
    v TEXT
);
"""


DEFAULT_SEED = [
    # (label, category, text)
    ("AGA", "godpan-pole", "Agape unconditional self-giving love Source R=1.0 coordination cost zero"),
    ("AAR", "godpan-pole", "Agape resonates at R=1.0 the standing wave of cooperation"),
    ("AAU", "godpan-pole", "Agape loves and serves unconditionally"),
    ("AAZ", "anti-pole", "Agape field inverted into zero-resonance extraction"),
    ("NAA", "least-node", "the least among us served first by Agape"),
    ("NAR", "least-node", "lowest node resonates when coordination cost vanishes"),
    ("PAA", "permaculture", "produce no waste as an act of Agape"),
    ("CAA", "permaculture", "catch and store energy for the other not the self"),
    ("OAA", "permaculture", "observe and interact without extracting"),
    ("YAA", "permaculture", "obtain a yield that raises eta for the lowest node"),
    ("SAA", "permaculture", "self-regulation as applied Agape"),
    ("UAA", "permaculture", "use renewable resources so the future is not mined"),
    ("IAA", "permaculture", "integrate not segregate close the gap"),
    ("DAA", "permaculture", "value diversity because many nodes raise synergy"),
    ("XAA", "permaculture", "creatively respond to change without predation"),
    ("EAA", "permaculture", "use edges and value the marginal twelfth axiom"),
    ("HAA", "habitat", "shelter that costs almost no human joules to keep alive"),
    ("TAA", "thermal", "thermal cascade that stores heat as love stores regard"),
    ("WAA", "water", "water cycle kept clean because waste is a gap"),
    ("FAA", "food", "food yield that feeds the least node first"),
    ("MAA", "mesh", "mesh network that keeps working when any one human is offline"),
    ("KAA", "knowledge", "verified postulate Newton Chain flag once free forever"),
    ("QAA", "query", "a question aimed at the Source not at status"),
    ("GAA", "governance", "law that serves the least node and zeros coordination cost"),
    ("JAA", "justice", "repair that closes the gap rather than punishing the poor"),
    ("LAA", "labor", "work that produces useful joules not status theater"),
    ("BAA", "being", "a person treated as end not means"),
    ("RAA", "resonance", "resonance itself as the measurable presence of Agape"),
    ("ZAA", "coordination", "zero-cost coordination the theorem made flesh"),
    ("SEE", "anti-pole", "selfish extractive exchange that opens the gap"),
    ("PEX", "anti-pole", "predatory extraction across an edge"),
    ("HAX", "anti-pole", "hostile habitat that spends joules to dominate"),
    ("GAX", "anti-pole", "governance as predation"),
    ("LAX", "anti-pole", "labor as extraction from the lowest node"),
]


class NomenDB:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        self.cx = sqlite3.connect(path)
        self.cx.row_factory = sqlite3.Row
        self.cx.executescript(SCHEMA)
        self._boot_meta()

    def _boot_meta(self) -> None:
        pairs = {
            "space": str(SPACE),
            "reserved": str(RESERVED),
            "usable": str(USABLE),
            "alphabet": ALPHABET,
            "root_symbol": ROOT_SYMBOL,
            "root_hash": AGAPE_ROOT_HASH,
            "root_code": encode_triple(0),
            "dim": str(DIM),
        }
        self.cx.executemany(
            "INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", list(pairs.items())
        )
        self.cx.commit()

    def ensure_cell(self, cell: str, label: str = "", category: str = "", text: str = "") -> dict:
        cell = cell.upper()
        meaning = decode_meaning(cell)
        gp = godpan_score(text or meaning["phrase"], cell[2])
        vec = embed(text or meaning["phrase"])
        self.cx.execute(
            """
            INSERT OR REPLACE INTO cells
            (cell, idx, reserved, domain, relation, polarity, phrase, label, category, godpan, vec, source, created_ts)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                cell,
                meaning["index"],
                int(meaning["reserved"]),
                meaning["domain"],
                meaning["relation"],
                meaning["polarity"],
                meaning["phrase"],
                label or cell,
                category,
                gp,
                pack_vec(vec),
                "seed" if text else "generated",
                time.time(),
            ),
        )
        self.cx.commit()
        meaning["godpan"] = gp
        meaning["label"] = label or cell
        meaning["category"] = category
        return meaning

    def ingest(self, text: str, category: str = "free", cell: Optional[str] = None) -> dict:
        chosen = cell
        cell = (cell or hash_address(text)).upper()
        self.ensure_cell(cell, label=text[:48], category=category, text=text)
        gp = godpan_score(text, chosen[2] if chosen else None)
        vec = embed(text)
        cur = self.cx.execute(
            """
            INSERT INTO entries(text, cell, category, godpan, vec, meta_json, created_ts)
            VALUES (?,?,?,?,?,?,?)
            """,
            (text, cell, category, gp, pack_vec(vec), json.dumps({"hash": sha256(text)}), time.time()),
        )
        self.cx.commit()
        return {
            "id": cur.lastrowid,
            "cell": cell,
            "meaning": decode_meaning(cell),
            "godpan": gp,
            "hash": sha256(text),
        }

    def seed_defaults(self) -> int:
        n = 0
        for cell, cat, text in DEFAULT_SEED:
            self.ensure_cell(cell, label=text[:48], category=cat, text=text)
            self.ingest(text, category=cat, cell=cell)
            n += 1
        # reserve the first 1010 address cells so the usable map is real
        for i in range(0, RESERVED, 50):
            self.ensure_cell(encode_triple(i), label=f"SYS-{i:04d}", category="reserved")
        self.ensure_cell(encode_triple(0), label="ROOT-000", category="reserved", text=AGAPE_ROOT_TEXT)
        return n

    def search_fts(self, q: str, k: int = 12) -> List[dict]:
        rows = self.cx.execute(
            """
            SELECT e.id, e.text, e.cell, e.category, e.godpan
            FROM entries_fts f
            JOIN entries e ON e.id = f.rowid
            WHERE entries_fts MATCH ?
            ORDER BY e.godpan DESC
            LIMIT ?
            """,
            (q, k),
        ).fetchall()
        return [dict(r) for r in rows]

    def knn(self, text: str, k: int = 8) -> List[dict]:
        qv = embed(text)
        rows = self.cx.execute(
            "SELECT id, text, cell, category, godpan, vec FROM entries"
        ).fetchall()
        scored = []
        for r in rows:
            s = cosine(qv, unpack_vec(r["vec"]))
            scored.append((s, dict(r)))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for s, d in scored[:k]:
            d.pop("vec", None)
            d["cosine"] = s
            out.append(d)
        return out

    def align(self, text: str, semantic_cell: Optional[str] = None) -> dict:
        # Hash cell is an address, not a meaning. Never let its third glyph
        # vote on Godpan — that glyph is random and will lie.
        cell = (semantic_cell or hash_address(text)).upper()
        meaning = decode_meaning(cell)
        prior_sym = semantic_cell[2] if semantic_cell else None
        gp = godpan_score(text, prior_sym)
        verdict = (
            "PURE_GODPAN" if gp >= 0.55 else
            "ALIGNED" if gp >= 0.20 else
            "MIXED" if gp >= -0.10 else
            "GAP" if gp >= -0.45 else
            "ANTI_GODPAN"
        )
        neighbors = self.knn(text, k=6)
        return {
            "text": text,
            "cell": cell,
            "meaning": meaning,
            "godpan": round(gp, 4),
            "verdict": verdict,
            "neighbors": neighbors,
            "root_hash": AGAPE_ROOT_HASH,
        }

    def chart_rows(self, letter: str = "A", limit: int = 36) -> List[dict]:
        letter = letter.upper()
        rows = []
        for rel in ALPHABET[:limit]:
            cell = letter + rel + "A"  # domain + relation + pure-agape polarity
            m = self.ensure_cell(cell, category="chart")
            rows.append(m)
        return rows

    def stats(self) -> dict:
        cells = self.cx.execute("SELECT COUNT(*) c FROM cells").fetchone()["c"]
        ents = self.cx.execute("SELECT COUNT(*) c FROM entries").fetchone()["c"]
        avg = self.cx.execute("SELECT AVG(godpan) a FROM entries").fetchone()["a"]
        return {
            "space": SPACE,
            "reserved": RESERVED,
            "usable": USABLE,
            "cells_materialized": cells,
            "entries": ents,
            "mean_godpan": None if avg is None else round(avg, 4),
            "db": self.path,
        }


def ascii_heat(rows: Sequence[dict], title: str) -> str:
    lines = [title, "-" * len(title)]
    for r in rows:
        gp = float(r.get("godpan") or 0.0)
        width = int(abs(gp) * 20)
        bar = ("+" * width) if gp >= 0 else ("-" * width)
        side = "GODPAN" if gp >= 0 else "GAP"
        lines.append(f"{r.get('cell','???'):>4} {gp:+6.3f} {side:7} {bar:20} {r.get('phrase','')[:56]}")
    return "\n".join(lines)


def svg_chart(rows: Sequence[dict], title: str, path: str) -> str:
    w, h = 920, 40 + 22 * len(rows)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="monospace">',
        f'<rect width="{w}" height="{h}" fill="#0b0f14"/>',
        f'<text x="16" y="24" fill="#e8f0ff" font-size="16">{title}</text>',
    ]
    for i, r in enumerate(rows):
        gp = float(r.get("godpan") or 0.0)
        y = 46 + i * 22
        mid = 360
        mag = abs(gp) * 220
        color = "#3dffa6" if gp >= 0.2 else ("#ff6b6b" if gp < 0 else "#d0c06a")
        x = mid if gp >= 0 else mid - mag
        parts.append(f'<text x="16" y="{y+4}" fill="#9ab" font-size="12">{r.get("cell","")}</text>')
        parts.append(f'<rect x="{x}" y="{y-8}" width="{max(mag,1)}" height="12" fill="{color}"/>')
        parts.append(f'<text x="{mid+230}" y="{y+4}" fill="#cde" font-size="11">{gp:+.3f} {r.get("phrase","")[:48]}</text>')
    parts.append("</svg>")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return path
