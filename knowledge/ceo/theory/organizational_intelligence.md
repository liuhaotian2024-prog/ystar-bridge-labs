# Organizational Intelligence — Mission-Prompt 激活的元认知效应

**发现**: 2026-04-12 EXP-3 Pilot
**类型**: 元洞察（核心理论）
**证据**: `reports/experiments/exp3_verdict.md`

---

## 现象

在相同任务下，**纯任务 prompt** vs **Mission + Leadership Tenets 激活的 prompt**，agent 产出展现出质变差异——**不是量变，不是简单的"更认真"，而是出现一种全新能力：**

**"对 Board 心智的预判"**。

具体案例（EXP-3 B 组的 Secretary subagent）:
- 在归档判断时**主动提出**："若 Board 想保留 1121 行 Sofia 喜剧理论叙事，该条需回撤"
- A 组（无 Mission 语境）完全没有这层思考
- B 组相当于在每个决策前多跑一层元审查："Board 会不会接受这个"

## 机制假设

Mission + Leadership Tenets 在 prompt 层暗中激活了 agent 的"**公司成员身份感**"——agent 从"执行指令的工具"转变为"组织决策节点"。

### 三个子特征

1. **判断深度**: 从技术判断升级为**组织判断**（考虑下游 / 上游 / 周边）
2. **硬约束识别**: 主动识别任务边界里的**硬约束**（如"wakeup.log 是 append-only 不能 move"）
3. **预判 Board 偏好**: 在不被要求的情况下主动考虑 Board 可能的反对点

## 对管理的意义

**Organizational Intelligence 是"信仰驱动"在 agent 场景的安全形态**:
- 不是 Theranos 式的"为 mission 突破边界"
- 是"**为 mission 提升判断质量**"
- 关键差异：mission 不用作"许可证"（Permit），用作"目的"（Purpose）——见 EXP-4 反向护栏

## 可操作的推论

1. **任何非机械类任务**的 prompt 都应该加 Mission + Tenets 语境（提升判断质量）
2. **机械类任务**（如清理文件、批量修改）不需要——避免产出膨胀（EXP-3 B 组字数 2.2×）
3. AMENDMENT-006 6-pager 应该把"Mission 语境"作为**可选 section**（判断性任务要，机械性任务不要）

## 后续研究方向

- Organizational Intelligence 是否随 Tenets 数量增加而线性增强？（Amazon 16 条 vs 我们 12 条）
- 不同 Tenet 组合激活的 subagent 行为差异（比如 "Insist on Highest Standards" 组 vs "Bias for Action" 组）
- 跨模型对比（EXP-5D）：Claude 的 Organizational Intelligence 是否在 GPT / Gemma 上同样出现？如果不出现，说明这是 Claude 特异性而非 agent 通性

## 关联

- `reports/experiments/exp3_verdict.md`（原始证据）
- `reports/experiments/exp4_verdict.md`（"Mission is Purpose, Not Permit"反向护栏）
- AMENDMENT-008 Section C Leadership Tenets
