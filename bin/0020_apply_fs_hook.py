import pathlib

eng = pathlib.Path("computational_flow/agape_engine.py")
lines = eng.read_text().split("\n")

# Find insertion point
idx = None
for i, line in enumerate(lines):
    if "# 6. f5: Synthesize" in line:
        idx = i
        break

if idx is None:
    print("ERROR: target '# 6. f5: Synthesize' not found")
    raise SystemExit(1)

# Build injection as plain strings
block = [
    "    # --- FS HOOK INJECTION START ---",
    "    QUERY_LOWER = query.lower()",
    "    FS_KEYWORDS = ['repo', 'structure', 'files', 'filesystem', 'directory', 'organize', 'redundant', 'clean']",
    "    if any(kw in QUERY_LOWER for kw in FS_KEYWORDS):",
    "        try:",
    "            with open('/sdcard/openroot/agape_kb/repo_snapshot.json') as f:",
    "                snap = json.load(f)",
    "            top_dirs = sorted(snap.get('by_directory', {}).items(), key=lambda x: -x[1])[:5]",
    "            top_exts = sorted(snap.get('by_extension', {}).items(), key=lambda x: -x[1])[:5]",
    "            dir_parts = []",
    "            for d, c in top_dirs:",
    "                dir_parts.append(str(d) + '(' + str(c) + ')')",
    "            ext_parts = []",
    "            for e, c in top_exts:",
    "                ext_parts.append(str(e) + '(' + str(c) + ')')",
    "            dir_str = ', '.join(dir_parts)",
    "            ext_str = ', '.join(ext_parts)",
    "            fs_msg = '[FS HOOK] ' + str(snap['file_count']) + ' files, ' + format(snap['total_bytes'], ',') + ' bytes. Top dirs: ' + dir_str + '. Top exts: ' + ext_str + '. Refresh: python3 computational_flow/fs_hook.py snap'",
    "            synthesis = {'answer': fs_msg, 'sources': ['filesystem'], 'confidence': 0.95, 'eta': float('inf')}",
    "            verified = {'answer': fs_msg, 'sources': ['filesystem'], 'verification': {'verified': True}, 'eta': float('inf')}",
    "            _fs_override_active = True",
    "        except Exception as e:",
    "            _fs_override_active = False",
    "    else:",
    "        _fs_override_active = False",
    "    # --- FS HOOK INJECTION END ---",
    ""
]

# Insert
for i, line_content in enumerate(block):
    lines.insert(idx + i, line_content)

# Ensure json import
has_json = any(line.strip() == "import json" for line in lines)
if not has_json:
    for i, line in enumerate(lines):
        if line.strip().startswith("import"):
            lines.insert(i + 1, "import json")
            break

eng.write_text("\n".join(lines))
print("OK: fs_hook patch applied successfully")
