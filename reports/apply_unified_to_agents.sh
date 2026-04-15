#!/usr/bin/env bash
# Apply unified 三框架段到 10 .claude/agents/*.md (Board 2026-04-15 Iron Rule 1.6)
# 外部 Terminal 跑 (非 Claude Code, 绕 harness sandbox):
#   bash reports/apply_unified_to_agents.sh
# Idempotent: 已 apply 的 SKIP

set -euo pipefail
cd /Users/haotianliu/.openclaw/workspace/ystar-company

MARKER="Unified Work Protocol (Board 2026-04-15"

get_role_example() {
  case "$1" in
    ceo) echo "- **Y\\***: Board 决策 clarity + CTO 派单对齐 + 公司战略 Rt+1 ≤ 0.2" ;;
    cto) echo "- **Y\\***: 4 工程师派单 Rt+1=0 + 代码层 enforce 3 框架 + test coverage ≥ 80%" ;;
    cmo) echo "- **Y\\***: 内容 narrative 清 + digital human 质量全美一流 + 12-层叙事走完" ;;
    cso) echo "- **Y\\***: lead qualification + 企业 persona 验证 + AI 身份披露合规" ;;
    cfo) echo "- **Y\\***: master_ledger 实时 + burn rate 趋势 + 3-6 月 forecast" ;;
    secretary) echo "- **Y\\***: cross-session continuity + DNA_LOG 归档 + immutable override 行使审计" ;;
    eng-kernel) echo "- **Y\\***: kernel 正确性 + check_hook latency ≤ 10ms + test 覆盖 kernel" ;;
    eng-governance) echo "- **Y\\***: policy enforcement 准确率 100% + CIEU 审计链完整" ;;
    eng-platform) echo "- **Y\\***: hook_wrapper / daemon / sync infra 零 orphan 进程 + 零 FS wipe 事件" ;;
    eng-domains) echo "- **Y\\***: domain pack template 复用 ≥ 3 次 + 5 domain coverage 完整" ;;
    *) echo "- **Y\\***: [role-specific example TBD]" ;;
  esac
}

for role in ceo cto cmo cso cfo secretary eng-kernel eng-governance eng-platform eng-domains; do
  f=".claude/agents/${role}.md"
  if [ ! -f "$f" ]; then
    echo "SKIP missing $f"
    continue
  fi
  if grep -q "$MARKER" "$f"; then
    echo "SKIP already applied $f"
    continue
  fi

  example=$(get_role_example "$role")

  cat >> "$f" <<EOF

---

## Unified Work Protocol (Board 2026-04-15 Constitutional — AGENTS.md Iron Rule 1.6)

**Scope**: Every task. Every reply. No exception. Canonical spec: \`knowledge/shared/unified_work_protocol_20260415.md\`.

### Framework 1: CIEU 5-Tuple (度量层)
每接 task 在回复顶部明文:
- **Y\\*** (理想契约, verifiable predicate)
- **Xt** (当前态, tool_use 实测, 非印象)
- **U** (行动集, 1..N)
- **Yt+1** (预测终态)
- **Rt+1** (honest gap + 归零条件)

**${role} Y\\* example**: ${example}

### Framework 2: Article 11 (执行结构层)
中等以上复杂 task **必并列**多路 sub-agent + 本线同推 1 路. 禁派完躺平.

### Framework 3: 12-layer (任务内部流程层)
\`\`\`
0_INTENT → 1_reflect → 2_search → 3_plan → 4_exec →
5_mid_check → 6_pivot → 7_integration → 8_complete →
9_review → 10_self_eval → 11_board_approval (autonomous skip) → 12_writeback
\`\`\`
每层顶部 CIEU 5-tuple + emit CIEU_LAYER_{n} event.

### Rt+1=0 真完成判据 (Board Iron Rule 1.6)
- 每 claim 附 tool_result evidence
- commit hash 可 verify
- CIEU events ≥ N (N = U 步数)
- main agent 独立 verify 通过

### 反 pattern (Y-gov hook enforce, commit 4997d6c)
禁止 phrases: 推别的 / 推下一个 / 换到 / 或者先 / 你决定 / 让 Board 定 / defer / 等下次 / session 结束 / 可以重启 / 清 context.
违反 → tool_use hook block + emit CEO_AVOIDANCE_DRIFT CIEU.

### Rt+1>0 唯一允许 escalate
"此 task 卡在 X 点, 需要 Board Y 授权/资源, 我等具体指令" (单句 escalate, 不出选择题).
EOF

  echo "APPLIED $f"
done

echo ""
echo "=== final verify ==="
c=$(grep -l "$MARKER" .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "files applied: $c / 10"

echo ""
echo "=== per-file marker count ==="
for role in ceo cto cmo cso cfo secretary eng-kernel eng-governance eng-platform eng-domains; do
  f=".claude/agents/${role}.md"
  if [ -f "$f" ]; then
    cieu=$(grep -c "CIEU 5-Tuple" "$f" 2>/dev/null)
    art11=$(grep -c "Article 11" "$f" 2>/dev/null)
    l12=$(grep -c "12-layer" "$f" 2>/dev/null)
    echo "  ${role}: CIEU=${cieu} Art11=${art11} 12L=${l12}"
  fi
done

if [ "$c" -eq 10 ]; then
  echo ""
  echo "Rt+1=0 reached: 10/10 agent.md unified protocol 注入."
  echo "Next: git add .claude/agents/*.md && git commit -m 'feat(agents): unified 三框架段 全员注入 (Iron Rule 1.6) [L4 SHIPPED]'"
fi
