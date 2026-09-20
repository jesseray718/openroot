"""canonical/ecosystem_dashboard.py
The canonical index node — reads ecosystem manifest and generates dashboard."""
import json, os
from pathlib import Path
from datetime import datetime, timezone

UNE = Path(os.environ.get("UNE_DIR", str(Path.home() / "une")))
HERE = Path(__file__).parent
MANIFEST = UNE / "ecosystem_manifest.json"

def generate():
    if not MANIFEST.exists():
        return {"error": "manifest not found"}
    
    manifest = json.loads(MANIFEST.read_text())
    repos = manifest.get("repos", {})
    node_map = manifest.get("node_map", {})
    
    status = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_repos": len(repos),
        "active_nodes": len([r for r in repos.values() if r.get("health") == "active"]),
        "total_files": sum(r.get("files", 0) for r in repos.values()),
        "total_lines": sum(r.get("lines", 0) for r in repos.values()),
        "max_depth": node_map.get("max_depth", 0),
        "capacity": node_map.get("capacity", 0),
        "repos": repos
    }
    
    (HERE / "status.json").write_text(json.dumps(status, indent=2))
    
    md = f"# Ecosystem Dashboard\n\n"
    md += f"**Generated:** {status['generated']}\n\n"
    md += f"| Repos | Active | Files | Lines | Depth | Capacity |\n|---|---|---|---|---|---|\n"
    md += f"| {status['total_repos']} | {status['active_nodes']} | {status['total_files']} | {status['total_lines']} | {status['max_depth']} | {status['capacity']} |\n\n"
    md += "## Repos\n\n"
    md += "| Repo | Role | Health | Files | Lines |\n|---|---|---|---|---|\n"
    for name, data in repos.items():
        role = ", ".join(data.get("role", []))
        health = data.get("health", "unknown")
        files = data.get("files", 0)
        lines = data.get("lines", 0)
        icon = "✅" if health == "active" else "⚠️" if health == "minimal" else "❌"
        md += f"| {name} | {role} | {icon} {health} | {files} | {lines} |\n"
    
    (HERE / "dashboard.md").write_text(md)
    print(f"[CANONICAL] Dashboard regenerated — {status['active_nodes']} active repos")
    return status

if __name__ == "__main__":
    generate()
