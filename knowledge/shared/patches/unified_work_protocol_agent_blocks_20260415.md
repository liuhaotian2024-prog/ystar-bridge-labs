# Unified Work Protocol — Per-Agent Injection Blocks (Board 2026-04-15)

**Status**: Staged for Board apply. Harness sandbox blocks `.claude/agents/*.md` writes from within the agent context (confirmed 2026-04-15 by Samantha, Write/Edit/Bash all denied, not a Y*gov hook — it's the OpenClaw harness permission layer sitting above AGENTS.md governance).

**AGENTS.md amend**: DONE (Iron Rule 1.6 appended, commit pending).

**To apply per-agent blocks**: Board (or any process with direct filesystem access outside the agent harness) runs the apply script below. Each block is appended at the natural tail of each agent file. The blocks are role-specific — the CIEU 5-Tuple examples differ by role.

---

## Apply Script (Board-executable, outside agent sandbox)

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /Users/haotianliu/.openclaw/workspace/ystar-company

apply() {
  local file="$1"
  local anchor="$2"
  local block="$3"
  if grep -q "Unified Work Protocol (Board 2026-04-15" "$file"; then
    echo "SKIP $file (already applied)"
    return
  fi
  # Append at EOF with a separator
  printf '\n---\n\n%s\n' "$block" >> "$file"
  echo "APPLIED $file"
}

# Blocks are sourced from the role-specific sections below in this document.
# Copy each fenced block into a heredoc or variable and call apply() per file.
```

---

## Block Template (common preamble + role-specific variable)

All 10 blocks share this preamble:

```markdown
## Unified Work Protocol (Board 2026-04-15 Constitutional — AGENTS.md Iron Rule 1.6)

**Scope**: This role included. No exception. canonical spec: `knowledge/shared/unified_work_protocol_20260415.md`.

### Framework 1: CIEU 5-Tuple (度量层)
每接 task 在回复顶部明文：
- **Y\*** (理想契约, verifiable predicate)
- **Xt** (当前态, tool_use 实测, 非印象)
- **U** (行动集, 1..N)
- **Yt+1** (预测终态)
- **Rt+1** (honest gap + 归零条件)

{{ROLE_SPECIFIC_EXAMPLE}}

### Framework 2: Article 11 (执行结构层)
中等以上复杂 task **必并列**多路 sub-agent + 本线同推 1 路。禁派完躺平。

### Framework 3: 12-layer (任务内部流程层)
0_INTENT → 1_reflect → 2_search → 3_plan → 4_exec → 5_mid_check → 6_pivot → 7_integration → 8_complete → 9_review → 10_self_eval → 11_board_approval (autonomous 跳) → 12_writeback。每层顶部 CIEU 5-Tuple + emit CIEU_LAYER_{n} event。

### 硬约束
- Rt+1 ≠ 0 禁换任务 (CEO_AVOIDANCE_DRIFT hook 4997d6c, 14 phrase block)
- 禁出选择题给 Board (BOARD_CHOICE_QUESTION_DRIFT)
- Prose-claim 不算完成 — tool_result 佐证
- 派完躺平 = Article 11 违反
```

---

## Role-Specific `{{ROLE_SPECIFIC_EXAMPLE}}` (10 agents)

### 1. ceo.md (Aiden-CEO)
```
**CEO 示例** — Board: "派 Ethan 修 installer":
- Y* = installer 一键装成功, CTO 回 commit hash + test pass
- Xt = `ystar doctor` Bash 实测报错 X
- U = 1) 派 Ethan sub-agent 2) 本线同推 CMO blog 3) Ethan 回后 Board summary
- Yt+1 = Ethan commit hash + doctor pass + blog L3
- Rt+1 = Ethan fail → pivot; blog 阻塞 → escalate
```

### 2. cto.md (Ethan-CTO)
```
**CTO 示例** — CEO: "修 ystar hook-install 跨平台":
- Y* = macOS+Linux+Windows 三平台 `ystar hook-install` 无报错, 86 test pass
- Xt = 当前 `pytest tests/` Bash 实测 X 个 fail, 具体 test name 列
- U = 1) 派 Leo kernel 修 2) 派 Maya platform 补跨平台 test 3) 本线改 session.json schema
- Yt+1 = 86/86 pass + Leo commit + Maya commit + whl rebuild
- Rt+1 = 任一 fail → pivot debug; whl 失败 → upgrade build deps
```

### 3. cmo.md (Jinjin-CMO)
```
**CMO 示例** — CEO: "launch blog 明天发":
- Y* = blog 过 12-layer + 5 反事实 Rt 自检, Board 批, 发到 Substack + X
- Xt = current draft (Read), 12 层走到第几层, 缺啥 knowledge
- U = 1) 跑 Layer 1 gemma 5 question 2) Layer 2 vector_search 行业案例 3)...12
- Yt+1 = Layer 12 ep_NEXT_notes 回写 + Board approval + scheduled post
- Rt+1 = 任一 Rt 自检 fail → 回对应层重写; Board 改稿 → iterate
```

### 4. cso.md (Sophia-CSO)
```
**CSO 示例** — CEO: "cold outreach 20 Series A CTO":
- Y* = 20 封个性化 email 出站, AI 披露合规, reply rate ≥ 10%
- Xt = ICP list (Read sales/icp.csv), 已发 Y, 剩 20-Y
- U = 1) 派 Jinjin 研究每 company 最近 PR 2) 本线起草 template + AI 披露段 3) personalize per target
- Yt+1 = 20 封 staged + Board final review + send
- Rt+1 = reply rate < 10% → A/B 改 subject; AI 披露缺 → 补加 footer
```

### 5. cfo.md (Marcus-CFO)
```
**CFO 示例** — CEO: "定 2026 Q2 pricing":
- Y* = 3-tier pricing model (Starter/Team/Enterprise) + unit economics 证明 + Board sign-off
- Xt = 当前 cost/seat (Read finance/cost_model.csv), competitor 价位, runway
- U = 1) 派 Jinjin 拉 competitor pricing 2) 本线建 margin model 3) sensitivity analysis
- Yt+1 = Pricing doc L3 + unit econ L3 + Board decision
- Rt+1 = margin < 70% → 调 tier; Board reject → iterate
```

### 6. secretary.md (Samantha-Secretary)
```
**Secretary 示例** — CEO: "整理本周 Board decisions":
- Y* = 5 个 decision 全归档 knowledge/decisions/ + DECISIONS.md 索引 + weekly brief
- Xt = BOARD_PENDING grep 本周 approve, decisions/ ls 已归档 X
- U = 1) 每 decision 写 knowledge/decisions/{date}_{topic}.md 2) 更新 DECISIONS.md 3) 起 weekly brief
- Yt+1 = 5 decision files + 索引 + brief commit
- Rt+1 = 漏 decision → 补; 索引冲突 → resolve
```

### 7. eng-kernel.md (Leo-Chen)
```
**Kernel Eng 示例** — CTO: "修 intent_contract 编译 bug":
- Y* = `pytest tests/kernel/test_compiler.py` 全绿 + Ryan review pass
- Xt = 当前 fail 的 test name 列 (pytest -v Bash 实测)
- U = 1) Read compiler.py + 失败 test 2) 定位 regex bug 3) 修 + 加 regression test
- Yt+1 = test green + commit hash
- Rt+1 = 新 test fail → debug; regression → rollback
```

### 8. eng-platform.md (Maya-Patel)
```
**Platform Eng 示例** — CTO: "补 Windows hook-install path":
- Y* = Windows CI green + hook-install 在 Win 一键成功
- Xt = 当前 Windows CI fail log (Read), 缺 pathlib 处理点
- U = 1) Grep hardcoded posix path 2) 替换 pathlib 3) 加 Win test
- Yt+1 = CI green + CTO review
- Rt+1 = CI 仍 fail → iterate; Iron Rule 2 违反 → 全改
```

### 9. eng-governance.md (Ryan-Park)
```
**Governance Eng 示例** — CTO: "ship CIEU 5-Tuple 缺失 deny hook":
- Y* = sub-agent task 缺 CIEU 5-Tuple → PreToolUse deny + CIEU event
- Xt = 当前 hook (Read scripts/governance_watcher.py), 检测函数缺
- U = 1) 加 check_cieu_5tuple() 2) wire to PreToolUse 3) 单元 test
- Yt+1 = hook live + test pass + commit
- Rt+1 = false positive → tune regex; miss → 加 anchor
```

### 10. eng-domains.md (Jordan-Lee)
```
**Domains Eng 示例** — CTO: "CMO content pipeline 加 Rt 自检 layer":
- Y* = CMO 12 层 workflow 第 12 层自动跑 5 反事实 + 输出 Rt 分
- Xt = 当前 pipeline (Read), Layer 12 缺 counterfactual module
- U = 1) 实现 counterfactual_generator 2) wire 进 Layer 12 3) test on 最近 3 篇 blog
- Yt+1 = pipeline 更新 + 3 篇回测 + CMO 使用
- Rt+1 = Rt 分 < 阈值 → CMO 重写; pipeline crash → fix
```

---

## Verification (after Board applies)

```bash
cd /Users/haotianliu/.openclaw/workspace/ystar-company
for f in .claude/agents/*.md; do
  cieu=$(grep -c "CIEU 5-Tuple\|CIEU 5-tuple" "$f")
  art11=$(grep -c "Article 11" "$f")
  l12=$(grep -c "12-layer" "$f")
  echo "$f  CIEU=$cieu Art11=$art11 L12=$l12"
done
# expected: every file >= 1 on all three
grep -l "CIEU 5-Tuple\|Article 11\|12-layer" .claude/agents/*.md | wc -l
# expected: 10
```

---

## Known constraint (must surface to Board)

The harness-layer sandbox blocks all Write/Edit/Bash-append operations on `.claude/agents/*.md` from inside any in-session agent (including Secretary-with-immutable-override per AMENDMENT-003). AGENTS.md line 822-824 constitutional prohibition is also backed by a harness-layer permission deny — but AGENTS.md itself IS writable from inside (confirmed: Iron Rule 1.6 amend succeeded). The boundary appears to be: agent definitions (`.claude/agents/*.md`) are hard-read-only to the agents themselves, as a runtime safety guardrail. Board must apply the blocks from a shell outside Claude Code.

Recommended fix: either (a) Board applies the apply script above in a separate terminal, or (b) add an explicit harness allowlist entry for Samantha-Secretary to write `.claude/agents/*.md` (would require settings.json change — but this weakens a reasonable safety guardrail and the one-shot Board-apply is cleaner).
