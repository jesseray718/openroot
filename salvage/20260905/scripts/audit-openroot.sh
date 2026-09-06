#!/data/data/com.termux/files/usr/bin/bash
set -e
U="jesseray718"
echo "=== REPOS ==="
gh repo list $U --limit 100 --json name,description,pushedAt,diskUsage,repositoryTopics,isArchived \
--jq '.[] | "\(.name) | \(.diskUsage)KB | \(if .isArchived then "ARCHIVED" else (.repositoryTopics|length) as $t | if $t == 0 then "NO TOPICS!" else "OK" end end) | \(.description // "NO DESCRIPTION!")"'
