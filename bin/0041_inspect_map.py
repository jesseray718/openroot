#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("file_map.sqlite")

# 1. Locate Git / Code Project Workspaces
print("=== DETECTED REPOSITORIES / WORKSPACES ===")
repos = conn.execute("""
    SELECT DISTINCT directory 
    FROM file_map 
    WHERE filename IN ('.git', 'pyproject.toml', 'package.json', 'Cargo.toml', 'requirements.txt')
    ORDER BY directory ASC
""").fetchall()
for r in repos:
    print(f"  [repo] {r[0]}")

# 2. Top 10 Largest Files
print("\n=== TOP 10 LARGEST FILES ===")
largest = conn.execute("""
    SELECT full_path, ROUND(size_bytes / (1024.0 * 1024.0), 2) as MB
    FROM file_map
    ORDER BY size_bytes DESC
    LIMIT 10
""").fetchall()
for path, mb in largest:
    print(f"  {mb:>8.2f} MB  |  {path}")

# 3. Duplicate Files (>1KB, excluding system noise)
print("\n=== TOP DUPLICATE FILES ===")
duplicates = conn.execute("""
    SELECT filename, size_bytes, COUNT(*) as count, GROUP_CONCAT(full_path, '\n         ') as paths
    FROM file_map
    WHERE filename NOT IN ('.DS_Store', '__init__.py', '.gitignore', 'README.md', 'LICENSE')
      AND size_bytes > 1024
    GROUP BY filename, size_bytes
    HAVING count > 1
    ORDER BY size_bytes * count DESC
    LIMIT 5
""").fetchall()

for name, size, count, paths in duplicates:
    mb = round((size * count) / (1024.0 * 1024.0), 2)
    print(f"\n  • {name} ({count} copies, ~{mb} MB total wasted):")
    print(f"         {paths}")

conn.close()
