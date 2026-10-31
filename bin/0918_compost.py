#!/usr/bin/env python3
"""OpenRoot Compost — Produce No Waste.
Absolute paths only. Phone-first. No tilde.

Turns terminal logs / keyword hits / file lists into:
  seeds/     durable facts (training base)
  gamma.jsonl  cross-window couplings
  eta.jsonl    useful-work rows
  cash.jsonl   only when a seed has DOI/CID/BOM/money
  ash.jsonl    classified then eligible to die
  dossier.md   the one-dot page you actually open

Does NOT fine-tune a model. Seeds *are* the training base.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

OPENROOT = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot"))
TERMUX = Path(os.environ.get("TERMUX_HOME", "/data/data/com.termux/files/home"))
SD_COLD = Path("/storage/emulated/0/OpenRoot/cold/compost")
DOCS_LOGS = Path("/storage/emulated/0/Documents/terminal-logs")
MARKOR = Path("/storage/emulated/0/Documents/markor")

OUT = OPENROOT / "compost"
SEEDS = OPENROOT / "session_seeds"
KB = OPENROOT / "agape_kb"
LEDGER = OPENROOT / "ledger"

SECRET_RX = re.compile(
    r"(?i)(aws_secret|aws_access|sk-[a-z0-9]{10,}|ghp_[a-z0-9]+|"
    r"zenodo.?token|api[_-]?key\s*[:=]\s*\S+|password\s*[:=]\s*\S+|"
    r"BEGIN (RSA |OPENSSH )?PRIVATE KEY)"
)

TOKEN_SPECS = [
    ("cid", re.compile(r"\b(Qm[1-9A-HJ-NP-Za-km-z]{44,}|bafy[a-z0-9]{20,})\b")),
    ("doi", re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)),
    ("ticker", re.compile(r"\$(?:SPY|QQQ|ES|NQ|GLD|SLV|BTC|ETH|SOL|ACRE)\b")),
    ("axiom", re.compile(r"\b(?:STANDING[_ ]WAVE|η|eta3|Γ|R=1\.0|H-003|AE-GFRC|ACRE|UNE|AGAPE)\b")),
    ("money", re.compile(r"\$\d+(?:\.\d{2})?|\b\d+\s*(?:usd|joule|kWh)\b", re.I)),
    ("path", re.compile(r"(?:/sdcard|/storage/emulated/0|/data/data/com\.termux|/home/optiplex)/[^\s:]+")),
    ("error", re.compile(r"(?i)\b(error|traceback|permission denied|no such file|oom|killed)\b")),
    ("cmd", re.compile(r"^\s*(?:\$ |# )?(git|python3?|ipfs|ollama|rclone|syncthing|pkg|pip|ssh)\b")),
]

USEFUL_CMD = {
    "git", "ipfs", "python", "python3", "rclone", "syncthing",
    "extract_seed", "stamp_context", "run.py", "bridge.py",
}

SKIP_EXT = {".so", ".ldb", ".pyc", ".jpg", ".jpeg", ".png"}
SKIP_NAME = {".nomedia", ".database_uuid", "LOCK", "CURRENT", "RECORD", "WHEEL", "INSTALLER"}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:12]


def redact(text: str) -> tuple[str, int]:
    n = 0

    def _sub(m):
        nonlocal n
        n += 1
        return f"<REDACTED:{m.group(0)[:4]}…>"

    return SECRET_RX.sub(_sub, text), n


def session_from_name(p: Path) -> str:
    m = re.search(r"(20\d{6}_\d{6})", p.name)
    if m:
        return m.group(1)
    try:
        st = p.stat()
        return datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    except OSError:
        return "unknown"


def tokenize(line: str) -> list[tuple[str, str]]:
    found = []
    for kind, rx in TOKEN_SPECS:
        for m in rx.finditer(line):
            tok = m.group(0).rstrip(".,;:)/")
            if kind == "path" and Path(tok).name in SKIP_NAME:
                continue
            if kind == "path" and Path(tok).suffix.lower() in SKIP_EXT:
                continue
            found.append((kind, tok[:240]))
    return found


def look_like_seed(line: str) -> bool:
    s = line.strip()
    if len(s) < 24 or len(s) > 400:
        return False
    if s.startswith("$") or s.startswith("#"):
        return False
    hits = ("therefore", "because", "η", "eta", "axiom", "validated",
            "DOI", "CID", "standing wave", "next:", "decision:", "claim:")
    return any(h.lower() in s.lower() for h in hits) or bool(re.search(r"\b(PO-|AX-|N\d{2})\b", s))


def ensure_dirs() -> None:
    for d in (OUT, SEEDS, KB, LEDGER, SD_COLD, OUT / "raw_hash"):
        d.mkdir(parents=True, exist_ok=True)


def iter_sources(extra: list[Path]) -> list[Path]:
    srcs: list[Path] = []
    for root in (DOCS_LOGS, Path("/storage/emulated/0"), TERMUX):
        if not root.exists():
            continue
    if DOCS_LOGS.exists():
        srcs.extend(sorted(DOCS_LOGS.glob("auto_*.log")))
    hits = Path("/storage/emulated/0/keyword_hits_20260723_215812.log")
    if hits.exists():
        srcs.append(hits)
    hist = TERMUX / ".bash_history"
    if hist.exists():
        srcs.append(hist)
    if MARKOR.exists():
        srcs.extend(MARKOR.glob("*.md*"))
    for p in extra:
        if p.exists() and p.is_file():
            srcs.append(p)
    # de-dupe
    seen = set()
    out = []
    for p in srcs:
        rp = str(p)
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    try:
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        return f"unreadable:{e}"


def compost(paths: list[Path]) -> dict:
    ensure_dirs()
    gamma_idx: dict[str, list[dict]] = defaultdict(list)
    eta_rows = []
    seeds = []
    cash = []
    ash = []
    secret_hits = 0
    lines_in = 0
    files_ok = 0

    for src in paths:
        digest = hash_file(src)
        (OUT / "raw_hash" / f"{src.name}.{digest[:12]}").write_text(
            json.dumps({"path": str(src), "sha256": digest, "bytes": src.stat().st_size if src.exists() else 0, "ts": utcnow()})
            + "\n"
        )
        sess = session_from_name(src)
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            ash.append({"src": str(src), "why": f"unreadable:{e}"})
            continue
        files_ok += 1
        text, nsec = redact(text)
        secret_hits += nsec
        for i, raw in enumerate(text.splitlines()):
            lines_in += 1
            line = raw.strip()
            if not line:
                continue
            toks = tokenize(line)
            for kind, tok in toks:
                key = f"{kind}|{tok.lower()}"
                gamma_idx[key].append({
                    "session": sess,
                    "src": src.name,
                    "line": i + 1,
                    "kind": kind,
                    "token": tok,
                })
            useful = any(c in line for c in USEFUL_CMD) and "error" not in line.lower()
            if useful:
                eta_rows.append({
                    "ts": utcnow(),
                    "session": sess,
                    "src": src.name,
                    "line": line[:300],
                    "eta_hint": 1.0 if any(x in line for x in ("ipfs add", "git commit", "extract_seed", "stamp_context")) else 0.3,
                })
            if look_like_seed(line):
                sid = sha12(f"{sess}|{line}")
                seed = {
                    "id": sid,
                    "ts": utcnow(),
                    "session": sess,
                    "src": src.name,
                    "text": line[:500],
                    "tokens": toks[:12],
                    "yield": "seed",
                }
                seeds.append(seed)
                if any(k in ("doi", "cid", "money") for k, _ in toks):
                    cash.append({**seed, "yield": "cashpath"})
        # original file is now digested — eligible for cold or ash
        ash.append({
            "src": str(src),
            "sha256": digest,
            "session": sess,
            "lines": text.count("\n") + 1,
            "secrets_redacted": nsec,
            "next": "move-to-cold-then-delete-hot",
        })

    # Γ only when a token spans ≥2 sessions
    gamma_rows = []
    for key, occ in gamma_idx.items():
        sessions = sorted({o["session"] for o in occ})
        if len(sessions) < 2:
            continue
        gamma_rows.append({
            "key": key,
            "sessions": sessions,
            "n_sessions": len(sessions),
            "n_hits": len(occ),
            "gamma": round(min(2.0, (len(sessions) - 1) + 0.1 * min(20, len(occ))), 3),
            "sample": occ[:3],
        })
    gamma_rows.sort(key=lambda r: (-r["n_sessions"], -r["n_hits"]))

    coherence = 0.0
    if gamma_idx:
        multi = sum(1 for k, o in gamma_idx.items() if len({x["session"] for x in o}) >= 2)
        coherence = multi / max(1, len(gamma_idx))

    report = {
        "ts": utcnow(),
        "files": files_ok,
        "lines_in": lines_in,
        "secrets_redacted": secret_hits,
        "seeds": len(seeds),
        "gamma_links": len(gamma_rows),
        "eta_rows": len(eta_rows),
        "cashpaths": len(cash),
        "ash_files": len(ash),
        "standing_wave_coherence": round(coherence, 4),
        "wave_state": "standing" if coherence >= 0.12 else "decohering",
        "note": "coherence = fraction of tokens that appear in ≥2 sessions. This is the work-wave, not cosmology.",
    }

    def dump_jsonl(path: Path, rows: list):
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dump_jsonl(OUT / "gamma.jsonl", gamma_rows)
    dump_jsonl(OUT / "eta.jsonl", eta_rows[-2000:])
    dump_jsonl(OUT / "cash.jsonl", cash)
    dump_jsonl(OUT / "ash.jsonl", ash)
    dump_jsonl(SEEDS / f"compost_{report['ts'][:10]}.jsonl", seeds)

    # current seed = strongest gamma link + latest seed text
    current = {
        "timestamp": report["ts"],
        "eta3": round(sum(r.get("eta_hint", 0) for r in eta_rows[-50:]) / max(1, min(50, len(eta_rows))), 4),
        "coherence": report["standing_wave_coherence"],
        "wave_state": report["wave_state"],
        "top_gamma": gamma_rows[:7],
        "latest_seeds": seeds[-12:],
        "open_dot": (gamma_rows[0]["key"] if gamma_rows else None),
    }
    (SEEDS / "current_seed.json").write_text(json.dumps(current, indent=2, ensure_ascii=False))
    (OUT / "report.json").write_text(json.dumps(report, indent=2))

    # one-page dossier — the thing you open when you need one dot
    lines = [
        f"# Dossier {report['ts']}",
        "",
        f"wave: **{report['wave_state']}**  coherence={report['standing_wave_coherence']}  "
        f"η-hint-tail={current['eta3']}",
        f"in: {files_ok} files / {lines_in} lines   out: {len(seeds)} seeds, {len(gamma_rows)} Γ, {len(cash)} cashpaths",
        f"secrets redacted: {secret_hits}",
        "",
        "## Open dot (highest Γ)",
        f"`{current['open_dot']}`" if current["open_dot"] else "_none yet — need two sessions sharing a token_",
        "",
        "## Cross-window couplings",
    ]
    for g in gamma_rows[:15]:
        lines.append(f"- Γ={g['gamma']}  `{g['key'][:120]}`  sessions={g['n_sessions']} hits={g['n_hits']}")
    lines += ["", "## Latest seeds"]
    for s in seeds[-15:]:
        lines.append(f"- `{s['id']}` {s['text'][:180]}")
    lines += ["", "## Cashpaths (DOI/CID/money only)", ""]
    if not cash:
        lines.append("_none. Monetization is not a mood. It waits for a claim artifact._")
    for c in cash[-10:]:
        lines.append(f"- {c['text'][:180]}")
    lines += [
        "",
        "## Ash (digested, eligible to leave hot storage)",
        f"{len(ash)} files hashed. Move to `{SD_COLD}` then delete the hot copy.",
        "Do not delete until `raw_hash/` has the sha256.",
        "",
        "## How to use this",
        "1. Open this dossier when a window dies. The open dot is the stitch.",
        "2. Paste `current_seed.json` into the next model call. That is context, not slurry.",
        "3. OptiPlex embeds `session_seeds/compost_*.jsonl` into agape_vector_index.db.",
        "4. Markets need market data. This file will not hedge a fund.",
    ]
    dossier = OUT / "dossier.md"
    dossier.write_text("\n".join(lines) + "\n")
    # also drop a copy where Markor already looks
    try:
        (MARKOR / "dossier.md").write_text(dossier.read_text())
    except OSError:
        pass
    return report


def main(argv: list[str]) -> int:
    extra = [Path(a) for a in argv[1:]]
    paths = iter_sources(extra)
    if not paths:
        print("NO INPUT — drop logs in /storage/emulated/0/Documents/terminal-logs or pass files")
        return 1
    report = compost(paths)
    print(json.dumps(report, indent=2))
    print(f"dossier: {OUT / 'dossier.md'}")
    print(f"current_seed: {SEEDS / 'current_seed.json'}")
    bridge = OPENROOT / "context_bridge" / "bridge.py"
    if bridge.exists():
        import subprocess
        try:
            subprocess.run(
                ["python3", str(bridge), "--repo", str(OPENROOT)],
                check=False, timeout=30,
            )
        except Exception as e:
            print(f"bridge skip: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
