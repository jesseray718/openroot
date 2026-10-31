#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
Markor Document Fetcher & Compiler
Fetches new/updated documents from past 24 hours and compiles into single output
Compatible with: OptiPlex 3060 (Ubuntu 24.04) + Termux/Samsung A15

Usage: python3 markor_compiler.py [--days 1] [--output /path/to/output.md] [--source /path/to/markor]
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

# Configuration
DEFAULT_DAYS = 1
DEFAULT_OUTPUT = "/home/jesse/openroot/context_bridge/markor_daily_compile.md"
DEFAULT_MARKOR_PATHS = [
    "/home/jesse/markor_notes",              # Local sync path
    "/data/data/net.gs.markor/files",        # Android internal (requires root/Termux)
    "/storage/emulated/0/Markor",            # Android SD card
]

def find_markor_documents(source_dirs: List[str]) -> List[Tuple[Path, float]]:
    """Find all .md files in Markor directories with modification times."""
    documents = []
    
    for base_dir in source_dirs:
        if not os.path.exists(base_dir):
            continue
            
        try:
            for root, dirs, files in os.walk(base_dir):
                for filename in files:
                    if filename.endswith('.md'):
                        filepath = Path(root) / filename
                        mtime = os.path.getmtime(filepath)
                        documents.append((filepath, mtime))
        except PermissionError:
            print(f"[SKIPPED] Permission denied: {base_dir}", file=sys.stderr)
            continue
    
    return documents

def filter_by_timeframe(documents: List[Tuple[Path, float]], days: int) -> List[Tuple[Path, float]]:
    """Filter documents modified within specified timeframe."""
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    return [(path, mtime) for path, mtime in documents if mtime >= cutoff]

def read_document_content(filepath: Path) -> str:
    """Read markdown content with UTF-8 encoding."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Failed reading {filepath}: {e}", file=sys.stderr)
        return ""

def extract_metadata(content: str, filepath: Path) -> dict:
    """Extract YAML front-matter or infer metadata."""
    metadata = {
        'filename': filepath.name,
        'modified': None,
        'word_count': 0,
        'line_count': 0
    }
    
    # Extract word/line count
    lines = content.split('\n')
    metadata['line_count'] = len(lines)
    metadata['word_count'] = len(content.split())
    
    # Try to extract modified date from filename pattern (YYYY-MM-DD_*)
    if '_' in filepath.stem:
        parts = filepath.stem.split('_')
        if len(parts[0]) == 10 and parts[0][4] == '-':
            try:
                metadata['modified'] = datetime.strptime(parts[0], '%Y-%m-%d').isoformat()
            except ValueError:
                pass
    
    # Try YAML front-matter
    if content.startswith('---'):
        end_marker = content.find('---', 3)
        if end_marker > 0:
            yaml_block = content[:end_marker + 3]
            metadata['has_frontmatter'] = True
    
    return metadata

def compile_documents(filtered_docs: List[Tuple[Path, float]]) -> str:
    """Compile documents into single markdown with headers and separators."""
    if not filtered_docs:
        return "# Markor Daily Compile\n\nNo documents found in the specified timeframe.\n"
    
    output_lines = [
        f"# Markor Daily Compilation",
        f"",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Documents compiled:** {len(filtered_docs)}",
        f"**Timeframe:** Past 24 hours",
        f"",
        f"---",
        f""
    ]
    
    for filepath, mtime in sorted(filtered_docs, key=lambda x: x[1]):
        content = read_document_content(filepath)
        metadata = extract_metadata(content, filepath)
        
        mod_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        output_lines.extend([
            f"",
            f"## 📄 {metadata['filename']}",
            f"",
            f"- **Modified:** {mod_date}",
            f"- **Lines:** {metadata['line_count']}",
            f"- **Words:** {metadata['word_count']}",
            f"",
            f"```\n{content}\n```",
            f"",
            f"{'─' * 80}",
            f""
        ])
    
    # Add summary section
    total_words = sum(extract_metadata(read_document_content(fp), fp)['word_count'] 
                      for fp, _ in filtered_docs)
    total_lines = sum(extract_metadata(read_document_content(fp), fp)['line_count'] 
                      for fp, _ in filtered_docs)
    
    output_lines.extend([
        f"",
        f"## 📊 Summary Statistics",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Documents | {len(filtered_docs)} |",
        f"| Total Lines | {total_lines} |",
        f"| Total Words | {total_words} |",
        f"",
        f"---",
        f"",
        f"*End of compilation*"
    ])
    
    return '\n'.join(output_lines)

def save_compiled_doc(content: str, output_path: str) -> bool:
    """Save compiled document to output path."""
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[DONE] Saved to: {output_file.absolute()}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[ERROR] Failed saving: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Markor Document Compiler')
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS,
                        help=f'Days back to search (default: {DEFAULT_DAYS})')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT,
                        help=f'Output file path (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--source', type=str, action='append', default=[],
                        help='Source directory paths (can specify multiple)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without saving')
    
    args = parser.parse_args()
    
    # Use provided sources or defaults
    source_dirs = args.source if args.source else DEFAULT_MARKOR_PATHS
    
    print(f"[INFO] Searching {args.days} days back...", file=sys.stderr)
    print(f"[INFO] Source directories: {len(source_dirs)}", file=sys.stderr)
    
    # Step 1: Find all documents
    all_docs = find_markor_documents(source_dirs)
    print(f"[INFO] Found {len(all_docs)} total documents", file=sys.stderr)
    
    # Step 2: Filter by timeframe
    filtered = filter_by_timeframe(all_docs, args.days)
    print(f"[INFO] Modified in past {args.days} days: {len(filtered)}", file=sys.stderr)
    
    if not filtered:
        print("[WARN] No documents found in timeframe. Exiting.", file=sys.stderr)
        sys.exit(0)
    
    # Step 3: Compile
    compiled = compile_documents(filtered)
    doc_stats = {
        'documents_processed': len(filtered),
        'output_size_bytes': len(compiled.encode('utf-8')),
        'output_file': args.output,
        'timestamp': datetime.now().isoformat()
    }
    print(json.dumps(doc_stats), file=sys.stderr)
    
    # Step 4: Save or dry-run
    if args.dry_run:
        print(f"[DRY-RUN] Would save to: {args.output}", file=sys.stderr)
        print("\n=== PREVIEW ===")
        print(compiled[:2000] + "..." if len(compiled) > 2000 else compiled)
    else:
        if save_compiled_doc(compiled, args.output):
            print(f"[COMPLETE] Compilation successful", file=sys.stderr)
            sys.exit(0)
        else:
            print(f"[FAILED] Compilation failed", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
