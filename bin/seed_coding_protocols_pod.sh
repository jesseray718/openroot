#!/usr/bin/env bash
set -Eeuo pipefail
cd ~/openroot
POD="coding_protocols_pasteable_v1"
SEED_DIR="$(mktemp -d)"
trap 'rm -rf "$SEED_DIR"' EXIT
mkdir -p "$SEED_DIR"/openrouter "$SEED_DIR"/cheatsheets "$SEED_DIR"/installers

fetch_url() {
  local url="$1" out="$2"
  python3 - "$url" "$out" <<'PY'
import sys, urllib.request, re, html
url, out = sys.argv[1], sys.argv[2]
try:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenRoot-pod-seed/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode("utf-8", errors="replace")
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S|re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)
    body = re.sub(r"\s+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    with open(out, "w") as f:
        f.write(f"# Source: {url}\n\n{body.strip()}\n")
    print(f"  ok: {out}")
except Exception as e:
    print(f"  skip: {url} ({e})")
PY
}

for url in "https://openrouter.ai/docs/api-reference/overview" "https://openrouter.ai/docs/api-reference/chat-completion" "https://openrouter.ai/docs/quickstart" "https://openrouter.ai/docs/models" "https://openrouter.ai/docs/credits" "https://openrouter.ai/docs/keys"; do
  name="$(echo "$url" | sed 's|.*/docs/||; s|/|_|g').md"
  fetch_url "$url" "$SEED_DIR/openrouter/$name"
done

cat > "$SEED_DIR/cheatsheets/subprocess_anti_hang.md" <<'MD'
# subprocess.run — anti-hang pattern
## The bug: subprocess.run inherits stdin, child blocks on EOF
## Fix: always pass stdin=subprocess.DEVNULL
MD

cat > "$SEED_DIR/cheatsheets/ssh_config.md" <<'MD'
# ~/.ssh/config — pinned identity with BatchMode=yes
# IdentitiesOnly=yes stops fingerprint leaks, BatchMode=yes prevents hangs
MD

cat > "$SEED_DIR/cheatsheets/cat_eof_pattern.md" <<'MD'
# cat << 'PYEOF' — single-quoted delimiter means no shell expansion
# Safe for Python containing $, backticks, quotes
MD

cat > "$SEED_DIR/cheatsheets/openrouter_404.md" <<'MD'
# OpenRouter 404 — slug retirement recovery
# Parse "use this slug instead:" from error, update DEFAULT_CHAIN
MD

cp -p ~/openroot/bin/packet_query_v1.py "$SEED_DIR/installers/" 2>/dev/null || true

python3 bin/pod_loader_v1.py ingest "$POD" "$SEED_DIR"
python3 bin/pod_loader_v1.py seal "$POD"
python3 bin/pod_loader_v1.py query "$POD" "subprocess hang ssh" --top-k 3 --budget 2000
