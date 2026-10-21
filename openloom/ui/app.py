#!/usr/bin/env python3
"""Minimal local-only OpenLoom manual evidence UI."""

from __future__ import annotations

import argparse
import html
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def render_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #111; color: #eee; }}
a {{ color: #7dd3fc; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #444; padding: .45rem; text-align: left; vertical-align: top; }}
th {{ background: #222; }}
code, pre {{ background: #1c1c1c; padding: .15rem .35rem; border-radius: 4px; }}
pre {{ overflow-x: auto; padding: .75rem; }}
form {{ margin: 1rem 0; }}
input {{ padding: .45rem; width: min(520px, 90%); }}
button {{ padding: .45rem .8rem; }}
.badge {{ display: inline-block; background: #14532d; padding: .2rem .5rem; border-radius: 999px; }}
</style>
</head>
<body>
<h1>OpenLoom Evidence UI</h1>
<p class="badge">local read-only</p>
{body}
</body>
</html>"""


def table_list(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        """
        SELECT table_id, pdf_page, row_count, column_count,
               csv_sha256, jsonl_sha256
        FROM manual_tables
        ORDER BY pdf_page, table_id
        """
    ).fetchall()

    body = ["<h2>Manual tables</h2><table><tr><th>Table</th><th>Page</th><th>Rows</th><th>Columns</th><th>CSV SHA-256</th><th>JSONL SHA-256</th></tr>"]
    for table_id, page, row_count, col_count, csv_hash, jsonl_hash in rows:
        body.append(
            f"<tr><td><a href=\"/table?table_id={html.escape(table_id)}\">"
            f"{html.escape(table_id)}</a></td>"
            f"<td>{page}</td><td>{row_count}</td><td>{col_count}</td>"
            f"<td><code>{html.escape(csv_hash[:16])}…</code></td>"
            f"<td><code>{html.escape(jsonl_hash[:16])}…</code></td></tr>"
        )
    body.append("</table>")

    source = conn.execute(
        "SELECT title, manifest_path, manifest_sha256 FROM manual_sources ORDER BY source_id DESC LIMIT 1"
    ).fetchone()

    if source:
        title, manifest_path, manifest_hash = source
        body.append(
            "<h2>Source provenance</h2>"
            f"<p><strong>{html.escape(title)}</strong><br>"
            f"Manifest: <code>{html.escape(manifest_path)}</code><br>"
            f"Manifest SHA-256: <code>{html.escape(manifest_hash)}</code></p>"
        )

    return "\n".join(body)


def table_detail(conn: sqlite3.Connection, table_id: str) -> str:
    table = conn.execute(
        """
        SELECT table_id, pdf_page, row_count, column_count,
               csv_path, jsonl_path, csv_sha256, jsonl_sha256
        FROM manual_tables WHERE table_id = ?
        """,
        (table_id,),
    ).fetchone()

    if not table:
        return "<h2>Table not found</h2>"

    _, page, row_count, col_count, csv_path, jsonl_path, csv_hash, jsonl_hash = table
    rows = conn.execute(
        """
        SELECT row_index, row_json, row_sha256
        FROM manual_table_rows
        WHERE table_id = ?
        ORDER BY row_index
        """,
        (table_id,),
    ).fetchall()

    body = [
        f"<h2>{html.escape(table_id)}</h2>",
        f"<p>PDF page: {page} &middot; Rows: {row_count} &middot; Columns: {col_count}</p>",
        f"<p>CSV: <code>{html.escape(str(csv_path))}</code><br>"
        f"CSV SHA-256: <code>{html.escape(csv_hash)}</code></p>",
        f"<p>JSONL: <code>{html.escape(str(jsonl_path))}</code><br>"
        f"JSONL SHA-256: <code>{html.escape(jsonl_hash)}</code></p>",
        "<table><tr><th>Row</th><th>Content</th><th>Row SHA-256</th></tr>",
    ]

    for row_index, row_json, row_hash in rows:
        record = json.loads(row_json)
        cells = "".join(
            f"<td>{html.escape(str(value))}</td>"
            for key, value in record.items()
            if not key.startswith("_")
        )
        body.append(
            f"<tr><td>{row_index}</td>{cells}"
            f"<td><code>{html.escape(row_hash[:16])}…</code></td></tr>"
        )

    body.append("</table>")
    body.append('<p><a href="/">Back to all tables</a></p>')
    return "\n".join(body)


def search_results(conn: sqlite3.Connection, query: str) -> str:
    body = [f"<h2>Search: {html.escape(query)}</h2>"]

    try:
        rows = conn.execute(
            """
            SELECT table_id, pdf_page,
                   snippet(manual_tables_fts, 2, '[', ']', ' … ', 16)
            FROM manual_tables_fts
            WHERE manual_tables_fts MATCH ?
            LIMIT 50
            """,
            (query,),
        ).fetchall()
    except sqlite3.OperationalError as exc:
        return body.append(f"<p>Search error: {html.escape(str(exc))}</p>") or "\n".join(body)

    if not rows:
        body.append("<p>No matching tables.</p>")

    body.append("<table><tr><th>Table</th><th>Page</th><th>Match</th></tr>")
    for table_id, page, snippet in rows:
        body.append(
            f"<tr><td><a href=\"/table?table_id={html.escape(table_id)}\">"
            f"{html.escape(table_id)}</a></td><td>{page}</td>"
            f"<td>{html.escape(snippet)}</td></tr>"
        )
    body.append("</table>")
    body.append('<p><a href="/">Back to all tables</a></p>')
    return "\n".join(body)


class Handler(BaseHTTPRequestHandler):
    database: Path

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        conn = sqlite3.connect(self.database)

        try:
            if parsed.path == "/":
                title, body = "Tables", table_list(conn)
            elif parsed.path == "/table":
                table_id = params.get("table_id", [""])[0]
                title, body = f"Table {table_id}", table_detail(conn, table_id)
            elif parsed.path == "/search":
                query = params.get("q", [""])[0]
                title, body = "Search", search_results(conn, query)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")
                return

            content = render_page(title, body).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        finally:
            conn.close()

    def log_message(self, fmt, *args):
        print("[ui]", fmt % args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")

    Handler.database = args.db.resolve()
    server = ThreadingHTTPServer((args.host, args.port), Handler)

    print(f"OpenLoom UI: http://{args.host}:{args.port}")
    print(f"Database: {Handler.database}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUI stopped.")


if __name__ == "__main__":
    main()
