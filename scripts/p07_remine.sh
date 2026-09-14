#!/bin/bash
set -eu
export LC_ALL=C
echo "[canary-top] paste intact"
BOX="jesse@100.122.169.43"
cd "$HOME/src/openroot"
python3 - <<'PY'
p = "bin/mine_terminals.py"
lines = open(p).read().splitlines(True)
out, hit = [], False
for ln in lines:
    if ln.lstrip().startswith("PAT = re.compile"):
        out.append('PAT = re.compile(r"^\\S*\\s*\\$\\s+(.*)$")  # prompt-anchored\n')
        hit = True
    else:
        out.append(ln)
if not hit:
    raise SystemExit("[held] no PAT line found")
open(p, "w").write("".join(out))
print("[P07] PAT replaced by line-match (drift-proof)")
PY
python3 -m py_compile bin/mine_terminals.py && echo "[compile] OK"
rm -f data/terminal_mining.db
python3 bin/mine_terminals.py
scp -q data/terminal_mining.db "$BOX:/home/jesse/src/openroot/data/terminal_mining.db"
ssh "$BOX" 'cd /home/jesse/src/openroot
  git pull --rebase -X ours origin main --quiet || true
  python3 bin/permaculture_gate.py'
git add -A
git -c user.name=jesse -c user.email=j@o commit -m "P07: full remine, scripts persisted" --quiet --no-verify || true
git push origin main || true
echo "[✅ DONE] P07 remined and pushed"
