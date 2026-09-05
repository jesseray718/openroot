-- OpenRoot kit ledger. stdlib sqlite3. No ORM.
PRAGMA journal_mode=DELETE;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS meta (
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL,
  t TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pane_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  t TEXT NOT NULL,
  pane TEXT NOT NULL CHECK (pane IN ('A15','SSH','UNKNOWN')),
  host TEXT,
  cwd TEXT,
  ok INTEGER NOT NULL DEFAULT 1,
  note TEXT
);

CREATE TABLE IF NOT EXISTS error_pred (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  round INTEGER NOT NULL,
  family TEXT NOT NULL,
  trigger TEXT NOT NULL,
  symptom TEXT NOT NULL,
  fix TEXT NOT NULL,
  severity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tidbit (
  id TEXT PRIMARY KEY,
  module TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  pane TEXT NOT NULL,
  eta_note TEXT,
  created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ssh_session (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  t TEXT NOT NULL,
  target TEXT NOT NULL,
  key_path TEXT,
  rc INTEGER,
  latency_ms INTEGER,
  note TEXT
);

CREATE TABLE IF NOT EXISTS coder_job (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  t TEXT NOT NULL,
  model TEXT,
  endpoint TEXT,
  prompt_hash TEXT,
  tokens_in INTEGER,
  tokens_out INTEGER,
  offline INTEGER NOT NULL DEFAULT 1,
  ok INTEGER NOT NULL DEFAULT 0,
  note TEXT
);

CREATE INDEX IF NOT EXISTS idx_error_round ON error_pred(round);
CREATE INDEX IF NOT EXISTS idx_tidbit_module ON tidbit(module);
