#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p ~/backups
tar -czf ~/backups/aegis_$DATE.tar.gz ~/aegis ~/start_llm.sh 2>/dev/null
echo "✅ Backup: ~/backups/aegis_$DATE.tar.gz"
