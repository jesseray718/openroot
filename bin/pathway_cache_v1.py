#!/usr/bin/env python3
"""pathway_cache_v1.py — sealed, replayable pathways for the OpenRoot commons.

A pathway is a recorded, working way to accomplish a recurring task: the
exact steps, the evidence they produced, and hashes sealing both. Pathways
chain linearly (each entry links to its parent), so refinements compound:
the next person replays a cached pathway instead of rediscovering it, then
records the refinement.

The cache is append-only and hash-sealed. Nothing is ever executed
automatically; `record` only writes what you explicitly pass. Steps that
look destructive are refused unless --allow-dangerous is given (and are then
flagged in the entry).

Usage:
  python3 bin/pathway_cache_v1.py record --name "run aerocement audit" \
      --step "python3 ~/aerocement_corpus_audit_v1.py <dir> --write-ledger ac.jsonl" \
      --step "head -5 ac.jsonl" \
      --evidence ac.jsonl --notes "tool pin 8e15fb47, 12 findings"
  python3 bin/pathway_cache_v1.py list
  python3 bin/pathway_cache_v1.py show <seq|name-substring>
  python3 bin/pathway_cache_v1.py search <term>
  python3 bin/pathway_cache_v1.py verify
  python3 bin/pathway_cache_v1.py export-md PATHWAYS.md
  python3 bin/pathway_cache_v1.py --self-test
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path("/home/jesse/openroot")
DEFAULT_LEDGER = "data/pathway_cache.jsonl"
MAX_STEPS = 64
MAX_STEP_CHARS = 2000
MAX_EVIDENCE_FILES = 32

DANGEROUS_RES = [
    r"\brm\b[^#\n]*\s-[a-zA-Z]*[rf]",          # rm with -r or -f or -rf
    r"\bgit\s+push\b",                          # pushes need the human gate
    r"\bdd\b\s+if=",
    r"\bmkfs\b",
    r"\bshred\b",
    r"\btruncate\b\s+(-s\s*0|\s-s\s+0)",
    r">\s*/dev/(?:sd|nvme|hd)",
    r"\bchmod\b\s+-R\s+777\s+/",
    r":\(\)\s*\{.*\};\s*:",                     # forkbomb
]
DANGEROUS = [re.compile(p, re.I) for p in DANGEROUS_RES]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ledger_path(root: Path, ledger_arg: str | None) -> Path:
    p = Path(ledger_arg) if ledger_arg else root / DEFAULT_LEDGER
    return p if p.is_absolute() else root / p


def load_chain(lp: Path):
    if not lp.exists():
        return []
    out = []
    for line in lp.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def entry_hash(entry: dict) -> str:
    core = {k: v for k, v in entry.items() if k != "hash"}
    return sha256_bytes(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode())


def dangerous_steps(steps):
    bad = []
    for i, s in enumerate(steps, 1):
        if any(rx.search(s) for rx in DANGEROUS):
            bad.append(i)
    return bad


def cmd_record(args, root: Path):
    steps = [s for s in (args.step or [])][:MAX_STEPS]
    for s in steps:
        if len(s) > MAX_STEP_CHARS:
            print(f"[error] step too long ({len(s)} chars): {s[:60]}...",
                  file=sys.stderr)
            return 1
    bad = dangerous_steps(steps)
    if bad and not args.allow_dangerous:
        print("[refused] step(s) look destructive: "
              + ", ".join(map(str, bad)), file=sys.stderr)
        for i in bad:
            print(f"    step {i}: {steps[i - 1][:120]}", file=sys.stderr)
        print("pathways are replayed by newcomers; re-run with "
              "--allow-dangerous only if the step is genuinely safe and "
              "reviewed.", file=sys.stderr)
        return 2
    evidence = []
    for e in (args.evidence or [])[:MAX_EVIDENCE_FILES]:
        p = Path(e)
        try:
            data = p.read_bytes()
        except OSError as exc:
            print(f"[error] evidence unreadable: {e} ({exc})", file=sys.stderr)
            return 1
        evidence.append({"path": str(p.resolve()), "bytes": len(data),
                         "sha256": sha256_bytes(data)})
    lp = ledger_path(root, args.ledger)
    chain = load_chain(lp)
    parent = args.parent if args.parent is not None else (
        chain[-1]["seq"] if chain else 0)
    entry = {
        "seq": len(chain) + 1,
        "event": "PATHWAY_RECORDED",
        "name": args.name,
        "actor": args.actor,
        "steps": steps,
        "evidence": evidence,
        "notes": args.notes or "",
        "dangerous": bad if bad else [],
        "parent_seq": parent,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    prev = chain[-1]["hash"] if chain else None
    entry["previous_hash"] = prev
    entry["hash"] = entry_hash(entry)
    lp.parent.mkdir(parents=True, exist_ok=True)
    with open(lp, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    flags = f"  DANGEROUS steps: {bad}" if bad else ""
    print(f"[ok] pathway #{entry['seq']} sealed: {entry['name']}")
    print(f"     hash {entry['hash'][:16]}... parent #{parent}{flags}")
    print(f"     ledger {lp}")
    return 0


def cmd_list(args, root: Path):
    chain = load_chain(ledger_path(root, args.ledger))
    if not chain:
        print("[info] pathway cache empty. Record one with 'record'.")
        return 0
    print(f"{'seq':>4}  {'date':<10}  {'actor':<8}  name")
    for e in chain:
        date = (e.get("created_at") or "")[:10]
        print(f"{e.get('seq', 0):>4}  {date:<10}  "
              f"{(e.get('actor') or '-')[:8]:<8}  {e.get('name', '-')}")
    return 0


def find_entry(chain, key: str):
    if key.isdigit():
        seq = int(key)
        for e in chain:
            if e.get("seq") == seq:
                return e
        return None
    for e in chain:
        if key.lower() in (e.get("name") or "").lower():
            return e
    return None


def cmd_show(args, root: Path):
    chain = load_chain(ledger_path(root, args.ledger))
    e = find_entry(chain, args.key)
    if not e:
        print(f"[error] no pathway matches: {args.key}", file=sys.stderr)
        return 1
    print(json.dumps(e, indent=2))
    return 0


def cmd_search(args, root: Path):
    term = args.term.lower()
    chain = load_chain(ledger_path(root, args.ledger))
    hits = []
    for e in chain:
        hay = " ".join([e.get("name", ""), e.get("notes", ""),
                        " ".join(e.get("steps", [])),
                        " ".join(s.get("path", "")
                                 for s in e.get("evidence", []))]).lower()
        if term in hay:
            hits.append(e)
    if not hits:
        print(f"[info] no pathway matches: {term}")
        return 0
    for e in hits:
        print(f"#{e.get('seq')}  {e.get('name')}  ({e.get('created_at', '')[:10]})")
        for s in e.get("steps", []):
            if term in s.lower():
                print(f"    step: {s[:160]}")
                break
    return 0


def cmd_verify(args, root: Path):
    lp = ledger_path(root, args.ledger)
    chain = load_chain(lp)
    if not chain:
        print("[info] empty or absent chain — nothing to verify "
              f"({lp})")
        return 0
    prev = None
    for i, e in enumerate(chain, 1):
        if e.get("seq") != i:
            print(f"[fail] seq break at position {i} (seq={e.get('seq')})")
            return 1
        if e.get("previous_hash") != prev:
            print(f"[fail] previous_hash mismatch at seq {i}")
            return 1
        if e.get("hash") != entry_hash(e):
            print(f"[fail] hash mismatch at seq {i} — entry was tampered")
            return 1
        prev = e.get("hash")
    print(f"[ok] chain verified: {len(chain)} entries, tip "
          f"{prev[:16]}...")
    return 0


def cmd_export(args, root: Path):
    lp = ledger_path(root, args.ledger)
    chain = load_chain(lp)
    out = Path(args.out) if args.out else root / "PATHWAYS.md"
    lines = [
        "# PATHWAYS — the cached way to do things here",
        "",
        "Generated from the sealed pathway cache "
        f"(`{lp.name}`); every entry is hash-chained, so this",
        "document can be regenerated at any time with "
        "`python3 bin/pathway_cache_v1.py export-md PATHWAYS.md`.",
        "Replay a pathway by hand, step by step. Nothing here runs "
        "automatically.",
        "",
    ]
    if not chain:
        lines += ["_The cache is empty — record the first pathway with "
                  "`pathway_cache_v1.py record`._", ""]
    for e in chain:
        lines += [
            f"## #{e.get('seq')} — {e.get('name')}",
            "",
            f"- actor: {e.get('actor', '-')}",
            f"- sealed: {(e.get('created_at') or '')[:19]}",
            f"- parent: #{e.get('parent_seq', 0)}",
            f"- hash: `{e.get('hash', '')[:32]}...`",
            "",
        ]
        if e.get("notes"):
            lines += [f"_{e['notes']}_", ""]
        if e.get("dangerous"):
            lines += [f"**WARNING: contains flagged step(s) "
                      f"{e['dangerous']} — review before replaying.**", ""]
        lines += ["Steps:", ""]
        for i, s in enumerate(e.get("steps", []), 1):
            lines.append(f"{i}. `{s}`")
        if e.get("evidence"):
            lines += ["", "Evidence (sealed by hash):", "",
                      "| file | bytes | sha256 |", "|---|---|---|"]
            for ev in e["evidence"]:
                lines.append(f"| `{ev['path']}` | {ev['bytes']} | "
                             f"`{ev['sha256'][:32]}...` |")
        lines.append("")
    lines += [
        "---",
        "",
        "To add a refinement, record it with `--parent <seq>` of the "
        "pathway you improved. The chain is the compounding.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote {out} ({len(chain)} pathways) "
          f"sha256 {sha256_bytes(out.read_bytes())[:16]}...")
    return 0


def self_test():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="pathway_selftest_"))
    try:
        ev = tmp / "evidence.txt"
        ev.write_text("sealed evidence bytes\n")
        base = ["--root", str(tmp), "--ledger", str(tmp / "led.jsonl")]

        def run(*extra):
            import subprocess
            return subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), *base, *extra],
                capture_output=True, text=True)

        r = run("record", "--name", "first pathway", "--actor", "tester",
                "--step", "echo one", "--step", "echo two",
                "--evidence", str(ev), "--notes", "the beginning")
        assert r.returncode == 0, r.stderr
        r = run("record", "--name", "refinement", "--parent", "1",
                "--step", "echo one -- improved")
        assert r.returncode == 0, r.stderr
        r = run("record", "--name", "bad", "--step", "rm -rf /tmp/x")
        assert r.returncode == 2, "dangerous step was not refused"
        r = run("verify")
        assert r.returncode == 0 and "[ok] chain verified" in r.stdout, r.stdout
        r = run("search", "improved")
        assert "#2" in r.stdout, r.stdout
        r = run("export-md", str(tmp / "PATHWAYS.md"))
        assert r.returncode == 0, r.stderr
        md = (tmp / "PATHWAYS.md").read_text()
        assert "first pathway" in md and "refinement" in md
        # tamper: rewrite a step inside the ledger, verify must fail
        lp = tmp / "led.jsonl"
        rows = [json.loads(l) for l in lp.read_text().strip().split("\n")]
        rows[0]["steps"] = ["echo tampered"]
        lp.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
        r = run("verify")
        assert r.returncode == 1 and "tampered" in r.stdout.lower(), r.stdout
        print("pathway_cache_v1 self-test: ALL PASS "
              "(record/verify/search/export/refusal/tamper)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if "--self-test" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser(description="OpenRoot pathway cache v1")
    ap.add_argument("--root", type=str, default=str(DEFAULT_ROOT))
    ap.add_argument("--ledger", type=str, default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="seal a new pathway")
    rec.add_argument("--name", required=True)
    rec.add_argument("--actor", default="jesse")
    rec.add_argument("--step", action="append", default=[])
    rec.add_argument("--evidence", action="append", default=[])
    rec.add_argument("--notes", default="")
    rec.add_argument("--parent", type=int, default=None)
    rec.add_argument("--allow-dangerous", action="store_true")

    sub.add_parser("list", help="list all pathways")
    show = sub.add_parser("show", help="show one pathway (seq or name part)")
    show.add_argument("key")
    search = sub.add_parser("search", help="search name/notes/steps/evidence")
    search.add_argument("term")
    sub.add_parser("verify", help="verify the whole chain")
    exp = sub.add_parser("export-md", help="regenerate the human pathways doc")
    exp.add_argument("out", nargs="?", default=None)

    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[error] root is not a directory: {root}", file=sys.stderr)
        return 1
    if args.cmd == "record":
        return cmd_record(args, root)
    if args.cmd == "list":
        return cmd_list(args, root)
    if args.cmd == "show":
        return cmd_show(args, root)
    if args.cmd == "search":
        return cmd_search(args, root)
    if args.cmd == "verify":
        return cmd_verify(args, root)
    if args.cmd == "export-md":
        return cmd_export(args, root)
    return 1


if __name__ == "__main__":
    sys.exit(main())
