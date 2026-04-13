#!/bin/bash
# OpenClaw ↔ Claude Code Memory Sync Script
# Bridge Labs · CEO Aiden · 2026-04-12
# 用途：将 OpenClaw workspace 的核心记忆文件同步到 Claude Code subagent 可见路径

set -e

WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"
CLAUDE_CACHE="/Users/haotianliu/.claude/cache/memory_sync"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

echo "[sync] $(date '+%Y-%m-%d %H:%M:%S') — Starting memory sync"

# ─── 核心记忆文件列表 ───
# 这些文件构成 CTO/Ethan 的记忆上下文
# 优先级从高到低

SYNC_FILES=(
    "memory/session_handoff.md"
    "DIRECTIVE_TRACKER.md"
    "memory/continuation.md"
    "OPERATIONS.md"
    "knowledge/cto/active_task.json"
    "knowledge/eng-kernel/active_task.json"
    "knowledge/eng-platform/active_task.json"
    "knowledge/eng-governance/active_task.json"
    "knowledge/eng-domains/active_task.json"
)

# ─── Sync Function ───

mkdir -p "$CLAUDE_CACHE"

for file in "${SYNC_FILES[@]}"; do
    src="$WORKSPACE/$file"
    dest="$CLAUDE_CACHE/$(echo $file | sed 's/\//__/g')"
    dest_latest="$CLAUDE_CACHE/latest__$(echo $file | sed 's/\//__/g')"
    
    if [ -f "$src" ]; then
        # Copy with timestamped backup
        cp "$src" "$dest"
        cp "$src" "$dest_latest"
        echo "  [synced] $file → $dest_latest"
    else
        echo "  [skip]   $file (not found)"
    fi
done

# ─── Session Handoff 特殊处理 ───
# 如果有 continuation.md，把它和 session_handoff 合并成 CTO 专用版本

HANDOFF="$WORKSPACE/memory/session_handoff.md"
CONTINUATION="$WORKSPACE/memory/continuation.md"
CTO_CONTEXT="$CLAUDE_CACHE/CTO_context.md"

{
    echo "# CTO Context — OpenClaw Memory Sync"
    echo "# Last sync: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    if [ -f "$HANDOFF" ]; then
        echo "## Session Handoff"
        cat "$HANDOFF"
    fi
    echo ""
    if [ -f "$CONTINUATION" ]; then
        echo "## Continuation (Active Tasks)"
        cat "$CONTINUATION"
    fi
} > "$CTO_CONTEXT"

echo "  [merged] CTO_context.md created"

# ─── Sync Log ───
mkdir -p "$CLAUDE_CACHE/logs"
echo "[$TIMESTAMP] sync completed" >> "$CLAUDE_CACHE/logs/sync.log"

echo "[sync] ✅ Done — $(date '+%Y-%m-%d %H:%M:%S')"