#!/usr/bin/env bash
#
# fleet_census_v1.sh — OPENROOT CONSOLIDATION CENSUS (READ-ONLY TEST RUN)
#
# Purpose: find EVERY copy of the openroot lineage on this machine — clones,
#   nested clones, renamed copies, diverged home-dir repos, sdcard/USB residue —
#   fingerprint them with git remotes + HEAD sha + file-level sha256, then
#   grade overlap (duplicate files, unique files, divergence) and emit sealed
#   receipts. MUTATES NOTHING. Commits nothing, deletes nothing, merges nothing.
#
# Environments: Termux (A15) AND Ubuntu (OptiPlex) — detects python3 via `command -v`.
#
# Usage:      bash fleet_census_v1.sh [--root DIR] [--name PATTERN]
#   --root    where to search (default: $HOME; add /sdcard on Termux separately)
#   --name    repo-name substring to hunt (default: openroot)
#
# Output:     ~/openroot_census_<TS>/
#               census_repos.txt        every candidate repo: path, remote(s), HEAD
#               census_divergence.txt   local HEAD vs each remote HEAD, ahead/behind
#               census_manifest.tsv     sha256 \t size \t path  (ALL copies, all files)
#               census_duplicates.tsv   hash -> list of ALL paths sharing it
#               census_unique_by_copy.tsv  files that exist in exactly ONE copy
#               census_grade.md         per-copy report card + orphan-tool hits
#               CENSUS_RECEIPT.md       sealed summary w/ manifest sha256 (Newton-bindable)
# Exit codes: 0 ok; 1 no python3; 2 no candidates; 3 root missing.
#
# SEAL: READ-ONLY. Safe to run on both nodes. Same output format both sides.

set -euo pipefail

ROOT="$HOME"; NAMEPAT="openroot"
while [ $# -gt 0 ]; do
  case "$1" in
    --root)  ROOT="$2"; shift 2 ;;
    --name)  NAMEPAT="$2"; shift 2 ;;
    *) echo "unknown arg: $1"; exit 3 ;;
  esac
done
[ -d "$ROOT" ] || { echo "DEFECT: root $ROOT missing"; exit 3; }
command -v python3 >/dev/null || { echo "DEFECT: python3 required"; exit 1; }

TS="$(date -u +%Y%m%dT%H%M%SZ)"
HOST="$(hostname 2>/dev/null || echo unknown)"
OUT="$HOME/openroot_census_${TS}"
mkdir -p "$OUT"
echo "[0/6] Census ${TS} @ ${HOST}  root=${ROOT}  pattern=${NAMEPAT}"
echo "      Output: ${OUT}   (READ-ONLY: nothing will be modified)"

# ---------------------------------------------------- 1. Find candidate copies
echo "[1/6] Hunting git repos matching '${NAMEPAT}' under ${ROOT}..."
: > "${OUT}/census_repos.txt"
FOUND=0
while IFS= read -r -d '' gdir; do
  wt="$(dirname "$gdir")"
  # Skip the census output itself and .git dirs nested inside .git
  case "$wt" in */openroot_census_*) continue ;; esac
  remotes="$({ git -C "$wt" remote -v || true; } 2>/dev/null | awk '{print $2}' | sort -u | tr '\n' '|' )"
  head="$(git -C "$wt" rev-parse HEAD 2>/dev/null || echo NO_COMMITS)"
  branch="$(git -C "$wt" branch --show-current 2>/dev/null || echo detached)"
  dirty="$({ git -C "$wt" status --porcelain 2>/dev/null || true; } | wc -l)"
  printf 'COPY=%s\tBRANCH=%s\tHEAD=%s\tDIRTY=%s\tREMOTES=%s\n' \
    "$wt" "$branch" "$head" "$dirty" "${remotes:-none}" >> "${OUT}/census_repos.txt"
  FOUND=$((FOUND+1))
done < <(find "$ROOT" -type d -name .git -print0 2>/dev/null)

# Also: plain directories named like the pattern WITHOUT .git (copied folders)
echo "-- non-git directories named '*${NAMEPAT}*' --" >> "${OUT}/census_repos.txt"
find "$ROOT" -maxdepth 6 -type d -iname "*${NAMEPAT}*" ! -path "*/.git/*" ! -name ".git" 2>/dev/null \
  | while read -r d; do
      [ -d "$d/.git" ] || printf 'NOGIT_DIR=%s\n' "$d" >> "${OUT}/census_repos.txt"
    done

[ "$FOUND" -eq 0 ] && { echo "DEFECT: no matching repos found"; exit 2; }
echo "      Found ${FOUND} git copies (+ any NOGIT_DIR lines)."

# --------------------------------------------------------- 2. Divergence per copy
echo "[2/6] Divergence vs remotes..."
: > "${OUT}/census_divergence.txt"
grep '^COPY=' "${OUT}/census_repos.txt" | while IFS=$'\t' read -r _; do
  wt="$(printf '%s' "$_" | sed 's/^COPY=//;s/\t.*//')"
  git -C "$wt" fetch --dry-run >/dev/null 2>&1 || true   # dry-run: NO ref update
  for R in $(git -C "$wt" remote 2>/dev/null); do
    ab="$(git -C "$wt" rev-list --left-right --count "HEAD...${R}/main" 2>/dev/null \
       || git -C "$wt" rev-list --left-right --count "HEAD...${R}/master" 2>/dev/null \
       || echo '??\t??')"
    printf '%s\tREMOTE=%s\tAHEAD/BEHIND=%s\n' "$wt" "$R" "$(echo "$ab" | tr '\t' '/')" \
      >> "${OUT}/census_divergence.txt"
  done
done
DIVS="$(wc -l < "${OUT}/census_divergence.txt")"
echo "      ${DIVS} remote-comparison lines."

# ------------------------------------------- 3. Full sha256 manifest of every copy
echo "[3/6] Hashing every file in every copy (this is the long step)..."
: > "${OUT}/census_manifest.tsv"
python3 - "$OUT" "$NAMEPAT" <<'PYEOF'
import os, sys, hashlib, datetime
out = sys.argv[1]; pat = sys.argv[2].lower()
copies = []
for line in open(os.path.join(out, "census_repos.txt")):
    line = line.strip()
    if line.startswith("COPY=") or line.startswith("NOGIT_DIR="):
        copies.append(line.split("=", 1)[1].split("\t")[0])
mf = open(os.path.join(out, "census_manifest.tsv"), "w", buffering=1)
n = h_fail = 0
for c in copies:
    for dirpath, dirs, files in os.walk(c):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for fn in files:
            p = os.path.join(dirpath, fn)
            try:
                h = hashlib.sha256()
                with open(p, "rb") as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        h.update(chunk)
                sz = os.path.getsize(p)
                mf.write(f"{h.hexdigest()}\t{sz}\t{p}\n"); n += 1
            except OSError:
                h_fail += 1
print(f"      hashed={n} unreadable={h_fail}")
PYEOF

# ------------------------------------------------------ 4. Dedup / unique split
echo "[4/6] Building duplicate groups and unique-per-copy sets..."
python3 - "$OUT" <<'PYEOF'
import os, sys
from collections import defaultdict
out = sys.argv[1]
by_hash = defaultdict(list)
for line in open(os.path.join(out, "census_manifest.tsv")):
    h, sz, p = line.rstrip("\n").split("\t", 2)
    by_hash[h].append((int(sz), p))
with open(os.path.join(out, "census_duplicates.tsv"), "w") as d, \
     open(os.path.join(out, "census_unique_by_copy.tsv"), "w") as u:
    dup_groups = uniq_files = dup_bytes = 0
    for h, lst in sorted(by_hash.items(), key=lambda kv: -kv[1][0][0]):
        paths = [p for _, p in lst]
        if len(paths) > 1:
            dup_groups += 1
            dup_bytes += lst[0][0] * (len(paths) - 1)
            d.write(h + "\t" + " ; ".join(paths) + "\n")
        else:
            uniq_files += 1
            u.write(h + "\t" + paths[0] + "\n")
    print(f"      duplicate-groups={dup_groups} reclaimable-bytes~{dup_bytes} unique-files={uniq_files}")
PYEOF

# ------------------------------------------------------------------ 5. Grade
echo "[5/6] Grading each copy (overlap, dirt, orphan-tools)..."
: > "${OUT}/census_grade.md"
python3 - "$OUT" <<'PYEOF'
import os, sys, re
from collections import defaultdict
out = sys.argv[1]
copies = defaultdict(lambda: {"files": 0, "unique": 0})
owners = defaultdict(list)
for line in open(os.path.join(out, "census_manifest.tsv")):
    h, sz, p = line.rstrip("\n").split("\t", 2)
    owners[h].append(p)
for h, paths in owners.items():
    for p in paths:
        top = None
        for c in copies:
            if p.startswith(c + "/") or p == c:
                top = c; break
        if top: copies[top]["files"] += 1
    if len(paths) == 1 and top:
        copies[top]["unique"] += 1
gm = open(os.path.join(out, "census_grade.md"), "w")
gm.write(f"# Copy grade report\n\n")
gm.write("| copy | files | unique-to-this-copy | overlap % | verdict |\n|---|---|---|---|---|\n")
for c, s in copies.items():
    if s["files"] == 0: continue
    ov = 100 * (s["files"] - s["unique"]) // s["files"]
    verdict = ("KEEP (has unique content)" if s["unique"] > 50
               else "REVIEW (mostly duplicate)" if ov >= 90
               else "MERGE CANDIDATE")
    gm.write(f"| {c} | {s['files']} | {s['unique']} | {ov}% | {verdict} |\n")
gm.write("\nGrades are advisory. NO deletion/merge performed by this script.\n")
PYEOF
echo "      Grades written."

# ------------------------------------------------------------------ 6. Receipt
echo "[6/6] Sealing receipt..."
MAN_SHA="$(sha256sum "${OUT}/census_manifest.tsv" | cut -d' ' -f1)"
cat > "${OUT}/CENSUS_RECEIPT.md" <<EOF
# Fleet Census Receipt — ${TS}
- **Host:** ${HOST} (${OSTYPE:-unknown})
- **Root searched:** ${ROOT}   **Pattern:** ${NAMEPAT}
- **Copies found:** ${FOUND} git + $(grep -c '^NOGIT_DIR=' "${OUT}/census_repos.txt" || echo 0) non-git
- **Files hashed:** $(wc -l < "${OUT}/census_manifest.tsv")
- **Duplicate groups:** $(grep -c . "${OUT}/census_duplicates.tsv" || echo 0)
- **Unique files (exist in exactly one copy):** $(grep -c . "${OUT}/census_unique_by_copy.tsv" || echo 0)
- **Manifest sha256 (binds this census; Newton-chain-ready):** ${MAN_SHA}
- **Action taken:** NONE — read-only census. Merge/dedup decisions await human review.
EOF

echo ""
echo "=== CENSUS COMPLETE (read-only) ==="
echo "Review, in order:"
echo "  ${OUT}/census_repos.txt         — every copy found + its remotes"
echo "  ${OUT}/census_divergence.txt    — who is ahead/behind whom"
echo "  ${OUT}/census_grade.md          — KEEP / REVIEW / MERGE verdicts"
echo "  ${OUT}/census_duplicates.tsv    — full sha256 duplicate map (dedup ledger)"
echo "  ${OUT}/census_unique_by_copy.tsv— files that exist NOWHERE else (rescue list)"
echo "  ${OUT}/CENSUS_RECEIPT.md        — sealed summary, manifest-bound"
echo "Next: run on BOTH nodes, compare the two receipt manifests, THEN approve merges."

