# OpenRoot Restructure Plan — CORRECTED (Human-Gated)

## Repository Pins (6 — real repos only)
```
1. openroot — flagship thermal systems + PoPW verification
2. openroot-canon — canonical constitution
3. agapenet — agape-fractal mesh protocol
4. black-locust-rmh — carbon-negative RMH thermal cascade
5. OpenCell-Thermal-System — aerocement absorber engineering
6. und-protocol — offline edge LLM descriptors + Newton Chain
```

## Cleanup Commands (LOW effort, measurable benefit)
```bash
# 1. Untrack bloat (preserves local copies, removes from repo history)
git rm -r --cached attic consolidation-backups
git checkout -- attic consolidation-backups  # restore locally
echo 'attic/* consolidation-backups/*' >> .gitignore
git add .gitignore .git/info/exclude
git commit -m '[FIX] Untrack attic/ and consolidation-backups/ — reduce clone size ~2GB'

# 2. Archive stale repos via gh CLI
gh repo archive AeroCement_Ecosystem --yes
gh repo archive aerocement --yes
gh repo archive open-cell-thermal-loop --yes
gh repo delete skills-introduction-to-github --yes
```

## Spoke Pinning Summary
Spoke repos (agapenet*, fractallattice*, oscillation-mesh*, renaissance-protocol, une, wisdom-scaffold) — do NOT pin, keep discoverable via ecosystem readme.

