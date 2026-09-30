#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -Eeuo pipefail
shopt -s nullglob

ROOT="${ROOT:-$HOME/openroot}"
CB="$ROOT/context_bridge"
STATE="$ROOT/.tinycrew"
REG="$ROOT/model_registry"
INBOX="$ROOT/lumo_inbox"
OUTBOX="$ROOT/lumo_outbox"
LOG="$STATE/logs"
TS="$(date +%Y%m%d_%H%M%S)"
RUN_ID="tinycrew-$TS"
RUN="$STATE/runs/$RUN_ID"
CANARY="[TINYCREW-SUPERLOOP-$TS]"
LOCK="$STATE/.bootstrap.lock"
TMP=""
EXIT_WRITTEN=0

die() {
  printf '%s [fatal] %s\n' "$CANARY" "$*" >&2
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || die "missing executable: $1"
}

write_exit() {
  local rc="${1:-1}"
  local finished_at
  finished_at="$(date -Is)"

  if [[ "$EXIT_WRITTEN" -eq 0 && -n "${RUN:-}" && -d "$RUN" ]]; then
    cat > "$RUN/exit.json" <<EOF
{
  "run_id": "$RUN_ID",
  "timestamp": "$TS",
  "finished_at": "$finished_at",
  "exit": $rc
}
EOF
    EXIT_WRITTEN=1
  fi
}

cleanup() {
  local rc=$?
  write_exit "$rc"

  if [[ -n "${TMP:-}" && -d "$TMP" ]]; then
    rm -rf "$TMP"
  fi

  exit "$rc"
}

on_error() {
  local rc=$?
  local line="${1:-UNKNOWN}"
  printf '%s [error] line=%s exit=%s\n' "$CANARY" "$line" "$rc" >&2
  exit "$rc"
}

trap cleanup EXIT
trap 'on_error "$LINENO"' ERR

need bash
need python3
need sqlite3
need sha256sum
need grep
need sed
need awk
need find
need flock
need date
need readlink
need cp
need ln
need mkdir
need chmod
need test

[[ -d "$ROOT" ]] || die "repository root absent: $ROOT"

mkdir -p \
  "$CB" \
  "$STATE/runs" \
  "$REG" \
  "$INBOX" \
  "$OUTBOX" \
  "$LOG"

exec 9>"$LOCK"
flock -n 9 || {
  printf '%s [busy] tinycrew bootstrap already running\n' "$CANARY" >&2
  exit 75
}

mkdir -p "$RUN"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/tinycrew-bootstrap.XXXXXX")"

log() {
  printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG/$RUN_ID.log"
}

safe_read_db() {
  local db="$1"
  local label="$2"

  [[ -n "$db" && -f "$db" ]] || return 0

  sqlite3 -readonly "$db" ".tables" > "$RUN/${label}.tables.txt" 2>&1 || true
  sqlite3 -readonly "$db" ".schema" > "$RUN/${label}.schema.sql" 2>&1 || true
  sqlite3 -readonly "$db" "PRAGMA integrity_check;" > "$RUN/${label}.integrity.txt" 2>&1 || true
}

db_exists() {
  local candidate="$1"
  [[ -f "$candidate" || -f "${candidate}-wal" || -f "${candidate}-shm" ]]
}

find_db() {
  local db_name="$1"
  local candidate
  local found=""

  for candidate in \
    "$ROOT/$db_name" \
    "$ROOT/data/$db_name" \
    "$ROOT/state/$db_name" \
    "$ROOT/context_bridge/$db_name" \
    "$ROOT/.state/$db_name"; do
    if db_exists "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  found="$(
    find "$ROOT" -maxdepth 6 -type f -name "$db_name" -print -quit 2>/dev/null || true
  )"

  if [[ -n "$found" && -f "$found" ]]; then
    printf '%s\n' "$found"
  fi
}

part_d_extract() {
  local source="$CB/TINY_CREW_V1.md"
  local destination="$RUN/tinycrew_part_d.md"

  if [[ -f "$source" ]]; then
    sed -n '/^## Part D/,/^## /p' "$source" > "$destination" || true
  fi

  if [[ ! -s "$destination" ]]; then
    cat > "$destination" <<'EOF'
# Tiny Crew Part D

status=UNKNOWN
reason=Part D unavailable or empty at bootstrap time
action=HUMAN_GATE_REQUIRED
EOF
  fi
}

copy_module() {
  local source="$1"
  local destination="$2"

  if [[ -f "$source" ]]; then
    cp -- "$source" "$destination"
    chmod 700 "$destination"
  else
    printf 'ABSENT: %s\n' "$source" > "$destination.absent"
  fi
}

ROUTE_DB="$(find_db route_cache.db || true)"
HARNESS_DB="$(find_db harness_metrics.db || true)"
COMPOST_DB="$(find_db compost_v1.db || true)"
KNOWLEDGE_DB="$(find_db knowledge_base.db || true)"

if [[ -n "$ROUTE_DB" && -f "$ROUTE_DB" ]]; then
  :
else
  ROUTE_DB=""
fi

if [[ -n "$HARNESS_DB" && -f "$HARNESS_DB" ]]; then
  :
else
  HARNESS_DB=""
fi

if [[ -n "$COMPOST_DB" && -f "$COMPOST_DB" ]]; then
  :
else
  COMPOST_DB=""
fi

if [[ -n "$KNOWLEDGE_DB" && -f "$KNOWLEDGE_DB" ]]; then
  :
else
  KNOWLEDGE_DB=""
fi

log "[run] $RUN_ID"
log "[root] $ROOT"
log "[route_db] ${ROUTE_DB:-ABSENT}"
log "[harness_db] ${HARNESS_DB:-ABSENT}"
log "[compost_db] ${COMPOST_DB:-ABSENT}"
log "[knowledge_db] ${KNOWLEDGE_DB:-ABSENT}"

part_d_extract

if command -v ollama >/dev/null 2>&1; then
  ollama list > "$RUN/ollama_list.txt" 2>&1 || true
  ollama ps > "$RUN/ollama_ps.txt" 2>&1 || true
  OLLAMA_STATUS="OBSERVED"
else
  printf 'ollama unavailable\n' > "$RUN/ollama_list.txt"
  printf 'ollama unavailable\n' > "$RUN/ollama_ps.txt"
  OLLAMA_STATUS="UNAVAILABLE"
fi

safe_read_db "$ROUTE_DB" "route_cache"
safe_read_db "$HARNESS_DB" "harness_metrics"
safe_read_db "$COMPOST_DB" "compost"
safe_read_db "$KNOWLEDGE_DB" "knowledge"

find "$ROOT" -maxdepth 6 -type f \
  \( \
    -name 'smart_router.py' -o \
    -name 'turing_tidbits_v1.py' -o \
    -name 'mistake_engine_v1.py' -o \
    -name 'launch_ladder_v1.py' -o \
    -name 'harness_tune_v1.py' -o \
    -name 'agape_vector_index.py' -o \
    -name 'openroot_local_loop_v2.sh' \
  \) \
  -print | sort > "$RUN/existing_organs.txt"

if [[ -f "$ROOT/harness_tune_v1.py" ]]; then
  nl -ba "$ROOT/harness_tune_v1.py" | sed -n '205,255p' > "$RUN/harness_tune_lines_205_255.txt"
else
  printf 'ABSENT: harness_tune_v1.py\n' > "$RUN/harness_tune_lines_205_255.txt"
fi

python3 - \
  "$RUN/ollama_list.txt" \
  "$RUN/roster.json" \
  "$OLLAMA_STATUS" \
  "$TS" <<'PY'
import datetime
import json
import pathlib
import re
import sys

source = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
ollama_status = sys.argv[3]
timestamp = sys.argv[4]

text = source.read_text(encoding="utf-8", errors="replace")
models = []

for raw in text.splitlines():
    line = raw.strip()

    if not line or line.lower().startswith("name"):
        continue

    columns = re.split(r"\s{2,}", line)
    name = columns[0].strip()

    if not name or name.lower() == "ollama":
        continue

    family = re.split(r"[:@]", name.lower(), maxsplit=1)[0]

    models.append(
        {
            "name": name,
            "family": family,
            "status": "observed_unbenchmarked",
            "roles": [],
            "source": "ollama_list",
        }
    )

payload = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "timestamp": timestamp,
    "ollama_status": ollama_status,
    "policy": {
        "unknown_models_are_not_routable": True,
        "producer_grader_must_differ_by_family": True,
        "no_model_downloads": True,
        "no_new_sqlite_databases": True,
    },
    "unknown_slots": {
        "phi_4_grader": "UNKNOWN",
        "tool_tiny": "UNKNOWN",
        "math_tiny": "UNKNOWN",
    },
    "models": models,
}

destination.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

cp -- "$RUN/roster.json" "$REG/roster-$TS.json"
ln -sfn "roster-$TS.json" "$REG/roster-current.json"

python3 - \
  "$RUN" \
  "$ROOT" \
  "$ROUTE_DB" \
  "$HARNESS_DB" \
  "$COMPOST_DB" \
  "$KNOWLEDGE_DB" \
  "$TS" \
  "$RUN_ID" <<'PY'
import datetime
import json
import pathlib
import sys

run = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2])
route_db = sys.argv[3] or None
harness_db = sys.argv[4] or None
compost_db = sys.argv[5] or None
knowledge_db = sys.argv[6] or None
timestamp = sys.argv[7]
run_id = sys.argv[8]

def text_file(name: str, limit: int = 24000) -> str:
    path = run / name
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]

def db_snapshot(path: str | None, prefix: str) -> dict:
    return {
        "path": path,
        "present": bool(path),
        "tables": text_file(f"{prefix}.tables.txt"),
        "schema_excerpt": text_file(f"{prefix}.schema.sql", 12000),
        "integrity": text_file(f"{prefix}.integrity.txt", 4000),
    }

roster = json.loads((run / "roster.json").read_text(encoding="utf-8"))
models = roster.get("models", [])
families = sorted(
    {
        str(model.get("family", "")).strip()
        for model in models
        if str(model.get("family", "")).strip()
    }
)

manifest = {
    "run_id": run_id,
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "timestamp": timestamp,
    "root": str(root),
    "policy": {
        "git_write_forbidden": True,
        "git_commit_forbidden": True,
        "git_push_forbidden": True,
        "main_merge_forbidden": True,
        "model_download_forbidden": True,
        "new_sqlite_database_forbidden": True,
        "new_schema_forbidden": True,
        "new_sha_identity_system_forbidden": True,
        "unknown_model_routing_forbidden": True,
        "producer_grader_same_family_forbidden": True,
        "network_output_must_be_sealed_through_existing_tidbit_path": True,
    },
    "routing_doctrine": [
        "lookup-before-dispatch",
        "store-after-network",
        "instrument-before-builder",
        "never-guess-route",
        "unknown-slot-means-no-route",
        "human-is-the-only-merge-gate",
    ],
    "existing_organs": text_file("existing_organs.txt").splitlines(),
    "database_inventory": {
        "route_cache": db_snapshot(route_db, "route_cache"),
        "harness_metrics": db_snapshot(harness_db, "harness_metrics"),
        "compost": db_snapshot(compost_db, "compost"),
        "knowledge": db_snapshot(knowledge_db, "knowledge"),
    },
    "model_roster": {
        "model_count": len(models),
        "families": families,
        "all_models_observed_unbenchmarked": True,
        "unknown_slots": roster.get("unknown_slots", {}),
    },
    "required_patch_targets": [
        "router_cache_shim_v1.py",
        "smart_router.py",
        "specialist_dispatch_v1.sh",
        "specialist_loop_v1.yml",
    ],
    "required_outputs": [
        "router_cache_shim_v1.py",
        "patched smart_router.py",
        "specialist_dispatch_v1.sh",
        "specialist_loop_v1.yml",
    ],
}

(run / "superloop_manifest.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

cat > "$RUN/PERPLEXITY_BUILD_PROMPT.md" <<PROMPT_EOF
# OpenRoot Tiny Crew Superloop — Implementation Delivery Contract

Repository root:

\`\`\`
$ROOT
\`\`\`

Active run directory:

\`\`\`
$RUN
\`\`\`

Read these evidence artifacts before constructing the deliverable:

\`\`\`
$RUN/superloop_manifest.json
$RUN/roster.json
$RUN/existing_organs.txt
$RUN/route_cache.schema.sql
$RUN/harness_metrics.schema.sql
$RUN/compost.schema.sql
$RUN/knowledge.schema.sql
\`\`\`

## Existing-organ rule

Use only discovered interfaces from existing organs:

\`\`\`
route_cache.db
harness_metrics.db
compost_v1.db
turing_tidbits_v1.py
knowledge_base.db
mistake_engine_v1.py
launch_ladder_v1.py
model_registry
lumo_inbox
lumo_outbox
\`\`\`

No new SQLite database, schema, table, virtual table, index, trigger, cache, SHA identity layer, package, model download, network fetch, Git write, commit, push, merge, branch, checkout, reset, rebase, or tag.

## Required routing ladder

\`\`\`
route_cache.db
-> existing FTS5 lookup when discovered
-> existing embedding lookup when discovered
-> dispatch only on real miss
-> opposing-family grade
-> existing turing tidbit seal path
-> promote verified reusable pathway
\`\`\`

## Mandatory policy

\`\`\`
lookup-before-dispatch
store-after-network
instrument-before-builder
never-guess-route
unknown-slot-means-no-route
human-is-the-only-merge-gate
\`\`\`

- A model absent from \`roster.json\` is UNKNOWN and must not be routed.
- All observed models are unbenchmarked until actual local benchmark evidence is recorded.
- Producer and opposing grader must be different model families.
- Missing database, tidbit, FTS, embedding, RAPL, or metrics interfaces must emit \`UNKNOWN_INTERFACE\` or \`HUMAN_GATE_REQUIRED\`, never invent an interface.
- \`sqlite3.connect(\` is forbidden everywhere except \`router_cache_shim_v1.py\`; there it may only open the discovered existing route-cache path in read-only mode.
- \`hashlib.sha256\` is forbidden as a new identity implementation. Delegate identity/sealing to existing \`turing_tidbits_v1.py\` only when its callable interface is discovered.

## Return exactly two fenced code blocks and no prose

### Block 1 — Unified patch

One unified diff affecting only these paths:

\`\`\`
router_cache_shim_v1.py
smart_router.py
specialist_dispatch_v1.sh
specialist_loop_v1.yml
\`\`\`

The patch must:

- Default to read-only / dry-run operation.
- Never create or mutate SQLite schema.
- Use read-only lookup-first behavior.
- Refuse all UNKNOWN model slots.
- Enforce producer-family != grader-family.
- Emit machine-readable JSON event records.
- Preserve task provenance, selected route, selected model family, cache disposition, timestamp, and human-gate state.
- Contain literal \`CONFIRM=PATCH\`, \`CONFIRM=SUPERLINEAR\`, \`UNKNOWN_INTERFACE\`, and \`HUMAN_GATE_REQUIRED\` decision paths.
- Refuse sealing when the existing tidbit interface is undiscovered.
- Not contain Git-mutating, model-pull, package-install, network-fetch, or remote-execution commands.

### Block 2 — Bash audit script

One complete executable Bash audit script.

The audit script must:

- Use \`set -Eeuo pipefail\`.
- Default to read-only.
- Reject unauthorized paths.
- Reject schema creation/mutation, package installation, model pulls, remote code execution, and Git-mutating commands.
- Reject new \`hashlib.sha256\` identity code.
- Permit \`sqlite3.connect(\` only inside \`router_cache_shim_v1.py\` with visible discovered-path and read-only safeguards.
- Run \`git apply --check\`.
- Require literal \`CONFIRM=PATCH\` to apply a patch.
- Refuse a dirty working tree before application.
- Never create a branch, commit, or push.
- Write a dated report in \`context_bridge/\`.
- End by requiring human review with:

\`\`\`bash
git diff --check
git diff
git status --short
\`\`\`
PROMPT_EOF

cat > "$RUN/task_probe.md" <<'TASK_EOF'
# OpenRoot bounded task probe

Goal:
Read the existing repository interfaces and identify the exact available route-cache,
FTS5, embedding, tidbit-seal, and specialist-routing interfaces without modifying files.

Required output:
- Existing route-cache location, tables, and read-only access path.
- Existing FTS5 tables or explicit UNKNOWN_FTS_INTERFACE.
- Existing embedding interface or explicit UNKNOWN_EMBED_INTERFACE.
- Existing smart-router entrypoint and call sites.
- Existing turing-tidbit seal/ingest callable interface.
- Existing harness metrics table/column candidates.
- A no-write integration plan.

Hard constraints:
- Read only.
- No database/schema changes.
- No model download.
- No package install.
- No Git action.
- No invented interfaces.
TASK_EOF

cat > "$RUN/local_preflight.sh" <<'PREFLIGHT_EOF'
#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -Eeuo pipefail

ROOT="${ROOT:-$HOME/openroot}"
RUN="${RUN:-$(readlink -f "$ROOT/.tinycrew/current")}"
TS="$(date +%Y%m%d_%H%M%S)"
CANARY="[LOCAL-PREFLIGHT-$TS]"
REPORT="$RUN/local_preflight-$TS.md"

[[ -d "$ROOT" ]] || { echo "$CANARY [fatal] root absent: $ROOT" >&2; exit 1; }
[[ -d "$RUN" ]] || { echo "$CANARY [fatal] run absent: $RUN" >&2; exit 1; }

{
  printf '# OpenRoot Local Preflight\n\n'
  printf 'Timestamp: %s\n\n' "$TS"

  printf '## Git state\n\n```\n'
  git -C "$ROOT" status --short || true
  printf '```\n\n'

  printf '## Candidate organs\n\n```\n'
  find "$ROOT" -maxdepth 6 -type f \
    \( \
      -name 'smart_router.py' -o \
      -name 'turing_tidbits_v1.py' -o \
      -name 'router_cache_shim_v1.py' -o \
      -name 'specialist_dispatch_v1.sh' -o \
      -name 'specialist_loop_v1.yml' \
    \) \
    -print | sort
  printf '```\n\n'

  printf '## Route cache / FTS candidates\n\n```\n'
  grep -RInE \
    'route_cache|CREATE[[:space:]]+VIRTUAL[[:space:]]+TABLE.*fts5|fts5\(' \
    --include='*.py' \
    --include='*.sql' \
    --include='*.sh' \
    --include='*.md' \
    "$ROOT" 2>/dev/null | head -n 300 || true
  printf '```\n\n'

  printf '## Tidbit seal candidates\n\n```\n'
  grep -RInE \
    'def .*tidbit|def .*seal|def .*ingest|argparse|__main__|tidbit' \
    --include='turing_tidbits_v1.py' \
    "$ROOT" 2>/dev/null | head -n 300 || true
  printf '```\n\n'

  printf '## Router candidates\n\n```\n'
  grep -RInE \
    'def |class |argparse|route_cache|dispatch|embed|fts|ollama' \
    --include='smart_router.py' \
    "$ROOT" 2>/dev/null | head -n 300 || true
  printf '```\n'
} > "$REPORT"

printf '%s\n' "$CANARY"
printf '[banked] report=%s\n' "$REPORT"
printf '%s [exit=0]\n' "$CANARY"
PREFLIGHT_EOF

cat > "$RUN/README.md" <<README_EOF
# Tiny Crew Superloop Run

Run ID: \`$RUN_ID\`

## Read-only first

\`\`\`bash
cd "$ROOT"
RUN="$RUN"
"$RUN/local_preflight.sh"
cat "$RUN/PERPLEXITY_BUILD_PROMPT.md"
\`\`\`

## Future builder extraction path

\`\`\`bash
cd "$ROOT"
bin/superloop_operator_v1.sh extract /path/to/saved_builder_response.md
bin/superloop_operator_v1.sh audit
bin/superloop_operator_v1.sh inspect
\`\`\`

## Explicit human application gate

\`\`\`bash
cd "$ROOT"
bin/superloop_operator_v1.sh apply
git diff --check
git diff
git status --short
\`\`\`

No bootstrap action creates a database/schema, pulls a model, installs packages,
runs specialist dispatch, modifies Git, creates a branch, commits, pushes, or merges.
README_EOF

copy_module "$ROOT/bin/audit_superloop_patch_v1.sh" "$RUN/audit_superloop_patch_v1.sh"
copy_module "$ROOT/bin/superloop_operator_v1.sh" "$RUN/superloop_operator_v1.sh"
copy_module "$ROOT/bin/extract_two_blocks.py" "$RUN/extract_two_blocks.py"

if [[ -f "$RUN/extract_two_blocks.py" ]]; then
  chmod 700 "$RUN/extract_two_blocks.py"
fi

exec 9>&-

declare -a REQUIRED_ARTIFACTS=(
  "$RUN/roster.json"
  "$RUN/superloop_manifest.json"
  "$RUN/PERPLEXITY_BUILD_PROMPT.md"
  "$RUN/audit_superloop_patch_v1.sh"
  "$RUN/README.md"
  "$RUN/extract_two_blocks.py"
  "$RUN/superloop_operator_v1.sh"
  "$RUN/task_probe.md"
  "$RUN/local_preflight.sh"
)

for artifact in "${REQUIRED_ARTIFACTS[@]}"; do
  [[ -s "$artifact" ]] || die "mandatory artifact absent or empty: $artifact"
done

python3 -m json.tool "$RUN/roster.json" >/dev/null
python3 -m json.tool "$RUN/superloop_manifest.json" >/dev/null
bash -n "$RUN/audit_superloop_patch_v1.sh"
bash -n "$RUN/superloop_operator_v1.sh"
bash -n "$RUN/local_preflight.sh"
python3 -m py_compile "$RUN/extract_two_blocks.py"

sha256sum "${REQUIRED_ARTIFACTS[@]}" > "$RUN/SHA256SUMS"

MANIFEST_SHA="$(sha256sum "$RUN/superloop_manifest.json" | awk '{print $1}')"
ROSTER_SHA="$(sha256sum "$RUN/roster.json" | awk '{print $1}')"
PROMPT_SHA="$(sha256sum "$RUN/PERPLEXITY_BUILD_PROMPT.md" | awk '{print $1}')"
AUDIT_SHA="$(sha256sum "$RUN/audit_superloop_patch_v1.sh" | awk '{print $1}')"

cat > "$RUN/COMPLETE" <<EOF
run_id=$RUN_ID
timestamp=$TS
status=COMPLETE
canary=$CANARY
manifest_sha256=$MANIFEST_SHA
roster_sha256=$ROSTER_SHA
prompt_sha256=$PROMPT_SHA
audit_sha256=$AUDIT_SHA
EOF

ln -sfn "$RUN" "$STATE/current"

write_exit 0

printf '%s\n' "$CANARY"
printf '[banked] tinycrew superloop bootstrap sealed: %s\n' "$RUN"
printf '[banked] sha256 manifest: %s\n' "$MANIFEST_SHA"
printf '[banked] sha256 roster: %s\n' "$ROSTER_SHA"
printf '%s [exit=0]\n' "$CANARY"
