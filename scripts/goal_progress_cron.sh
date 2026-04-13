#!/usr/bin/env bash
# Goal Progress Dashboard Auto-Refresh
# Run by cron: */15 * * * * /path/to/goal_progress_cron.sh
# Refreshes dashboard every 15 minutes

WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"
cd "$WORKSPACE" || exit 1

# Regenerate dashboard
python3 scripts/goal_progress.py --output reports/goal_progress.md &>/dev/null

# Log refresh
echo "$(date +%Y-%m-%d_%H:%M:%S) Dashboard refreshed" >> logs/goal_progress_cron.log
