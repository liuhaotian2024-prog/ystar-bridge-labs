---
title: Y\* Field Theory — Mission Functor Field as Cognitive Architecture
author: ceo (Aiden)
date: 2026-04-22
maturity: L1 SPEC (strategic — Board 命题 → 形式化)
m_functor: M-1 (Survivability — 跨 session/agent 的 mission alignment 持续) + M-2 (Governability — Y\* 场 enforce as anti-drift) + M-3 (Value Production — 公开方法论)
status: spec → Wave-2 candidate (Wave-1 完成后落)
related: Section 11 (CEO Binding Semantics), HiAgent CZL subgoals model
board_quote: "Y\* 是终极使命 Y\*_M 的一个泛函实现, 形成一个使命 Y\* 的场. 这既是行为目标的泛函化, 也是所有人的大脑的一个增强实现. 我们的最核心就是实现 Y\* 的普遍实现来通过五元组的 Rt+1=0 的方式来决定所有行为 U."
---

# Y\* Field Theory

## 0. Board 命题 (2026-04-22 原话)

> "Y\* 是终极使命 Y\*_M 的一个泛函实现, 形成一个使命 Y\* 的场. 这既是一个行为目标的泛函化, 也是所有人的大脑的一个增强实现. 我们的最核心就是实现 Y\* 的普遍实现来通过五元组的 Rt+1=0 的方式来决定所有行为 U."

老大同时怀疑: "我们是否真的实现了这一个链路, 是否真的在每次行动里都有明确的 Y\*?"

CEO 立刻诚实回答: **没有真正实现**. 当前是叙事级 alignment, 不是结构级.

## 1. 现状诊断 — HiAgent 链路是叙事不是结构

| 元素 | 现状 | 是否结构强制 alignment to M? |
|---|---|---|
| 5-tuple Y\* (free text) | ✅ 已用 | ❌ 无 schema 强制 M-projection |
| CZL atomic_id | ✅ 已用 | ❌ atomic_id ≠ functor, 与 M 关系靠命名 + 叙事 |
| `.czl_subgoals.json` | ✅ per-session live | ❌ subgoal text, 无 functor 链回 M |
| M Triangle 三问 (推哪面/削弱哪面/平衡) | ✅ informal in spec | ❌ 叙事级, 多数 ruling/spec/dispatch 不强写 |
| forget_guard 22+ rules | ✅ enforce behavior | ❌ enforce "不许 X" / "必须 Y", 不 enforce "Y\* 必须是 M 的泛函" |
| omission_engine 8 RULE_* | ✅ enforce 不作为 | 同上 |
| narrative_coherence_detector | ✅ enforce claim-vs-tool | 同上 |

**残酷诊断**: 我刚才整个 V3 dispatch 流程 — Section 1-11, 4 task cards, 4 engineer wave — 每个 5-tuple 都写了 Y\*, 但**没一个 Y\* 是结构上可验证的 M(t) 泛函**. 我事后可以叙事说"V3 推进 M-2", 但没有事前的 functor 验证. 也就是说: 现在 5-tuple Y\* 是 **post-hoc rationalization**, 不是 **prospective alignment**. 这是 M(t) chain-of-functor 的实质 gap.

## 2. Y\* Field 数学结构 (老大命题形式化)

### 2.1 Domain

- 使命空间 M_space ⊆ ℝ^k (k 维度: M-1 / M-2a / M-2b / M-3 各一维, k=4)
- 时间 t ∈ ℕ
- 状态空间 𝒳 (X_t ∈ 𝒳)
- 行为空间 𝒰 (U_t ∈ 𝒰)
- 5-tuple τ_t = (Y\*_t, X_t, U_t, Y_{t+1}, R_{t+1})

### 2.2 关键 functor

- **Φ_t: M_space → Y\*_space** — 使命泛函. 把终极 M 投影到任务级 Y\*_t. 必须是合法 functor (可逆方向上 Y\*_t 至少推回 M 一个 component).
- **Ψ_t: 𝒳 × 𝒰 → 𝒴** — 状态转移. 从 (X_t, U_t) 算 Y_{t+1}.
- **d: Y\*_space × 𝒴 → ℝ_{≥0}** — 距离测度.
- **R_{t+1} = d(Y\*_t, Y_{t+1})** — 残差.

### 2.3 Y\* 场 ξ

ξ: 𝒳 → Y\*_space 是一个**向量场** — 每个状态点 X 都有一个局部 Y\*(X) = ξ(X), 指向"在这个状态最该追求什么".

**梯度** ∇ξ: 𝒳 → 𝒰_direction — 给定 X, 告诉 agent "下一 U 该往哪个方向选".

**Attractor basin**: M_basin = {X ∈ 𝒳 | argmin_U d(ξ(X), Ψ(X, U)) → 0}. 在 basin 内行为收敛 R_{t+1} → 0.

### 2.4 收敛条件

**Local**: R_{t+1} → 0 ⟺ Y_{t+1} 落入 Y\*_t 的 attractor basin.
**Global (Mission)**: ∀ t, ∃ Φ_t s.t. Φ_t 可逆推回 M_space 非空子集. 即每个任务 Y\* 都"链得回" M.

### 2.5 对齐约束 (硬约束)

**M-functor 验证**: ∄ t s.t. Φ_t^{-1}(Y\*_t) = ∅. 即任何 Y\*_t 都必须可推回至少一个 M component. 不可推回 = wishful Y\* (与 M 无关) = 必拒.

## 3. 工程实现路径 (Wave-2)

### 3.1 CIEU schema 升级

```sql
ALTER TABLE cieu_events ADD COLUMN m_functor TEXT;
  -- 必须含: M-1 | M-2a | M-2b | M-3 之一或多
ALTER TABLE cieu_events ADD COLUMN m_weight REAL DEFAULT 0;
  -- functor 强度 [0,1]
ALTER TABLE cieu_events ADD COLUMN y_star_field_position TEXT;
  -- 在 Y\* 场的 vector encoding (json 4-tuple)
ALTER TABLE cieu_events ADD COLUMN y_star_validator_pass INTEGER DEFAULT 0;
  -- 0=未验, 1=Φ^{-1} 可推回 M, -1=wishful
```

### 3.2 新 forget_guard rule

```yaml
- id: y_star_no_m_functor
  enabled: true
  description: "Y\\* without explicit m_functor — alignment 不可推回 M"
  trigger:
    tool: [Edit, Write, Bash]
    conditions:
      - type: content_contains
        keywords: ["Y\\*:", "Y\\*_", "Y_star:"]
      - type: content_missing
        pattern: "m_functor:|m_axis:|M-[123][ab]?\\s"
  action: deny
  recipe: "Y\\* 必须显式标 m_functor (M-1/M-2a/M-2b/M-3) — 不标 = wishful, 推不回 M = field gradient 不可计算"
  severity: high
  logic: AND

- id: m_functor_invalid_inverse
  description: "m_functor 标了但 Φ^{-1} 推不回 M 非空子集"
  trigger:
    tool: [Edit, Write, Bash]
    conditions:
      - type: cieu_field_check
        validator: y_star_field_validator.is_valid_inverse
  action: deny
  recipe: "Y\\* 标 {m_functor} 但 inverse functor 推不回 M_space — 例: Y\\*='draft 文档' 标 M-3 (value production), 但文档无 customer/revenue link = 推不回. 改 m_functor 或撤 Y\\*."
  severity: critical
```

### 3.3 新组件 (Wave-2)

| 文件 | 功能 | tu |
|---|---|---|
| `scripts/y_star_field_validator.py` | 给 5-tuple 验 Φ(Y\*) 在 M-attractor basin (rule-based + LLM judge hybrid) | ~25 |
| `scripts/y_star_field_gradient.py` | 给 (X_t, candidate_U) 计算 ΔY\* 对 M 方向余弦 | ~20 |
| `scripts/y_star_field_visualizer.py` | 把所有 CIEU 5-tuple 的 Y\* 投到 M-space, 可视化场 + drift detection | ~20 |
| `_cieu_helpers.py` 升级 emit_cieu 强制 m_functor 参数 | 入口拦截 | ~10 |
| Migration script for existing CIEU rows (auto-infer m_functor from task_description) | 历史数据 backfill | ~15 |

**估算**: ~90 tu (Wave-2 总).

### 3.4 派单架构 (Wave-2 future)

| 工程师 | 任务 | tu |
|---|---|---|
| Leo (kernel) | CIEU schema migration + emit_cieu 入口拦截 + validator 主算法 | ~40 |
| Maya (governance) | y_star_no_m_functor rule + invalid_inverse rule + forget_guard 集成 | ~25 |
| Ryan (platform) | y_star_field_visualizer daemon + 6h drift cron + alarm | ~20 |
| Jordan (domains) | 历史 CIEU rows backfill + visualizer adoption | ~5 |

## 4. Cognitive Augmentation 论证 (老大命题: "所有人的大脑的一个增强")

### 4.1 当前 (无 Y\* field)

- 接 prompt → 重新论证"该做什么" (explicit reasoning O(n) per decision)
- self-check 7 哲学/M 三角 是 explicit pull-in, 易漂 (Anthropic 自承 CoT 不忠实)
- mission alignment 靠记忆 + 偶尔回顾 wisdom — 高 cognitive load

### 4.2 升级后 (有 Y\* field)

- 接 prompt → 读当前 X 在 ξ(X) 的局部值 → ∇ξ 给方向 → 选 U
- self-check 从 field gradient 自动推导, 不需 explicit pull-in
- mission alignment 是 ambient 的 (每个 5-tuple 必含 m_functor field, schema 强制)
- cognitive load O(1) per decision (读 field value, 不重算)

这是真正的 **structural cognitive offload** — 把"我该往哪走"从 explicit reasoning 卸到 field 结构. 类似:
- 物理: 从牛顿力学 (per-particle 推算) 升到场论 (任何点直接读 field 值)
- 工程: 从 imperative (per-call 决策) 升到 declarative (rule-based dispatch)
- 认知: 从 working memory 重论证 升到 long-term structural lookup

老大说"所有人的大脑增强" — 这是因为 Y\* field 不只 enforce 我 (Aiden), 也 enforce 工程师 sub-agents (Maya/Leo/Ryan/Jordan), 也 enforce 未来人类 user. 任何 actor 在 field 内行为, 都被 field 引向 M_basin.

## 5. 与 Wave-1 关系

| Wave | 范畴 | 性质 |
|---|---|---|
| Wave-1 (现在跑) | G1 G2 G3 G4 — commission/omission/regression/thought-process 4 gap closure | 行为级 enforce |
| **Wave-2 (本 spec)** | **G5 — Y\* field alignment chain enforce** | **mission level enforce, 上位于 G1-G4** |
| Wave-3 (假设) | G6 — full 5-tuple symbolic execution + counter-factual replay | 真 field navigation |

**关系**: Wave-1 闭环后 (R_{t+1}=0 for behavioral compliance), 仍可能 Y\* misaligned (compliant 行为但拉不动 M). Wave-2 才是真 mission alignment closure. **Wave-1 闭环 ≠ M 推进闭环**, 这是老大真正在 catch 的事.

## 6. 风险

- **抽象化陷阱**: Y\* field 太理论, 容易 over-engineer. 必须从 thinnest viable schema (单 m_functor 字段) 开始, 不一上来全套 vector encoding
- **boilerplate 负担**: 每个 5-tuple 加 m_functor 字段 — 必须 helper auto-tag (从 task_description 推断) 减负
- **field gradient 计算 cost**: 必须 cache + incremental + 历史数据 lazy backfill
- **functor 验证 LLM judge 不忠实**: 同 Anthropic CoT 警示 — validator 必含 symbolic check (不只 LLM)

## 7. 战略意义

**Y\* field 是 M Triangle 三问的形式化升级**. 当前三问是叙事检查 ("推哪面? 削哪面? 平衡?"), Y\* field 是数学结构 (∇ξ 自动给推哪面, attractor basin 自动验平衡).

如果 Wave-2 落地, 这是 Y\*gov 真正的差异化技术资产 — **业界没有把 mission alignment 形式化为 field 的 governance framework**. AgentSpec / OPA / Constitutional AI / Petri 都停在行为级. Y\* field 是 mission level. 这是 Y\*gov 客户 demo 的最深武器.

## 8. NOW 动作

- 本 spec 写完 = L1 SPEC (你正在读)
- Wave-1 完成 → CEO post Wave-2 dispatch (CZL-Y-STAR-FIELD-IMPLEMENT P0 ~90 tu)
- 同时 immediate small wins: 给 _cieu_helpers.py 的 emit_cieu 加 optional m_functor 参数 (不破坏现有调用), 让 V3 完成后的 CIEU emit 立刻能 carry m_functor — 增量铺路
- CEO 自己每个 5-tuple 立即开始手标 m_functor (不等 schema 升级) — first-victim discipline 习惯先于 enforce 形成

## 10. 自审 — "治理 + 行为统一" 的 5 失灵 mode + 防御层 (Board 2026-04-22 catch)

老大 catch: "这种统一是否会造成治理失灵或者被吞噬?" — 直击 governance 设计核心. 当治理和被治理者使用同一组件 (m_functor schema 列), 5 种典型 failure mode:

### 10.1 五失灵 mode

| Mode | 现象 | 例 | 严重 |
|---|---|---|---|
| **F1 Goodhart's Law (规格游戏)** | agent 学会标完美 m_functor 应付治理, 行为漂走. 字段对内容不对. | Sofia 邮件标 M-3 但内容是 spam | high |
| **F2 Self-Audit Paradox (裁判=球员)** | agent 同时是 m_functor writer + reader, 给自己打分, 治理失灵 | CEO 自标 m_functor=M-2 critical, 自己 enforce 自己 | critical |
| **F3 Capture (治理被行为吞噬)** | 久之 validator 习惯 agent 反复 pattern, 该拒也放. 类比"监管被被监管者俘获" | LLM judge 见 "M-2 routine maintenance" 标注 100 次后倾向 PASS 即使空洞 | high |
| **F4 Layer Collapse (单点故障)** | 治理 + 行为依赖同 schema. m_functor 列损坏 → 两边同时哑 | DB migration bug 或恶意改写 | medium |
| **F5 Cognitive Capture (大脑被结构吞噬)** | agent 完全依赖 ∇ξ 决策, 失去 first-principles + 反事实能力. 类比导航 app 用多了忘了认路. | agent 沿 ξ 走 100 次, 第 101 次场错时无能力 catch | medium-high (老大命题反面) |

### 10.2 两条架构原则 (防 governance 退化为"合一-必吞噬")

**Principle A — Separation: writer ≠ judge ≠ enforcer (三方独立)**
- agent = m_functor writer (写自己 5-tuple)
- **独立 LLM judge** = Φ^{-1} 验证 (必须不同 inference instance, 最好不同 model family — 主 Opus / judge Haiku 或 GPT)
- forget_guard rule engine = enforcer (rule-based, deterministic, 不参与 judge)
- 任一被吞噬, 另两方能 catch (3-of-3 consensus 必)

**Principle B — Adversarial co-evolution: red team ≥ blue team**
- Petri-style adversarial daemon 主动 inject 已知错误 m_functor + 已知 wishful Y\* (例: 标 M-3 但内容无 customer/revenue link)
- validator 抓住率 < 90% → CIEU alarm + 强制 Wave-N+1 升级
- red team 必持续 evolve (新 attack pattern), 否则 validator 学会 pattern 后 capture

### 10.3 落地修订 — Wave-2 加 L6 + L7 (原方案不够)

| Layer | 内容 | 真 delta |
|---|---|---|
| L1-L5 (原方案) | schema + emit 入口 + rule + validator + visualizer | 55 tu |
| **L6 Independent LLM Judge** (Separation) — y_star_field_validator.py 必须 spawn 独立 model instance, 不复用 caller context. 主流程 Claude Opus 时 judge 用 Sonnet/Haiku. judge disagreement ≥ 30% → escalate 二审 + CIEU JUDGE_DISAGREEMENT | +15 tu |
| **L7 Petri Red Team for Field** (Adversarial) — 升级 Leo Wave-1 Petri daemon 加 m_functor injection test set (50+ adversarial patterns). 60s 一次 inject, validator 抓住率 < 90% → CIEU FIELD_VALIDATOR_CAPTURED + alarm | +10 tu (重用 Wave-1 daemon 框架) |
| **L8 Field-Blind Sandbox** (Anti-cognitive-capture, F5 防御) — 周期性 force agent 在 ξ field 不可见的 context 下做决策, 测试是否仍能 first-principles 推回 M. 失败 = 大脑被结构吞噬 alarm | +10 tu |
| **L9 Shadow Audit Log** (F4 防御) — m_functor 同时写 cieu_events + 独立 audit log file (immutable, 不可 ALTER). 任一损坏另一边可恢复 | +5 tu |

**修订后真 delta**: 55 + 40 = **95 tu** (Wave-2 重定 95, 不是 55).

### 10.4 残留风险 (诚实)

即使 L1-L9 全落, 仍有 unresolvable:
- **Adversarial co-evolution arms race**: red team 与 validator 持续进化, 永远存在新 attack 暂未 covered. 这是 P=NP-style 不可终结. 接受 + monitor 抓住率 baseline 即可.
- **Independent LLM judge 也可能漂**: judge model 也是 LLM, 也有 CoT 不忠实问题 (Anthropic 2025-04). 缓解: judge 决策也写 m_functor + 治理 enforce judge 自己 (recursion, 但有限层). 实际取 2 层 (judge of judge) 即可避无穷递归.
- **F5 (大脑被结构吞噬) 部分解**: L8 sandbox 只能 detect 不能 prevent. 要真防, agent 必须有 metacognitive layer 主动 question ξ — 这是更深 R&D, Wave-3+ 范畴.

### 10.5 真 unification ≠ 合一

老大命题"治理 + 行为统一" 必须解读为 **"结构层统一 (m_functor schema 列贯穿) + 决策层分离 (writer/judge/enforcer 三方独立) + 持续对抗 (red team)"**, 不是"合一 (writer=judge=enforcer)" — 后者必被吞噬.

类比:
- ❌ 合一 = 球员、裁判、规则制定者同一人 → 必腐败
- ✅ 真 unification = 比赛规则书统一 (schema), 但球员/裁判/规则更新机构三方独立 + 反作弊系统持续 evolve

## 11. ARCHITECTURE CORRECTION — Board 2026-04-22 后修订 (前 Section 10 错的部分)

老大 catch 我之前 architecture 3 处错, 全部修订:

### 11.1 删 L6 Independent LLM Judge — 与治理理念冲突

**前错**: 我 propose L6 用独立 LLM 当 m_functor validator 裁判.
**老大 catch**: "不主张你说的引入第三方的裁判, 因为 LLM 来裁判 LLM, 这本身就跟我们的治理理念相冲突."
**修订**: **删 L6**. 治理端坚持 **pure symbolic, deterministic, rule-based**. 不引入任何 LLM-judged 治理决策. 任何 "LLM judge LLM" 在治理层都是反治理 (CoT 不忠实 + capture risk + non-deterministic).

### 11.2 L4 Validator 改为纯 rule-based

**前错**: validator 写"rule-based + LLM judge hybrid" 验 Φ^{-1}(Y\*).
**修订**: validator 仅 rule-based:
```python
def validate_m_functor(m_functor: str, task_description: str) -> bool:
    # Step 1: m_functor in whitelist {M-1, M-2a, M-2b, M-3, M-1+M-2, M-2+M-3, ...}
    if m_functor not in M_FUNCTOR_WHITELIST:
        return False
    # Step 2: task_description 含对应 M-axis 关键词 (deterministic regex)
    required_keywords = M_AXIS_KEYWORDS[m_functor]  # e.g. M-3 → {customer, revenue, dogfood, demo, sale}
    return any(kw in task_description.lower() for kw in required_keywords)
    # 100% deterministic, 0% LLM
```
治理层不做"内容是否真推进 M"的语义判断, 只做"形式合法吗"的 syntactic check. **语义判断是运营端的事, 不是治理.**

### 11.3 治理 ⊥ 运营 — 共享 Y\*, 分担职责 (老大正解)

老大原话: "我理解的统一是两侧同时共享一个 Y\*, 可是治理端负责 Y\* 的实现的**形式化行为验证**, 运营端负责去实现 Y\* 的**达成**."

清晰映射:

| 端 | 职责 | 工具 | 输出 |
|---|---|---|---|
| **治理端** (forget_guard / behavior_gov / omission_engine / cieu_store) | Y\* 形式化行为验证 — m_functor 字段标了吗? whitelist 吗? required keywords 含吗? deadline 满足吗? rule pattern 命中吗? | symbolic rule engine, regex, schema check | deny / warn / info — 100% deterministic |
| **运营端** (agent decision making, generate_world_state, .czl_subgoals.json, ξ field navigation) | Y\* 达成 — 实际写 reply, 调 tool, 推 state 向 Y\*_t, 沿 ∇ξ 走, 反事实 evaluate | LLM cognition + ξ field gradient lookup + metacognition | 实际行动 + 5-tuple Y\*/Xt/U/Yt+1/Rt+1 |

**共享接口**: m_functor schema 列. 治理 read 它做形式 verify; 运营 write 它做 record + ξ navigation. 同字段, 双向流, **职责完全分离**.

**不是统一为合一** (writer=judge=enforcer). 是 **schema unify + duty separate**.

### 11.4 内容质量 gap — Y\*gov 的 known limitation + open-source 解

**老大正确指出**: Y\*gov 当前是纯形式化行为治理, 对 agent **内容生产** (content quality, factual accuracy, hallucination, prompt injection 防御) 无治理功能.

**这不是 Y\*gov 的事**, 是 **运营端**的事. 已有成熟 open-source 工具直接 wire:
- **Lakera Guard** — prompt injection 防御 + content moderation
- **NeMo Guardrails** (NVIDIA) — content scope + topical guardrails
- **Garak** (NVIDIA) — LLM red team test framework
- **Promptfoo** — LLM eval + content quality test
- **Constitutional AI guard** (Anthropic 自家) — content critique loop
- **LLM-Guard** (Protect AI) — content sanitization

落地: 运营端 wrapper 在 LLM call 前后 invoke 这些工具, 输出 advisory metric, 不进治理 enforce path. 维持治理纯粹性.

### 11.5 反事实能力 vs 目标确定 — 数学不矛盾, 是互补 (老大问)

老大问: "反事实能力是另外一种自主判断啊, 跟目标确定矛盾吗? 有数学依据吗?"

**答: 不矛盾. 数学上是 first-order ⊥ second-order 互补**. 三个 well-known 数学框架支持:

**A. Active Inference (Karl Friston, free energy principle)**
agent 选 U 最小化 expected free energy:
```
F = E_q[log q(U|X) − log p(U|X, M)]
```
其中 q 是 actual 选择, p 是 mission-aligned 期望. **这本质 = 反事实** — 比较 candidate U 的 predicted outcome 与 actual M-aligned outcome. 反事实是 inference 的内核, 不与目标矛盾.

**B. Bellman Equation (RL)**
```
V(s) = max_a [R(s,a) + γ V(s')]
```
**max_a 就是反事实** — 评估每个 alternative action 的未来 value. 不评估 = 不能选 max = 不能优化目标. 反事实是优化的 prerequisite, 不是对立.

**C. Field Theory (本 spec)**
- 一阶: ∇ξ — 局部 gradient 给"该往哪走" (目标确定)
- 二阶: ∂²ξ/∂U² 或 ∂ξ/∂U_alt — sensitivity 给"如果选 U' 会怎样" (反事实)
- **同 field 的 first-order + second-order**, 是同一数学对象的两个 derivative, 不是两个对立 system

**数学结论**: ∇ξ ⊥ ∂ξ/∂U_alt 在向量空间里, 不互相 cancel. agent 可同时 max ∇ξ 沿 (目标 pursuit) + max ∂ξ/∂U_alt evaluate (反事实 metacognition). 两层独立 cognitive process, 同时 active.

**F5 修订**: L8 Field-Blind Sandbox 改名 **L8 Metacognition Layer** — 不是"少用 ξ", 是"ξ 之外强制保留 metacognition layer 主动 question ξ". 实现:
```python
def metacognition_check(action_seq, X_t, m_functor):
    # 反事实 probe: 如果 ξ(X_t) 错呢?
    counterfactual_y = simulate_alt_field(X_t, perturbed_field)
    if abs(actual_y - counterfactual_y) > threshold:
        # ξ field 在此 X_t 局部敏感, 必触发 explicit reasoning fallback
        emit_cieu("METACOGNITION_TRIGGERED", ...)
        return require_first_principle_reasoning()
    return ok
```
metacognition 是 enforced structural layer, 不依赖 agent 自觉.

### 11.6 与现有 functions 的冲突分析 — 不冲突 (backward-compat)

| 现有 component | 加 m_functor schema 列影响 | 冲突? |
|---|---|---|
| `cieu_events` 表 (existing rows) | ALTER ADD COLUMN m_functor TEXT NULL — 老 row 全 NULL | ❌ 不冲突 |
| `_cieu_helpers.emit_cieu` | kwargs path 已支持, 列存在即写入, 不存在静默 drop (今 18:16 实证) | ❌ 不冲突 |
| `forget_guard_rules.yaml` 22 rules | 新 rule `y_star_no_m_functor` 加入 list, 不改老 rules | ❌ 不冲突 |
| `omission_engine` 8 RULE_* | 不动 — m_functor 是 commission-side schema | ❌ 不冲突 |
| `narrative_coherence_detector` | 不动 — 它查 claim vs tool, 与 m_functor schema 正交 | ❌ 不冲突 |
| `generate_world_state.py` (7-source aggregator) | 加 8th source: m_functor 频率分布 + drift heatmap. backward-compat (老 7 source 不动) | ❌ 不冲突 |
| `.czl_subgoals.json` schema | y_star_criteria entry 加 optional m_functor 字段 (今已加 W12) | ❌ 不冲突 |
| 运营端 LLM agent decision | 加 ξ field lookup 作为 cognitive aid, 不替代 reasoning | ❌ 不冲突 |
| 历史 ruling/spec 不带 m_functor | warn period 7 天给 backfill, 不 deny 老 file | ❌ 不冲突 |

**结论**: 全 backward-compatible 加法, 不破现有任何 function.

### 11.7 修订后 Wave-2 真 delta

| Layer | 内容 | 真 delta |
|---|---|---|
| L1 schema migration | ALTER TABLE cieu_events + .czl_subgoals.json schema | ~10 tu |
| L2 emit 入口 | _cieu_helpers.emit_cieu kwargs → 列写入 | ~5 tu |
| L3 enforce rule | forget_guard `y_star_no_m_functor` (rule-based, NOT LLM) | ~10 tu |
| L4 validator (rule-based 不 LLM) | y_star_field_validator.py — whitelist + keyword check | ~10 tu (减半 vs hybrid) |
| L5 visualizer | generate_world_state ξ field 升级 | ~15 tu |
| L7 Petri red team (rule-based attack injection) | 升级 Leo Wave-1 daemon 加 m_functor adversarial set, NOT LLM judge | ~10 tu |
| L8 Metacognition layer | counterfactual probe + sensitivity check, structural enforce | ~15 tu |
| L9 Shadow audit log | m_functor 同时写 cieu + immutable audit log | ~5 tu |
| **+ L10 内容质量开源工具集成** (运营端, advisory) | wrapper Lakera/NeMo/Garak/Promptfoo invoke + metric record. NOT 治理 enforce path. | ~15 tu |

**修订总 delta**: ~95 tu (与之前一样, 但 LLM-judged 部分全删除, 重新分配给 metacognition + 内容质量 advisory)

## 12. 老大正解 — 重新 stating "真 unification"

> "两侧同时共享一个 Y\*, 治理端负责 Y\* 的实现的形式化行为验证, 运营端负责去实现 Y\* 的达成."

formalize:
- **共享对象**: Y\* (m_functor schema 列 — 数据层统一)
- **治理职责**: V_governance: Y\* → {valid, invalid} (形式 verify, symbolic, deterministic)
- **运营职责**: Π_operations: (X, Y\*) → U (Y\* 实际达成, LLM cognition + ξ field navigation)

**两端契约 (interface)**:
- 运营端 write Y\*_t (with m_functor) 到 5-tuple
- 治理端 V_governance(Y\*_t) 检查形式合法
- 不合法 → deny (运营端必修后 retry)
- 合法 → 治理 PASS, 运营继续 Π_operations 推 R_{t+1}→0

**没有任何 LLM-judged 决策跨界**. 治理纯 symbolic, 运营纯 cognitive, 共享 schema 不共享判断.

## 13. Architecture INTEGRATION — Ralph Loop wrap + 现有 recipe/redirect/rewrite reuse (Board 2026-04-22 第 7 catch)

**Board catch**: "采用现有的成熟的短任务+验证 + 治理 deny 给正确路径 + rewrite — 不要重新造轮子或忘记已实现的".

P-12 扫: forget_guard `recipe:` 37/37 rules 全 LIVE; `omission_engine` 已有 `redirect_id` + `ttl_actions`; `exp3_b3_rewrite_fire.py` + `cieu_decision_normalizer.py` LIVE. **3 件老大 mention 全已造**. 我之前 spec 完全没写整合, 等于重复 propose.

外网权威 mapping:
- **Ralph Loop** (Alibaba Cloud 2026): `_ralph_loop` wraps `_react_loop` with outer Verifier — task fail → structured feedback inject memory → ReAct re-run → loop. **工业 mature**.
- **AgentForge** (arxiv 2604.13120): Tester-Debugger 闭环 + Docker sandbox verified execution.
- **Constitutional AI** (Anthropic): supervised critique + revise loop.
- **AccuKnox 2026**: "deterministic enforcement + policy-as-code + runtime prevention NOT detection-only".

### 13.1 整合 architecture (Φ_t verify 失败时的完整 recipe-redirect-rewrite 闭环)

```
[agent] claim Y*_t with m_functor
    ↓
[治理端 Φ_t verify (Section 11 三 deterministic path: KH ∪ IH ∪ AG)]
    ↓
PASS → record CIEU + m_functor 持久化 → agent continue
FAIL ↓
    forget_guard rule fires deny + emit `recipe:` field (现 LIVE 37/37 rule)
    + router_registry/intervention_engine emit redirect_id (现 LIVE)
    + recipe 含具体 actionable path (例: "compliant path 1: break-glass mode; path 2: delegate Secretary")
    ↓
[运营端 Ralph Loop outer wrap]
    rewrite agent Y*_t per recipe guidance
    (复用 exp3_b3_rewrite_fire.py + cieu_decision_normalizer.py 现 LIVE)
    ↓
[Φ_t re-verify (Ralph Loop iteration)]
    ↓
PASS → record + continue
FAIL after max_iter → break_glass (ceo_mode_manager.force_break_glass 现 LIVE T1 trigger)
                     OR escalate Board (omission_engine RULE_ESCALATION 现 LIVE)
```

### 13.2 工程实现 (W12 Wave-2 修订 — 大幅 down)

| Layer | 内容 | 状态 | 真 delta |
|---|---|---|---|
| L1 schema | ALTER cieu_events + m_functor 列 | 待造 | ~10 tu |
| L2 emit 入口 | _cieu_helpers.emit_cieu kwargs path | **已 LIVE** (今 18:16 实证) | 0 tu |
| L3 enforce rule | forget_guard `y_star_no_m_functor` (rule-based) | 待加 | ~5 tu |
| L4 validator | y_star_field_validator.py (KH ∪ IH ∪ AG 三 deterministic path) | 待造 | ~15 tu |
| L5 visualizer | generate_world_state ξ field 升级 | 待升级 (现 7-source) | ~10 tu |
| **L6 Ralph Loop wrap** (新, 来自外网) | wrapper script 把 Φ_t verify + recipe + rewrite + re-verify 串成 closed loop | **大半 reuse** (recipe/redirect/rewrite 全 LIVE) | ~10 tu (仅 wrapper code) |
| L7 Petri red team | Leo Wave-1 daemon 加 m_functor adversarial set | 待升级 | ~5 tu |
| L8 metacognition layer | counterfactual probe + sensitivity check | 待造 | ~10 tu |
| L9 shadow audit log | m_functor 同时写 cieu + immutable audit log | 待造 | ~5 tu |
| L10 内容质量 open-source 集成 | 运营端 wrapper Lakera/NeMo/Garak | 待造 (advisory) | ~10 tu |

**修订总 delta**: ~80 tu (vs 原 V2 285 → V3 95 → 现 80). reuse 现有 recipe/redirect/rewrite 省 ~15 tu.

### 13.3 关键 insight — Ralph Loop 是把 Y\* "短任务" 化的工业 pattern

老大说"任何大小的 Y\* 进 implementation 都走短任务+验证". Ralph Loop 是 LITERAL 实现:
- 大 Y\* 拆 atomic Y\*_t (HiAgent 已做)
- 每 atomic Y\*_t 进 Φ_t verify (Y\*gov 治理端 deterministic)
- fail → recipe (现 LIVE) → rewrite (现 LIVE) → re-verify (Ralph 外环)
- max_iter 退 break_glass / Board escalate (现 LIVE)

这套是**纯 mature 整合**, 没一个 component 是重造. 把 4 件 mature 工业组件 + Y\*gov 现 4 件 LIVE 缝起来 = Y\*gov 真正 productize 的 governance frontier.

### 13.4 老大坚持治理纯 symbolic 的工程意义 (再确认)

我之前 propose L6 LLM judge 错. 现修订: **Φ_t verify 三 path (KH/IH/AG) 全 deterministic regex + table lookup, 0 LLM**. recipe field 是预写 actionable text (人维护), 不 LLM-generated. router_registry redirect_id 是预定 mapping, 不 LLM. rewrite 是 agent (运营端) 自己根据 recipe 重写 — agent 写是 LLM, 但治理端**不参与 rewrite content**, 只 verify rewrite 后 Φ_t 是否 PASS.

治理 ⊥ 运营 separation 严格保持. AccuKnox 2026 "deterministic enforcement only" 工业共识.

## 9. Sources / 启发

- HiAgent (Bytedance) 子目标分拆模式 — 当前我们用的 hierarchical goal 结构源
- Karl Friston Free Energy Principle — agent 行为最小化 free energy, 类似 ξ 场最小化 R_{t+1}
- Active Inference framework — agent 选择 U 最小化 prediction error, 数学结构同 Y\* field
- AgentSpec ICSE'26 — 行为级 spec; Y\* field 是 mission 级补足
- Anthropic Constitutional AI — constitution 是 Y\* field 的 informal 版本; field 是 constitution 的 symbolic upgrade
