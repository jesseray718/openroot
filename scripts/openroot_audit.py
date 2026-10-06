#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".openroot-audit"
OUT.mkdir(parents=True, exist_ok=True)

def run(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result.stdout

def gh_json(*args: str) -> Any:
    text = run("gh", *args)
    return json.loads(text) if text.strip() else []

def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

def write_json(name: str, value: Any) -> Path:
    path = OUT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path

def write_text(name: str, value: str) -> Path:
    path = OUT / name
    path.write_text(value, encoding="utf-8")
    return path

def exists(path: str) -> bool:
    return (ROOT / path).exists()

def first_line(value: str) -> str:
    return value.strip().splitlines()[0] if value.strip() else ""

def main() -> int:
    if not shutil.which("git") or not shutil.which("gh"):
        raise RuntimeError("Both git and gh must be installed and available on PATH.")

    if not (ROOT / ".git").exists():
        raise RuntimeError(f"{ROOT} is not a Git repository.")

    dirty = run("git", "status", "--porcelain")
    repo = gh_json(
        "repo", "view",
        "--json",
        "nameWithOwner,url,description,defaultBranchRef,isPrivate,"
        "hasDiscussionsEnabled,hasIssuesEnabled,licenseInfo,repositoryTopics,"
        "createdAt,updatedAt,pushedAt"
    )
    owner_repo = repo["nameWithOwner"]
    default_branch = repo["defaultBranchRef"]["name"]

    run("git", "fetch", "--all", "--prune")
    local_branches = run(
        "git", "for-each-ref",
        "--format=%(refname:short)\t%(upstream:short)\t%(objectname:short)\t%(committerdate:iso8601)\t%(subject)",
        "refs/heads/"
    )
    remote_branches_raw = run(
        "git", "for-each-ref",
        "--format=%(refname:short)\t%(objectname:short)\t%(committerdate:iso8601)\t%(subject)",
        "refs/remotes/origin/"
    )

    remote_branches = []
    merged_branches = []
    unmerged_branches = []

    for line in remote_branches_raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 3)
        branch = parts[0].removeprefix("origin/")
        if branch == "HEAD" or branch == default_branch:
            continue

        is_merged = subprocess.run(
            ["git", "merge-base", "--is-ancestor", f"origin/{branch}", f"origin/{default_branch}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0

        ahead = run(
            "git", "rev-list", "--count",
            f"origin/{default_branch}..origin/{branch}"
        ).strip()

        item = {
            "branch": branch,
            "sha": parts[1] if len(parts) > 1 else "",
            "date": parts[2] if len(parts) > 2 else "",
            "subject": parts[3] if len(parts) > 3 else "",
            "merged_into_default": is_merged,
            "commits_ahead_of_default": int(ahead or "0"),
        }
        remote_branches.append(item)
        (merged_branches if is_merged else unmerged_branches).append(item)

    fields = (
        "number,title,state,isDraft,author,headRefName,baseRefName,"
        "mergeStateStatus,reviewDecision,updatedAt,createdAt,mergedAt,url,labels"
    )
    prs_open = gh_json("pr", "list", "--repo", owner_repo, "--state", "open", "--limit", "200", "--json", fields)
    prs_merged = gh_json("pr", "list", "--repo", owner_repo, "--state", "merged", "--limit", "200", "--json", fields)
    prs_closed = gh_json("pr", "list", "--repo", owner_repo, "--state", "closed", "--limit", "200", "--json", fields)

    issues_open = gh_json(
        "issue", "list", "--repo", owner_repo, "--state", "open", "--limit", "200",
        "--json", "number,title,updatedAt,createdAt,author,labels,milestone,url"
    )
    milestones = gh_json(
        "api", f"repos/{owner_repo}/milestones?state=all&per_page=100"
    )
    releases = gh_json(
        "api", f"repos/{owner_repo}/releases?per_page=100"
    )

    discussions: list[dict[str, Any]] = []
    discussion_error = ""
    if repo.get("hasDiscussionsEnabled"):
        query = """
        query($owner:String!, $name:String!) {
          repository(owner:$owner, name:$name) {
            discussions(first:100, orderBy:{field:UPDATED_AT, direction:DESC}) {
              nodes {
                number
                title
                createdAt
                updatedAt
                url
                category { name slug }
                author { login }
              }
            }
          }
        }
        """
        try:
            owner, name = owner_repo.split("/", 1)
            raw = run(
                "gh", "api", "graphql",
                "-f", f"query={query}",
                "-F", f"owner={owner}",
                "-F", f"name={name}",
            )
            discussions = json.loads(raw)["data"]["repository"]["discussions"]["nodes"]
        except Exception as exc:
            discussion_error = str(exc)

    files = {
        "README.md": exists("README.md"),
        "LICENSE": exists("LICENSE") or exists("LICENSE.md"),
        "CONTRIBUTING.md": exists("CONTRIBUTING.md"),
        "CODE_OF_CONDUCT.md": exists("CODE_OF_CONDUCT.md"),
        "SECURITY.md": exists("SECURITY.md") or exists(".github/SECURITY.md"),
        "CODEOWNERS": exists("CODEOWNERS") or exists(".github/CODEOWNERS"),
        "Issue templates": exists(".github/ISSUE_TEMPLATE"),
        "PR template": exists(".github/pull_request_template.md") or exists("PULL_REQUEST_TEMPLATE.md"),
        "Workflows": exists(".github/workflows"),
        "Dependabot": exists(".github/dependabot.yml"),
        "EditorConfig": exists(".editorconfig"),
        "Python project metadata": exists("pyproject.toml"),
    }

    write_text("git-status.txt", run("git", "status", "--short"))
    write_text("local-branches.tsv", local_branches)
    write_json("repo.json", repo)
    write_json("open-prs.json", prs_open)
    write_json("merged-prs.json", prs_merged)
    write_json("closed-prs.json", prs_closed)
    write_json("open-issues.json", issues_open)
    write_json("milestones.json", milestones)
    write_json("releases.json", releases)
    write_json("discussions.json", discussions)
    write_json("remote-branches.json", remote_branches)
    write_json("merged-remote-branches.json", merged_branches)
    write_json("unmerged-remote-branches.json", unmerged_branches)
    write_json("repository-hygiene.json", files)
    if discussion_error:
        write_text("discussion-query-error.txt", discussion_error + "\n")

    now = datetime.now(timezone.utc).isoformat()
    stale_open = [
        pr for pr in prs_open
        if pr.get("updatedAt", "") < "2026-08-06T00:00:00Z"
    ]

    lines = [
        "# OpenRoot GitHub Audit",
        "",
        f"- Generated: `{now}`",
        f"- Repository: [{owner_repo}]({repo['url']})",
        f"- Default branch: `{default_branch}`",
        f"- Worktree clean: `{'yes' if not dirty.strip() else 'NO — resolve before write operations'}`",
        "",
        "## Repository snapshot",
        "",
        f"- Description: {repo.get('description') or '_none_'}",
        f"- Visibility: `{'private' if repo.get('isPrivate') else 'public'}`",
        f"- Discussions enabled: `{repo.get('hasDiscussionsEnabled')}`",
        f"- Issues enabled: `{repo.get('hasIssuesEnabled')}`",
        f"- License: `{(repo.get('licenseInfo') or {}).get('spdxId', 'none')}`",
        f"- Last push: `{repo.get('pushedAt')}`",
        "",
        "## Pull requests",
        "",
        f"- Open: **{len(prs_open)}**",
        f"- Merged returned by CLI: **{len(prs_merged)}**",
        f"- Closed without merge returned by CLI: **{len(prs_closed)}**",
        f"- Open PRs older than 60 days by last update: **{len(stale_open)}**",
        "",
    ]

    if prs_open:
        lines.extend(["### Open PR review queue", ""])
        for pr in prs_open:
            labels = ", ".join(label["name"] for label in pr.get("labels", [])) or "none"
            lines.append(
                f"- [#{pr['number']}]({pr['url']}) `{pr['headRefName']}` → `{pr['baseRefName']}` — "
                f"{pr['title']} — draft={pr['isDraft']}, merge={pr.get('mergeStateStatus')}, "
                f"review={pr.get('reviewDecision')}, labels={labels}, updated={pr['updatedAt']}"
            )
        lines.append("")

    lines.extend([
        "## Branch hygiene",
        "",
        f"- Remote feature branches already merged into `{default_branch}`: **{len(merged_branches)}**",
        f"- Remote feature branches not merged into `{default_branch}`: **{len(unmerged_branches)}**",
        "",
        "### Candidates for deletion after verification",
        "",
    ])
    if merged_branches:
        for branch in merged_branches:
            lines.append(
                f"- `{branch['branch']}` — merged; last commit `{branch['sha'][:12]}` "
                f"on `{branch['date']}` — {branch['subject']}"
            )
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.extend(["### Branches requiring decision", ""])
    if unmerged_branches:
        for branch in unmerged_branches:
            lines.append(
                f"- `{branch['branch']}` — {branch['commits_ahead_of_default']} commit(s) ahead of `{default_branch}`; "
                f"last commit `{branch['sha'][:12]}` on `{branch['date']}` — {branch['subject']}"
            )
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.extend(["## Milestones", ""])
    if milestones:
        for milestone in milestones:
            state = milestone.get("state", "unknown")
            due = milestone.get("due_on") or "no due date"
            lines.append(
                f"- #{milestone['number']} **{milestone['title']}** — `{state}`, "
                f"open={milestone['open_issues']}, closed={milestone['closed_issues']}, due={due}"
            )
    else:
        lines.append("- No milestones found.")
    lines.append("")

    lines.extend(["## Releases", ""])
    if releases:
        for release in releases:
            lines.append(
                f"- [{release['tag_name']}]({release['html_url']}) — "
                f"{'draft' if release['draft'] else 'published'}; "
                f"published={release.get('published_at') or 'not published'}"
            )
    else:
        lines.append("- No releases found.")
    lines.append("")

    lines.extend(["## Discussions", ""])
    if discussion_error:
        lines.append("- Unable to retrieve discussions; inspect `discussion-query-error.txt`.")
    elif not repo.get("hasDiscussionsEnabled"):
        lines.append("- Discussions are disabled.")
    elif discussions:
        for discussion in discussions:
            category = (discussion.get("category") or {}).get("name", "uncategorized")
            lines.append(
                f"- [#{discussion['number']}]({discussion['url']}) **{discussion['title']}** "
                f"— {category}; updated={discussion['updatedAt']}"
            )
    else:
        lines.append("- No discussions found.")
    lines.append("")

    lines.extend(["## Repository hygiene", ""])
    for name, present in files.items():
        lines.append(f"- [{'x' if present else ' '}] {name}")
    lines.append("")

    lines.extend([
        "## Decision rules",
        "",
        "1. Merge an open PR only when it has a clear purpose, passes checks, has no unresolved conflicts, and does not weaken the public/safety/evidence boundary.",
        "2. Use squash merge for approved work; delete its head branch only after merge.",
        "3. Do not delete unmerged branches just because they are old. Compare them first, then open a PR, archive with a tag, or delete with an explicit reason.",
        "4. Use milestones for bounded outcomes; use releases only for a stable, documented snapshot with notes.",
        "5. Use issues for concrete, actionable work; use discussions for open questions, design proposals, and community coordination.",
        "",
        "## Generated artifacts",
        "",
        "- `repo.json`",
        "- `open-prs.json`, `merged-prs.json`, `closed-prs.json`",
        "- `open-issues.json`, `milestones.json`, `releases.json`, `discussions.json`",
        "- `remote-branches.json`, `merged-remote-branches.json`, `unmerged-remote-branches.json`",
        "- `repository-hygiene.json`, `local-branches.tsv`, `git-status.txt`",
    ])

    write_text("REPORT.md", "\n".join(lines) + "\n")
    print(f"Audit complete: {OUT / 'REPORT.md'}")
    print(f"Repository: {owner_repo}")
    print(f"Default branch: {default_branch}")
    print(f"Open PRs: {len(prs_open)}")
    print(f"Merged remote branch candidates: {len(merged_branches)}")
    print(f"Unmerged remote branches requiring review: {len(unmerged_branches)}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
