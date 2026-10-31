#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# build_core_view.py — consolidate priority docs into single self-contained HTML view
# Jesse Ray / OpenRoot v1.0 | regenerate anytime; idempotent output path
import os, re, html, time

SRC_DIRS = [
    ("/home/jesse/openroot/HANDBOOK",        "Handbook"),
    ("/home/jesse/src/openroot",             "Main Repo"),
    ("/home/jesse/openroot/src/openroot-thesis/code/python", "Thesis Code"),
]
PRIORITY  = ["README.md", "HANDBOOK.md", "USER_GUIDE.md", "OPENROOT-THESIS-v3.md",
             "SUPPORT.md", "GOALS.md", "CONTRIBUTING.md"]
OUT_HTML  = "/home/jesse/openroot/data/core_view/index.html"
MAX_FILES = 60            # hard cap — view stays fast on phone
MAX_CHARS = 40_000        # per doc, truncated with marker

def md_to_html(text):
    text = html.escape(text)
    text = re.sub(r"^###### (.*)$", r"<h6>\1</h6>", text, flags=re.M)
    text = re.sub(r"^##### (.*)$",  r"<h5>\1</h5>", text, flags=re.M)
    text = re.sub(r"^#### (.*)$",  r"<h4>\1</h4>", text, flags=re.M)
    text = re.sub(r"^### (.*)$",   r"<h3>\1</h3>", text, flags=re.M)
    text = re.sub(r"^## (.*)$",    r"<h2>\1</h2>", text, flags=re.M)
    text = re.sub(r"^# (.*)$",     r"<h1>\1</h1>", text, flags=re.M)
    text = re.sub(r"```(\w*)\n(.*?)```", lambda m:
        "<pre><code>" + m.group(2) + "</code></pre>", text, flags=re.S)
    text = re.sub(r"^[-*] (.*)$",  r"<li>\1</li>", text, flags=re.M)
    text = re.sub(r"^&gt; (.*)$", r"<blockquote>\1</blockquote>", text, flags=re.M)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*",     r"<em>\1</em>", text)
    text = re.sub(r"(.+\n)+", lambda m:
        m.group(0).replace("\n", "<br>") if "<" not in m.group(0) else m.group(0), text)
    return text.replace("\n\n", "<br><br>")

print("[canary] paste intact | core view builder")
os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)

collected = []
seen = set()
for base, label in SRC_DIRS:
    if not os.path.isdir(base):
        continue
    for fname in PRIORITY:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "build", "__pycache__")]
            if fname in files:
                p = os.path.join(root, fname)
                if p in seen: continue
                seen.add(p)
                collected.append((p, label))

# fill remainder with newest .md files up to cap
for base, label in SRC_DIRS:
    if len(collected) >= MAX_FILES: break
    if not os.path.isdir(base): continue
    mds = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "build", "__pycache__")]
        for fn in files:
            if fn.endswith(".md"):
                p = os.path.join(root, fn)
                if p not in seen:
                    mds.append((os.path.getmtime(p), p))
    mds.sort(reverse=True)
    for _, p in mds[:MAX_FILES - len(collected)]:
        collected.append((p, label))
        seen.add(p)

parts, toc = [], []
for i, (path, label) in enumerate(collected):
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        continue
    trunc = ""
    if len(raw) > MAX_CHARS:
        raw, trunc = raw[:MAX_CHARS], "\n\n*(truncated — open source file for full doc)*"
    anchor = "doc%d" % i
    toc.append(f'<li><a href="#{anchor}">{html.escape(os.path.relpath(path, "/home/jesse"))}</a></li>')
    parts.append(f'<section id="{anchor}"><div class="tag">{label} · '
                 f'{time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(path)))}'
                 f'</div>{md_to_html(raw + trunc)}</section>')

page = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenRoot Core View</title><style>
body{font-family:-apple-system,sans-serif;background:#111;color:#ddd;max-width:850px;margin:auto;padding:16px}
h1,h2,h3{color:#a98aff;border-bottom:1px solid #333;padding-bottom:4px}
section{background:#1b1b1b;border-radius:10px;padding:14px;margin:14px 0}
.tag{color:#888;font-size:small;margin-bottom:8px}
nav{background:#161616;border-radius:10px;padding:12px}
nav li{margin:4px 0}
pre{background:#000;border-radius:6px;padding:10px;overflow-x:auto}
a{color:#a98aff}
</style></head><body>
<h1>OpenRoot — Core View</h1>
<p style="color:#888">__DOCS__ docs consolidated · generated __WHEN__ · OptiPlex node</p>
<nav><b>Contents</b><ul>__TOC__</ul></nav>
__BODY__
</body></html>"""
page = (page.replace("__DOCS__", str(len(parts)))
            .replace("__WHEN__", time.strftime("%Y-%m-%d %H:%M"))
            .replace("__TOC__", "".join(toc))
            .replace("__BODY__", "\n".join(parts)))

with open(OUT_HTML, "w") as f:
    f.write(page)
print(f"[banked] {len(parts)} docs -> {OUT_HTML} ({len(page)//1024}KB)")
