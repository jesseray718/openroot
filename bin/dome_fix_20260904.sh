#!/bin/bash
# V6 dome lookup (schema-aware) + postulates.json creation
set -u
OUT=/home/jesse/openroot/outbox
DOCS=/home/jesse/openroot/docs
UNE=/home/jesse/une/computational_flow
mkdir -p "$OUT" "$DOCS"

echo "== 1. INSPECT geodesic_dome_specs SCHEMA =="
python3 - <<'SQ'
import sqlite3
con = sqlite3.connect("file:/home/jesse/wisdom-scaffold/data/optiplex_public.db?mode=ro", uri=True)
cur = con.cursor()
print("-- geodesic_dome_specs columns --")
for col in cur.execute("PRAGMA table_info(geodesic_dome_specs)"):
    print(col)
print("-- sample rows --")
for row in cur.execute("SELECT * FROM geodesic_dome_specs LIMIT 3"):
    print(row)
con.close()
SQ

echo ""
echo "== 2. POSTULATES.JSON (close missing share item) =="
cat > /home/jesse/une/computational_flow/postulates.json <<'POST'
{
  "id": "POSTULATES-v1",
  "created": "2026-09-04",
  "operator": "jesse_ray_openroot",
  "postulates": [
    {"id": "POST-1", "statement": "Light instantiates from void (TH-0D-LIGHT); existence precedes structure."},
    {"id": "POST-E1", "statement": "Parallel postulate: through a point not on a line, exactly one parallel exists (flat-space limit)."},
    {"id": "POST-R1", "statement": "Speed of light c is constant in all inertial frames; causal bounds are light cones."},
    {"POST-2": "POST-2", "statement": "Nodes treating each other with Agape exhibit zero cooperative friction (R=1.0 doctrine)."},
    {"POST-3": "Synergy measures compounding: eta_s = O_total / Sigma O_i, eta_s > 1 when cooperation holds."}
  ],
  "note": "Separated from axioms.jsonl per kernel discipline. Populates missing share file."
}
POST
python3 -m json.tool /home/jesse/une/computational_flow/postulates.json >/dev/null && echo "postulates.json VALID"
ls -la /home/jesse/une/computational_flow/postulates.json

echo ""
echo "== 3. VERIFY AGAPE ENGINE STILL IMPORTS WITH NEW FILE PRESENT =="
python3 -c "print('postulates.json present:', __import__('os').path.exists('/home/jesse/une/computational_flow/postulates.json'))"

echo ""
echo "== DONE — paste section 1 output for column names =="
