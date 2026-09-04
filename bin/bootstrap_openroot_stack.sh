#!/usr/bin/env bash
# Public skeleton only. No *.db, no API keys, no Fuller ingest.
set -euo pipefail
PREFIX="${PREFIX:-$HOME/openroot-stack}"
mkdir -p "$PREFIX"/{bin,data,outbox}

sudo apt-get update -y
sudo apt-get install -y git curl python3 python3-venv sqlite3

# Ollama
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

# Public code
if [ ! -d "$PREFIX/src/openroot" ]; then
  git clone https://github.com/jesseray718/openroot.git "$PREFIX/src/openroot"
fi

python3 -m pip install --user aider-chat 2>/dev/null || true

# Empty public schema (theorems + V1-V3 demo, not 2.5M FTS)
python3 - <<'PY'
import sqlite3, json, os
p = os.path.expanduser(os.environ.get("PREFIX", os.path.expanduser("\~/openroot-stack")) + "/data/optiplex_public.db")
os.makedirs(os.path.dirname(p), exist_ok=True)
c = sqlite3.connect(p)
c.executescript("""
CREATE TABLE IF NOT EXISTS theorem_registry (
  flag_key TEXT PRIMARY KEY,
  domain TEXT, premise TEXT, verdict TEXT, compute_reduction_type TEXT
);
CREATE TABLE IF NOT EXISTS geodesic_dome_specs (
  frequency INTEGER PRIMARY KEY,
  radius_ft REAL, base_sq_ft REAL, total_struts INTEGER,
  unique_strut_types INTEGER, flange_click_type TEXT,
  corrugation_angle TEXT, cut_list_json TEXT
);
""")
c.execute("INSERT OR IGNORE INTO theorem_registry VALUES (?,?,?,?,?)",
          ("[THM-001:TRI_RIGIDITY]","Structural Geometry",
           "Planar 3-strut triangular facets are minimally rigid in R^2.",
           "VERIFIED (Laman Theorem)",
           "Bypasses FEA stiffness matrix recalculation for triangular meshes"))
c.execute("INSERT OR IGNORE INTO geodesic_dome_specs VALUES (?,?,?,?,?,?,?,?)",
          (6, 2.257, 16.0, 1080, 3,
           "Male/Female Snap-Lego Interlock",
           "90° Perpendicular Corrugation",
           json.dumps({"base_side_ft":4.0,"strut_type_lengths_inches":[7.21,7.11,7.02],
                       "wall_thickness_mm":12.0})))
c.commit(); print("db", p)
PY

cat > "$PREFIX/bin/orq" << 'ORQ'
#!/bin/sh
exec python3 - <<'PY' "$@"
import json,sys,urllib.request
cmd=sys.argv[1] if len(sys.argv)>1 else "health"
url="http://127.0.0.1:11434"
if cmd=="health":
    print(urllib.request.urlopen(url+"/api/tags", timeout=5).read()[:200]); raise SystemExit
if cmd=="ask":
    body=json.dumps({"model":"qwen2.5-coder:7b","prompt":" ".join(sys.argv[2:]),"stream":False}).encode()
    req=urllib.request.Request(url+"/api/generate", data=body, headers={"Content-Type":"application/json"})
    print(json.loads(urllib.request.urlopen(req, timeout=120).read())["response"])
PY
ORQ
chmod +x "$PREFIX/bin/orq" "$PREFIX/src/openroot/bin/bootstrap_openroot_stack.sh" 2>/dev/null || true
chmod +x "$PREFIX/bin/orq"
echo "STACK_ROOT $PREFIX"
echo "NEXT ollama serve   then   $PREFIX/bin/orq health"
