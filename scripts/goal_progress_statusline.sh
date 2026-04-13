#!/usr/bin/env bash
# Goal Progress Statusline — Extract today's average completion %
# Output format: [Goal:37%] with color coding
# Usage: source this from ~/.claude/statusline-command.sh

YSTAR_DIR="$1"

if [ -z "$YSTAR_DIR" ]; then
  YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
fi

if [ ! -f "$YSTAR_DIR/reports/goal_progress.md" ]; then
  exit 0
fi

# Extract first progress bar percentage from "Today" section
today_pct=$(grep "## Today" -A 10 "$YSTAR_DIR/reports/goal_progress.md" 2>/dev/null | \
            grep -o "[0-9]\+%" | head -n 1 | tr -d '%')

if [ -z "$today_pct" ]; then
  exit 0
fi

# Color coding
if [ "$today_pct" -ge 80 ]; then
  printf " \033[1;32m[Goal:%d%%]\033[0m" "$today_pct"
elif [ "$today_pct" -ge 50 ]; then
  printf " \033[1;33m[Goal:%d%%]\033[0m" "$today_pct"
else
  printf " \033[1;31m[Goal:%d%%]\033[0m" "$today_pct"
fi
