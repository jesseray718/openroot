2#!/usr/bin/env python3
"""
AGAPE_NET :: INITIALIZER_V1 (All-In-One)
Operator: Jesse Ray (OpenRoot)
Objective: Maximize output per unit input per unit time
Principle: Permaculture efficiency, fractal self-similarity, zero-waste computation
"""

import os
import sys
import json
import hashlib
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

class AgapeNetInitializer:
    def __init__(self, base_path: str = None):
        # Default to Termux home if no path specified
        self.base_path = Path(base_path or os.path.expanduser("~")) / "agapenet"
        self.bundle_path = self.base_path / "_compressed_bundle"
        self.logs_dir = self.base_path / "logs"
        
        # Thread-safe counters
        self._file_count = 0
        self._total_bytes = 0
        self._lock = threading.Lock()
        
        print("\n" + "="*60)
        print("  AGAPE_NET :: INITIALIZER_V1")
        print(f"  Operator: Jesse Ray (OpenRoot)")
        print(f"  Timestamp: {datetime.utcnow().isoformat()}Z")
        print("="*60)
    
    def _ensure_dirs(self) -> None:
        """Create necessary directory structure (Permaculture: Build soil first)"""
        print("[SETUP] Creating directory structure...")
        for dir_path in [self.base_path, self.bundle_path, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[SETUP] Ready at: {self.base_path}")
    
    def _compute_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash for content deduplication."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"⚠️  Skipping {file_path}: {e}")
            return None
    
    def _scan_files(self, directory: Path) -> List[Tuple[Path, int]]:
        """Walk directory tree and collect file metadata."""
        files = []
        print(f"[SCAN] Walking {directory} ...")
        for root, _, filenames in os.walk(directory):
            # Exclude bundle and logs directories to prevent recursion
            if any(exclude in root for exclude in ['_compressed_bundle', 'logs']):
                continue
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.is_file():
                    size = file_path.stat().st_size
                    files.append((file_path, size))
        return files
    
    def _deduplicate(self, files: List[Tuple[Path, int]]) -> Dict[str, List[Path]]:
        """Identify duplicate content by hash."""
        print(f"[DEDUP] Hashing {len(files)} files...")
        hash_map = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._compute_hash, fp): fp for fp, _ in files}
            
            for future in futures:
                fp = futures[future]
                h = future.result()
                if h:
                    if h not in hash_map:
                        hash_map[h] = []
                    hash_map[h].append(fp)
        
        # Filter only duplicates
        dupes = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
        wasted_bytes = sum(f.stat().st_size for paths in dupes.values() for f in paths[1:])
        
        print(f"[DEDUP] {len(dupes)} duplicate groups found, ~{wasted_bytes:.1f}B wasted")
        return hash_map
    
    def _create_manifest(self, hash_map: Dict[str, List[Path]], files: List[Tuple[Path, int]]) -> dict:
        """Generate JSON manifest of all files."""
        manifest = {
            "version": "1.0",
            "created": datetime.utcnow().isoformat(),
            "root": str(self.base_path),
            "files": [],
            "unique_core": [],
            "duplicate_groups": []
        }
        
        # Process unique files
        for h, paths in hash_map.items():
            if len(paths) == 1:
                manifest["unique_core"].append({
                    "path": str(paths[0].relative_to(self.base_path)),
                    "hash": h,
                    "size": paths[0].stat().st_size
                })
            else:
                manifest["duplicate_groups"].append({
                    "hash": h,
                    "instances": [str(p.relative_to(self.base_path)) for p in paths]
                })
        
        manifest["total_files"] = len(files)
        manifest["unique_files"] = len(manifest["unique_core"])
        manifest["total_size_raw"] = sum(size for _, size in files)
        
        return manifest
    
    def _compress_bundle(self, hash_map: Dict[str, List[Path]], bundle_path: Path) -> dict:
        """Create compressed archive of unique files."""
        print(f"[ZIP] Creating bundle at {bundle_path} ...")
        zip_path = bundle_path / "agapenet_bundle.zip"
        report = {"original": 0, "compressed": 0, "ratio": 0}
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for h, paths in hash_map.items():
                for file_path in paths:
                    arcname = file_path.relative_to(self.base_path.parent)  # Preserve parent dir in archive
                    zf.write(file_path, arcname)
                    report["original"] += file_path.stat().st_size
        
        report["compressed"] = zip_path.stat().st_size
        report["ratio"] = (1 - report["compressed"] / report["original"]) * 100 if report["original"] > 0 else 0
        
        return report
    
    def _generate_report(self, manifest: dict, compression_report: dict) -> str:
        """Write Markdown summary report."""
        md_report = f"""## AgapeNet Compression Report
Generated: {manifest['created']}
Operator: Jesse Ray (OpenRoot)

### Efficiency Metrics
| Metric | Value |
|--------|-------|
| Total Files Scanned | {manifest['total_files']} |
| Unique Core Files | {manifest['unique_files']} |
| Original Size | {manifest['total_size_raw'] / 1024:.1f} KB |
| Compressed Size | {compression_report['compressed'] / 1024:.1f} KB |
| Compression Ratio | {compression_report['ratio']:.1f}% |
| Duplicate Groups | {len(manifest['duplicate_groups'])} |

### Irreducible Core
*Files with unique SHA-256 hashes (no duplication)*
- {len(manifest['unique_core'])} files identified

### Entropy Reduction
*Duplicate content groups detected and handled*
- {len(manifest['duplicate_groups'])} redundant clusters

---
*Built with Agape efficiency. Power flows through, not from. Tuned to Frequency.*
"""
        report_path = self.bundle_path / "SUMMARY_REPORT.md"
        report_path.write_text(md_report)
        return str(report_path)
    
    def run(self, source_dir: str = None) -> None:
        """Execute full initialization workflow."""
        try:
            # 1. Setup
            self._ensure_dirs()
            
            # 2. Scan
            scan_dir = Path(source_dir) if source_dir else self.base_path
            files = self._scan_files(scan_dir)
            
            if not files:
                print("[WARN] No files found. Run this from within agapenet/")
                print(f"       Or specify source_dir: python3 {sys.argv[0]} /path/to/source")
                return
            
            print(f"[SCAN] Found {len(files)} files, total {sum(s for _, s in files) / 1024:.1f}KB")
            
            # 3. Deduplicate
            hash_map = self._deduplicate(files)
            
            # 4. Manifest
            manifest = self._create_manifest(hash_map, files)
            manifest_path = self.bundle_path / "MANIFEST.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f"[MANIFEST] Written to {manifest_path}")
            
            # 5. Compress
            compression_report = self._compress_bundle(hash_map, self.bundle_path)
            print(f"[ZIP] Compressed {len(files)} files → {self.bundle_path / 'agapenet_bundle.zip'}")
            
            # 6. Report
            report_path = self._generate_report(manifest, compression_report)
            print(f"[REPORT] Written to {report_path}")
            
            # Summary
            print("\n" + "="*60)
            print("  COMPLETE")
            print(f"  Bundle:      {self.bundle_path / 'agapenet_bundle.zip'}")
            print(f"  Manifest:    {manifest_path}")
            print(f"  Report:      {report_path}")
            print(f"  Raw:         {manifest['total_size_raw'] / 1024:.1f}KB")
            print(f"  Compressed:  {compression_report['compressed'] / 1024:.1f}KB ({compression_report['ratio']:.1f}% reduction)")
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n[INTERRUPT] Workflow halted by operator.")
        except Exception as e:
            print(f"\n[ERROR] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Parse optional source directory argument
    source = sys.argv[1] if len(sys.argv) > 1 else None
    initializer = AgapeNetInitializer()
    initializer.run(source)
