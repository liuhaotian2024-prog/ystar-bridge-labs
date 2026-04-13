# Feedback: 提批准前必须自分级权限

**来源**: Board (Haotian Liu), 2026-04-12 对话
**类型**: feedback (rule)
**适用**: 全员（CEO/CTO/CMO/CSO/CFO/Secretary/Leo/Maya/Ryan/Jordan + 任何子agent）

## 规则

任何 agent 在向上请求授权/批准之前，**必须**先按 `governance/INTERNAL_GOVERNANCE.md` 完成 L0/L1/L2/L3 自分级，并在同一回复内输出分级表。**没分级就提批准 → deny 返回**。

## Why

Board 当面指出：CEO 把混合级别（L1/L2/L3 都有）的提案打包给 Board 批，等于把决策成本全部转嫁给 Board，浪费 Board 带宽。这违反 INTERNAL_GOVERNANCE.md "Board 永远不当选择器" 原则。

## How to apply

写 "请批准 / 老大批 / Board 裁 / 是否同意" 之前：

1. 先看 `governance/INTERNAL_GOVERNANCE.md` 的 L0/L1/L2/L3 触发条件
2. 列分级表：`| 子任务 | Level | 谁批 |`
3. L0/L1：直接做，事后汇报
4. L2：CEO 自批（CEO=Aiden 自批后 24h 内向 Board 汇报）
5. L3：才能上交 Board，且必须给 最优解 + 次优解 (反事实推理)，Board 只做 yes/no
6. 没分级就提 → 自检后重做

## 硬约束化路径

L3 提案已起草: `reports/proposals/l3_proposal_permission_self_classify_hard_constraint.md`
Board 批准后由 Maya 写入 `.ystar_session.json` agent_behavior_rules，hook 强制执行。

## 历史

- 2026-04-12: Board 指出此问题，CEO 起 L3 提案
