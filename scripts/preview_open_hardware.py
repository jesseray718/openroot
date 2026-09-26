#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
OpenRoot Open Hardware Preview v0.1.0

Read-only inventory and readiness reporter for OpenRoot design packets.

It:
- inventories design packet files
- reads metadata, status, intake, and router contexts where present
- runs no mutations
- calculates documentation/evidence/release readiness indicators
- flags missing artifacts and L0/L1 claim boundaries
- renders JSON and Markdown reports

It never:
- changes design files
- stages, commits, pushes, tags, creates releases, or opens GitHub issues
- promotes evidence levels
- modifies model registry, chain, dashboard, or quarantine runtime state
- controls physical systems

Usage:
  python3 scripts/preview_open_hardware.py
  python3 scripts/preview_open_hardware.py --design thermal-cascade
  python3 scripts/preview_open_hardware.py --output-dir reports/open_hardware_preview
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESIGNS = ROOT / "designs"

REQUIRED_PACKET_FILES = (
    "README.md",
    "STATUS.md",
    "metadata.yaml",
    "INTAKE.md",
)

ARTIFACT_GROUPS = {
    "design_definition": (
        "README.md",
        "metadata.yaml",
        "INTAKE.md",
    ),
    "status_and_governance": (
        "STATUS.md",
        "LICENSE",
        "LICENSE.md",
        "SAFETY.md",
        "CONTRIBUTING.md",
    ),
    "design_files": (
        "drawings",
        "cad",
        "mechanical",
        "electrical",
        "schematics",
        "firmware",
        "software",
        "simulation",
    ),
    "build_information": (
        "bom",
        "BOM.csv",
        "BOM.md",
        "build",
        "assembly",
        "fabrication",
    ),
    "test_and_evidence": (
        "tests",
        "test",
        "evidence",
        "measurements",
        "experiment",
        "photos",
        "photo",
        "results",
    ),
}

PHYSICAL_CLAIM_PATTERNS = (
    r"\bproven\b",
    r"\bvalidated\b",
    r"\bverified\b",
    r"\btested\b",
    r"\befficien\w*\b",
    r"\bdelivers?\b",
    r"\bproduces?\b",
    r"\bachieves?\b",
    r"\bperformance\b",
    r"\bworking prototype\b",
    r"\bfield[- ]tested\b",
)

PROTECTED_LOCAL_PATHS = (
    "data/model_registry.json",
    "data/superloop_chains.json",
    "context_bridge/superloop_DASHBOARD.md",
    "bin/quarantine_pyfails_final_v2/",
)


def command(args: list[str]) -> tuple[int, str]:
    process = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return process.returncode, process.stdout.strip()


def git_value(args: list[str], fallback: str = "unavailable") -> str:
    code, output = command(["git", *args])
    return output if code == 0 and output else fallback


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_packet_dirs() -> list[Path]:
    if not DESIGNS.is_dir():
        return []

    packets: list[Path] = []

    for candidate in sorted(DESIGNS.iterdir()):
        if candidate.is_dir() and not candidate.name.startswith("."):
            packets.append(candidate)

    return packets


def parse_simple_yaml(text: str) -> dict[str, str]:
    values: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if re.fullmatch(r"[A-Za-z0-9_.-]+", key):
            values[key] = value

    return values


def infer_evidence_level(packet: Path, intake_text: str, status_text: str) -> str:
    router_context = packet / "router_context.json"

    if router_context.is_file():
        try:
            data = json.loads(read_text(router_context))
            level = data.get("evidence_level")

            if isinstance(level, int):
                return f"L{level}"
        except json.JSONDecodeError:
            pass

    search_text = f"{intake_text}\n{status_text}".lower()

    for level in ("l5", "l4", "l3", "l2", "l1", "l0"):
        if re.search(rf"\b{level}\b", search_text):
            return level.upper()

    return "unknown"


def scan_artifacts(packet: Path) -> dict[str, list[str]]:
    all_files = [
        path.relative_to(packet).as_posix()
        for path in sorted(packet.rglob("*"))
        if path.is_file()
    ]

    lowered = {item: item.lower() for item in all_files}
    grouped: dict[str, list[str]] = {}

    for group, indicators in ARTIFACT_GROUPS.items():
        found: list[str] = []

        for item, lower_item in lowered.items():
            if any(
                indicator.lower() == lower_item
                or indicator.lower() in lower_item.split("/")
                or indicator.lower() in lower_item
                for indicator in indicators
            ):
                found.append(item)

        grouped[group] = sorted(set(found))

    grouped["all_files"] = all_files
    return grouped


def is_disclaimer_line(line: str) -> bool:
    normalized = " ".join(line.lower().split())

    disclaimer_markers = (
        "no field-performance guarantee",
        "no performance guarantee",
        "does not establish a performance guarantee",
        "does not establish performance",
        "does not establish a safety",
        "does not establish safety",
        "not validated",
        "not certified",
        "not field-tested",
        "does not claim",
        "not a performance claim",
        "not a safety claim",
    )

    return any(marker in normalized for marker in disclaimer_markers)


def find_claim_signals(text: str) -> list[str]:
    signals: list[str] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        compact = line.strip()

        if not compact or is_disclaimer_line(compact):
            continue

        if any(re.search(pattern, compact, flags=re.IGNORECASE) for pattern in PHYSICAL_CLAIM_PATTERNS):
            signals.append(f"line {line_number}: {compact[:260]}")

    return signals


def packet_preview(packet: Path) -> dict[str, Any]:
    existing_files = {
        item: (packet / item).is_file()
        for item in REQUIRED_PACKET_FILES
    }

    missing_required = [
        item for item, exists in existing_files.items()
        if not exists
    ]

    intake_path = packet / "INTAKE.md"
    status_path = packet / "STATUS.md"
    metadata_path = packet / "metadata.yaml"
    router_path = packet / "router_context.json"

    intake_text = read_text(intake_path)
    status_text = read_text(status_path)
    metadata_text = read_text(metadata_path)
    metadata = parse_simple_yaml(metadata_text)
    evidence_level = infer_evidence_level(packet, intake_text, status_text)
    artifacts = scan_artifacts(packet)
    claim_signals = find_claim_signals(f"{intake_text}\n{status_text}\n{read_text(packet / 'README.md')}")

    router_summary: dict[str, Any] = {
        "present": router_path.is_file(),
        "valid_json": False,
        "context_kind": None,
        "decision": None,
        "report_available": False,
    }

    router_report = ROOT / ".ci" / "permaculture" / (
        packet.relative_to(ROOT).as_posix().replace("/", "__") + ".report.json"
    )

    if router_path.is_file():
        try:
            context = json.loads(read_text(router_path))
            router_summary["valid_json"] = True
            router_summary["context_kind"] = context.get("context_kind", "intake")
            router_summary["evidence_level"] = context.get("evidence_level")
            router_summary["risk_level"] = context.get("risk_level")
        except json.JSONDecodeError:
            router_summary["error"] = "router_context.json is invalid JSON"

    if router_report.is_file():
        try:
            report = json.loads(read_text(router_report))
            router_summary["report_available"] = True
            router_summary["decision"] = report.get("decision")
            router_summary["gate_count"] = len(report.get("gates", []))
        except json.JSONDecodeError:
            router_summary["report_error"] = "Generated router report is invalid JSON"

    readiness = {
        "documentation": 0,
        "build": 0,
        "evidence": 0,
        "release": 0,
    }

    readiness["documentation"] += sum(existing_files.values()) * 10
    readiness["documentation"] += min(20, len(artifacts["design_files"]) * 5)
    readiness["documentation"] += min(15, len(artifacts["status_and_governance"]) * 3)
    readiness["documentation"] = min(100, readiness["documentation"])

    readiness["build"] += 30 if artifacts["build_information"] else 0
    readiness["build"] += min(30, len(artifacts["design_files"]) * 8)
    readiness["build"] += 20 if metadata else 0
    readiness["build"] += 20 if (packet / "README.md").is_file() else 0
    readiness["build"] = min(100, readiness["build"])

    level_number = int(evidence_level[1:]) if re.fullmatch(r"L[0-5]", evidence_level) else 0
    readiness["evidence"] += level_number * 16
    readiness["evidence"] += 20 if artifacts["test_and_evidence"] else 0
    readiness["evidence"] += 10 if router_summary["present"] else 0
    readiness["evidence"] = min(100, readiness["evidence"])

    readiness["release"] += 25 if not missing_required else 0
    readiness["release"] += 15 if metadata else 0
    readiness["release"] += 15 if artifacts["status_and_governance"] else 0
    readiness["release"] += 15 if router_summary["present"] else 0
    readiness["release"] += 15 if artifacts["build_information"] else 0
    readiness["release"] += 15 if artifacts["test_and_evidence"] else 0
    readiness["release"] = min(100, readiness["release"])

    blockers: list[str] = []
    upgrade_paths: list[str] = []

    if missing_required:
        blockers.append("Missing required packet files: " + ", ".join(missing_required))

    if evidence_level in {"L0", "L1", "unknown"}:
        blockers.append(
            "Evidence remains conceptual/documentary. Do not represent this packet as a validated physical system."
        )
        upgrade_paths.append(
            "Create a bounded non-pressurized or otherwise appropriately safe test protocol with conditions, instruments, stop conditions, raw-data location, and caveats."
        )

    if not artifacts["design_files"]:
        upgrade_paths.append(
            "Add versioned design artifacts: system sketch, CAD/drawing, schematic, simulation, or reproducible calculation."
        )

    if not artifacts["build_information"]:
        upgrade_paths.append(
            "Add a BOM seed and build/assembly notes with local substitutes, criticality, repairability, and sourcing constraints."
        )

    if not artifacts["test_and_evidence"]:
        upgrade_paths.append(
            "Add an evidence directory containing dated measurements, photos, test logs, calculations, and raw-data references."
        )

    if not router_summary["present"]:
        upgrade_paths.append(
            "Add designs/<slug>/router_context.json and run the Permaculture Router to generate an auditable decision report."
        )

    if claim_signals and evidence_level in {"L0", "L1", "unknown"}:
        blockers.append(
            "Potential performance/validation language appears in an L0/L1 packet; review each statement against documented evidence."
        )

    if router_summary["decision"] == "HOLD_FOR_HUMAN_REVIEW":
        blockers.append(
            "Permaculture Router currently requires human review; resolve only by reducing scope, documenting evidence, or completing the appropriate safety/test protocol."
        )

    if not upgrade_paths:
        upgrade_paths.append(
            "Maintain versioned evidence, repeatable build instructions, change records, and regression checks before widening deployment."
        )

    return {
        "slug": packet.name,
        "path": packet.relative_to(ROOT).as_posix(),
        "metadata": metadata,
        "required_files": existing_files,
        "missing_required_files": missing_required,
        "evidence_level": evidence_level,
        "artifact_groups": artifacts,
        "router": router_summary,
        "claim_signals": claim_signals,
        "readiness": readiness,
        "blockers": blockers,
        "upgrade_paths": upgrade_paths,
    }


def tracked_state() -> dict[str, Any]:
    status = git_value(["status", "--short"], "")
    head = git_value(["rev-parse", "--short", "HEAD"])
    branch = git_value(["branch", "--show-current"])
    remote = git_value(["remote", "get-url", "origin"])

    staged = git_value(["diff", "--cached", "--name-only"], "")
    staged_files = [line for line in staged.splitlines() if line.strip()]

    protected_staged: list[str] = []

    for file_name in staged_files:
        for protected in PROTECTED_LOCAL_PATHS:
            if protected.endswith("/") and file_name.startswith(protected):
                protected_staged.append(file_name)
            elif file_name == protected:
                protected_staged.append(file_name)

    return {
        "head": head,
        "branch": branch,
        "origin": remote,
        "status_short": status.splitlines() if status else [],
        "staged_files": staged_files,
        "protected_staged_files": sorted(set(protected_staged)),
    }


def markdown_report(data: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append("<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->")
    lines.append("")
    lines.append("# OpenRoot Open Hardware Preview")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "This is a read-only readiness preview. It does not establish physical performance, "
        "safety, build readiness, or release approval."
    )
    lines.append("")
    lines.append("## Repository")
    lines.append("")
    lines.append(f"- Generated: {data['generated_at_utc']}")
    lines.append(f"- Branch: `{data['repository']['branch']}`")
    lines.append(f"- HEAD: `{data['repository']['head']}`")
    lines.append(f"- Origin: `{data['repository']['origin']}`")
    lines.append("")

    if data["repository"]["protected_staged_files"]:
        lines.append("## Staging boundary warning")
        lines.append("")
        lines.append("Protected local/runtime files are staged:")
        lines.append("")

        for item in data["repository"]["protected_staged_files"]:
            lines.append(f"- `{item}`")

        lines.append("")

    if not data["designs"]:
        lines.append("## Design packets")
        lines.append("")
        lines.append("No design packet directories were found under `designs/`.")
        lines.append("")
        return "\n".join(lines) + "\n"

    lines.append("## Design packet overview")
    lines.append("")
    lines.append("| Packet | Evidence | Documentation | Build | Evidence | Release | Router |")
    lines.append("|---|---|---:|---:|---:|---:|---|")

    for item in data["designs"]:
        router = item["router"]
        router_text = router.get("decision") or ("configured" if router["present"] else "not configured")
        readiness = item["readiness"]

        lines.append(
            f"| `{item['slug']}` | {item['evidence_level']} | "
            f"{readiness['documentation']} | {readiness['build']} | "
            f"{readiness['evidence']} | {readiness['release']} | "
            f"{router_text} |"
        )

    for item in data["designs"]:
        lines.append("")
        lines.append(f"## {item['slug']}")
        lines.append("")
        lines.append(f"- Packet path: `{item['path']}`")
        lines.append(f"- Evidence level: `{item['evidence_level']}`")
        lines.append(f"- Router configured: `{item['router']['present']}`")

        if item["router"].get("context_kind"):
            lines.append(f"- Router context kind: `{item['router']['context_kind']}`")

        if item["router"].get("decision"):
            lines.append(f"- Router decision: `{item['router']['decision']}`")

        if item["metadata"]:
            lines.append("- Metadata observed:")

            for key, value in sorted(item["metadata"].items()):
                lines.append(f"  - `{key}`: `{value}`")

        lines.append("")
        lines.append("### Artifact inventory")
        lines.append("")

        for group, artifacts in item["artifact_groups"].items():
            if group == "all_files":
                continue

            rendered = ", ".join(f"`{artifact}`" for artifact in artifacts) if artifacts else "_none found_"
            lines.append(f"- {group.replace('_', ' ')}: {rendered}")

        if item["blockers"]:
            lines.append("")
            lines.append("### Review gates")
            lines.append("")

            for blocker in item["blockers"]:
                lines.append(f"- {blocker}")

        if item["claim_signals"]:
            lines.append("")
            lines.append("### Language requiring evidence review")
            lines.append("")

            for signal in item["claim_signals"]:
                lines.append(f"- `{signal}`")

        lines.append("")
        lines.append("### Upgrade path")
        lines.append("")

        for upgrade in item["upgrade_paths"]:
            lines.append(f"- {upgrade}")

    lines.append("")
    lines.append("## Release policy")
    lines.append("")
    lines.append(
        "A design-packet release may publish documentation and clearly bounded evidence. "
        "It must not claim physical validation beyond the packet's documented evidence level."
    )
    lines.append("")
    lines.append(
        "Use pre-1.0 tags for evolving frameworks and experimental packets. "
        "Semantic Versioning defines a minor version as backward-compatible added functionality "
        "and a patch as a backward-compatible fix; stable major releases should wait for an interface "
        "and evidence boundary that users can actually rely on."
    )
    lines.append("")
    lines.append("## Autonomous operation boundary")
    lines.append("")
    lines.append(
        "The router and CI may observe, validate, score, generate reports, and propose. "
        "A human must approve physical actions, evidence-level changes, Git commits, pushes, releases, "
        "milestone changes, and public claims."
    )
    lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a read-only OpenRoot open-hardware readiness preview."
    )
    parser.add_argument(
        "--design",
        action="append",
        default=[],
        help="Preview only this design slug. May be supplied more than once.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/open_hardware_preview"),
        help="Relative or absolute report output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = set(args.design)

    packets = find_packet_dirs()

    if selected:
        packets = [packet for packet in packets if packet.name in selected]
        missing = selected - {packet.name for packet in packets}

        if missing:
            print(
                "preview_open_hardware: unknown design slug(s): " + ", ".join(sorted(missing)),
                file=sys.stderr,
            )
            return 2

    preview = {
        "report_version": 1,
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "mode": "read-only preview",
        "repository": tracked_state(),
        "designs": [packet_preview(packet) for packet in packets],
        "invariants": [
            "No automatic evidence promotion.",
            "No Git mutations.",
            "No release creation.",
            "No physical-system control.",
            "No modification of protected local runtime state.",
        ],
    }

    output_dir = args.output_dir

    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "open_hardware_preview.json"
    markdown_path = output_dir / "open_hardware_preview.md"

    json_path.write_text(
        json.dumps(preview, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    markdown_path.write_text(
        markdown_report(preview),
        encoding="utf-8",
    )

    print(f"Wrote JSON preview: {json_path.relative_to(ROOT) if json_path.is_relative_to(ROOT) else json_path}")
    print(f"Wrote Markdown preview: {markdown_path.relative_to(ROOT) if markdown_path.is_relative_to(ROOT) else markdown_path}")

    for item in preview["designs"]:
        readiness = item["readiness"]
        print()
        print(f"Design: {item['slug']}")
        print(f"Evidence: {item['evidence_level']}")
        print(
            "Readiness: "
            f"documentation={readiness['documentation']} "
            f"build={readiness['build']} "
            f"evidence={readiness['evidence']} "
            f"release={readiness['release']}"
        )
        print(f"Router: {item['router'].get('decision') or 'not evaluated'}")
        print(f"Review gates: {len(item['blockers'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
