#!/usr/bin/env python3
"""Inspect what jesseray718 actually pushed. Remote refs only. η-first."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = "jesseray718"
WATCH = [
    "openroot",
    "une",
    "agape-une",
    "aerocement",
    "black-locust-rmh",
    "openroot-spoke-template",
    "jesseray718",
    "canonical",
    "wisdom-scaffold",
    "axiom-library",
    "oscillation-mesh",
    "fractallattice",
    "aerocement-calc",
]
DUMP = Path("/home/jesse/openroot/dump")
OUTBOX = Path("/home/jesse/openroot/outbox")


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(cmd: str, cwd=None) -> str:
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return ((p.stdout or "") + (p.stderr or "")).rstrip()


def api(path: str):
    url = "https://api.github.com" + path
    req = urllib.request.Request(url, headers={"User-Agent": "openroot-inspect"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def local_git_roots():
    raw = sh(
        "find /home/jesse/openroot /home/jesse -maxdepth 4 -type d -name .git 2>/dev/null"
    )
    roots = []
    for line in raw.splitlines():
        if line.endswith("/.git"):
            roots.append(line[:-5])
    return sorted(set(roots))


def inspect_local(root: str) -> dict:
    d = {"root": root}
    d["remote"] = sh("git remote -v", cwd=root)
    d["status"] = sh("git status -sb", cwd=root)
    d["head"] = sh("git log -1 --format='%H %ci %s'", cwd=root)
    d["unpushed"] = sh("git log --oneline @{u}..HEAD", cwd=root)
    d["ls_remote_heads"] = sh("git ls-remote --heads origin", cwd=root)
    return d


def main():
    DUMP.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    report = {
        "utc": utc(),
        "pane_hint": "SSH expected; refuse if not jesse@optiplex3060",
        "host": sh("hostname"),
        "user": sh("whoami"),
        "repos": [],
        "events": [],
        "local": [],
    }
    try:
        repos = api("/users/%s/repos?per_page=100" % USER)
    except Exception as e:
        repos = []
        report["repos_error"] = str(e)
    for r in sorted(repos, key=lambda x: x.get("pushed_at") or "", reverse=True):
        report["repos"].append(
            {
                "name": r["name"],
                "pushed_at": r.get("pushed_at"),
                "updated_at": r.get("updated_at"),
                "default_branch": r.get("default_branch"),
                "fork": r.get("fork"),
                "archived": r.get("archived"),
                "html_url": r.get("html_url"),
                "watch": r["name"] in WATCH,
            }
        )
    try:
        events = api("/users/%s/events?per_page=30" % USER)
    except Exception as e:
        events = []
        report["events_error"] = str(e)
    for e in events:
        item = {
            "created_at": e.get("created_at"),
            "type": e.get("type"),
            "repo": (e.get("repo") or {}).get("name"),
        }
        p = e.get("payload") or {}
        if e.get("type") == "PushEvent":
            item["ref"] = p.get("ref")
            item["size"] = p.get("size")
            item["commits"] = [
                {
                    "sha": c.get("sha", "")[:12],
                    "msg": (c.get("message") or "").splitlines()[0][:120],
                }
                for c in (p.get("commits") or [])[:5]
            ]
        report["events"].append(item)
    for root in local_git_roots():
        report["local"].append(inspect_local(root))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = DUMP / ("github_pushed_%s.json" % stamp)
    md_path = OUTBOX / "GITHUB_PUSH_INSPECT.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GITHUB_PUSH_INSPECT",
        "utc: %s" % report["utc"],
        "host: %s" % report["host"],
        "user: %s" % report["user"],
        "",
        "## remote repos by last push",
    ]
    for r in report["repos"][:40]:
        mark = " WATCH" if r["watch"] else ""
        lines.append(
            "- %s  %s  default=%s  fork=%s  archived=%s%s"
            % (
                r["pushed_at"],
                r["name"],
                r["default_branch"],
                r["fork"],
                r["archived"],
                mark,
            )
        )
    lines += ["", "## recent events"]
    for e in report["events"][:20]:
        extra = ""
        if e.get("commits"):
            extra = " | " + " ; ".join(
                c["sha"] + " " + c["msg"] for c in e["commits"]
            )
        lines.append(
            "- %s  %s  %s  %s%s"
            % (e.get("created_at"), e.get("type"), e.get("repo"), e.get("ref", ""), extra)
        )
    lines += ["", "## local git roots vs origin"]
    for loc in report["local"]:
        lines.append("### %s" % loc["root"])
        lines.append("```")
        lines.append(loc.get("status") or "")
        lines.append(loc.get("head") or "")
        lines.append("unpushed:")
        lines.append(loc.get("unpushed") or "(none or no upstream)")
        lines.append("```")
        lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_path)
    print(md_path)
    print("repos", len(report["repos"]), "events", len(report["events"]), "local", len(report["local"]))


if __name__ == "__main__":
    sys.exit(main())
