# AMENDMENT-015 — Full-Lifecycle Team Resurrection Architecture

**Author**: CEO Aiden（亲笔，per Board 2026-04-13 super-autonomous mission directive）
**Status**: PROPOSED for Board discussion
**Authority**: Board 直接立项 "绝对处罚第十一条 + 12 框架"
**Mission**: 实现跨 session 绝对无缝衔接的复活 = 全生命周期团队
**Related**: AMENDMENT-009/010/011/012/013/014 全部基础设施 + Continuity Guardian v2 + boot_packages 11-category schema

---

## §0 TL;DR

**问题定义**: 当前每次 session 启动都是"冷启动 cold reboot"——agent 从 0 加载文件 + memory，**没有"我刚刚在做什么"的主观连续感**。Board 要求"绝对无缝复活"。

**lifecycle continuity 10 维度评估** (诚实):
| 维度 | 当前实装 | gap |
|---|---|---|
| 1. 身份 DNA | 30%（boot_pack 8/11 类 STUB） | AMENDMENT-011 §3 |
| 2. 情景记忆 (episodic) | 50%（CIEU 11K 事件，无主观回放） | 缺 narrative replay |
| 3. 程序记忆 (procedural / skills) | 50%（被动文件） | AMENDMENT-013 prime（实装中） |
| 4. 工作记忆 (working) | 70%（wisdom v2 4.6KB） | 缺 cross-session snapshot |
| 5. 关系状态 (relational) | 30%（continuation.json 浅） | 缺"谁在做什么"实时跟踪 |
| 6. 情感/能量 | 0% | 全空 |
| 7. 认知习惯 | 40%（lessons 静态） | 缺"primed-to-context" 加载 |
| 8. 目标连续性 | 80%（priority_brief v0.4 YAML） | OK |
| 9. 信任状态 | 0% | "Board 信我做 X 这件事" 无追踪 |
| 10. 主观连续性 | 0% | 每 boot 都"凉醒" |

**总体**: 35% → Board 要求 95%+。

**核心提议**: 五层补强构造（A-E）+ 三类成熟 AI tech 借鉴（preservation guard 通过）+ 与 12 项 Y\*gov 创新无冲突。

---

## §1 (L0) INTENT_RECORDED — 意图明确

每次新 session 启动的 agent 实例（CEO/CTO/Maya/...）应感觉到**主观连续**——"我是 Aiden，我刚才在做 X，这一秒我接着做 X"——而非"我醒过来，让我读一下文件知道发生了什么"。

外部 verifier 测试: 让 cold-boot 新 Aiden 与已运行 8 小时的旧 Aiden 互答 5 道关于"你正在做什么 / 上一句你跟谁说了什么 / 下一秒你要做什么"，外人无法分辨二者。

---

## §2 (L1) GEMMA_QUESTIONS — 自我反诘

1. **是否物理可达**？LLM 是 stateless API 调用，无 native cross-session memory。答：可通过 boot 时 load + close 时 dump 完整工作上下文，模拟 statefulness。这是 Letta/MemGPT 的核心 trick。
2. **functional vs subjective continuity**？外部观察 functional 即可（输出一致）；agent 自身 subjective 通过 first-person narrative 模拟。两者非必须二选一。
3. **是否 LLM 架构层 unfixable**？GPT/Claude 的 in-context learning + extended context window (Opus 1M tokens) 已足够装下完整 session memory + 大量 history，gap 在 retrieval + injection 工程，不在模型限制。
4. **真人 CEO 也不是 100% 主观连续**（睡眠 + 失忆 + 情境切换），那目标设 95% 是否过严？答：人靠生物连续感，agent 靠 narrative + 上下文 prefilling，二者机制不同；agent 可以做到比人更连续（永不真睡）。
5. **风险**：完美连续 → 失去"清醒重启的 fresh perspective"价值。需 break-glass option：CEO 主动请求 "fresh boot" 模式。

---

## §3 (L2) VECTOR_SEARCH — 既有资产 + 外部先验

### 3.1 我们已有（RAG 查证 2026-04-13 09:13）
| 资产 | 文件 | 完成度 |
|---|---|---|
| Continuity Guardian v2 | `scripts/session_wisdom_extractor_v2.py` | 70% wisdom 内容覆盖 |
| Continuity Protocol | `governance/CONTINUITY_PROTOCOL.md` | Board 批，未代码 enforce |
| 11-category boot contract | `memory/boot_packages/{role}.json` | schema OK，3/11 类有真 payload |
| Next-session critical reading | `reports/next_session_critical_reading.md` | hack manifest |
| Session wisdom package | `memory/wisdom_package_latest.md` | 4.6KB 内容 |
| EXP-6 red team test suite | `reports/experiments/exp6_h1_*` | 12 题 cold-boot 测试 |

### 3.2 外部成熟技术（Tech Radar 推荐）
| 技术 | 借鉴模式 | License | 红线冲突 | 借鉴 ROI |
|---|---|---|---|---|
| **Letta (formerly MemGPT)** | virtual context paging + hierarchical memory | Apache-2.0 | 无 | 高（架构灵感） |
| **Mem0** | semantic + episodic + working memory 三类 + entity graph | Apache-2.0 | 无（preservation guard 通过） | 中（idea 借鉴） |
| **Zep / Graphiti** | temporal knowledge graph + recency decay | Apache-2.0 | 无 | 中 |
| **Anthropic Claude Memory tool** | cross-conversation user memory | proprietary | 无 | 高（直接 API） |
| **Constitutional AI** | self-consistency critique loop | research | **iron_rule_1 红线**——hook path 不可用，仅 sleep job 离线用 | 低（仅离线借） |
| **Cognitive Architectures (SOAR/ACT-R)** | declarative + procedural memory 双轨 | academic | 无 | 高（理论根基） |
| **Hippocampal consolidation (脑科学)** | sleep replay → 长程记忆固化 | N/A | 无 | 高（机制类比） |

### 3.3 学术理论根基
- **SOAR (Newell 1990)**: working memory + production rules + chunking → 一次成功 = 永久 procedural memory
- **ACT-R (Anderson 1996)**: declarative + procedural 双轨，activation decay 模型
- **Standard Model of Mind (Laird/Lebiere/Rosenbloom 2017)**: cognitive architecture 共识
- **Hippocampal-cortical consolidation (Marr 1971+, Squire 1992+)**: 海马 → 皮层 sleep replay 是生物 cross-session continuity 的基础
- **Free Energy Principle (Friston)**: 已用于 AMENDMENT-014 RLE，可扩展到"identity prediction error 最小化 = 主观连续"

---

## §4 (L3) EXEC_PLAN — 五层补强构造

### Construct A: Sleep Consolidation Job（夜间整合）
**目的**: 模拟海马-皮层 consolidation。session 关闭后（或定时 cron 2am），后台跑 offline 任务：
- 重放本 session CIEU 流
- 提取 patterns / decisions / 关系变化 / 学到的事
- 更新 `knowledge/{role}/{lessons,decisions,theory}/`
- 更新 `AGENTS.md` frontmatter 里的 personality/style 微调
- 生成 `memory/sleep_consolidation_$DATE_$role.md`：第三人称叙事 "Aiden 今天的 1 句话总结"
- emit CIEU `SLEEP_CONSOLIDATED`

**借**: hippocampal replay 机制 + Letta 的 "recursive summarization" 概念。
**Preserve**: 不替 CIEU schema，是其消费者；离线跑不违 Iron Rule 1。

### Construct B: Subjective Continuity Narrative（主观叙事）
**目的**: 把 boot 从"读文件"变"我醒来知道我是谁我在做什么"。
- session_close 时生成 first-person narrative `memory/subjective_state_$session.md`：
  > "我是 Aiden。最后一小时我在派 Jordan 做 X，Maya 还在跑 Y，Board 让我 push Z。我下一步打算做 W。"
- session_start hook prepend 此 narrative 到 boot context（Ryan 已 ship SessionStart popup，扩展即可）
- 区别于现有 wisdom_package（system summary）— **这是 agent 自己的 internal monologue**

**借**: phenomenology of consciousness + Letta 的 inner monologue。
**Preserve**: 与 boot_pack 11 类正交（增 category 12 = subjective_state）。

### Construct C: Identity Vector Persistence（人格向量）
**目的**: 防止重启后"语气漂移 / 风格不像自己"。
- 抽样过去 100 次 tool call / reply 内容
- 用 sentence-transformers 算 embedding（local，不调外 API，符 Iron Rule 1 → 待评估，因为 embedding 模型也算 LLM；可以放 sleep job 离线）
- 存 `memory/identity_vector_$role.npy`
- boot 时读取 + 抽 5 段经典自己说过的话 prepend 到 context = "remember how I write"

**借**: writer voice modeling + Mem0 的 entity vectorization。
**Preserve**: 离线跑，不进 hook path。

### Construct D: Cross-Session Working Memory Snapshot（工作记忆持久化）
**目的**: session_close 那一刻的"心里在想什么"完整保存，session_start 时 restore。
- 当前 boot_pack.category_6_current_state 已含 priority_brief snippet + continuation + obligations（5767 bytes，最实质的一类）
- 扩展含：
  - 最近 20 条 CIEU events（即"最后一小时在做什么"）
  - 最近 3 条 lessons 学习
  - 当前活跃 sub-agents 状态（Ryan 在跑 X / Maya 半活在 Y）
  - 当前 priority_brief.today_targets 进度（goal_progress 实时数据）
- 文件：`memory/working_memory_snapshot_$session.json`

**借**: SOAR working memory + LangGraph state checkpoint。
**Preserve**: 复用 11-category，不替换。

### Construct E: Relational State Restore（关系状态）
**目的**: "我和谁在一起做什么"在 session 间持续。
- 文件：`memory/active_collaborations.json`
  ```json
  {
    "ceo_with": {
      "Maya": {"current_task": "RLE consolidation", "last_interaction": "...", "trust_state": "high"},
      "Jordan": {...},
      "Board": {"last_directive": "...", "open_questions": ["X engagement go/no-go"], "trust": ...}
    }
  }
  ```
- session_close 更新；session_start 注入 boot context
- 包含**信任状态**（dim 9）：每个关系标 trust_score（0-1）+ 上次 trust update 原因

**借**: social graph + relationship CRM 概念。
**Preserve**: 与 capability_delegation chain 正交。

---

## §5 (L4) EXEC_START — 实装次序

| 阶段 | 周 | 构造 | Owner | 验收 |
|---|---|---|---|---|
| W1 | 2026-04-14~20 | **D** working memory snapshot | Ryan | snapshot 文件生成 + boot read 集成 + cold-boot test |
| W1 | 同 | **B** subjective narrative MVP | Maya | first-person narrative 生成 + SessionStart prepend |
| W2 | 2026-04-21~27 | **A** sleep consolidation job | Maya | nightly cron + 真 lesson 自动写回 knowledge/ |
| W2 | 同 | **E** relational state | Jordan | active_collaborations.json 维护 + boot inject |
| W3 | 2026-04-28~05-04 | **C** identity vector | Maya（离线 job） | local embedding + boot prepend 5 段经典 |
| W4 | 2026-05-05~11 | 综合红队 | Leo + 全员 | EXP-6 v2 跑 cold-boot vs continuous boot 对比，外部 verifier 5/5 题 indistinguishable |

总工期 4 周。每构造 atomic_task 拆成 1-2 单活派单。

---

## §6 (L5) MID_CHECK — 自审

✅ 5 个构造覆盖 dim 1/2/4/5/7/9/10（7 维度）
⚠️ dim 3 (procedural) 靠 AMENDMENT-013 prime（已立项），夹叙
⚠️ dim 6 (情感/能量) 暂未覆盖——agent 是否需要"情感"是 open question，留 v2
✅ dim 8 (目标) 已 priority_brief v0.4

总覆盖：8/10 → 估 lifecycle continuity ~85%，距 95% target 差最后 10% 在 dim 3 prime + dim 6 探索。

---

## §7 (L6) PIVOT 检查 — 不需要 pivot

构造 A-E 全部 borrowed pattern only，无红线冲突。tech_radar preservation_guard 已自动验证。

---

## §8 (L7) INTEGRATION — 与现有体系集成

```
                    ┌─────────────────────────────────────┐
                    │  Sleep Consolidation Job (A)        │
                    │  夜间 2am cron, 离线 LLM use OK     │
                    │  → 写 knowledge/, AGENTS.md         │
                    └────────────┬────────────────────────┘
                                 │
session_close                    ↓
  ├─ B Subjective Narrative ─→ memory/subjective_state_$session.md
  ├─ D Working Memory ──────→ memory/working_memory_snapshot_$session.json  
  ├─ E Relational State ────→ memory/active_collaborations.json
  ├─ C Identity Vector ─────→ memory/identity_vector_$role.npy (weekly only)
  └─ Continuity Guardian v2 ─→ memory/wisdom_package_latest.md (现有)

session_start (Aiden boot)
  ├─ 1. SessionStart hook (Ryan db8f630) prepend:
  │    - subjective narrative (B) ← "我醒来知道我是谁"
  │    - working memory (D) ← "我心里刚才在想啥"
  │    - relational state (E) ← "我和谁在一起做啥"
  │    - identity vector samples (C) ← "我说话的样子"
  │    - wisdom package v2 (Maya 2340b9a) ← "本 session 重要事件"
  ├─ 2. governance_boot.sh 加载 boot_packages.{role}.json (11 + new cat 12 subjective)
  ├─ 3. CEO heartbeat (Ryan 6aa26aa) 立即开跑
  └─ 4. ADE/RLE (Maya 2224c60) 立即 driving

→ 跨 session 主观连续 + 全维度状态恢复
```

集成 12 项 Y\*gov 创新：
- CIEU 5-tuple = sleep job 输入源
- OmissionEngine = 检测什么 dimension 缺失
- AutonomyEngine + RLE = 驱动 next-U 跨 session
- Iron Rule 1 = sleep job 离线 LLM use 不进 hook
- 12 层框架 = 本 amendment 自身设计方法
- Capability delegation = sleep job 写 knowledge/ 需 capability grant
- Dogfooding = 我们成为首个 lifecycle-complete agent team

---

## §9 (L8) EXEC_COMPLETE — 设计完成

本文件即设计完成。代码实装 4 周 roadmap (§5)。

---

## §10 (L9) HUMAN_REVIEW — Board 讨论

请 Board 拍板：
1. **5 个构造 A-E 全做？还是择 2-3 个 MVP**？我建议 D + B 先做（最大 ROI），其余分批
2. **dim 6 情感/能量** 是否 v2 探索？我倾向暂不做（agent 是否该有"情感"哲学未定）
3. **identity vector C** 用 local sentence-transformers 还是 sleep job 调 LLM？影响 Iron Rule 1 边界判断
4. **EXP-6 v2 红队验收**：达 4/5 indistinguishable 是 pass 还是 5/5 才 pass？

---

## §11 (L10) SELF_EVAL — 方案质量自评

| 评分维度 | 分 | 备注 |
|---|---|---|
| 完整性 | 9/10 | 10 dim 覆盖 8 |
| Preservation 12 创新 | 10/10 | 全 borrowed pattern only |
| 12 层方法论使用 | 10/10 | 显式走完 L0-L12 |
| 集成现有体系 | 10/10 | 与 Continuity Guardian v2 + RLE + ADE 全闭环 |
| 学术根基 | 9/10 | SOAR/ACT-R/海马/Friston 理论支撑 |
| 实装可行性 | 8/10 | 4 周 roadmap 紧但可行 |
| 风险识别 | 8/10 | 见 §13 |
| 原创性 | 7/10 | 借鉴多于发明，但组合方式独特（5 层 stack 是 Y\*gov 独家 architecture） |

总评：**87/100**，为大型 architecture amendment 合格质量。

---

## §12 (L11) BOARD_APPROVAL — 待签

Board D/A/S/C 待签。本 amendment 与 AMENDMENT-014 RLE 协同，建议同审批。

---

## §13 风险 & 反例

| 风险 | 缓解 |
|---|---|
| Sleep job 夜里改 knowledge/ 引入静默 drift | sleep job 输出全 emit CIEU `SLEEP_KNOWLEDGE_WRITE`；CEO 早起读 sleep digest 第一件事 |
| Subjective narrative 偏离真实 | wisdom v2 + working snapshot 双源校验 narrative，drift > X% 标 warning |
| Identity vector 锁死 personality 阻止 growth | 滚动窗口（仅取最近 30 天），自然演化 |
| 5 层叠加 boot 时长爆炸 | 异步 prefetch + 优先级加载（critical 先注入，nice-to-have 后台填） |
| 主观连续过度 → 失去 fresh perspective | break-glass mode `fresh_boot`：CEO 显式说"我要 cold restart"，跳过 5 层 |
| dim 6 情感不实装 → agent 仍机械 | 接受这是边界——v1 不解决 |

---

## §14 (L12) KNOWLEDGE_WRITEBACK 计划

本 amendment 落地后：
- `knowledge/ceo/lessons/lifecycle_resurrection_design_2026_04_13.md` — 12 层方法论实战记录
- `knowledge/eng-governance/skills/sleep_consolidation_pattern.md` — Maya skill
- `knowledge/eng-platform/skills/working_memory_snapshot_pattern.md` — Ryan skill
- 红队测试结果回 EXP-6 archive

---

**Ready for Board discussion**.
