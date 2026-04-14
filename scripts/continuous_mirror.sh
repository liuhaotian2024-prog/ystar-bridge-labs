#!/bin/bash
# [L4 SHIPPED] Continuous mirror: ystar-company → ystar-company-test + video → iCloud
# Every 10 min: rsync workspace (skip .git + runtime db)
# Every hour: rsync big video to iCloud

cd /Users/haotianliu/.openclaw/workspace

# Workspace mirror (skip git + runtime artifacts)
rsync -aq --delete \
  --exclude='.git' \
  --exclude='.ystar_cieu*.db*' \
  --exclude='.labs_rag_index.pkl' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  ystar-company/ ystar-company-test/

# Hourly: big video → iCloud
if [ "$(date +%M)" = "00" ]; then
  mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/ystar_backup/
  rsync -aq --delete ystar-company/docs/cogvideo_long ~/Library/Mobile\ Documents/com~apple~CloudDocs/ystar_backup/
  rsync -aq --delete ystar-company/docs/micro_chain_full ~/Library/Mobile\ Documents/com~apple~CloudDocs/ystar_backup/
  rsync -aq --delete ystar-company/content/offended_ai ~/Library/Mobile\ Documents/com~apple~CloudDocs/ystar_backup/
fi
