#!/usr/bin/env python3
"""
spider_reconcile.py — join local SHA-256 inventory vs the GitHub inventory,
spider out along the timeline (time-clustered work sessions), and draft an
upgrade plan. READ-ONLY: writes reports only. Deletes/moves/pushes nothing.

Usage:
  python3 spider_reconcile.py                                # auto-find local inventory
  python3 spider_reconcile.py --local ~/.openroot_tap.tsv
  python3 spider_reconcile.py --build-local '~/openroot,~/openroot-main-clean'
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

DEF_ROOTS = ("~/openroot*,~/openroot_docs,~/github*,~/jesseray718*,"
             "~/jesseray718.github.io,~/une*,~/src,~/code,~/knowledge,"
             "~/knowledge-node,~/vault,~/Kai,~/Kai9000,~/A1,~/aerocement*,"
             "~/black-locust-rmh,~/renaissance-protocol,~/recovery,"
             "~/wisdom-scaffold,~/wisdom-recovery,~/lumo,~/work,~/workareas")

ap = argparse.ArgumentParser()
ap.add_argument("--local", help="existing local inventory file (columns auto-detected)")
ap.add_argument("--ghdir", help="github_hash_inventory.py output dir")
ap.add_argument("--mirror", help="mirror .git dir for CRLF-normalized re-hash")
ap.add_argument("--roots", default=DEF_ROOTS,
                help="comma-separated ~-relative patterns scoping the analysis")
ap.add_argument("--gap-hours", type=float, default=6.0, help="session split gap")
ap.add_argument("--build-local", metavar="ROOTS",
                help="walk+hash these roots into a fresh local inventory")
ap.add_argument("--out", help="output dir (default: same as --ghdir)")
args = ap.parse_args()

def die(m):
    print("[FATAL] " + m, file=sys.stderr)
    sys.exit(1)

def parse_any_ts(s):
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass
    try:
        f = float(s)
        if 1e9 < f < 2e9:
            return datetime.fromtimestamp(f)
    except ValueError:
        pass
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2})", s)
    if m:
        return datetime.fromisoformat(m.group(1) + " " + m.group(2))
    return None

# ---------- github side ----------
ghdir = Path(args.ghdir) if args.ghdir else None
if ghdir is None:
    cands = sorted((HOME / "openroot" / "reports").glob("gh-audit-*"),
                   key=lambda p: p.stat().st_mtime)
    if not cands:
        die("no ~/openroot/reports/gh-audit-* — run github_hash_inventory.py first")
    ghdir = cands[-1]
for f in ("github_head_files.tsv", "github_all_blobs.tsv", "github_timeline.tsv"):
    if not (ghdir / f).exists():
        die("missing %s in %s" % (f, ghdir))
OUT = Path(args.out) if args.out else ghdir
print("[1/6] github side: %s" % ghdir)

def rows(p):
    with open(p, errors="replace") as f:
        rdr = csv.reader(f, delimiter="\t")
        next(rdr, None)
        return [x for x in rdr if x]

head_rows = rows(ghdir / "github_head_files.tsv")   # sha256 sha1 size path
blob_rows = rows(ghdir / "github_all_blobs.tsv")
tl_rows = rows(ghdir / "github_timeline.tsv")

gh_head_path = {r[0].lower(): r[3] for r in head_rows if len(r) >= 4}
gh_head_sha1 = {r[0].lower(): r[1] for r in head_rows if len(r) >= 4}
gh_blob_meta = {r[0].lower(): r for r in blob_rows if len(r) >= 3}
tl = []
for r in tl_rows:
    if len(r) >= 4:
        dt = parse_any_ts(r[0])
        if dt:
            tl.append((dt, r[2], r[3]))
tl.sort(key=lambda x: x[0])

# ---------- local side ----------
def build_local(roots, outpath):
    PRUNE = {".git", "node_modules", ".next", "venv", "__pycache__",
             ".cache", ".ollama", ".npm", "snap", ".local", ".var"}
    n = 0
    with open(outpath, "w") as f:
        f.write("sha256\tsize\tmtime\tpath\n")
        for root in roots:
            for dp, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d not in PRUNE]
                for fn in files:
                    p = os.path.join(dp, fn)
                    try:
                        if os.path.islink(p) or not os.path.isfile(p):
                            continue
                        st = os.stat(p)
                        h = hashlib.sha256()
                        with open(p, "rb") as fh:
                            for chunk in iter(lambda: fh.read(1 << 20), b""):
                                h.update(chunk)
                        f.write("%s\t%d\t%s\t%s\n" % (
                            h.hexdigest(), st.st_size,
                            datetime.fromtimestamp(st.st_mtime).isoformat(
                                timespec="seconds"), p))
                        n += 1
                    except OSError:
                        pass
    print("[2/6] built fresh local inventory: %d files -> %s" % (n, outpath))
    return outpath

def load_local(path):
    """Auto-detect format; return list of (sha256, size|None, mtime|None, path)."""
    with open(path, errors="replace") as f:
        sample = [next(f, "") for _ in range(200)]
    nonempty = [l for l in sample if l.strip()]
    if not nonempty:
        raise ValueError("inventory file empty: %s" % path)
    if re.match(r"^[0-9a-fA-F]{64}\s{2}\S", nonempty[0]):   # sha256sum native
        out = []
        with open(path, errors="replace") as f:
            for line in f:
                m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$", line)
                if m:
                    out.append((m.group(1).lower(), None, None, m.group(2)))
        return out
    try:                                                     # jsonl
        obj = json.loads(nonempty[0])
        if isinstance(obj, dict):
            hk = next(k for k, v in obj.items()
                      if isinstance(v, str) and HASH_RE.match(v))
            pk = next(k for k, v in obj.items()
                      if isinstance(v, str) and ("/" in v or v.startswith("~")))
            out = []
            with open(path, errors="replace") as f:
                for line in f:
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(o, dict) and HASH_RE.match(str(o.get(hk, ""))):
                        out.append((str(o[hk]).lower(), None, None,
                                    str(o.get(pk, ""))))
            return out
    except Exception:
        pass
    delim = "\t" if nonempty[0].count("\t") >= 1 else (
        "," if nonempty[0].count(",") >= 1 else None)
    if delim is None:
        raise ValueError("unrecognized format: %s" % path)
    parsed = [l.rstrip("\n").split(delim) for l in nonempty]
    ncol = max(len(r) for r in parsed)
    hash_col = path_col = mt_col = None
    for c in range(ncol):
        vals = [r[c] for r in parsed if len(r) > c]
        if len(vals) < 10:
            continue
        if hash_col is None and sum(1 for v in vals
                if HASH_RE.match(v.strip())) / len(vals) > 0.8:
            hash_col = c
            continue
        if path_col is None and sum(1 for v in vals
                if v.strip().startswith(("/", "~", "./"))) / len(vals) > 0.5:
            path_col = c
        if mt_col is None and sum(1 for v in vals
                if TS_RE.match(v.strip()) or (v.strip().isdigit()
                and 1e9 < float(v.strip()) < 2e9)) / len(vals) > 0.5:
            mt_col = c
    if hash_col is None or path_col is None:
        raise ValueError("no hash/path columns found in %s" % path)
    out = []
    with open(path, errors="replace") as f:
        rdr = csv.reader(f, delimiter=delim)
        next(rdr, None)
        for r in rdr:
            if len(r) <= max(hash_col, path_col):
                continue
            h = r[hash_col].strip()
            if not HASH_RE.match(h):
                continue
            p = r[path_col].strip()
            if p.startswith("~"):
                p = str(HOME) + p[1:]
            elif not p.startswith("/"):
                p = os.path.join(str(HOME), p)
            mt = parse_any_ts(r[mt_col]) if mt_col is not None and len(r) > mt_col else None
            sz = None
            for c in range(ncol):
                if c in (hash_col, path_col, mt_col):
                    continue
                v = r[c].strip() if len(r) > c else ""
                if v.isdigit():
                    sz = int(v)
                    break
            out.append((h.lower(), sz, mt, p))
    return out

if args.build_local:
    roots = [os.path.expanduser(x) for x in args.build_local.split(",") if x.strip()]
    for r in roots:
        if not os.path.isdir(r):
            die("no such dir: %s" % r)
    local_file = build_local(roots, str(ghdir / "local_files.tsv"))
    local_rows = load_local(local_file)
else:
    if args.local:
        cands = [Path(args.local)]
    else:
        cands = [HOME / ".openroot_tap.tsv", HOME / "full_inventory.txt"]
        cands += sorted(HOME.glob("openroot-safety-inventory-*.txt"))
        cands = [c for c in cands if c.exists()]
        if not cands:
            die("no local inventory found; use --local or --build-local")
        cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    local_rows = None
    for c in cands:
        try:
            cand_rows = load_local(str(c))
        except (ValueError, OSError):
            continue
        if len(cand_rows) >= 100:
            local_rows = cand_rows
            print("[2/6] local inventory: %s (%d rows)" % (c, len(cand_rows)))
            break
    if local_rows is None:
        die("no parsable local inventory — use --build-local, or paste me `head -3` of yours")

# ---------- scope ----------
roots = []
for pat in args.roots.split(","):
    pat = pat.strip()
    if pat:
        roots += [str(p) for p in HOME.glob(pat.lstrip("~/"))]
roots = sorted(set(roots))

def under_roots(p):
    return any(p == r or p.startswith(r + "/") for r in roots)

scoped = [t for t in local_rows if under_roots(t[4 - 1])]
print("[3/6] scoped to %d ecosystem roots: %d of %d local rows" %
      (len(roots), len(scoped), len(local_rows)))

local_by_hash = defaultdict(list)
mt_by_path = {}
for h, sz, mt, p in scoped:
    local_by_hash[h].append(p)
    if mt:
        mt_by_path.setdefault(p, mt)

lh = set(local_by_hash)
on_head = lh & set(gh_head_path)
in_hist = (lh & set(gh_blob_meta)) - on_head
local_only = lh - set(gh_blob_meta)
gh_only = set(gh_head_path) - lh

# ---------- CRLF-normalized second pass ----------
print("[4/6] CRLF-normalized near-match pass ...")
SIZE_CAP = 2 * 1024 * 1024

def norm_hash_bytes(data):
    if b"\0" in data[:8192]:
        return None
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()

def norm_file(p):
    try:
        if os.path.islink(p) or os.path.getsize(p) > SIZE_CAP:
            return None
        with open(p, "rb") as f:
            return norm_hash_bytes(f.read())
    except OSError:
        return None

crlf_matches = []
mirror = args.mirror
if mirror is None:
    m = sorted((HOME / ".openroot_gh_audit").glob("mirror-*.git"),
               key=lambda p: p.stat().st_mtime)
    if m:
        mirror = str(m[-1])
if mirror and os.path.isdir(mirror) and gh_only and local_only:
    gh_norm = {}
    p = subprocess.Popen(["git", "--git-dir", mirror, "cat-file", "--batch"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for h in list(gh_only)[:4000]:
            sha1 = gh_head_sha1.get(h)
            if not sha1:
                continue
            p.stdin.write((sha1 + "\n").encode())
            p.stdin.flush()
            hdr = p.stdout.readline().decode("utf-8", "replace").split()
            if len(hdr) < 3:
                continue
            size = int(hdr[2])
            data, rem = b"", size
            while rem > 0:
                chunk = p.stdout.read(min(1 << 16, rem))
                if not chunk:
                    break
                data += chunk
                rem -= len(chunk)
            p.stdout.read(1)
            if size <= SIZE_CAP:
                nh = norm_hash_bytes(data)
                if nh:
                    gh_norm[nh] = h
    finally:
        try:
            p.stdin.close()
        except Exception:
            pass
        try:
            p.wait(timeout=10)
        except Exception:
            p.kill()
    loc_norm = defaultdict(list)
    for h in list(local_only)[:8000]:
        for path in local_by_hash[h][:3]:
            nh = norm_file(path)
            if nh:
                loc_norm[nh].append(path)
    for nh, paths in loc_norm.items():
        if nh in gh_norm:
            crlf_matches.append((gh_norm[nh], gh_head_path[gh_norm[nh]], paths))

# ---------- timeline spider: session clustering ----------
print("[5/6] spider: clustering local-only files into sessions ...")
items, orphaned = [], []
for h in local_only:
    for path in local_by_hash[h][:2]:
        mt = mt_by_path.get(path)
        if mt is None:
            try:
                mt = datetime.fromtimestamp(os.stat(path).st_mtime)
            except OSError:
                mt = None
        if mt is None:
            orphaned.append(path)
        else:
            items.append((mt, path, h))
items.sort()
gap = timedelta(hours=args.gap_hours)
clusters, cur = [], []
for it in items:
    if cur and (it[0] - cur[-1][0]) > gap:
        clusters.append(cur)
        cur = []
    cur.append(it)
if cur:
    clusters.append(cur)
clusters.sort(key=lambda c: c[-1][0])

def recommend(paths):
    live = [p for p in paths
            if p.startswith(str(HOME / "openroot") + "/") and "/reports/" not in p]
    if live:
        return "ADD-CANDIDATE — sits in the live repo tree but is not on GitHub"
    clones = {part for p in paths for part in p.split("/")
              if part.startswith("openroot-")}
    if clones:
        return "CLONE-REVIEW — lives in %s; check if that clone is stale" % \
               ", ".join(sorted(clones)[:3])
    return "REVIEW — outside the openroot tree; classify manually"

def gh_window(a, b):
    lo, hi = a - timedelta(hours=12), b + timedelta(hours=12)
    return [e for e in tl if lo <= e[0] <= hi]

sess_md = []
for i, c in enumerate(clusters[-60:], 1):
    start, end = c[0][0], c[-1][0]
    ev = gh_window(start, end)
    acts = Counter(e[1] for e in ev)
    dirs = Counter(os.path.dirname(p) for _, p, _ in c)
    paths = [p for _, p, _ in c]
    sess_md.append("### S%02d  %s -> %s  (%d files)  [%s]" %
                   (i, start, end, len(c), recommend(paths)))
    sess_md.append("- top dirs: %s" %
                   ", ".join("%s (%d)" % d for d in dirs.most_common(3)))
    sess_md.append("- github activity +-12h: %s" %
                   (", ".join("%s=%d" % kv for kv in sorted(acts.items()))
                    or "NONE — nothing reached GitHub in this window"))
    for e in ev[:12]:
        sess_md.append("    gh %s %s" % (e[1], e[2]))
    for p in paths[:25]:
        sess_md.append("    local %s" % p)
    if len(paths) > 25:
        sess_md.append("    ... +%d more" % (len(paths) - 25))
    sess_md.append("")

# ---------- reports ----------
print("[6/6] writing reports ...")
lo_bytes = 0
for h in local_only:
    for p in local_by_hash[h][:1]:
        try:
            lo_bytes += os.stat(p).st_size
        except OSError:
            pass

drift = []
for h in on_head:
    gp = gh_head_path[h]
    if not any(p.endswith(gp) or p == gp for p in local_by_hash[h]):
        drift.append((gp, local_by_hash[h][:2]))

gh_only_sorted = sorted(gh_only, key=lambda h: -int(gh_blob_meta.get(h, ["?", "?", "0"])[2]))

R = ["# RECONCILE REPORT", "",
     "local rows (scoped): %d | on GitHub HEAD: %d | in GitHub history only: %d" %
     (len(scoped), len(on_head), len(in_hist)),
     "LOCAL-ONLY content: %d hashes (~%.1f MB first-copy) | GITHUB-ONLY: %d" %
     (len(local_only), lo_bytes / 1e6, len(gh_only)),
     "CRLF near-matches: %d | sessions: %d | orphaned inventory paths: %d" %
     (len(crlf_matches), len(clusters), len(orphaned)), "",
     "## Sessions (newest 60; gap split at %.0fh)" % args.gap_hours, ""]
R += sess_md
R += ["## CRLF near-matches (same content, line endings differ)", ""]
for gh_h, gp, lps in crlf_matches[:40]:
    R.append("- gh:%s  ~=  local:%s" % (gp, lps[0]))
R += ["", "## Path drift (content on GitHub under a different path)", ""]
for gp, lps in drift[:30]:
    R.append("- gh:%s  |  local:%s" % (gp, ", ".join(lps)))
R += ["", "## Orphaned inventory entries (hash known, file gone)", ""]
R += ["- %s" % p for p in orphaned[:15]]
(OUT / "RECONCILE.md").write_text("\n".join(R) + "\n")

U = ["# UPGRADE PLAN — DRAFT (nothing executed)", "",
     "Sources: github=%s | mirror=%s" % (ghdir, mirror or "n/a"), "",
     "## A. Recovery candidates (local content absent from GitHub)",
     "See sessions marked ADD-CANDIDATE / CLONE-REVIEW in RECONCILE.md.", "",
     "## B. GitHub-only content (local restore candidates), top 40 by size", ""]
for h in gh_only_sorted[:40]:
    meta = gh_blob_meta.get(h, ["?", "?", "?"])
    U.append("- %s  %s bytes  first seen %s" % (gh_head_path.get(h, "?"), meta[2], meta[3]))
U += ["", "## C. CRLF variants — normalize before re-adding (up to 40)", ""]
for gh_h, gp, lps in crlf_matches[:40]:
    U.append("- gh:%s ~= local:%s" % (gp, lps[0]))
U += ["", "## Proposed next actions (awaiting sign-off)",
      "1. Per ADD-CANDIDATE session: explicit `git add` file list, one commit",
      "   per session — preserves the work timeline in history.",
      "2. CLONE-REVIEW dirs: diff each clone's HEAD vs origin before retiring",
      "   (scriptable on request).",
      "3. If CRLF variants appear: settle a .gitattributes policy once, then",
      "   normalize in a single commit.",
      "4. GITHUB-ONLY items: restorable via checkout; verify none are files",
      "   you deliberately deleted locally.",
      "",
      "Caveats: clone working-tree mtimes reflect clone/checkout time, not",
      "authoring — authoring time for cloned dirs lives in that clone's git",
      "log. GITHUB-ONLY accuracy depends on the local inventory's coverage.",
      "Nothing above runs without explicit approval."]
(OUT / "UPGRADE_PLAN.md").write_text("\n".join(U) + "\n")

print()
print("  scoped rows      : %d" % len(scoped))
print("  on GitHub HEAD   : %d" % len(on_head))
print("  history-only     : %d" % len(in_hist))
print("  local-only       : %d (~%.1f MB)" % (len(local_only), lo_bytes / 1e6))
print("  github-only      : %d" % len(gh_only))
print("  CRLF near-matches: %d" % len(crlf_matches))
print("  sessions         : %d" % len(clusters))
print()
print("  RECONCILE.md   : %s" % (OUT / "RECONCILE.md"))
print("  UPGRADE_PLAN.md: %s" % (OUT / "UPGRADE_PLAN.md"))
