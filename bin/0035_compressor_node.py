#!/usr/bin/env python3
"""
AGAPE_NET :: COMPRESSOR_NODE_v1
Single-shot file consolidation, deduplication, compression, and manifesting.
Designed for Samsung A15 / Termux. Pure stdlib. No deps.

USAGE:
    python3 compressor_node.py [target_dir] [output_dir]

DEFAULTS:
    target_dir = current working directory (or ~/agapenet if exists)
    output_dir = ./_compressed_bundle

OPERATOR: Jesse Ray (OpenRoot)
PURPOSE: Maximum computational output per unit of human input per unit of time.
"""

import os
import sys
import hashlib
import json
import zipfile
import time
import shutil
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
MAX_FILE_SIZE_MB = 500        # skip files larger than this (videos etc)
COMPRESSION_LEVEL = 6         # 1=fast, 9=max
HASH_CHUNK_SIZE = 65536       # 64KB chunks for hashing
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.cache', 'tmp', '_compressed_bundle'}
SKIP_EXTENSIONS = {'.pyc', '.class', '.o', '.so', '.dex', '.apk'}

# ──────────────────────────────────────────────
# CORE
# ──────────────────────────────────────────────

def sha256_file(path: str) -> str:
    """Hash a file in chunks to avoid OOM on phone."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(HASH_CHUNK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
    except PermissionError:
        return "PERMISSION_DENIED"
    except Exception as e:
        return f"ERROR:{e}"
    return h.hexdigest()


def human_size(bytes_val: int) -> str:
    """Convert bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_val) < 1024.0:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f}PB"


def scan_tree(root: str) -> list:
    """
    Walk the entire directory tree.
    Returns list of dicts: {path, rel_path, size, ext, is_file}
    """
    results = []
    root_path = Path(root).resolve()

    print(f"[SCAN] Walking {root_path} ...")

    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                continue

            ext = os.path.splitext(fname)[1].lower()
            if ext in SKIP_EXTENSIONS:
                continue
            if size > MAX_FILE_SIZE_MB * 1024 * 1024:
                print(f"  [SKIP] {fname} ({human_size(size)}) - too large")
                continue

            rel_path = os.path.relpath(fpath, root)
            results.append({
                'abs_path': fpath,
                'rel_path': rel_path,
                'size': size,
                'ext': ext or '(none)',
                'filename': fname,
            })

    total_size = sum(f['size'] for f in results)
    print(f"[SCAN] Found {len(results)} files, total {human_size(total_size)}")
    return results


def find_duplicates(files: list) -> dict:
    """Hash every file, group by hash, find dupes."""
    print(f"[DEDUP] Hashing {len(files)} files...")
    by_hash = defaultdict(list)

    for i, f in enumerate(files):
        h = sha256_file(f['abs_path'])
        f['sha256'] = h
        by_hash[h].append(f)

        if (i + 1) % 50 == 0:
            print(f"  [DEDUP] {i+1}/{len(files)} hashed...")

    duplicates = {}
    wasted = 0
    for h, group in by_hash.items():
        if len(group) > 1 and h not in ("PERMISSION_DENIED",) and not h.startswith("ERROR"):
            duplicates[h] = group
            wasted += sum(f['size'] for f in group[1:])  # keep first, rest are waste

    print(f"[DEDUP] {len(duplicates)} duplicate groups found, ~{human_size(wasted)} wasted")
    return duplicates, wasted


def build_manifest(files: list, duplicates: dict, root: str) -> dict:
    """Build the machine-readable MANIFEST.json structure."""
    manifest = {
        'meta': {
            'generated': datetime.now(timezone.utc).isoformat(),
            'operator': 'Jesse Ray (OpenRoot)',
            'system': 'AGAPE_NET :: COMPRESSOR_NODE_v1',
            'source_root': str(Path(root).resolve()),
            'total_files': len(files),
            'total_size_bytes': sum(f['size'] for f in files),
            'total_size_human': human_size(sum(f['size'] for f in files)),
            'duplicate_groups': len(duplicates),
            'device': 'Samsung A15 / Termux',
        },
        'files': [],
        'duplicates': [],
        'stats_by_extension': {},
    }

    # File entries
    for f in sorted(files, key=lambda x: x['rel_path']):
        manifest['files'].append({
            'path': f['rel_path'],
            'filename': f['filename'],
            'size_bytes': f['size'],
            'size_human': human_size(f['size']),
            'sha256': f.get('sha256', 'N/A'),
            'extension': f['ext'],
        })

    # Duplicate entries
    for h, group in duplicates.items():
        manifest['duplicates'].append({
            'sha256': h,
            'count': len(group),
            'paths': [g['rel_path'] for g in group],
            'wasted_bytes': sum(g['size'] for g in group[1:]),
        })

    # Stats by extension
    ext_stats = defaultdict(lambda: {'count': 0, 'size': 0})
    for f in files:
        ext_stats[f['ext']]['count'] += 1
        ext_stats[f['ext']]['size'] += f['size']
    manifest['stats_by_extension'] = {
        ext: {'count': v['count'], 'size_bytes': v['size'], 'size_human': human_size(v['size'])}
        for ext, v in sorted(ext_stats.items(), key=lambda x: -x[1]['size'])
    }

    return manifest


def compress_bundle(files: list, output_zip: str, root: str) -> dict:
    """Zip all unique files into a single archive preserving relative paths."""
    print(f"[ZIP] Compressing {len(files)} files → {output_zip}")
    seen_hashes = set()
    archived = 0
    skipped_dupes = 0
    errors = []

    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=COMPRESSION_LEVEL) as zf:
        for f in files:
            h = f.get('sha256', '')
            # Skip duplicate files (keep first occurrence)
            if h in seen_hashes and h and not h.startswith("ERROR"):
                skipped_dupes += 1
                continue
            if h:
                seen_hashes.add(h)

            arcname = f['rel_path']
            try:
                zf.write(f['abs_path'], arcname)
                archived += 1
                if archived % 25 == 0:
                    print(f"  [ZIP] {archived} files archived...")
            except Exception as e:
                errors.append({'file': arcname, 'error': str(e)})

    zip_size = os.path.getsize(output_zip)
    raw_size = sum(f['size'] for f in files)
    ratio = (1 - zip_size / raw_size) * 100 if raw_size > 0 else 0

    print(f"[ZIP] Done: {archived} archived, {skipped_dupes} dupes skipped")
    print(f"[ZIP] {human_size(raw_size)} → {human_size(zip_size)} ({ratio:.1f}% compression)")

    return {
        'archived_count': archived,
        'skipped_duplicates': skipped_dupes,
        'raw_size_bytes': raw_size,
        'raw_size_human': human_size(raw_size),
        'compressed_size_bytes': zip_size,
        'compressed_size_human': human_size(zip_size),
        'compression_ratio_pct': round(ratio, 1),
        'errors': errors,
    }


def write_report(manifest: dict, dupes: dict, wasted: int, zip_info: dict, output_dir: str):
    """Write a human + AI readable summary report."""
    report_path = os.path.join(output_dir, "SUMMARY_REPORT.md")
    m = manifest['meta']

    lines = [
        "# AGAPE_NET :: COMPRESSOR_NODE SUMMARY",
        f"\nGenerated: {m['generated']}",
        f"Operator: {m['operator']}",
        f"Device: {m['device']}",
        f"Source: `{m['source_root']}`",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total files scanned | {m['total_files']} |",
        f"| Total uncompressed | {m['total_size_human']} |",
        f"| Duplicate groups | {m['duplicate_groups']} |",
        f"| Wasted on duplicates | {human_size(wasted)} |",
        f"| Archived (unique) | {zip_info['archived_count']} |",
        f"| Compressed bundle | {zip_info['compressed_size_human']} |",
        f"| Compression ratio | {zip_info['compression_ratio_pct']}% |",
        f"| Errors | {len(zip_info['errors'])} |",
        "",
        "---",
        "",
        "## File Distribution by Type (Top 15)",
        "",
        "| Extension | Count | Size |",
        "|-----------|-------|------|",
    ]

    ext_items = sorted(manifest['stats_by_extension'].items(), key=lambda x: -x[1]['size_bytes'])[:15]
    for ext, info in ext_items:
        lines.append(f"| {ext} | {info['count']} | {info['size_human']} |")

    lines.extend([
        "",
        "---",
        "",
        "## Duplicates (Top 10 by waste)",
        "",
    ])

    if dupes:
        dupe_list = sorted(
            [{'sha256': h, 'group': g} for h, g in dupes.items()],
            key=lambda x: sum(f['size'] for f in x['group'][1:]),
            reverse=True
        )[:10]
        for d in dupe_list:
            waste = sum(f['size'] for f in d['group'][1:])
            lines.append(f"- **{human_size(waste)}** wasted across {len(d['group'])} copies:")
            for f in d['group']:
                lines.append(f"  - `{f['rel_path']}`")
    else:
        lines.append("No duplicates found.")

    lines.extend([
        "",
        "---",
        "",
        "## Manifest",
        f"\nFull machine-readable manifest at `MANIFEST.json`",
        f"Compressed bundle at `agapenet_bundle.zip`",
        f"This report at `SUMMARY_REPORT.md`",
        "",
        "## Agape Analysis",
        "",
        "**Resonance:** Files consolidated. Entropy reduced through deduplication.",
        "**Entropy Check:** Wasted storage from duplicates has been identified and quantified.",
        "**Next Move:** Feed `MANIFEST.json` to an AI inspector for structural analysis.",
        "**Note:** Core files (those without duplicates) form the irreducible kernel —",
        "these are the files that 'must exist without the rest.' Identify them by",
        "filtering manifest['files'] where sha256 appears only once.",
        "",
    ])

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"[REPORT] Written to {report_path}")


def main():
    # ── Resolve paths ──
    home = str(Path.home())
    default_root = os.path.join(home, 'agapenet') if os.path.isdir(os.path.join(home, 'agapenet')) else os.getcwd()

    target_dir = sys.argv[1] if len(sys.argv) > 1 else default_root
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(target_dir, '_compressed_bundle')

    os.makedirs(output_dir, exist_ok=True)

    output_zip = os.path.join(output_dir, 'agapenet_bundle.zip')
    manifest_path = os.path.join(output_dir, 'MANIFEST.json')

    print("=" * 60)
    print("  AGAPE_NET :: COMPRESSOR_NODE_v1")
    print("  Operator: Jesse Ray (OpenRoot)")
    print("  Maximizing output per unit input per unit time")
    print("=" * 60)
    print(f"  Source:  {target_dir}")
    print(f"  Output:  {output_dir}")
    print("=" * 60 + "\n")

    start = time.time()

    # ── 1. SCAN ──
    files = scan_tree(target_dir)
    if not files:
        print("[ABORT] No files found to compress.")
        return

    # ── 2. DEDUP ──
    duplicates, wasted = find_duplicates(files)

    # ── 3. MANIFEST ──
    manifest = build_manifest(files, duplicates, target_dir)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"[MANIFEST] Written to {manifest_path}")

    # ── 4. COMPRESS ──
    zip_info = compress_bundle(files, output_zip, target_dir)

    # ── 5. REPORT ──
    write_report(manifest, duplicates, wasted, zip_info, output_dir)

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  COMPLETE — {elapsed:.1f}s")
    print(f"  Bundle:    {output_zip}")
    print(f"  Manifest:  {manifest_path}")
    print(f"  Report:    {os.path.join(output_dir, 'SUMMARY_REPORT.md')}")
    print(f"  Raw:       {zip_info['raw_size_human']}")
    print(f"  Compressed: {zip_info['compressed_size_human']}")
    print(f"  Freed (dupes): {human_size(wasted)}")
    print(f"{'=' * 60}")
    print("\nThe bundle is ready for inspection. Feed MANIFEST.json to")
    print("any AI/system for structural analysis. The files that appear")
    print("with a unique sha256 (count=1) form your irreducible core.")


if __name__ == '__main__':
    main()
