#!/usr/bin/env python3
import pathlib

eng = pathlib.Path("computational_flow/agape_engine.py")
content = eng.read_text()
lines = content.split("\n")

# Find the line with "synthesis = f5_synthesize"
target_idx = None
for i, line in enumerate(lines):
    if 'synthesis = f5_synthesize' in line:
        target_idx = i
        break

if target_idx is None:
    print("ERROR: Could not find synthesis line")
    exit(1)

# Build the injection block (plain strings only, NO f-strings)
indent = "    "
injection = [
    "",
    indent + "# --- FS HOOK: Check for structural queries ---",
    indent + "QUERY_LOWER = query.lower()",
    indent + "FS_KEYWORDS = ['repo', 'structure', 'files', 'filesystem', 'directory', 'organize', 'redundant', 'clean']",
    indent + "_fs_override_active = False",
    indent + "if any(kw in QUERY_LOWER for kw in FS_KEYWORDS):",
    indent + "    try:",
    indent + "        with open('/sdcard/openroot/agape_kb/repo_snapshot.json') as f:",
    indent + "            snap = json.load(f)",
    indent + "        top_dirs = sorted(snap.get('by_directory', {}).items(), key=lambda x: -x[1])[:5]",
    indent + "        top_exts = sorted(snap.get('by_extension', {}).items(), key=lambda x: -x[1])[:5]",
    indent + "        dir_parts = []",
    indent + "        for d, c in top_dirs:",
    indent + "            dir_parts.append(str(d) + '(' + str(c) + ')')",
    indent + "        ext_parts = []",
    indent + "        for e, c in top_exts:",
    indent + "            ext_parts.append(str(e) + '(' + str(c) + ')')",
    indent + "        dir_str = ', '.join(dir_parts)",
    indent + "        ext_str = ', '.join(ext_parts)",
    indent + "        fs_msg = '[FS HOOK] ' + str(snap['file_count']) + ' files, ' + format(snap['total_bytes'], ',') + ' bytes. Top dirs: ' + dir_str + '. Top exts: ' + ext_str + '. Refresh: python3 computational_flow/fs_hook.py snap'",
    indent + "        # Override synthesis and verified immediately",
    indent + "        synthesis = {'answer': fs_msg, 'sources': ['filesystem'], 'confidence': 0.95, 'eta': float('inf')}",
    indent + "        verified = {'answer': fs_msg, 'sources': ['filesystem'], 'verification': {'verified': True}, 'eta': float('inf')}",
    indent + "        _fs_override_active = True",
    indent + "    except Exception as e:",
    indent + "        # If snapshot fails, fall through to normal synthesis",
    indent + "        _fs_override_active = False",
    indent + "# --- END FS HOOK ---",
    ""
]

# Insert the block right before the synthesis line
for i, line_content in enumerate(injection):
    lines.insert(target_idx + i, line_content)

# Ensure json import exists
has_json = any(line.strip() == "import json" for line in lines)
if not has_json:
    for i, line in enumerate(lines):
        if line.strip().startswith("import"):
            lines.insert(i + 1, "import json")
            break

# Write back
eng.write_text("\n".join(lines))
print("OK: fs_hook injected successfully at line " + str(target_idx))
