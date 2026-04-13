# L3 修宪提案：把"权限自分级"列为全员硬约束

**提案人**: CEO Aiden
**提交对象**: Board (Haotian Liu)
**Level**: L3（修改 `.ystar_session.json` agent_behavior_rules 全员宪法）
**日期**: 2026-04-12
**Board原话**: "如果你在遇到提出授权的时候，没有自己先自己区分权限就提出，会被deny返回。其他的团队成员也都是一样的"

## 问题陈述

INTERNAL_GOVERNANCE.md 已写明 L0/L1/L2/L3 决策权限层级，但**没有任何 hook/MCP 检查**强制 agent 在请求批准前先做自分级。结果：
- Agent（包括 CEO）习惯性把混合级别的请求打包上交 Board
- Board 被迫做 L1/L2/L3 三种决策，带宽被低层决策吞噬
- 违反 INTERNAL_GOVERNANCE.md "Board 永远不当选择器" 原则

## 提案：硬约束化"权限自分级"

### 新增 agent_behavior_rule：`require_self_classification_before_escalation`

**适用对象**: 全部 agent（CEO/CTO/CMO/CSO/CFO/Secretary/Leo/Maya/Ryan/Jordan + 任何子agent）

**触发条件**: agent 输出包含以下任一关键字时
- "请批准 / 老大批 / Board 裁 / 请确认 / 是否同意"
- "需要授权 / 需要批准 / awaiting approval"
- 对外发起 escalation 的 MCP 调用

**强制要求**: agent 必须**在同一回复内**先输出权限自分级表，格式：

```
| 子任务 | Level | 谁批 |
|---|---|---|
| ... | L0/L1/L2/L3 | Self / CEO / Board |
```

**Hook 检查逻辑**:
- 检查输出是否包含 "Level" + "L0|L1|L2|L3" + 上述触发关键字之一
- 如果触发关键字出现但无自分级表 → DENY，返回 "MISSING_SELF_CLASSIFICATION: 请先按 INTERNAL_GOVERNANCE.md 对子任务分级"
- 检查在 PostToolUse / response 层（不阻塞推理）

### 备选实现路径（反事实推理）

**最优解**：response-level hook 检查（覆盖最全，但需新增 hook 类型）
**次优解**：MCP 层 `gov_escalate` 工具强制要求 self_classification 入参（覆盖 MCP escalate 路径，不覆盖纯文本上交）
**第三优**：在 agent 定义 (.claude/agents/*.md) 加文字提醒，靠 prompt 自律（不是真硬约束，等同没改）

**推荐**: 最优 + 次优 双层（hook 兜底 + MCP 强制结构化）

## 影响范围

- `.ystar_session.json` agent_behavior_rules 增 1 条
- `scripts/_hook_daemon.py` 增 response-level 检查（如选最优）
- `Y-star-gov/ystar/governance/gov_escalate.py` 增 self_classification 入参（如选次优）
- 所有 .claude/agents/*.md 增提醒段落
- governance/INTERNAL_GOVERNANCE.md 增 "Hard-constraint enforcement" 小节交叉引用

## 风险

- 早期可能误伤 agent 正常对话（"请确认" 在日常上下文也常用）→ 缓解：精确化触发 keywords，加 whitelist
- agent 可能用同义词绕过 → 缓解：CIEU 记录此类规避，定期 review 扩充触发词

## 收益

- Board 带宽从"决策机器"回归"战略仲裁"角色
- 团队真正按 INTERNAL_GOVERNANCE.md 运转，治理从纸面走入运行时
- 这是 Y*gov 自身的 dogfooding——把"自决纪律"写进产品，对外 Show HN 时可以说"我们的 governance 强制 agent 不当甩手掌柜"

## Board 决策点

1. 批准新增 `require_self_classification_before_escalation` 硬约束？(Y/N)
2. 选实现路径（最优 / 次优 / 双层）？
3. 授权 Maya 起草具体 .ystar_session.json patch 和 hook 代码？

Board 批准后由 Secretary 走 BOARD_CHARTER_AMENDMENTS 流程，Maya/Ryan 落地实现。
