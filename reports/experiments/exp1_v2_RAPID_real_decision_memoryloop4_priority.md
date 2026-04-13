# RAPID Pilot v2 — 真实决策运行："闭环4 优先级如何排序"

**实验**: EXP-1 Pilot v2，RAPID 框架跑**真决策**（非纸面对比）
**决策题目**: Memory 闭环 4（Secretary auto-memory sync）在当前 pipeline 里的优先级排序
**决策 Level**: L2（跨岗位协调 + 优先级可逆，CEO Decide）
**批准**: Board 2026-04-12 授权本 pilot

---

## 决策框架

本文件不是一份 brief，是 RAPID 五角色的产出汇总模板。每个角色填自己那段，最后 D 方做决定。

---

## R — Recommend (Secretary Samantha Lin)

**职责**: 提方案和证据。不拍板。

### R.1 方案陈述

Secretary 提出闭环 4 优先级排序建议：

[待 Secretary subagent 填充]

### R.2 证据

- 当前 `knowledge/{role}/` 下 feedback/decisions/lessons 条目数
- Claude harness auto-memory 路径当前状态
- 闭环 4 未上线对今日 session 的实际影响（比如今天 CEO 记的 feedback 因为走 knowledge/ceo/ 没进 auto-memory，下次 session 启动时 prompt 里不会自动出现）

### R.3 备选方案

- 方案 A: 立即启动 (next delivery cycle)
- 方案 B: 排在 DIRECTIVE-003 (Sofia 白皮书 v2) 之后
- 方案 C: 排在 DIRECTIVE-004 (团队整理) 之后
- 方案 D: 先做 P0 架构修复 (DIRECTIVE-006 active_agent 并发) 再启动闭环 4

### R.4 Secretary 的 Recommend

[最终推荐 + 理由]

---

## A — Agree (Maya Patel, Governance)

**职责**: 否决权。推进到 Perform 前必须通过。

### A.1 治理角度审查

- Secretary write_paths 扩权是否与 DIRECTIVE-005（require_self_classification）产生 hook 冲突？
- Secretary write_paths 扩权对 Iron Rule 系列有没有破坏？
- 如果先做闭环 4 再做 DIRECTIVE-006（active_agent 并发），闭环 4 的 sync 动作会不会触发并发 bug 放大？

### A.2 Maya 的判决

- [ ] AGREE — 可推进到 Perform
- [ ] DISAGREE — 退回 R 重做（说明理由）
- [ ] CONDITIONAL — 同意但需要 R 补一些材料

[Maya 具体判决]

---

## P — Perform Plan (Ryan Park, Platform)

**职责**: 实施方案。在 D 决定前先给出 perform plan，让 D 方有信心。

### P.1 技术方案

- `scripts/secretary_auto_memory_sync.py` 草案结构
- 触发方式：cron vs fsnotify vs event-driven (CIEU trigger)
- atomic write + idempotent 保证
- 失败处理: fail-open

### P.2 前置依赖

- L3 扩 Secretary write_paths 必须先落地
- `.ystar_session.json` 该字段修改点

### P.3 Ryan 的工作量估计（用 causal chain depth，不用时间）

- [ ] 本次交付可在 1 个 intent completion 闭环内完成
- [ ] 需要 2-3 个 intent completion 闭环
- [ ] 更深——说明理由

---

## I — Input (CEO Aiden + CTO Ethan)

**职责**: 提供意见，不投票。Recommend 方收集后整合。

### I.1 CEO Aiden 的 Input

#### 资源与优先级视角

当前并发 pending：
- DIRECTIVE-003 Sofia 白皮书 v2（阻塞对外发布）
- DIRECTIVE-004 团队+治理关系整理（阻塞对外发布）
- DIRECTIVE-005 L3 权限自分级（依赖闭环 1，实际可推）
- DIRECTIVE-006 active_agent 并发 BUG（P0，但结构方案已在外部框架调研里——用 STL）
- 闭环 4 本身（待决）

**CEO 视角输入**：

- 对外发布（003+004）是公司战略主线，Phase 1 找客户的前置
- 003+004 要求 Secretary 能写 auto-memory（否则"团队整理"成果无法自动进入下次 session 的 prompt）
- 所以闭环 4 **不是独立优先级**，它是 004 的前置
- 建议：004 启动时一并带闭环 4 作为其技术前置

#### 叙事/品牌视角

- 闭环 4 上线后可以讲"Y\*gov 把 Secretary 的知识蒸馏权限扩展到 Claude Code 原生 auto-memory"——这是 gov-mcp 和 AI harness 生态集成的第一个示范
- 有外部叙事价值，不是纯内部补丁

### I.2 CTO Ethan 的 Input

[CTO subagent 填充]

#### 技术风险视角

- 并发安全：Secretary 的 sync 脚本如果和 CEO/其他 agent 同时在 knowledge/{role}/ 读写，会不会冲突？
- 历史同步 vs 增量同步：首次上线要不要把历史条目一次性 backfill？还是只处理增量？
- auto-memory 格式兼容：Claude harness 对 memory 文件的 frontmatter 格式有硬约束，Secretary 生成的格式必须严格对齐

---

## D — Decide (CEO Aiden, 因为 L2 属 CEO 自决)

**职责**: 看完 R 的推荐 + A 的判决 + P 的可行性 + I 的意见，做 yes/no/modify。

### D.1 决定

[CEO 最终决定]

### D.2 理由（≤100 字）

[决定理由]

### D.3 执行触发

- 谁开工: Ryan（P 角色）+ Secretary（验证）
- 前置条件: [L3 扩权 / 其他]
- 下游通知: Sofia（004 依赖链）、Maya（治理监控）

---

## RAPID 流程审计

| Gate | 状态 | 经手人 | 结论 |
|---|---|---|---|
| R 提方案 | [ ] | Secretary | — |
| A 同意/否决 | [ ] | Maya | — |
| P 给出 plan | [ ] | Ryan | — |
| I 收集完成 | [ ] | CEO + CTO | — |
| D 决定 | [ ] | CEO | — |

**本次 pilot 评估**：

- RAPID 是否让每个角色贡献都清晰可见？
- A 的否决权有没有真的被使用（或潜在会被使用）？
- I 的意见是否真的进入 R 的最终推荐？（不进入就是形式主义）
- D 做决定时有没有被迫替 P 做技术判断（如果是，说明 P 工作没做足）
- 对比用 L0-L3 处理同样决策的假想路径，效率是否真的更高？

这个自评段落与 Secretary/Maya/Ryan/CTO 的实际产出一起，组成 EXP-1 v2 的总结证据。
