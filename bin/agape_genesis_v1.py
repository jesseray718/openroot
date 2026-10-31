# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
import datetime, hashlib, json, pathlib
LEDGER = pathlib.Path("/home/jesse/openroot/ledger/agape/chain.jsonl")
payload = {
    "type": "genesis",
    "anchor_term": "ἀγάπη",
    "anchor_translit": "agape",
    "do_not_gloss_as": ["love", "caritas", "charity"],
    "greek_carving": {
        "agape": "ἀγάπη — unconditional, self-giving, directed act (not feeling)",
        "philia": "φιλία — mutual regard, friendship",
        "eros": "ἔρως — romantic desire, longing",
        "storge": "στοργή — familial affection, natural inclination"
    },
    "lineage": [
        "Hebrew אהב (ahav) — Septuagint chose ἀγαπάω as carrier verb",
        "Koine ἀγάπη — rare secular, became Christian technical term",
        "Latin caritas — dignity transferred, then narrowed to alms",
        "Old French charité → English charity — semantic narrowing",
        "Modern English 'love' — fourfold collapse into one polysemous word"
    ],
    "hypothesis": {
        "claim": "Transliteration preserves; translation bleaches",
        "testable": True,
        "method": "Track agape_score of the love-word per language per century",
        "forkable": "Adopters may reject Axiom 0 and seed a different anchor"
    },
    "axiom_0_declaration": (
        "ἀγάπη (agape) is an untranslatable loanword; English lacks a single "
        "equivalent. Anchor is human-decided origin, not derived measurement. "
        "Forking with a different anchor is permitted — chains diverge at genesis."
    ),
    "notes": {
        "bleaching_example": "charity: agape/caritas → almsgiving only",
        "loanword_preservation": "schadenfreude/karma preserved by import",
        "modern_counter_example": "Greek agápi = everyday word, unfiltered"
    },
    "created_by": "agape_genesis_v1"
}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
rid = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
rec = {"id": rid, "kind": "genesis", "parents": [], "created_utc":
       datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "payload": payload, "supersedes": None, "license": "CC BY-SA 4.0"}
LEDGER.parent.mkdir(parents=True, exist_ok=True)
if LEDGER.exists() and rid in LEDGER.read_text(encoding="utf-8"):
    print(f"[held] genesis already sealed {rid[:16]} — idempotent skip")
else:
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"[banked] genesis sealed {rid[:16]}")
print(f"[gate] payload sha256: {rid}")
