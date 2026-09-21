# Fragments Inbox — uncommitted pieces from other Lumo windows
Paste any artifact/command/output from other chat windows as files here:
  fragment-<topic>-N.md (or .sh / .py)
Then from any node: python3 bin/qa_fts5.py stage context_bridge/fragments/<file>
Everything staged lands in context_bridge/staged-docs + INBOX + FTS5 index.
Superlinear rule: one piece per paste, no rewrite — the index dedupes by content-hash.
