#!/usr/bin/env bash
# Rename "CIEU Five-Tuple" → "CIEU 5-Tuple" in 5 existing agents
# 用法: cd /Users/haotianliu/.openclaw/workspace/ystar-company && bash reports/apply_cieu_rename.sh
set -euo pipefail
cd /Users/haotianliu/.openclaw/workspace/ystar-company
for f in .claude/agents/ceo.md .claude/agents/cto.md .claude/agents/cmo.md .claude/agents/cso.md .claude/agents/cfo.md; do
  sed -i.bak 's/CIEU Five-Tuple Applied to Self/CIEU 5-Tuple Applied to Self/g' "$f"
  echo "RENAMED $f"
done
echo "=== final verify 10 files all count=1 ==="
grep -c "CIEU 5-Tuple Applied to Self" .claude/agents/*.md
echo "=== legacy residual all 0 ==="
grep -c "CIEU Five-Tuple" .claude/agents/*.md || echo "all 0"
