#!/usr/bin/env python3
"""
DOSSIER-AUGMENTED 100-QUESTION BENCHMARK
========================================
Executes 100 benchmark questions by recalling word dossiers and preloaded
contexts across active SQLite pods, summing execution times and tracking recall.
"""

import sys
import time
import sqlite3
import re
from pathlib import Path

QUESTIONS = [
    # Level 1-20: Repository Layout & Basic Git Operations
    "How do I initialize a new git repository?",
    "What is the command to check repository status?",
    "How do I stage modified files for commit?",
    "How do I create a commit with a message?",
    "How do I view commit history?",
    "What does git branch do?",
    "How do I switch between branches?",
    "How do I create and switch to a new branch?",
    "How do I push a branch to origin?",
    "How do I pull changes from a remote repository?",
    "How do I add a remote repository?",
    "How do I inspect remote URLs?",
    "What is the purpose of .gitignore?",
    "How do I ignore untracked files?",
    "How do I view differences in staged files?",
    "How do I discard local changes in a file?",
    "How do I rename a branch locally and remotely?",
    "How do I delete a local branch?",
    "How do I delete a remote branch?",
    "How do I stash uncommitted changes?",
    
    # Level 21-50: Advanced Merging, Branch Protection & Pull Requests
    "How do branch protection rules affect merging a pull request?",
    "What are GitHub Actions workflows?",
    "How do I create and merge a pull request on GitHub?",
    "What is a fast-forward merge versus a no-ff merge?",
    "How do I resolve merge conflicts locally?",
    "What is the purpose of CODEOWNERS in a repository?",
    "How do status checks block PR merging?",
    "What is a merge queue and when should it be used?",
    "How do I check out a pull request locally for testing?",
    "How do I configure automatic branch deletion after merging?",
    "What are GitHub Actions runners and how do self-hosted runners work?",
    "How do workflow triggers work on push and pull request events?",
    "How do I use matrix builds in GitHub Actions?",
    "How do I cache dependencies in GitHub Actions workflows?",
    "How do I store and use encrypted secrets in GitHub Actions?",
    "How do I use reusable workflows across repositories?",
    "What is the difference between actions/checkout@v4 and older versions?",
    "How do I set up concurrency groups to cancel redundant workflow runs?",
    "How do I debug a failing GitHub Actions workflow?",
    "How do I pin GitHub Actions to specific commit SHAs for security?",
    "What are GitHub security advisories and Dependabot alerts?",
    "How do I configure branch protection to require signed commits?",
    "How do I use R=1.0 zero-coordination property in the lattice?",
    "What is git cherry-pick and when is it useful?",
    "How do I perform an interactive rebase (git rebase -i)?",
    "What is the difference between git reset --soft, --mixed, and --hard?",
    "How do I recover a deleted commit using git reflog?",
    "How do I bisect a regression in git history?",
    "What is git submodule and how do I update submodules?",
    "How do I write effective commit messages following conventional commits?",

    # Level 51-80: OpenRoot Architecture & Lattice Engineering
    "What is the 6^6 hierarchical lattice structure in OpenRoot?",
    "How do the 12 Permaculture Principles map to computational roles?",
    "What is the Agape reward function equation and how does it compound cooperation?",
    "What is the R=1.0 zero-coordination property in the lattice?",
    "How does the SQLite FTS5 index store and retrieve knowledge chunks?",
    "What is the role of SHA256 content-addressable hashing in OpenRoot pods?",
    "How does the Merkle ledger verify lattice integrity?",
    "What is the purpose of cache state tracking for mtime and file hashes?",
    "How does the local LLM bridge interface with Ollama and llama-server?",
    "What is the fallback mechanism when no local LLM is detected?",
    "How does the word dossier compiler calculate inverse document frequency (IDF)?",
    "What is the purpose of chunk sentence-boundary cutting in context retrieval?",
    "How does the Universal Native Descriptor (und) protocol encode semantics?",
    "What is the Newton Chain thermodynamic ledger?",
    "How do Black Locust rocket mass heaters integrate with passive thermal systems?",
    "What is Aerocement 2.0 formulation and its use of zirconium AR-glass fibers?",
    "How do ferrocement geodesic domes utilize 2V mesh triangular panels?",
    "What is the Dell OptiPlex 3060 and Samsung Galaxy A15 edge node setup?",
    "How does SSH tunneling connect the mobile edge device to the OptiPlex primary node?",
    "What is the purpose of bin/kai in managing model cascading and token limits?",
    "How do cron jobs and systemd services maintain offline persistence?",
    "What is the structure of the knowledge database schema in SQLite?",
    "How do lateral pathways between permaculture principles enable cross-domain synthesis?",
    "What is the distinction between extractive baseline rewards and agape exponential growth?",
    "How do Python script compilations verify code integrity before execution?",
    "What is the workflow for merging salvage worktrees across repositories?",
    "How do JSONL data logs support offline retrieval-augmented generation?",
    "What is the significance of the v0.3.1-thermal-cascade-docs release?",
    "How do autonomous script agents interact with local vector databases?",
    "What is the ultimate vision of the OpenRoot sovereign offline engineering ecosystem?",

    # Level 81-100: Complex Systems & Meta-Engineering
    "How do decentralized thermodynamic ledgers prevent coordination decay?",
    "What are the mathematical properties of golden ratio scaling in cooperative networks?",
    "How do fractal computation lattices mirror biological homeostasis?",
    "What are the security implications of offline-first sovereign hardware nodes?",
    "How do multi-model fallback cascades optimize token expenditure and latency?",
    "What is the role of semantic word dossiers in eliminating redundant LLM prompt tokens?",
    "How do verifiable Merkle trees guarantee zero-tamper provenance across distributed pods?",
    "What is the thermodynamic cost of high-density supercomputer cluster operations?",
    "How do automated electronics recycling logistics integrate with local mesh compute nodes?",
    "What is the relationship between permaculture earth care, people care, and fair share in code architecture?",
    "How do self-healing SQLite FTS5 indexes recover from abrupt node termination?",
    "What are the trade-offs between centralized cloud intelligence and local edge reasoning?",
    "How do dynamic branch routing protocols simulate neural synaptic pathways?",
    "What is the mathematical proof of zero-coordination cost at R=1.0?",
    "How do resilient backup strategies preserve open-source hardware specifications across storage failures?",
    "What is the role of xanthan gum and rubbing alcohol slurry in thixotropic cement rheology?",
    "How do subterranean thermal mass labyrinths store seasonal solar energy?",
    "What is the architectural blueprint for an open-source autonomous engineering civilization?",
    "How do we evaluate the epistemic integrity of offline retrieval-augmented generation?",
    "What is the next evolutionary milestone for the Permaculture Lattice Engine?"
]

def significant_words(text: str) -> list:
    stopwords = {"how", "do", "i", "a", "an", "the", "and", "or", "to", "in", "is", "it", "of", "for", "on", "with", "what", "are", "by", "as", "at"}
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return [w for w in words if w not in stopwords]

def run():
    pods_dir = Path("~/pods").expanduser()
    pod_dbs = list(pods_dir.rglob("pod.db"))
    
    connections = []
    for pdb in pod_dbs:
        try:
            conn = sqlite3.connect(f"file:{pdb}?mode=ro", uri=True)
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "chunks_fts" in tables or "chunks" in tables:
                connections.append((pdb.parent.name, conn, "chunks_fts" in tables))
        except Exception:
            pass

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Active Pod Connections for Dossier Recall: {len(connections)}")
    total_q = len(QUESTIONS)
    latencies = []
    matches_count = 0
    total_dossiers_built = 0

    print(f"Running {total_q} dossier-augmented benchmark queries...\n" + "-"*65)

    for idx, q in enumerate(QUESTIONS, 1):
        t0 = time.perf_counter()
        words = significant_words(q)
        
        dossier_context = []
        dossier_hits = 0
        
        for w in words:
            for name, conn, has_fts in connections:
                try:
                    if has_fts:
                        rows = conn.execute("SELECT rowid, text FROM chunks_fts JOIN chunks ON chunks.chunk_id = chunks_fts.rowid WHERE chunks_fts MATCH ? LIMIT 1", (w,)).fetchall()
                    else:
                        rows = conn.execute("SELECT chunk_id, text FROM chunks WHERE text LIKE ? LIMIT 1", (f"%{w}%",)).fetchall()
                    
                    for r in rows:
                        dossier_hits += 1
                        total_dossiers_built += 1
                        dossier_context.append(f"[dossier word='{w}' pod='{name}' chunk={r[0]}]\n{r[1][:300]}")
                except Exception:
                    pass

        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)
        if dossier_hits > 0:
            matches_count += 1

        if idx <= 5 or idx % 20 == 0 or idx == total_q:
            print(f"[{idx:3d}/{total_q}] {elapsed:6.2f} ms | words={len(words):2d} dossiers={dossier_hits:2d} | {q[:45]}...")

    for _, conn, _ in connections:
        conn.close()

    total_time_ms = sum(latencies)
    print("-" * 65)
    print("=== DOSSIER-AUGMENTED BENCHMARK RESULTS ===")
    print(f"  Total Questions Tested: {total_q}")
    print(f"  Successful Recall Rate: {(matches_count / total_q) * 100:.1f}%")
    print(f"  Total Dossiers Compiled: {total_dossiers_built:,}")
    print(f"  Summed Execution Time:  {total_time_ms:,.2f} ms ({total_time_ms/1000:.2f} seconds)")
    print(f"  Average Latency:        {total_time_ms/total_q:.2f} ms per query")
    print(f"  Max Latency:            {max(latencies):.2f} ms")

if __name__ == "__main__":
    run()
