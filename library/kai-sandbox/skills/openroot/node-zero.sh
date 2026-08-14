#!/data/data/com.termux/files/usr/bin/bash
set -e
R=~/openroot; cd $R || { echo "openroot repo missing at ~/openroot"; exit 1; }
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ); D=$(date +%Y%m%d-%H%M)
[ -f archive/genesis-state.env ] && source archive/genesis-state.env

backup(){
  mkdir -p ~/backups
  tar -czf ~/backups/openroot-$D.tar.gz --exclude=backups --exclude=solmemo/node_modules -C ~ openroot
  if [ -d ~/storage/shared ]; then
    mkdir -p ~/storage/shared/OpenRoot-Backups
    cp ~/backups/openroot-$D.tar.gz ~/storage/shared/OpenRoot-Backups/
    ls -t ~/storage/shared/OpenRoot-Backups | tail -n +6 | while read f; do rm -f ~/storage/shared/OpenRoot-Backups/"$f"; done
    echo "Backup stored to corner: /sdcard/OpenRoot-Backups/ (survives Termux reinstall, keeps last 5)"
  else echo "Backup in ~/backups only — grant storage next run for the sdcard corner"; fi
}
[ "$1" = backup ] && { backup; exit 0; }

echo "== P1 storage bridge =="
[ -d ~/storage ] || { termux-setup-storage || true; sleep 2; }

echo "== P2 compaction =="
B4=$(df -h $PREFIX 2>/dev/null | awk 'NR==2{print $4}')
yes | pkg clean >/dev/null 2>&1 || true
apt-get -y autoclean >/dev/null 2>&1 || true
npm cache clean --force >/dev/null 2>&1 || true
pip cache purge >/dev/null 2>&1 || true
AF=$(df -h $PREFIX 2>/dev/null | awk 'NR==2{print $4}')
echo "free before: $B4 → after: $AF"
echo "-- largest items (manual review, nothing auto-deleted):"
du -ah ~ 2>/dev/null | sort -rh | head -6

echo "== P3 canonical tree =="
mkdir -p acre node docs archive backups .github

echo "== P4 ACRE genesis (ledger seed) =="
if [ ! -f acre/GENESIS.json ]; then
cat > acre/GENESIS.json << EOF
{"ledger":"ACRE","seq":0,"timestamp":"$TS",
"founder":"Jesse Ray","github":"github.com/jesseray718","doi":"10.5281/zenodo.20639511",
"mission":"Open-source appropriate technology: maximum good, most people, least effort.",
"minting_rule":"ACRE is minted ONLY upon verified physical work. No premine. Supply at genesis: 0.",
"status":"concept — hash-chained data-structure seed, not a live chain",
"anchors":{"ipfs":"${CID:-pending}","archive_doi":"${DOI:-pending}","solana_tx":"${TX:-pending}"},
"prev":null}
EOF
H=$(sha256sum acre/GENESIS.json | cut -d' ' -f1)
echo "{\"seq\":0,\"type\":\"genesis\",\"sha256\":\"$H\",\"prev\":null,\"ts\":\"$TS\"}" > acre/LEDGER.jsonl
cat > acre/README.md << EOF
# ACRE Ledger (status: concept)
Genesis sha256: \`$H\`
Rule: append-only JSONL; every entry embeds the sha256 of the previous line.
Minting: only for verified physical work. No premine — supply started at 0, publicly, on $TS.
Anchoring: genesis hash rides the next Solana memo (see genesis.sh pattern).
EOF
grep -q "ACRE-GENESIS" BRIDGE.md 2>/dev/null || printf '\nACRE-GENESIS sha256:%s ts:%s\n' "$H" "$TS" >> BRIDGE.md
echo "genesis sha256: $H"
else echo "exists — untouched (immutability starts at home)"; fi

echo "== P5 node zero manifest =="
cat > node/NODE.md << EOF
# Node 0 — OpenRoot Decentralized Web OS (status: in-progress pattern)
Hardware: Samsung Galaxy A15, Termux (cockpit) · Engine: Oracle VM / Codespaces
Identity: github.com/jesseray718 · DOI 10.5281/zenodo.20639511
Services: git (source of truth) · BRIDGE.md (AI context) · ACRE ledger seed · archive anchors (ipfs:${CID:-pending} doi:${DOI:-pending} sol:${TX:-pending})
Topology: phone ⇄ GitHub ⇄ VM(pinner) ⇄ IPFS ⇄ mesh(AEGIS, future)
The OS is the pattern: replicate this manifest = spawn node 1..N.
EOF

echo "== P6 jobsite app kit (F-Droid — tap to install, no root = no auto-install) =="
cat > docs/JOBSITE-APPS.md << 'EOF'
# F-Droid kit, impact-per-effort order
1. Termux:API — https://f-droid.org/packages/com.termux.api  (clipboard/sensors→scripts; required by termux-* cmds)
2. Termux:Widget — https://f-droid.org/packages/com.termux.widget  (home-screen one-tap backup)
3. Termux:Boot — https://f-droid.org/packages/com.termux.boot  (scripts survive reboot; Kai persistence)
4. KeePassDX — https://f-droid.org/packages/com.kunzisoft.keepass.libre  (vault your API tokens/keys)
5. Markor — https://f-droid.org/packages/net.gsantner.markor  (edit repo docs offline between pours)
6. Syncthing-Fork — https://f-droid.org/packages/com.github.catfriend1.syncthingandroid  (phone⇄PC/VM sync, no cloud)
7. Kiwix — https://f-droid.org/packages/org.kiwix.kiwixmobile  (offline Wikipedia/appropriate-tech libraries)
8. Forecastie — https://f-droid.org/packages/cz.martykan.forecastie  (pour-planning weather, no ads)
9. Open Camera — https://f-droid.org/packages/net.sourceforge.opencamera  (timestamped build documentation)
10. Organic Maps — https://f-droid.org/packages/app.organicmaps  (offline maps to sites)
EOF
head -12 docs/JOBSITE-APPS.md

echo "== P7 one-tap widget hook =="
mkdir -p ~/.shortcuts
printf '#!/data/data/com.termux/files/usr/bin/bash\nbash ~/openroot/node-zero.sh backup\n' > ~/.shortcuts/OpenRoot-Backup
chmod +x ~/.shortcuts/OpenRoot-Backup

echo "== P8 backup to the corner =="
backup

echo "== P9 push to GitHub =="
git add -A
git diff --cached --quiet || git commit -m "Node zero: ACRE genesis seed, manifest, app kit, compaction $D"
git push || echo "push failed — no signal? re-run: cd ~/openroot && git push"

echo "== DONE =="
echo "ACRE genesis: acre/GENESIS.json · Node: node/NODE.md · Apps: docs/JOBSITE-APPS.md"
echo "Re-run anytime (idempotent). One-tap backup after installing Termux:Widget."
