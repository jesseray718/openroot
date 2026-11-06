#!/usr/bin/env python3
"""friction_observer_v1.py — observe friction across the OpenRoot commons.

Read-only scan of the repo. It ranks the places where the pieces (docs,
tools, scripts, chains, entry points) fail to compound, so anyone can see
what to fix next. Writes nothing unless --write-ledger or --json is given;
its only writes are its own report artifacts. Never modifies, moves, or
deletes anything.

Findings (v1):
  missing_entry_point   expected onboarding/anchor files absent
  broken_link           markdown relative link whose target does not exist
  stub_doc              heading with no body beneath it (placeholder text)
  orphan_tool           bin/*.py never mentioned by any markdown doc
  backup_sprawl         .bak/.backup/version-duplicate pile-ups
  chain_health          newton chain / heartbeats / discovery absent or stale
  dead_symlink          symlink pointing at nothing
  root_clutter          too many loose files in the repo root

Usage:
  python3 bin/friction_observer_v1.py
  python3 bin/friction_observer_v1.py --root /home/jesse/openroot
  python3 bin/friction_observer_v1.py --write-ledger data/friction_ledger.jsonl
  python3 bin/friction_observer_v1.py --json friction_report.json
  python3 bin/friction_observer_v1.py --self-test
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path("/home/jesse/openroot")
MAX_FILES = 4000
MAX_FILE_BYTES = 300_000
MAX_TOTAL_BYTES = 80_000_000
MAX_MD_CORPUS_BYTES = 12_000_000
STALE_HEARTBEAT_HOURS = 26

SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules", "site-packages",
    "logs", "archive", "attic", "tmp", "consolidation-backups",
    "quarantine_handoff_corrupt", "harvest", "workareas", "demo-pod",
    ".venv", ".cache",
}

ENTRY_POINTS = {
    "README.md": "HIGH",
    "STARTHERE.md": "HIGH",
    "CONTRIBUTING.md": "MED",
    "GOALS.md": "MED",
    "TASK.md": "LOW",
    "MASTER_TODO.md": "LOW",
    "ARCHITECTURE.md": "LOW",
    "SESSION_STATE.md": "LOW",
    "CODE_OF_CONDUCT.md": "LOW",
    "SECURITY.md": "LOW",
}

CHAINS = [
    ("ledger/newton_chain.jsonl", "HIGH", "newton chain (the provenance spine)"),
    ("data/bot_heartbeats.jsonl", "MED", "bot heartbeats"),
    ("data/discovery_chain.jsonl", "LOW",
     "discovery chain (run newton_chain_discovery.py to create)"),
    ("data/pathway_cache.jsonl", "LOW",
     "pathway cache (run pathway_cache_v1.py record to create)"),
]

LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
BAK_RE = re.compile(r"(\.bak(\..*)?|\.backup(\..*)?|\.old|\~)$", re.I)
VER_SUFFIX_RE = re.compile(r"([_-]v\d+|[_-]\d{8,})$", re.I)
SEV_ORDER = {"HIGH": 0, "MED": 1, "LOW": 2}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def severity(item):
    return SEV_ORDER.get(item.get("severity", "LOW"), 3)


def walk_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def collect_corpus(root: Path):
    docs, md_paths = [], []
    files_seen = total_md_bytes = 0
    for p in walk_files(root):
        files_seen += 1
        if p.suffix.lower() == ".md":
            md_paths.append(p)
    for p in md_paths[:MAX_FILES]:
        try:
            if p.is_symlink() or not p.exists():
                continue
            if p.stat().st_size > MAX_FILE_BYTES:
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        b = len(text.encode("utf-8"))
        if total_md_bytes + b > MAX_MD_CORPUS_BYTES:
            break
        total_md_bytes += b
        docs.append((p, text))
    stats = {"files_seen": files_seen, "md_found": len(md_paths),
             "md_read": len(docs), "md_bytes": total_md_bytes}
    return docs, stats, md_paths


def check_entry_points(root: Path):
    out = []
    for name, sev in ENTRY_POINTS.items():
        if not (root / name).exists():
            out.append({
                "kind": "missing_entry_point", "severity": sev, "path": name,
                "detail": f"expected anchor file {name} is absent",
                "hint": f"create {name} (STARTHERE.md is the newcomer front door)",
            })
    return out


def check_broken_links(docs):
    out = []
    for p, text in docs:
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            t = Path(target)
            resolved = t if t.is_absolute() else (p.parent / t)
            try:
                if resolved.exists():
                    continue
            except OSError:
                continue
            line = text[: m.start()].count("\n") + 1
            out.append({
                "kind": "broken_link", "severity": "MED", "path": str(p),
                "detail": f"line \~{line} links to missing target: {target}",
                "hint": "fix the path or create the target file",
            })
            if len(out) >= 60:
                return out
    return out


def check_stub_docs(docs):
    out = []
    for p, text in docs:
        lines = text.split("\n")
        in_fence = False
        headings, body_chars = [], 0
        empty_sections = []
        for raw in lines:
            line = raw.strip()
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if line.startswith("#"):
                if headings and body_chars < 20:
                    empty_sections.append(headings[-1])
                headings.append(line.lstrip("#").strip() or "(untitled)")
                body_chars = 0
            elif line:
                body_chars += len(line)
        if headings and body_chars < 20:
            empty_sections.append(headings[-1])
        if len(headings) >= 2 and empty_sections:
            out.append({
                "kind": "stub_doc", "severity": "MED", "path": str(p),
                "detail": f"{len(empty_sections)} heading(s) with no body, e.g. "
                          + "; ".join(empty_sections[:4]),
                "hint": "fill the sections or delete the placeholder file",
            })
    return out


def check_orphan_tools(docs, root):
    corpus_text = "\n".join(t for _, t in docs)
    out = []
    count = 0
    tool_dirs = [root / "bin", root]
    seen = set()
    for d in tool_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.py")):
            if p.name in seen:
                continue
            seen.add(p.name)
            count += 1
            if count > 300:
                break
            stem = p.stem
            stem = VER_SUFFIX_RE.sub("", stem)
            stem = BAK_RE.sub("", stem)
            if stem and stem not in corpus_text:
                out.append({
                    "kind": "orphan_tool", "severity": "LOW", "path": str(p),
                    "detail": "never mentioned by any markdown doc in the repo",
                    "hint": "document it in STARTHERE.md tool map or docs/, "
                            "or retire it",
                })
            if len(out) >= 40:
                return out
    return out


def check_sprawl(md_paths, root):
    out = []
    baks, groups = [], {}
    for p in walk_files(root):
        name = p.name
        if BAK_RE.search(name):
            baks.append(str(p))
            continue
        if p.suffix == ".py" and p.parent in (root, root / "bin"):
            base = VER_SUFFIX_RE.sub("", p.stem)
            base = BAK_RE.sub("", base).lower()
            groups.setdefault(base, []).append(p.name)
    multi = {k: v for k, v in groups.items() if len(v) >= 3}
    if baks:
        out.append({
            "kind": "backup_sprawl", "severity": "LOW", "path": str(root),
            "detail": f"{len(baks)} .bak/.backup/.old files, e.g. "
                      + ", ".join(baks[:3]),
            "hint": "move backups out of the live tree or into archive/",
        })
    if multi:
        worst = max(multi.items(), key=lambda kv: len(kv[1]))
        out.append({
            "kind": "backup_sprawl", "severity": "MED", "path": str(root),
            "detail": f"{len(multi)} script names with 3+ live variants; "
                      f"worst: {worst[0]} -> {', '.join(sorted(worst[1])[:5])}",
            "hint": "consolidate to one canonical version per script; "
                    "history belongs in git, not in filename suffixes",
        })
    return out


def check_chains(root):
    out = []
    for rel, sev, label in CHAINS:
        p = root / rel
        if not p.exists():
            out.append({
                "kind": "chain_health", "severity": sev, "path": rel,
                "detail": f"{label} is absent",
                "hint": "create it with the matching tool when ready",
            })
            continue
        if rel.endswith("bot_heartbeats.jsonl"):
            age_h = (time.time() - p.stat().st_mtime) / 3600.0
            if age_h > STALE_HEARTBEAT_HOURS:
                out.append({
                    "kind": "chain_health", "severity": "MED", "path": rel,
                    "detail": f"heartbeats stale: last write {age_h:.1f}h ago",
                    "hint": "check the bot loop / heartbeat writer",
                })
    return out


def check_dead_symlinks(root):
    out = []
    dead = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames + dirnames:
            p = Path(dirpath) / name
            try:
                if p.is_symlink() and not p.exists():
                    dead.append(str(p))
            except OSError:
                continue
        if len(dead) >= 200:
            break
    if dead:
        out.append({
            "kind": "dead_symlink", "severity": "MED", "path": str(root),
            "detail": f"{len(dead)} dead symlinks, e.g. " + ", ".join(dead[:5]),
            "hint": "remove or retarget them (they break every walker)",
        })
    return out


def check_root_clutter(root):
    try:
        loose = [x for x in root.iterdir() if x.is_file()
                 and not x.is_symlink() and x.suffix != ".md"]
    except OSError:
        return []
    if len(loose) > 60:
        return [{
            "kind": "root_clutter", "severity": "LOW", "path": str(root),
            "detail": f"{len(loose)} loose non-doc files in the repo root",
            "hint": "move scripts into bin/, data into data/, logs into logs/",
        }]
    return []


def scan(root: Path):
    docs, stats, _ = collect_corpus(root)
    findings = []
    findings += check_entry_points(root)
    findings += check_broken_links(docs)
    findings += check_stub_docs(docs)
    findings += check_orphan_tools(docs, root)
    findings += check_sprawl(docs, root)
    findings += check_chains(root)
    findings += check_dead_symlinks(root)
    findings += check_root_clutter(root)
    findings.sort(key=lambda f: (severity(f), f["kind"], str(f.get("path", ""))))
    counts = {"HIGH": 0, "MED": 0, "LOW": 0}
    for f in findings:
        counts[f["severity"]] += 1
    return {
        "tool": "friction_observer_v1",
        "root": str(root),
        "generated": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "counts": counts,
        "findings": findings,
    }


def print_report(rep):
    print("=" * 72)
    print(f"FRICTION OBSERVER v1 — {rep['root']}")
    print(f"generated {rep['generated']}")
    print(f"scanned: {rep['stats']['files_seen']} files, "
          f"{rep['stats']['md_read']} markdown read "
          f"({rep['stats']['md_bytes'] // 1024} KiB)")
    print(f"findings: HIGH {rep['counts']['HIGH']} / "
          f"MED {rep['counts']['MED']} / LOW {rep['counts']['LOW']}")
    print("=" * 72)
    cur = None
    for f in rep["findings"]:
        if f["severity"] != cur:
            cur = f["severity"]
            print(f"\n--- {cur} ---")
        print(f"[{f['kind']}] {f.get('path', '-')}")
        print(f"    {f['detail']}")
    highs = [f for f in rep["findings"] if f["severity"] == "HIGH"]
    meds = [f for f in rep["findings"] if f["severity"] == "MED"]
    path = highs + meds
    if path:
        print("\n--- SUGGESTED PATHWAY (fix in this order) ---")
        hints, seen = [], set()
        for f in path:
            h = f["hint"]
            if h not in seen:
                seen.add(h)
                hints.append(h)
        for i, h in enumerate(hints[:12], 1):
            print(f"  {i}. {h}")
        print("\nWhen a fix works, seal it:")
        print("  python3 bin/pathway_cache_v1.py record --name \"...\" "
              "--step \"...\" --evidence <file>")
    else:
        print("\nNo HIGH/MED friction found. The commons is compounding clean.")


def chain_append(ledger: Path, entry: dict) -> str:
    prev = None
    if ledger.exists():
        try:
            lines = ledger.read_text(encoding="utf-8").strip().split("\n")
            if lines and lines[-1].strip():
                prev = json.loads(lines[-1]).get("hash")
        except (json.JSONDecodeError, OSError):
            prev = None
    entry["previous_hash"] = prev
    core = {k: v for k, v in entry.items() if k != "hash"}
    entry["hash"] = sha256_bytes(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode())
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry["hash"]


def main():
    if "--self-test" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser(description="OpenRoot friction observer v1")
    ap.add_argument("--root", type=str, default=str(DEFAULT_ROOT))
    ap.add_argument("--write-ledger", type=str, default=None)
    ap.add_argument("--json", dest="json_out", type=str, default=None)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[error] root is not a directory: {root}", file=sys.stderr)
        return 1
    rep = scan(root)
    print_report(rep)
    if args.json_out:
        out = Path(args.json_out)
        out.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"\n[ok] report json -> {out} "
              f"(sha256 {sha256_bytes(out.read_bytes())[:16]}...)")
    if args.write_ledger:
        ledger = Path(args.write_ledger)
        if not ledger.is_absolute():
            ledger = root / ledger
        entry = {
            "event": "FRICTION_SCAN",
            "ts": rep["generated"],
            "root": rep["root"],
            "stats": rep["stats"],
            "counts": rep["counts"],
            "high": [f for f in rep["findings"] if f["severity"] == "HIGH"][:10],
        }
        h = chain_append(ledger, entry)
        print(f"[ok] sealed scan -> {ledger} (hash {h[:16]}...)")
    return 0


def self_test():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="friction_selftest_"))
    try:
        (tmp / "bin").mkdir()
        (tmp / "ledger").mkdir()
        (tmp / "README.md").write_text(
            "# Repo\n\nSee [guide](docs/guide.md).\n\n"
            "documented_tool is documented here.\n")
        (tmp / "STUB.md").write_text("# Alpha\n\n# Beta\n\n# Gamma\n\n")
        (tmp / "bin").joinpath("orphan_one.py").write_text("print(1)\n")
        (tmp / "bin").joinpath("documented_tool.py").write_text("print(2)\n")
        (tmp / "old_thing.py.bak.20260101").write_text("x\n")
        (tmp / "ledger").joinpath("newton_chain.jsonl").write_text(
            '{"event":"X","hash":"a"}\n{"event":"Y","hash":"b"}\n')
        hb = tmp / "data" / "bot_heartbeats.jsonl"
        hb.parent.mkdir()
        hb.write_text('{"event":"HEARTBEAT"}\n')
        old = time.time() - 40 * 3600
        os.utime(hb, (old, old))
        broken = tmp / "dangling"
        broken.symlink_to(tmp / "nope_missing")
        rep = scan(tmp)
        kinds = {f["kind"] for f in rep["findings"]}
        assert "missing_entry_point" in kinds, "entry point check failed"
        assert "broken_link" in kinds, "broken link check failed"
        assert "stub_doc" in kinds, "stub doc check failed"
        assert "orphan_tool" in kinds, "orphan tool check failed"
        assert "backup_sprawl" in kinds, "sprawl check failed"
        assert "chain_health" in kinds, "chain health check failed"
        assert "dead_symlink" in kinds, "dead symlink check failed"
        led = tmp / "led.jsonl"
        h1 = chain_append(led, {"event": "T1"})
        h2 = chain_append(led, {"event": "T2"})
        assert h1 != h2
        recs = [json.loads(l) for l in led.read_text().strip().split("\n")]
        assert recs[1]["previous_hash"] == recs[0]["hash"]
        bl = [f for f in rep["findings"] if f["kind"] == "broken_link"]
        assert any("docs/guide.md" in f["detail"] for f in bl)
        print("friction_observer_v1 self-test: ALL PASS "
              f"({len(rep['findings'])} findings on fixture)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
