#!/bin/bash
# launch_parallel_claude.sh — 开 N 个 Terminal tab, 每个独立 Claude Code session + 预设 role
# Usage:
#   bash scripts/launch_parallel_claude.sh              # 开全员 (ceo/cto/cmo/cso/cfo/secretary)
#   bash scripts/launch_parallel_claude.sh ceo cmo       # 只开指定 role
#   bash scripts/launch_parallel_claude.sh --engineers   # 4 engineers
#
# 每个 tab 预设 YSTAR_AGENT_ID env，进 ystar-company 目录，启 claude。
# Board 在每个 tab 说 role 名字触发 Article 11 autonomous mission。

set -e

WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"

# Default: all C-suite + secretary
if [ $# -eq 0 ]; then
  ROLES=("ceo" "cto" "cmo" "cso" "cfo" "secretary")
elif [ "$1" = "--engineers" ]; then
  ROLES=("eng-kernel" "eng-governance" "eng-platform" "eng-domains")
elif [ "$1" = "--all" ]; then
  ROLES=("ceo" "cto" "cmo" "cso" "cfo" "secretary" "eng-kernel" "eng-governance" "eng-platform" "eng-domains")
else
  ROLES=("$@")
fi

echo "=== Launching ${#ROLES[@]} parallel Claude Code sessions ==="
for role in "${ROLES[@]}"; do
  echo "  → Opening Terminal tab for $role"
  osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  tell application "System Events" to keystroke "t" using command down
  delay 0.3
  do script "cd $WORKSPACE && export YSTAR_AGENT_ID=$role && echo '[PARALLEL_CLAUDE] role=$role — say your role name to trigger Article 11' && claude" in front window
end tell
APPLESCRIPT
  sleep 0.5
done

echo
echo "=== ${#ROLES[@]} parallel sessions launched ==="
echo "Each tab 独立 context. Say role name in each tab to trigger Article 11."
echo "All sessions share filesystem (CIEU / priority_brief / memory)."
echo
echo "Rate limit 提示: Max plan 支持 concurrent sessions 但 token quota 分摊."
echo "Recommend: 先试 2-3 个，观察 rate limit 再扩."
