#!/data/data/com.termux/files/usr/bin/bash
set -u
export HOME="${HOME:-/data/data/com.termux/files/home}"
SD="/sdcard/openroot"
LOG="\( HOME/openroot/workflow/stage_push_ \)(date +%Y%m%d_%H%M%S).log"
REPORT="\( SD/context_bridge/STAGE_PUSH_REPORT_ \)(date +%Y%m%d_%H%M%S).txt"
mkdir -p "$HOME/openroot/workflow" "$SD/context_bridge" "$SD/ledger" "$SD/session_seeds" "$SD/agape_kb"
exec > >(tee -a "$LOG") 2>&1
echo "=== OPENROOT STAGE+PUSH $(date -Iseconds) HOME=$HOME SD=$SD ==="

DO_NOT_PUSH="firmware LXMF markor MeshCore Reticulum RNode_Firmware tinyGS skills-introduction-to-github civilization2.0 aerocement- open-cell-thermal-open-cell-the AeroCement_Ecosystem renaissance-protocol OpenCell-Thermal-System"

declare -A REMOTE
REMOTE[openroot]=https://github.com/jesseray718/openroot.git
REMOTE[une]=https://github.com/jesseray718/une.git
REMOTE[black-locust-rmh]=https://github.com/jesseray718/black-locust-rmh.git
REMOTE[aerocement]=https://github.com/jesseray718/aerocement.git
REMOTE[agape-une]=https://github.com/jesseray718/agape-une.git
REMOTE[agape-primitives]=https://github.com/jesseray718/agape-primitives.git
REMOTE[agapenet]=https://github.com/jesseray718/agapenet.git
REMOTE[jesseray718]=https://github.com/jesseray718/jesseray718.git
REMOTE[canonical]=https://github.com/jesseray718/canonical.git
REMOTE[und-protocol]=https://github.com/jesseray718/und-protocol.git
REMOTE[wisdom-scaffold]=https://github.com/jesseray718/wisdom-scaffold.git
REMOTE[agape-coordination]=https://github.com/jesseray718/agape-coordination.git
REMOTE[agape-ipfs]=https://github.com/jesseray718/agape-ipfs.git
REMOTE[agape-crossover-key]=https://github.com/jesseray718/agape-crossover-key.git
REMOTE[agaperesonance]=https://github.com/jesseray718/agaperesonance.git
REMOTE[etaledger]=https://github.com/jesseray718/etaledger.git
REMOTE[fractallattice]=https://github.com/jesseray718/fractallattice.git
REMOTE[openroot-spoke-template]=https://github.com/jesseray718/openroot-spoke-template.git
REMOTE[oscillation-mesh]=https://github.com/jesseray718/oscillation-mesh.git

echo "=== HOME GIT TREES ==="
find "$HOME" -maxdepth 3 -type d -name .git 2>/dev/null | sort | while read -r g; do
  d="$(dirname "\( g")"; name=" \)(basename "$d")"
  br="$(git -C "$d" rev-parse --abbrev-ref HEAD 2>/dev/null || echo NONE)"
  url="$(git -C "$d" remote get-url origin 2>/dev/null || echo NO_ORIGIN)"
  dirty="$(git -C "$d" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  echo "HOME $name dirty=$dirty branch=$br origin=$url path=$d"
done

echo "=== SD LIST + GIT (git on SD should be rare) ==="
ls -la "$SD" 2>/dev/null || echo "MISSING $SD"
find "$SD" /sdcard /storage/emulated/0 -maxdepth 4 -type d -name .git 2>/dev/null | sort

echo "=== SD DIMENSION CANDIDATES ==="
find "$SD" /sdcard/Documents /storage/emulated/0/Documents -maxdepth 5 \( \
  -iname '*dimension*' -o -iname '*drawing*' -o -iname '*spec*' \
  -o -iname '*blueprint*' -o -iname '*rmh*' -o -iname '*dome*' \
  -o -iname '*micro-node*' -o -iname '*micronode*' -o -iname '*measure*' \
  -o -iname '*.dxf' -o -iname '*.svg' -o -iname '*BOM*' \) 2>/dev/null | head -200

echo "=== ENSURE ORIGIN ON EXISTING CLONES (will not clone missing) ==="
for name in "${!REMOTE[@]}"; do
  dest="$HOME/\( name"; url=" \){REMOTE[$name]}"
  if [ ! -d "$dest/.git" ]; then echo "MISSING $dest"; continue; fi
  cur="$(git -C "$dest" remote get-url origin 2>/dev/null || true)"
  if [ -z "$cur" ]; then git -C "$dest" remote add origin "$url"; echo "ADDED origin $name"; else echo "OK $name $cur"; fi
done

route_copy() {
  src="$1"; dest_repo="$2"; rel="$3"
  [ -e "$src" ] || return 0
  mkdir -p "$(dirname "$HOME/$dest_repo/$rel")"
  if [ -d "$src" ]; then mkdir -p "$HOME/$dest_repo/$rel"; cp -an "$src"/. "$HOME/$dest_repo/$rel"/ 2>/dev/null || true
  else cp -an "$src" "$HOME/$dest_repo/$rel" 2>/dev/null || true; fi
  echo "ROUTED $src -> $HOME/$dest_repo/$rel"
}

for p in "$SD/dimensions" "$SD/drawings" "$SD/research" "$SD/black-locust-rmh" "$SD/rmh" "$SD/dome" "$SD/aerocement" "$SD/micro_node" "$SD/micronode"; do
  [ -e "$p" ] || continue
  base="$(basename "$p")"
  case "$base" in
    black-locust-rmh|rmh) route_copy "$p" black-locust-rmh "from_sd/$base" ;;
    aerocement) route_copy "$p" aerocement "from_sd/$base" ;;
    *) route_copy "$p" openroot "from_sd/$base" ;;
  esac
done

while IFS= read -r f; do
  [ -f "$f" ] || continue
  bn="$(basename "$f" | tr 'A-Z' 'a-z')"
  case "$bn" in
    *rmh*|*rocket*|*locust*|*thermal_cascade*) route_copy "\( f" black-locust-rmh "from_sd/ \)(basename "$f")" ;;
    *aero*|*gfrc*|*mix*|*foam*) route_copy "\( f" aerocement "from_sd/ \)(basename "$f")" ;;
    *dimension*|*drawing*|*blueprint*|*dome*|*labyrinth*|*micro-node*|*micronode*)
      route_copy "\( f" openroot "from_sd/dimensions/ \)(basename "$f")" ;;
  esac
done < <(find "$SD" -maxdepth 3 -type f \( -iname '*dimension*' -o -iname '*drawing*' -o -iname '*blueprint*' -o -iname '*rmh*' -o -iname '*dome*' -o -iname '*aero*' -o -iname '*micro-node*' -o -iname '*micronode*' -o -iname '*.md' -o -iname '*.svg' -o -iname '*.dxf' \) 2>/dev/null | head -300)

push_one() {
  name="$1"; dest="$HOME/$name"
  [ -d "$dest/.git" ] || { echo "SKIP $name no clone"; return 0; }
  case " $DO_NOT_PUSH " in *" $name "*) echo "REFUSE $name"; return 0 ;; esac
  echo "---- $name ----"
  gi="$dest/.gitignore"; touch "$gi"
  for pat in .ssh '*.pem' '*.key' '*.gguf' '*.bin' __pycache__ '*.pyc' '.syncthing.*.tmp' ENDOF* session_seeds ledger/live context_bridge/context.json; do
    grep -qxF "$pat" "$gi" 2>/dev/null || echo "$pat" >> "$gi"
  done
  git -C "$dest" add -A
  git -C "$dest" reset -q -- '*.pem' '*.key' id_rsa id_ed25519 .ssh '*.gguf' '*.safetensors' 2>/dev/null || true
  if git -C "$dest" diff --cached --quiet; then echo "CLEAN $name"
  else git -C "$dest" commit -m "stage: route local + SD-owned artifacts into $name $(date +%Y-%m-%d)"; echo "COMMITTED $name"; fi
  git -C "$dest" status -sb
}

for name in "${!REMOTE[@]}"; do push_one "$name"; done

auth_ok=0
command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1 && auth_ok=1
[ -f "$HOME/.ssh/id_ed25519" ] || [ -f "$HOME/.ssh/id_rsa" ] && auth_ok=1
if [ "$auth_ok" -eq 1 ]; then
  for name in "${!REMOTE[@]}"; do
    dest="$HOME/$name"; [ -d "$dest/.git" ] || continue
    case " $DO_NOT_PUSH " in *" $name "*) continue ;; esac
    br="$(git -C "$dest" rev-parse --abbrev-ref HEAD)"
    echo "PUSH $name $br"
    git -C "$dest" push -u origin "$br" || echo "PUSH FAIL $name"
  done
else
  echo "NO AUTH — commits local only. Next: pkg install gh && gh auth login"
fi

{ echo "STAGE_PUSH $(date -Iseconds)"; echo "HOME=$HOME SD=$SD"; find "$HOME" -maxdepth 3 -type d -name .git | sort; echo "LOG $LOG"; } > "$REPORT"
echo "REPORT $REPORT"
echo "LOG $LOG"
echo "DONE"
