#!/usr/bin/env python3
"""kai_search_v1 — FTS5 search over ingested msgs (kai9000 + relay traffic). Usage: python3 bin/kai_search_v1.py 'query' [limit]"""
import sys, sqlite3
DB = "/home/jesse/openroot/context_bridge/lumo_inbox/ingested.sqlite"

def ensure_fts(conn):
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS msgs_fts USING fts5(
        id UNINDEXED, src UNINDEXED, subject, body,
        content='msgs', content_rowid='rowid')""")
    conn.commit()
    # refresh FTS if row counts drifted
    base = conn.execute("SELECT COUNT(*) FROM msgs").fetchone()[0]
    idx = conn.execute("SELECT COUNT(*) FROM msgs_fts").fetchone()[0]
    if base != idx:
        conn.execute("INSERT INTO msgs_fts(msgs_fts) VALUES('rebuild')")
        conn.commit()
    return base

def main():
    if len(sys.argv) < 2:
        print("usage: python3 bin/kai_search_v1.py 'query terms' [limit]"); sys.exit(1)
    q, limit = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10
    conn = sqlite3.connect(DB)
    total = ensure_fts(conn)
    sql = """SELECT m.src, m.subject, snippet(msgs_fts, 3, '[', ']', '…', 24), m.id
             FROM msgs_fts JOIN msgs m ON m.rowid = msgs_fts.rowid
             WHERE msgs_fts MATCH ? ORDER BY rank LIMIT ?"""
    hits = conn.execute(sql, (q, limit)).fetchall()
    print(f"[gate] '{q}' — {total} docs indexed, {len(hits)} hits")
    for src, subj, snip, mid in hits:
        print(f"\n[{src}] {subj}\n  id={mid}\n  …{snip}…")
    print("[exit=0]"); conn.close()

if __name__ == "__main__":
    try: main()
    except Exception as e:
        import traceback; traceback.print_exc(); sys.exit(1)
