"""Validate parts_library/tidbits.json: schema integrity + connection graph.

This is the "test connections of all kinds" harness referenced in the tidbit
library. It checks:
  1. Every tidbit/external entry has the required fields.
  2. Every id is unique across tidbits + external_repos.
  3. Every connects_to edge points at an id that actually exists in the library
     (no dangling references -- a prerequisite for a Turing-motor-style network
     where any part can be looked up from any other part).
  4. Every local tidbit's `path` exists on disk in this repo (reposcope: only
     local, verifiable claims are checked against the filesystem).
  5. The local tidbit graph (treated as undirected) has no isolated node --
     every local part connects to at least one other local part.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY_PATH = ROOT / "parts_library" / "tidbits.json"

REQUIRED_TIDBIT_FIELDS = {"id", "scope", "path", "kind", "summary", "provides", "requires", "connects_to"}
REQUIRED_EXTERNAL_FIELDS = {"id", "scope", "repo", "status", "note"}


def load_library() -> dict:
    with LIBRARY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def all_ids(library: dict) -> set[str]:
    return {t["id"] for t in library["tidbits"]} | {e["id"] for e in library["external_repos"]}


def test_library_loads():
    library = load_library()
    assert "tidbits" in library and "external_repos" in library
    assert len(library["tidbits"]) > 0
    print(f"  OK  loaded {len(library['tidbits'])} local tidbits, "
          f"{len(library['external_repos'])} external repo stubs")


def test_schema_fields():
    library = load_library()
    for t in library["tidbits"]:
        missing = REQUIRED_TIDBIT_FIELDS - t.keys()
        assert not missing, f"tidbit {t.get('id')} missing fields: {missing}"
        assert t["scope"] == "local", f"tidbit {t['id']} must have scope=local"
    for e in library["external_repos"]:
        missing = REQUIRED_EXTERNAL_FIELDS - e.keys()
        assert not missing, f"external repo {e.get('id')} missing fields: {missing}"
        assert e["scope"] == "external", f"external repo {e['id']} must have scope=external"
    print("  OK  all entries have required schema fields")


def test_unique_ids():
    library = load_library()
    ids = [t["id"] for t in library["tidbits"]] + [e["id"] for e in library["external_repos"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate ids: {dupes}"
    print(f"  OK  {len(ids)} ids are unique")


def test_connections_resolve():
    library = load_library()
    known = all_ids(library)
    for t in library["tidbits"]:
        for edge in t["connects_to"]:
            assert edge in known, f"{t['id']} connects_to unknown id '{edge}'"
    print("  OK  every connects_to edge resolves to a known tidbit")


def test_local_paths_exist():
    library = load_library()
    for t in library["tidbits"]:
        path_field = t["path"].split("#", 1)[0]  # strip doc anchors like README.md#section
        target = ROOT / path_field
        assert target.exists(), f"{t['id']} declares path '{path_field}' which does not exist"
    print("  OK  every local tidbit path exists on disk")


def test_graph_no_isolated_local_nodes():
    library = load_library()
    local_ids = {t["id"] for t in library["tidbits"]}
    # Build undirected adjacency restricted to local ids.
    adjacency: dict[str, set[str]] = {i: set() for i in local_ids}
    for t in library["tidbits"]:
        for edge in t["connects_to"]:
            if edge in local_ids:
                adjacency[t["id"]].add(edge)
                adjacency[edge].add(t["id"])
    isolated = [i for i, neighbors in adjacency.items() if not neighbors]
    assert not isolated, f"isolated local tidbits (no connections): {isolated}"
    print(f"  OK  no isolated local tidbits ({len(local_ids)} nodes all connected to >=1 peer)")


def test_reposcope_report():
    """Summarize scope coverage: local vs external, verified vs unindexed."""
    library = load_library()
    local_n = len(library["tidbits"])
    external_n = len(library["external_repos"])
    unindexed = sum(1 for e in library["external_repos"] if e["status"] == "unindexed")
    archived = sum(1 for e in library["external_repos"] if e["status"] == "archived")
    assert unindexed + archived == external_n
    print(f"  OK  reposcope: {local_n} local (verified) + {external_n} external "
          f"({unindexed} unindexed, {archived} archived)")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("All tidbit library tests passed.")
