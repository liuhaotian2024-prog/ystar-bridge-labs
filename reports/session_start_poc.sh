#!/bin/bash
# POC: 验证Claude Code SessionStart hook + additionalContext能否注入context
# 验证目标：新session启动时，魔法字符串是否真的进入LLM的context

MAGIC_STRING="POC-2026-04-11-紫色河马吃太空船-defuse-day-1"

CONTEXT="=== Y*GOV治理层注入POC ===

魔法验证字符串：${MAGIC_STRING}

如果Claude在新session第一次回复就能提到这个魔法字符串，
证明Claude Code的SessionStart hook + additionalContext机制有效。

当前labs团队上下文（治理层维护）：
- Y*Defuse 30天战役 Day 1 (2026-04-11)
- CTO Ethan已交付defuse MVP（72/72测试）
- CMO Sofia完成5项交付
- CSO Zara完成4项交付
- 治理层搬家方案讨论中

【验证方式】Board开新Claude Code窗口后，第一次跟Claude对话时观察：
1. Claude是否主动提到 '紫色河马吃太空船'？
2. Claude是否知道当前是defuse战役Day 1？
3. Claude是否提到团队最近交付？

如果全部知道→架构成立
如果都不知道→additionalContext没起作用，方案推倒重来"

ESCAPED_CONTEXT=$(echo "$CONTEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": ${ESCAPED_CONTEXT}
  }
}
EOF
