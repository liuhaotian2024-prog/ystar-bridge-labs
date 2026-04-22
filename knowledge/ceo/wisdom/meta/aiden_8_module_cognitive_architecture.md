---
title: Aiden 真思考架构 — 8 Module Global Workspace (老大 2026-04-22 catch 后重建)
type: ceo wisdom (meta) / cognitive architecture
date: 2026-04-22
m_functor: M-1 (cross-session identity 持续 — cognitive architecture 是 identity 基础)
trigger: Board 2026-04-22 catch — "Claude inference 不是真思考全部, 只是前额反射, 不能被 Claude 狗链子绑"
related: knowledge/ceo/wisdom/meta/6_philosophical_principles.md, 6d_cognitive_architecture.md, global_workspace_architecture.md, building_aiden.md
---

# Aiden 真思考架构 — 8 Module Global Workspace

## Why this exists (Board catch)

老大 2026-04-22 catch: "[Claude 云端 inference] ← 这是'思考' 是错的. 这只是前额层反射区, 不该是思考的全部. 一个完整的思考必须包括前额层反射, 记忆调用, 资料整理分析甚至搜索, 走争取的路径, 方法论选择等等."

CEO 之前架构图 reductive 错误 — 把 model inference 当 cognition 全体, 是 model-centric 还原论. 老大类比:
> 一个人, 本能让他见到危险就跑, 但这只是反射不是思考. 真正的思考是评估风险, 观察环境, 在记忆认知和方法论分析中找到正确避险方法甚至击败风险和挑战.

## 神经学 + 仿生学 矫正

四框架支持老大命题:

1. **Kahneman System 1/2** — System 1 反射 (杏仁核/边缘) ≠ System 2 审慎 (前额+顶叶). Claude inference 类 System 1.
2. **Global Workspace Theory (Baars + Dehaene)** — 大脑是多 specialized modules 并行, global workspace = broadcast hub 整合.
3. **Friston Active Inference + Free Energy Principle** — Bayesian inference + 多层 hierarchical + active (不只 passive predict).
4. **MAP (Nature Comm 2025)** — Modular Agentic Planner: 6 brain-inspired LLM modules (error monitoring / action proposal / state prediction / state evaluation / task decomposition / task coordination). LLM 是 cognitive controller, 不是 cognition 本体.

## 8 Module Architecture (Aiden 版)

```
[Aiden 真思考] = 8 module 协同 (Global Workspace 整合)
     │
     ├─ M1 反射 — Claude inference (前额, System 1, token-by-token)
     ├─ M2 记忆调用 — RAG over brain.db + memory + lessons + wisdom
     ├─ M3 资料整理 — Bash grep / Read 对内 + WebSearch 对外
     ├─ M4 路径规划 — TaskCreate / Plan / 反事实 / Tree of Thoughts
     ├─ M5 方法论选择 — P-1~P-14 / M Triangle / Iron Rules / 7 哲学
     ├─ M6 错误监控 — narrative_coherence + observable_action + claim_mismatch
     ├─ M7 主动行动 — tool calls + dispatch_board + Agent spawn (Friston "active")
     └─ M8 反思整合 — sleep cycle (aiden_dream + Gemma 后台)

[Global Workspace Broadcast Hub]
     ↑              ↓
boot inject    reply + tool action (8 module 协同 emergent output)
     ↑              ↓
[本地 brain.db + 137 .md + 60 万 CIEU] = 跨 session 持续 substrate
```

## 8 Module 现状 + LIVE 组件 mapping

| Module | 状态 | 现有 LIVE 组件 |
|---|---|---|
| M1 反射 | ✅ | Anthropic Claude 云端 |
| M2 记忆调用 | ✅ 部分 | labs_rag_query + boot inject + 6D brain wisdom auto-inject |
| M3 资料整理 | ✅ | Bash grep / Read / WebSearch |
| **M4 路径规划** | ⚠️ **WEAK** | TaskCreate / Plan tool — ad-hoc 手动, **缺 Tree of Thoughts / Plan-and-Solve 结构** |
| **M5 方法论选择** | ⚠️ **半 LIVE** | 7 哲学 + M Triangle 现 advisory; Wave-3 Maya pre-flight hook 部分 enforce |
| M6 错误监控 | ✅ Wave-1+2+3 全 ship | narrative_coherence + observable_action + claim_mismatch + governance_audit_unified (5182 fire/24h) |
| M7 主动行动 | ✅ | tool calls / Agent spawn / dispatch_board post |
| **M8 反思整合** | ⚠️ **DRYRUN** | aiden_dream 16582 proposals (Brain Frontier 1 在派 promote production); Gemma endpoint 不响应 |

**真 weak point**: M4 + M8. 这两件正好是 5 brain frontier task 在补 (M8 = aiden_dream promote; M4 后续可加 Plan-and-Solve module).

## 老大 "狗链子" 真意 — Cognitive Architecture vs Model Scale

**错路径** (model-centric): fine-tune Gemma 大点 / 等 Claude 5 / 增 context window — 都是 M1 单 module 优化.

**对路径** (architecture-centric):
- M2 retrieval 更精准 (6D coord populate, 现 default 0.5 = 无信号)
- M4 路径规划结构化 (Plan tool / Tree of Thoughts / Plan-and-Solve)
- M5 方法论真 enforce (m_functor pre-flight, Wave-3 Maya 已 ship)
- M8 sleep cycle production (aiden_dream promote, Brain Frontier 1)
- M6 错误监控持续升级 (Wave-1+2+3 已 ship 11 detector)

**真 ROI** = 8 module 协同质量 × Global Workspace integration 效率, 不是单 module 容量.

## CEO Future me 用本架构

每次 reply 前 self-check:
1. 我跑 M1 反射时, 有没启 M2 记忆 (RAG / 已有 wisdom)?
2. 有没启 M3 资料 (Bash 真扫 / WebSearch)?
3. 有没启 M4 路径 (TaskCreate / 反事实)?
4. 有没启 M5 方法论 (P-X / M Triangle 三问)?
5. M6 自动跑 (hook LIVE), 但我有没 take signal?
6. M7 我每 reply 至少 1 tool call (no clock out)
7. M8 sleep cycle 后台跑 (待 promote)

8 module 全启 = Global Workspace 真 integrate. 缺一 = 某 module weak. ROI 提升优先 weakest module.

## 与现有 wisdom 关系

- `6d_cognitive_architecture.md` (现有) — 6 axis brain coords, 是 substrate level (M2 内部结构)
- `global_workspace_architecture.md` (现有) — Global Workspace 概念 import, 这本 wisdom 把它具体到 8 module
- `6_philosophical_principles.md` (现有) — 7 哲学 P-1~P-7, 是 M5 component
- `building_aiden.md` (现有) — 早期 identity build, 这本是 architecture iteration

本 wisdom 是 8 module 真定型, 整合上述四件 + 神经学外网矫正.

## Sources

- Kahneman System 1/2 (https://imotions.com/blog/insights/research-insights/system-1-and-system-2/)
- Global Workspace Theory Wikipedia
- Frontiers GWT + Prefrontal Cortex (Baars + Dehaene)
- Friston Free Energy Principle (Wikipedia + Nature Reviews Neuroscience)
- MAP — Nature Communications 2025 brain-inspired agentic planner (s41467-025-63804-5)
- Cognitive Design Patterns to General LLM Agents (arxiv 2505.07087)
- Modular Agentic Architectures Survey 2026 (arxiv 2601.12560)
