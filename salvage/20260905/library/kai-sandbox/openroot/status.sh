#!/data/data/com.termux/files/usr/bin/bash
# openroot status — calls out and reports all the numbers
set -e

echo "========================================="
echo "  OPENROOT STATUS — $(date '+%Y-%m-%d %H:%M')"
echo "========================================="
echo ""

# --- DISK ---
echo "[ DISK ]"
df -h ~ | awk 'NR==2{printf "  Home:   %s used / %s total / %s free\n",$3,$2,$4}'
df -h /sdcard 2>/dev/null | awk 'NR==2{printf "  SD:     %s used / %s total / %s free\n",$3,$2,$4}'
df -h /storage 2>/dev/null | awk 'NR==2{printf "  Ext:    %s used / %s total / %s free\n",$3,$2,$4}'
echo ""

# --- GITHUB REPO STATS ---
echo "[ GITHUB: jesseray718/openroot ]"
repo_json=$(gh repo view jesseray718/openroot --json name,visibility,defaultBranchRef,stargazerCount,forkCount,issues,pullRequests,diskUsage)
echo "$repo_json" | jq -r '
  "  Visibility:      \(.visibility)",
  "  Default branch:  \(.defaultBranchRef.name)",
  "  Stars:           \(.stargazerCount)",
  "  Forks:           \(.forkCount)",
  "  Open issues:     \(.issues.totalCount // .issues | if type=="array" then length else . end)",
  "  Open PRs:        \(.pullRequests.totalCount // .pullRequests | if type=="array" then length else . end)",
  "  Repo size (KB):  \(.diskUsage)"
'

echo ""
echo "[ GITHUB: COMMITS ]"
commit_total=$(gh api repos/jesseray718/openroot/commits --jq 'length' 2>/dev/null || echo "?")
echo "  Total commits (recent page): $commit_total"
last_commit=$(gh api repos/jesseray718/openroot/commits/main --jq '.sha[:7] + " — " + .commit.message' 2>/dev/null | head -1)
echo "  Latest commit: $last_commit"
echo ""

echo "[ GITHUB: RELEASES ]"
gh release list --repo jesseray718/openroot 2>/dev/null | head -5
echo ""

echo "[ GITHUB: TAGS ]"
git -C ~/openroot tag -l 2>/dev/null || echo "  (no local tags)"
echo ""

echo "[ GITHUB: BRANCHES ]"
git -C ~/openroot branch -a 2>/dev/null || echo "  (no branches)"
echo ""

# --- TOKEN STATUS ---
echo "[ SECRETS: ~/.openroot-secrets ]"
if [ -f ~/.openroot-secrets ]; then
  grep -q "PASTE_HERE" ~/.openroot-secrets && \
    echo "  ⚠  Tokens still PLACEHOLDER — fill from pinata.cloud + zenodo.org" || \
    echo "  ✓  Tokens appear populated"
else
  echo "  ✗  ~/.openroot-secrets not found"
fi
echo ""

# --- MODELS ON DEVICE ---
echo "[ LOCAL MODELS ]"
for m in /sdcard/termux-data/models/*.gguf /storage/0000-0000/kai_shared/moved_ai-setup/models/*.gguf; do
  [ -f "$m" ] && echo "  $(du -h "$m" | awk '{print $1}')  $m"
done 2>/dev/null || echo "  (none found)"
echo ""

# --- LLAMA.CPP BUILD ---
echo "[ LLAMA.CPP BUILD ]"
if [ -f ~/llama.cpp-fix/bin/llama-cli ]; then
  echo "  ✓  Built — bin/llama-cli exists"
  ls -lh ~/llama.cpp-fix/bin/llama-cli ~/llama.cpp-fix/bin/llama-server 2>/dev/null | awk '{print "     "$NF, $5}'
else
  echo "  ✗  Not built — run cmake+ninja in ~/llama.cpp-fix"
fi
echo ""

echo "========================================="
echo "  END STATUS"
echo "========================================="
