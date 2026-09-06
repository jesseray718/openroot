pkg install -y jq nodejs termux-api
mkdir -p ~/openroot/archive && chmod 700 ~/openroot/archive
# Secrets: get PINATA_JWT (pinata.cloud free acct → API Keys) and
# ZENODO_TOKEN (zenodo.org → Applications → token w/ deposit scopes)
cat > ~/.openroot-secrets << 'S'
export PINATA_JWT="PASTE_HERE"
export ZENODO_TOKEN="PASTE_HERE"
S
chmod 600 ~/.openroot-secrets
# Conversation in: copy full convo in Claude app, then:
termux-clipboard-get > ~/openroot/archive/conversation.md 2>/dev/null || nano ~/openroot/archive/conversation.md
head -5 ~/openroot/archive/conversation.md  # sanity check