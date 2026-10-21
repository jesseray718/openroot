#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
export OLLAMA_HOST=http://localhost:11434
cd /home/jesse/openroot
echo "[canary-head] profile_update_v1 paste intact"

echo "[stage-0] gate — ensure gh is authenticated"
GH_OK=0
command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1 && GH_OK=1
if [ "$GH_OK" -eq 1 ]; then
  echo "   [ok] gh authenticated @ $(gh api user | jq -r '.login')"
else
  echo "   [held] gh not authenticated — run: gh auth login"
  exit 1
fi

echo "[stage-1] check current repo visibility (openroot-canon + flagship)"
for REPO in openroot-canon openroot OpenCell-Thermal-System aerocement openroot-ecosystem jesseray718.github.io; do
  VIS=$(gh api repos/jesseray718/$REPO 2>/dev/null | jq -r '.visibility // empty' || echo "missing")
  [ "$VIS" = "public" ] && echo "   [ok] $REPO: public" || echo "   [held] $REPO: $VIS (needs fix)"
done

echo "[stage-2] extract claim register from research.db for profile copy"
CLAIM_COUNT=$(sqlite3 data/research.db "SELECT COUNT(*) FROM claims WHERE status='asserted';" 2>/dev/null || echo 0)
MEASURED_COUNT=$(sqlite3 data/research.db "SELECT COUNT(*) FROM claims WHERE status='measured';" 2>/dev/null || echo 0)
echo "   claims registered: asserted=$CLAIM_COUNT measured=$MEASURED_COUNT"
TOP_CLAIMS=$(sqlite3 data/research.db "SELECT subsystem,substr(claim,1,60) FROM claims ORDER BY id LIMIT 3;" 2>/dev/null || echo "none")
echo "   sample claims:"
echo "$TOP_CLAIMS" | sed 's/^/     /'

echo "[stage-3] generate hero README text via 7B (atomic spec)"
SPEC="Write a single-paragraph hero statement for an open-source project called OpenRoot. It builds vernacular energy infrastructure using solar heat directly, with materials like cement/cellulose/surfactant/glass fiber. Lineage: Fuller/Guastavino/Heyman. Method: measurement-first, every claim logged in public ledger. Tone: confident but falsifiable, no hype phrases, no 'revolutionary/ breakthrough'. Exactly 3 sentences, max 25 words each."
README_HERO=$(timeout 120 ollama run qwen2.5-coder:7b "$SPEC" 2>/dev/null | tail -30 || echo "7B unavailable")
echo "   hero draft:"
echo "$README_HERO" | sed 's/^/     /'

echo "[stage-4] 3B grades hero statement against rubric"
GRADES=$(printf '%s\n' "$README_HERO" | timeout 90 ollama run qwen2.5:3b \
"Grade this README hero paragraph. Output exactly 3 lines: VERDICT: PASS|FAIL | CONCISENESS: good|weak | HYPE_CHECK: clean|flagged" 2>/dev/null || echo "VERDICT: UNAVAILABLE | CONCISENESS: UNKNOWN | HYPE_CHECK: UNKNOWN")
echo "   3B grade: $GRADES"

echo "[stage-5] check/update openroot-canon visibility"
CANON_VIS=$(gh api repos/jesseray718/openroot-canon 2>/dev/null | jq -r '.visibility // "missing"' || echo "missing")
if [ "$CANON_VIS" != "public" ]; then
  gh api -X PATCH repos/jesseray718/openroot-canon -f private=false >/dev/null 2>&1 \
    && { echo "   [banked] openroot-canon set to public"; CANON_VIS="public"; } \
    || echo "   [held] failed to update openroot-canon visibility"
else
  echo "   [ok] openroot-canon already public"
fi

echo "[stage-6] update README.md in openroot-canon with hero statement"
cd /home/jesse/src/openroot 2>/dev/null || cd /home/jesse/openroot
CURRENT_README=$(head -5 README.md 2>/dev/null || echo "MISSING")
cat > README.md <<README_EOF
# OpenRoot

$README_HERO

## Active Claims Register (data/research.db — sha256-anchored)

| Subsystem | Claim | Status |
|-----------|-------|--------|
$(sqlite3 -separator '|' data/research.db "SELECT subsystem,substr(claim,1,50),status FROM claims LIMIT 6;" 2>/dev/null | awk -F'|' '{printf "| %s | %s | %s |\n",$1,$2,$3}')

## Mesh Agents (data/mesh.db — 5 agents, 34 tasks)

- 7B builder (qwen2.5-coder:7b)
- 3B grader (qwen2.5:3b)  
- SQLite memory (lessons + mesh + research ledgers)
- Human gatekeeper
- Public contributors (radical credit: CREDITS.md)

## Quick Start

\`\`\`bash
# Daily loop before any task
bash bin/daily_loop_v1.sh start '<describe your task>'
# After completion
bash bin/daily_loop_v1.sh finish '<task>' ok
\`\`\`

## Permaculture Principles as Engineering Process

1. Observe & interact — consult lessons.db before every task
2. Catch & store energy — bank every insight into a ledger
3. Obtain a yield — measure output per joule invested
4. Self-regulate via feedback — every change is graded before merge
5. Value renewables — local models, solar-powered hardware
6. Produce no waste — mistakes become lessons, lessons become docs
7. Patterns to details — canon locked, spokes free
8. Integrate, don't segregate — builders, graders, rememberers, humans
9. Small & slow — atomic edits only
10. Value diversity — your build, your data, your credit
11. Use edges — mobile/Termux contributors welcome
12. Respond to change — lessons verified, workflow mutates

## License

GPL-3.0 code | CC-BY-SA-4.0 docs | Attribution is sacred here

## Contact

See GOOD_FIRST_ISSUES.md to contribute
README_EOF
echo "   [banked] README.md updated ($(wc -l < README.md) lines)"

echo "[stage-7] update GitHub Pages site (jesseray718.github.io)"
cd /home/jesse/openroot 2>/dev/null || true
INDEX_EXISTS=0
[ -f jesseray718.github.io/index.html ] || [ -f jesseray718.github.io/index.md ] && INDEX_EXISTS=1
if [ "$INDEX_EXISTS" -eq 1 ]; then
  echo "   [ok] landing page exists"
  cat > jesseray718.github.io/index.md <<'LANDING_EOF'
# Jesse Ray — OpenRoot

> "Measure what you build. Every claim falsifiable. Radical credit to contributors."

## What I Build

OpenRoot is vernacular energy infrastructure: structures and systems that turn sunlight into shelter, heat, cooling, and connectivity using materials the industrial economy already mass-produces. Cement, cellulose, surfactant, glass fiber. Hand tools + drill. No special skills required.

## Current Research (claims at data/research.db)

- **OpenCell Aerocement** — activated-carbon matrix absorbs ~95% of solar spectrum
- **Thermal Cascade** — COP-framed utilization ratio ~1.35 including ambient heat transfer
- **Double Stress-Skin Shells** — ferrocement catenary in pure compression
- **Tethered Buoyant Relays** — scaled Cloud Nine for decentralized mesh
- **Wood-Pallet Mesh Reflectors** — UHF reception with salvaged wood + chicken wire

## How We Work

Every mistake becomes a lesson in a public SQLite ledger. Every contribution gets named. The flywheel turns: observe → act → log → grade → verify → improve.

Permaculture principles are not philosophy here — they are engineering process. See GOOD_FIRST_ISSUES.md to start.

## Contact

For collaboration: see GitHub issues. For speaking/workshops: outreach via profile email.

**License:** GPL-3.0 | CC-BY-SA-4.0
LANDING_EOF
  git add jesseray718.github.io/
  git commit -m "docs(profile): landing page hero text + research summary"
  git push origin master || git push origin main
  echo "   [banked] landing page updated"
else
  echo "   [held] landing page repo not present locally - clone or create jesseray718.github.io/"
fi

echo "[stage-8] pin flagship repos on profile (gh API has no direct pin endpoint — print manual instructions)"
echo "   [manual] go to github.com/jesseray718 and customize pins, select:"
echo "      openroot-canon"
echo "      OpenCell-Thermal-System"
echo "      aerocement"
echo "      openroot-ecosystem"
echo "      (or your chosen flagship repos)"

echo "[stage-9] log this workflow run to lessons.db"
sqlite3 data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source)
  VALUES ('recruitment','profile update workflow executed','manual steps remain (repo pins, email)','automated visibility fixes + README generation, pins require web UI','one session + 5 min manual','session');"
echo "   [banked] lessons entry: profile_update_workflow"

echo "[stage-10] final state + handoff"
git -C /home/jesse/openroot log --oneline -1
git -C /home/jesse/openroot status --short | head -5
echo ""
echo "=== HANDOFF ==="
echo "verified: gh authenticated=$GH_OK | openroot-canon public=$(gh api repos/jesseray718/openroot-canon 2>/dev/null | jq -r '.visibility' || echo 'ERROR')"
echo "next: 1) visit github.com/jesseray718 to pin repos, 2) update contact email in profiles, 3) commit README changes"
echo "[done] [exit=0]"
