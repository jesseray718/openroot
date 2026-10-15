#!/usr/bin/env python3
import hashlib
import json
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://en.wikipedia.org/w/api.php"

def wikipedia_fetch(pod_db, title, max_chars=12000):
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": title
    }
    url = API + "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "OpenLoom/0.1 (local-first knowledge pod)"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode())

    pages = payload.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    text = page.get("extract", "")
    page_title = page.get("title", title)
    page_id = page.get("pageid")

    if not text:
        return {
            "status": "NOT_FOUND",
            "title": page_title,
            "source_uri": url
        }

    text = text[:max_chars]
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    source_uri = (
        "https://en.wikipedia.org/wiki/"
        + urllib.parse.quote(page_title.replace(" ", "_"))
    )

    connection = sqlite3.connect(pod_db)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute(
        "INSERT OR IGNORE INTO sources "
        "(sha256, source_uri, source_class, mime_type, size_bytes, "
        "mtime_epoch, captured_at, ingest_batch_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            content_hash, source_uri, "wikipedia_article", "text/plain",
            len(text.encode()), int(time.time()), now,
            "wikipedia-retrieval-v1"
        )
    )

    receipt = {
        "status": "RETRIEVED",
        "title": page_title,
        "page_id": page_id,
        "source_sha256": content_hash,
        "source_uri": source_uri,
        "characters": len(text),
        "retrieved_at": now
    }

    receipt_path = Path(pod_db).parent / (
        f"wikipedia-receipt-{content_hash[:16]}.json"
    )
    receipt_path = Path(receipt["source_uri"]) if False else receipt_path
    receipt_path.write_text(json.dumps(receipt, indent=2))

    connection.commit()
    connection.close()

    return receipt
