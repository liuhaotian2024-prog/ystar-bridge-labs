#!/bin/bash
# [L2→L3] WIP Auto-Commit — Prevent work-in-flight evaporation
# Cron: */10 * * * * (every 10 minutes)

set -euo pipefail

WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"
cd "$WORKSPACE"

# Check if there are uncommitted changes in governance-critical directories
if [ -n "$(git status --porcelain scripts/ governance/ .claude/ 2>/dev/null)" ]; then
    git add scripts/ governance/ .claude/
    git commit -m "auto: WIP snapshot $(date +%H:%M) [L2 IMPL]" 2>/dev/null || true
    echo "[$(date)] WIP auto-committed"
else
    echo "[$(date)] No WIP changes"
fi
