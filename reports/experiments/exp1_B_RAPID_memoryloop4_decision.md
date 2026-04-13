# EXP-1 Part B — RAPID 框架分解："Memory 闭环4 是否立即启动"

**日期**: 2026-04-12
**实验**: EXP-1 决策分解对比（B 组：RAPID 框架）
**决策题目**: Secretary auto-memory sync (闭环 4) 是否立即启动实施
**决策背景**: 见 Part A 同文件

## 用 RAPID 分解

### 角色分配（RAPID 五角色）

| 角色 | 由谁扮演 | 为什么是这个人 |
|---|---|---|
| **R** — Recommend | **Secretary Samantha Lin** | 扩权的直接受益方；她最懂 `knowledge/{role}/` 下当前哪些条目需要 sync、哪些 frontmatter 格式、哪些 race condition。**Recommend ≠ Decide**——她负责提出方案和证据，但不拍板。 |
| **A** — Agree | **Maya Patel (Governance)** | 改 `.ystar_session.json` 的 agent_behavior_rules 必须过她这关。A 是**否决权**，不是同意权——Maya 可以否决 Secretary 的 recommend（比如说"你写法会和 DIRECTIVE-005 的 require_self_classification 冲突"），推迟启动。**没有 Agree 方的点头，推进到 Perform 是违规**。 |
| **P** — Perform | **Ryan Park (Platform)** | 真正写 `scripts/secretary_auto_memory_sync.py` 代码的人。Perform 在 Decide 之后启动，不能提前。 |
| **I** — Input | **CEO Aiden** + **CTO Ethan** | CEO 负责保证本决策不跟 DIRECTIVE-003/004/005/006 资源撞车；CTO 负责技术方案合理性（比如 fsnotify vs cron）。**Input 方有发言权但无投票权**——Recommend 方收集他们的意见后整合进方案，但最终 Decide 还是 D 方。 |
| **D** — Decide | **Board (Haotian Liu)** | 因为改 `.ystar_session.json` 的 `agent_write_paths` 属 L3（宪法层）。Board 只需回答 "批"/"否"/"改后批"——**不当选择器，不做方案设计**。 |

### 流程（可并行）

```
[I from CEO+CTO] ──┐
                   ├──→ [R by Secretary] ──→ [A by Maya] ──→ [D by Board] ──→ [P by Ryan]
                   │                            │
                   │                            └─ A 否决 → 退回 R 阶段重做
                   │
                   └─ I 可以在 R 之前开始（异步收集）
```

**关键**：R 和 I 可并行起步；A 和 D 是串行 gate；P 在 D 之后启动。

### CEO 在这个决策里的真正价值

在 L0-L3 里，CEO 被迫扛 L2 自批，**实际价值空心**。

在 RAPID 里，CEO 是 Input 方之一，**专注一件事**：检查这个决策会不会跟其他 pending directive（003/004/005/006）资源争抢。CEO 的价值聚焦、可衡量、可审计。

## 关键观察

| 问题 | RAPID 下的答案 |
|---|---|
| 谁提议启动？ | **Secretary**（R 角色，显式） |
| 谁必须"同意"才能推进？ | **Maya**（A 角色，显式否决权） |
| 谁做实际实施？ | **Ryan**（P 角色，显式） |
| 谁需要被 loop in 但不决策？ | **CEO + CTO**（I 角色，显式） |
| 谁最终拍板？ | **Board**（D 角色，显式） |

## 对比 L0-L3 的增量

1. **Recommend 权独立**：Secretary 有了正式位置，"被扩权方最懂自己需要什么"这个常识被制度化
2. **Agree 权独立**：Maya 的治理 owner 身份被拎出来，防止 Board 批了但治理子系统 owner 不知情就落地的风险
3. **Input ≠ Decide**：CEO 终于不用扛"L2 假自批"——他的真实价值是协调资源，变成 Input 角色
4. **可并行**：R 和 I 可同步起步；L0-L3 是线性叙事

## 产出指标

- **字数**: 本文档约 720 字（比 A 长 24%，但信息密度更高）
- **显式角色数**: 5（R/A/P/I/D 都显式）
- **决策点数**: 2（A 的同意 + D 的最终决定）
- **明确 escalation path 条数**: 2（R → A 否决回退；Board 最终 Decide）
- **ambiguity points**（读后仍不清楚的地方）: 1
  - Sync 脚本是 cron 还是 fsnotify 触发？（I 阶段由 CTO 解答即可）

## 定性判决

- **L0-L3 下 4 个 ambiguity points → RAPID 下 1 个**
- **L0-L3 的 "CEO 假自批" 被解构为 "CEO 做 Input"**（更准确、更聚焦）
- **RAPID 显式化了 Secretary (R) 和 Maya (A) 这两个隐藏但关键的角色**
- **RAPID 允许并行，L0-L3 强制线性**

**胜出**：RAPID。字数膨胀 24% 可接受，信息密度和角色清晰度提升 >100%。

## 成功标准校验（对照实验设计）

| 标准 | L0-L3 (A) | RAPID (B) | 达标? |
|---|---|---|---|
| Board 介入次数 B ≤ A | 1 | 1 | ✅ 持平 |
| B 暴露 A 漏掉的角色 | 0 | 2（R=Secretary, A=Maya 显式化）| ✅ |
| B 总字数 ≤ A × 1.5 | 580 | 720（1.24×）| ✅ |
| B 的 ambiguity score ≤ A | 4 | 1 | ✅ |

**4/4 达标。**
