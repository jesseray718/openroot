#!/usr/bin/env python3
"""
github_hash_inventory.py — SHA-256 inventory of every file on GitHub.

GitHub does NOT expose SHA-256 (its API serves git blob SHA-1s only). The
equivalent — strictly better — is a mirror clone: one transfer gets every
blob on every branch/tag/PR ref, and we hash each blob locally.

Default target: jesseray718/openroot. Override with:
    GH_REPO_URL=https://github.com/jesseray718/<repo>.git python3 <this>

Outputs (default ~/openroot/reports/gh-audit-<ts>/):
  github_head_files.tsv   files on the default branch right now
  github_all_blobs.tsv    every distinct blob reachable from any ref
  github_timeline.tsv     every add/modify/delete event, oldest first
  GITHUB_INVENTORY.md     human summary

Side effects: one mirror at ~/.openroot_gh_audit/ (reused on later runs).
Your working repos are never touched. Nothing is pushed or deleted.
"""
import hashlib, os, re, subprocess, sys, time
from pathlib import Path

REPO_URL = os.environ.get("GH_REPO_URL", "https://github.com/jesseray718/openroot.git")
TS   = time.strftime("%Y%m%d-%H%M%S")
OUT  = Path(os.environ.get("GH_AUDIT_OUT",
         str(Path.home() / "openroot" / "reports" / ("gh-audit-" + TS))))
name = re.sub(r"[^A-Za-z0-9_.-]", "_", REPO_URL.rsplit("/", 1)[-1])
name = name[:-4] if name.endswith(".git") else name
MIRROR = Path.home() / ".openroot_gh_audit" / ("mirror-" + name + ".git")

TOK = [re.compile(p) for p in (
    r"gh[pousr]_[A-Za-z0-9]{16,}", r"github_pat_[A-Za-z0-9_]{16,}",
    r"sk-[A-Za-z0-9]{16,}", r"AKIA[0-9A-Z]{12,}",
    r"xox[baprs]-[A-Za-z0-9-]+", r"(?i)bearer\s+[A-Za-z0-9._-]{12,}")]

def redact(s):
    for p in TOK:
        s = p.sub("<REDACTED>", s)
    return s

def sh(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True,
                          errors="replace")

def die(m):
    print("[FATAL] " + m, file=sys.stderr)
    sys.exit(1)

OUT.mkdir(parents=True, exist_ok=True)

# ---- 1. mirror ------------------------------------------------------
if (MIRROR / "HEAD").exists():
    print("[1/5] updating mirror: %s" % MIRROR)
    r = sh("--git-dir", str(MIRROR), "remote", "update", "--prune")
    if r.returncode:
        die("mirror update failed: %s" % r.stderr.strip()[:400])
else:
    print("[1/5] mirror cloning: %s" % REPO_URL)
    r = sh("clone", "--mirror", REPO_URL, str(MIRROR))
    if r.returncode:
        die("clone failed (auth/network?): %s" % r.stderr.strip()[:400])

db = sh("--git-dir", str(MIRROR), "symbolic-ref", "--short", "HEAD").stdout.strip()
if not db:
    db = sh("--git-dir", str(MIRROR), "for-each-ref",
            "--format=%(refname:short)", "refs/heads").stdout.split("\n")[0].strip()
    if not db:
        die("could not determine default branch")
head = sh("--git-dir", str(MIRROR), "rev-parse", db).stdout.strip()
refs = sh("--git-dir", str(MIRROR), "for-each-ref",
          "--format=%(refname)").stdout.split()
print("      branch=%s HEAD=%s refs=%d" % (db, head[:10], len(refs)))

# ---- 2. timeline walk (oldest -> newest) ---------------------------
fmt = "%H%x01%aI%x01%an%x01%s"
r = sh("--git-dir", str(MIRROR), "log", "--all", "--topo-order",
       "--reverse", "--format=" + fmt)
commits = []
for line in r.stdout.splitlines():
    p = line.split("\x01")
    if len(p) == 4:
        commits.append((p[0], p[1], redact(p[2]), redact(p[3])[:120]))
print("[2/5] commits: %d" % len(commits))

events, first_seen, last_seen, blob_paths = [], {}, {}, {}
for ch, ts, an, subj in commits:
    raw = subprocess.run(["git", "--git-dir", str(MIRROR), "diff-tree", "-r",
                          "--root", "--no-commit-id", "--no-renames", "-z", ch],
                         capture_output=True).stdout
    toks = raw.split(b"\0")
    j = 0
    while j < len(toks):
        t = toks[j]
        if not t:
            j += 1
            continue
        if t.startswith(b":"):
            m = t.decode("utf-8", "replace").split()
            if len(m) >= 5 and "160000" not in (m[0].lstrip(":"), m[1]):
                osha, nsha, status = m[2], m[3], m[4][:1]
                path = toks[j + 1].decode("utf-8", "replace") if j + 1 < len(toks) else "?"
                blob = nsha if status in ("A", "M", "T") else osha
                if blob and set(blob) != {"0"}:
                    events.append((ts, ch[:10], status, path, blob))
                    last_seen[blob] = ts
                    if blob not in first_seen:
                        first_seen[blob] = (ts, ch, path)
                    blob_paths.setdefault(blob, set()).add(path)
            j += 2
        else:
            j += 1

# ---- 3. blob universe ----------------------------------------------
r = sh("--git-dir", str(MIRROR), "ls-tree", "-r", "-z", db)
head_files = []
for entry in r.stdout.split("\0"):
    if not entry:
        continue
    meta, _, path = entry.partition("\t")
    m = meta.split()
    if len(m) >= 3 and m[1] == "blob":
        head_files.append((path, m[2]))

objects = set(first_seen) | {s for _, s in head_files}
for line in sh("--git-dir", str(MIRROR), "rev-list",
               "--objects", "--all").stdout.splitlines():
    parts = line.split(" ", 1)
    if parts and re.fullmatch(r"[0-9a-f]{40}", parts[0]):
        objects.add(parts[0])

# ---- 4. sha256 every blob ------------------------------------------
print("[4/5] hashing %d objects (non-blobs filtered out) ..." % len(objects))
blobinfo = {}
p = subprocess.Popen(["git", "--git-dir", str(MIRROR), "cat-file", "--batch"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
try:
    for sha in objects:
        p.stdin.write((sha + "\n").encode())
        p.stdin.flush()
        hdr = p.stdout.readline().decode("utf-8", "replace").split()
        if len(hdr) < 3:            # "<sha> missing" — no content follows
            continue
        osha, otype, size = hdr[0], hdr[1], int(hdr[2])
        h, rem = hashlib.sha256(), size
        while rem > 0:
            chunk = p.stdout.read(min(1 << 16, rem))
            if not chunk:
                break
            h.update(chunk)
            rem -= len(chunk)
        p.stdout.read(1)             # trailing newline after content
        if otype == "blob":
            blobinfo[osha] = (h.hexdigest(), size)
finally:
    try:
        p.stdin.close()
    except Exception:
        pass
    try:
        p.wait(timeout=15)
    except Exception:
        p.kill()

# ---- 5. outputs -----------------------------------------------------
def tab(s):
    return str(s).replace("\t", "<TAB>")

with open(OUT / "github_head_files.tsv", "w") as f:
    f.write("sha256\tsha1\tsize\tpath\n")
    for path, sha1 in sorted(head_files):
        s256, size = blobinfo.get(sha1, ("?", -1))
        f.write("%s\t%s\t%d\t%s\n" % (s256, sha1, size, tab(path)))

with open(OUT / "github_all_blobs.tsv", "w") as f:
    f.write("sha256\tsha1\tsize\tfirst_ts\tfirst_commit\tlast_ts\tn_paths\tpaths\n")
    for sha1, (s256, size) in sorted(blobinfo.items(), key=lambda kv: -kv[1][1]):
        fts, fch, _ = first_seen.get(sha1, ("?", "?", "?"))
        paths = sorted(blob_paths.get(sha1, set()))
        pshow = "|".join(tab(x) for x in paths[:5])
        if len(paths) > 5:
            pshow += "|...+%d" % (len(paths) - 5)
        f.write("%s\t%s\t%d\t%s\t%s\t%s\t%d\t%s\n" %
                (s256, sha1, size, fts, fch[:10], last_seen.get(sha1, "?"),
                 len(paths), pshow))

with open(OUT / "github_timeline.tsv", "w") as f:
    f.write("ts\tcommit\taction\tpath\tblob_sha1\n")
    for ts, c, st, path, blob in events:
        f.write("%s\t%s\t%s\t%s\t%s\n" % (ts, c, st, tab(path), blob))

co = sh("--git-dir", str(MIRROR), "count-objects", "-vH").stdout
pack = next((l for l in co.splitlines() if l.startswith("size-pack")), "?")
L = ["# GITHUB INVENTORY — %s" % TS, "",
     "- repo: %s" % REPO_URL,
     "- default branch: `%s` @ %s" % (db, head[:12]),
     "- refs: %d | commits: %d | mirror pack: %s" %
     (len(refs), len(commits), pack.split(":")[-1].strip())]
if commits:
    L.append("- history span: %s -> %s" % (commits[0][1], commits[-1][1]))
L += ["- files on default branch now: %d" % len(head_files),
      "- distinct blobs on any ref: %d" % len(blobinfo),
      "- timeline events (A/M/D): %d" % len(events), "",
      "## 15 largest blobs"]
for sha1, (s256, size) in sorted(blobinfo.items(), key=lambda kv: -kv[1][1])[:15]:
    L.append("- %.1f MB  %s  (first seen %s)" %
             (size / 1e6, sorted(blob_paths.get(sha1, {"?"}))[0],
              first_seen.get(sha1, ("?",))[0]))
L += ["", "Token-redacted. Read-only. Secret contents never read."]
(OUT / "GITHUB_INVENTORY.md").write_text("\n".join(L) + "\n")

print("[5/5] done")
print()
print("  head files : %d" % len(head_files))
print("  blobs      : %d" % len(blobinfo))
print("  events     : %d" % len(events))
print("  report dir : %s" % OUT)
print("  mirror     : %s  (reused next run)" % MIRROR)
