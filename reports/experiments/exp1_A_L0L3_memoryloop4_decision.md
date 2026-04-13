# EXP-1 Part A — L0-L3 框架分解："Memory 闭环4 是否立即启动"

**日期**: 2026-04-12
**实验**: EXP-1 决策分解对比（A 组：现有 L0-L3 框架）
**决策题目**: Secretary auto-memory sync (闭环 4) 是否立即启动实施

## 决策背景（两组共用）

- 闭环 4 目标：把 `knowledge/{role}/feedback|decisions|lessons` 同步到 `~/.claude/projects/<hash>/memory/`
- 阻塞：Secretary `write_paths` 不包含 `~/.claude/.../memory/` 路径
- 外部状态：Board 2026-04-12 当面已原则批准"Secretary auto-memory 写路径扩权"
- 并发任务：DIRECTIVE-003（Sofia 白皮书 v2）、DIRECTIVE-004（团队整理）、DIRECTIVE-005（L3 权限自分级）、DIRECTIVE-006（active_agent 并发）同时 PENDING
- 下游依赖度：**不阻塞** DIRECTIVE-003/004/005/006 任何一个——这几个都不依赖 auto-memory sync

## 用 L0-L3 框架分解

### 步骤 1：CEO 对"是否立即启动"做 Level 判定

触发条件检查：
- 影响 `.ystar_session.json` 的 agent_behavior_rules → **L3（宪法层）**
- 需要 Board 批准 agent_write_paths 修改

### 步骤 2：CEO 起 L3 提案

提案内容：Secretary write_paths 增加 `~/.claude/projects/**/memory/**`

### 步骤 3：Board 批/否

Board 批准后：

### 步骤 4：Secretary 更新 .ystar_session.json

### 步骤 5：Ryan 实现 scripts/secretary_auto_memory_sync.py

### 步骤 6：测试

### 步骤 7：部署

## 关键观察

| 问题 | L0-L3 下的答案 |
|---|---|
| 谁提议启动？ | 隐式——CEO 或 Secretary 先想到的 |
| 谁必须"同意"才能推进？ | **不显式**——L0-L3 只管"谁批"，不管"谁必须同意才能做" |
| 谁做实际实施？ | 隐式——按既往分工推测 Ryan |
| 谁需要被 loop in 但不决策？ | **缺失概念**——L0-L3 没有"Input only"角色 |
| CEO 在这个决策里扮演什么？ | L2 自批 + 对上汇报——**但这是个 L3 决策，CEO 的角色定位变空洞** |
| Secretary 作为"被扩权方"有没有发言权？ | **不在框架里**——她是 Perform 方，但她最懂自己需要什么路径 |

## 暴露的缺陷（CEO 自审）

1. **单轴 4 层压扁了二维关系**：决策权、执行权、推荐权、同意权本来是四条独立轴，被 L0-L3 压成一条"升级阶梯"
2. **Recommend / Input 角色被隐没**：Secretary 作为扩权的受益方应该是 Recommend 角色，在 L0-L3 里她没位置
3. **CEO 被迫"扛一切"**：任何跨岗位 + 可逆就是 L2，CEO 自批——实际上 CEO 在这个决策里既不是最懂需求的（Secretary 更懂），也不是执行者（Ryan 执行），也不是最终 Decide 者（Board）——**CEO 的 L2 自批是假自批，真实价值低**
4. **流程线性顺序**：步骤 1-7 是串行叙事，隐含"CEO 先想 → 提案 → Board 批 → 执行"。没有并行可能。

## 产出指标

- **字数**: 本文档约 580 字
- **显式角色数**: 3（CEO/Board/Secretary 隐性，Ryan 隐性）
- **决策点数**: 2（L 级判定 + Board 批）
- **明确 escalation path 条数**: 1（CEO → Board）
- **ambiguity points**（读后仍不清楚的地方）: 4
  - Secretary 的角色？Perform 还是 Consult？
  - Ryan 什么时候被通知？
  - 如果 Secretary 和 Ryan 对实现有分歧，谁裁？
  - CEO 的"L2 自批"到底批了什么？
