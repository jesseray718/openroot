#!/usr/bin/env python3
"""Check local link destinations in README.md and top-level docs Markdown."""

import html
import hashlib
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFINITION = re.compile(r"^\s{0,3}\[[^]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXCLUSIONS = (
    {
        "path": "docs/README.draft.md",
        "reason": (
            "Pinned draft contains two known broken links, ./CODE_OF_CONDUCT.md "
            "and ./LICENSE; exclusion hides them but does not fix them."
        ),
        "sha256": "518b6643428d443338cdcfb65ee6be3715b8b57fdbf6331e8f8b2170634eb2ce",
    },
)


class HtmlLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src"):
            self.links.append(attrs["src"])
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])


def without_code(text):
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            lines.append("\n")
        elif match:
            fence = match.group(1)
            lines.append("\n")
        else:
            lines.append(line)
    text = "".join(lines)
    return re.sub(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)", "", text, flags=re.DOTALL)


def destination(text, start):
    i = start
    while i < len(text) and text[i] in " \t\n":
        i += 1
    if i < len(text) and text[i] == "<":
        end = text.find(">", i + 1)
        if end == -1:
            return None
        value = text[i + 1 : end]
        i = end + 1
    else:
        value = ""
        depth = 0
        while i < len(text):
            char = text[i]
            if char == "\\" and i + 1 < len(text):
                value += text[i + 1]
                i += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            value += char
            i += 1
        if depth:
            return None
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] in "\"'":
        quote = text[i]
        i += 1
        while i < len(text) and text[i] != quote:
            if text[i] == "\\":
                i += 1
            i += 1
        i += 1
        while i < len(text) and text[i].isspace():
            i += 1
    if i >= len(text) or text[i] != ")":
        return None
    return value, i


def markdown_links(text):
    links = []
    brackets = []
    i = 0
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "[":
            brackets.append(i)
        elif text[i] == "]" and brackets:
            brackets.pop()
            if i + 1 < len(text) and text[i + 1] == "(":
                parsed = destination(text, i + 2)
                if parsed:
                    value, i = parsed
                    links.append(value)
        i += 1
    links.extend(match.group(1).strip("<>") for match in DEFINITION.finditer(text))
    return links


def anchors(text, html_ids):
    seen = {}
    result = set(html_ids)
    for match in HEADING.finditer(text):
        heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", match.group(1))
        heading = re.sub(r"<[^>]*>", "", html.unescape(heading)).lower()
        slug = "".join(
            c for c in heading
            if c in "-_" or not unicodedata.category(c).startswith(("P", "S"))
        ).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def check_file(path, root=ROOT):
    text = without_code(path.read_text(encoding="utf-8"))
    parser = HtmlLinks()
    parser.feed(text)
    errors = []
    for link in markdown_links(text) + parser.links:
        parsed = urlsplit(html.unescape(link))
        if parsed.scheme or parsed.netloc:
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
        if not target.is_relative_to(root.resolve()) or not target.exists():
            errors.append(f"{path.relative_to(root)}: missing or out-of-repository target: {link}")
            continue
        if parsed.fragment and target.is_file() and target.suffix.lower() == ".md":
            target_text = without_code(target.read_text(encoding="utf-8"))
            target_html = HtmlLinks()
            target_html.feed(target_text)
            if unquote(parsed.fragment) not in anchors(target_text, target_html.ids):
                errors.append(f"{path.relative_to(root)}: missing anchor: {link}")
    return errors


def validate_exclusions(root=ROOT, exclusions=EXCLUSIONS):
    excluded_paths = set()
    errors = []
    root = root.resolve()
    for exclusion in exclusions:
        relative_path = Path(exclusion["path"])
        path = (root / relative_path).resolve()
        if not path.is_relative_to(root):
            errors.append(f"exclusion path escapes repository: {relative_path}")
            continue
        if not path.is_file():
            errors.append(f"excluded file is missing: {relative_path}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != exclusion["sha256"]:
            errors.append(
                f"excluded file SHA-256 changed: {relative_path} "
                f"(expected {exclusion['sha256']}, got {digest})"
            )
            continue
        excluded_paths.add(relative_path.as_posix())
    return excluded_paths, errors


def check_files(files, root=ROOT, exclusions=EXCLUSIONS):
    excluded_paths, errors = validate_exclusions(root, exclusions)
    if errors:
        return excluded_paths, errors
    errors = [
        error
        for path in files
        if path.relative_to(root).as_posix() not in excluded_paths
        for error in check_file(path, root)
    ]
    return excluded_paths, errors


def main():
    files = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    excluded_paths, errors = check_files(files)
    if errors and any(error.startswith("excluded file ") for error in errors):
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1
    for exclusion in EXCLUSIONS:
        print(f"[excluded] {exclusion['path']}: {exclusion['reason']}", file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"{len(errors)} broken relative link(s)", file=sys.stderr)
        return 1
    print(f"Relative link check passed for {len(files)} Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
