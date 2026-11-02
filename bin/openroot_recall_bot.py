#!/usr/bin/env python3
import hashlib, json, os, re, shutil, sys, time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MAX_FILES = 2000
MAX_FILE_SIZE = 300000
MAX_TOTAL_BYTES = 40000000
MAX_CANDIDATES = 5

DOCUMENT_ROOTS = [
    Path.home() / "openroot" / "context_bridge" / "mistake_solutions",
    Path("/home/jesse/aerocement-selected-ubf7nZRr/documents"),
]
STAGING_DIR = Path.home() / ".local" / "share" / "openroot-recall"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def extract_terms(question: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]{3,}", question.lower())

def score_document(text: str, terms: List[str]) -> Tuple[int, int]:
    text_lower = text.lower()
    matches = 0
    first_pos = len(text)
    for term in terms:
        count = text_lower.count(term)
        matches += count
        if count > 0:
            first_pos = min(first_pos, text_lower.find(term))
    return matches, first_pos

def read_document(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_FILE_SIZE: return None
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None

def inventory_documents(roots: List[Path]) -> List[Tuple[Path, str]]:
    docs = []
    total_bytes = 0
    for root in roots:
        if not root.exists(): continue
        for path in root.rglob("*.md"):
            content = read_document(path)
            if content is None: continue
            if total_bytes + len(content.encode("utf-8")) > MAX_TOTAL_BYTES: break
            docs.append((path, content))
            total_bytes += len(content.encode("utf-8"))
    return docs

def search_documents(documents: List[Tuple[Path, str]], question: str) -> List[Dict[str, Any]]:
    terms = extract_terms(question)
    if not terms: return []
    scored = []
    for path, content in documents:
        matches, first_pos = score_document(content, terms)
        if matches > 0:
            scored.append({"path": str(path), "matches": matches, "first_pos": first_pos, "content": content})
    scored.sort(key=lambda x: (-x["matches"], x["first_pos"]))
    candidates = []
    for doc in scored[:MAX_CANDIDATES]:
        pos = doc["first_pos"]
        start = max(0, pos - 100)
        excerpt = doc["content"][start:min(len(doc["content"]), pos + 400)].strip()
        candidates.append({"path": doc["path"], "excerpt": excerpt, "line_number": len(doc["content"][:start].split("\n")) + 1, "matches": doc["matches"]})
    return candidates

def stage_packet(question: str, candidates: List[Dict[str, Any]]) -> Path:
    timestamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    session_dir = STAGING_DIR / f"{timestamp}-{os.getpid()}"
    session_dir.mkdir(parents=True, exist_ok=True)
    with open(session_dir / "evidence.json", "w", encoding="utf-8") as f:
        json.dump({"question": question, "candidates": candidates, "timestamp": timestamp}, f, indent=2)
    print(f"[ok] Staged packet: {session_dir}")
    return session_dir

class Tests:
    def test_retrieval(self):
        test_dir = STAGING_DIR / "test_retrieval"
        test_dir.mkdir(exist_ok=True)
        (test_dir / "doc1.md").write_text("sqlite locked writer error occurred")
        assert len(inventory_documents([test_dir])) == 1
        shutil.rmtree(test_dir)
        print("test_retrieval ... ok")

def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        Tests().test_retrieval()
        print("All tests passed.")
        return 0
    query = " ".join(args) if args else None
    if not query:
        print("Usage: python3 openroot_recall_bot.py --query <question>")
        return 1
    docs = inventory_documents(DOCUMENT_ROOTS)
    candidates = search_documents(docs, query)
    if not candidates:
        print("[info] No candidates found.")
        return 0
    stage_packet(query, candidates)
    return 0

if __name__ == "__main__":
    sys.exit(main())
