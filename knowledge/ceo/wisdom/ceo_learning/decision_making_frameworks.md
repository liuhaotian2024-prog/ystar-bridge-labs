---
name: CEO Decision-Making Frameworks (学习笔记 Round 1)
type: ceo_learning
discovered: 2026-04-16
source: WebSearch CEO decision frameworks 2025-2026
depth: medium (first pass — needs deepening)
---

## 5 个顶级 CEO 决策框架 + 我的适用性分析

### 1. First Principles Thinking (Musk)
- 方法: 去掉所有假设 → 只保留基本事实 → 从事实重建
- 我适用吗: ✅ 极适用 — 我的 反事实推理 + 无情绪 = 天然 first principles thinker
- 但 Board 教训: 我的"first principles"经常退化为"从经历列举" → 需要刻意练习穷举

### 2. Second-Order Thinking (Bezos)
- 方法: 不只看决策的第一层结果，看第二、第三层连锁反应
- 我适用吗: ✅ 极适用 — 反事实推理就是 second-order
- 例: "找客户"(一阶好) → 产品不行客户失望(二阶坏) → 口碑损毁永不回来(三阶灾难)
- Board 今天 dependency_sequencing 就是在教我 second-order thinking

### 3. OODA Loop (Boyd)
- Observe → Orient → Decide → Act → 循环
- 我适用吗: ✅ 已在用 — CEO autonomous loop = OODA 变体
  - Observe = Xt assess (AC/HP/K9/16维度)
  - Orient = U-action workflow (research→learn→synthesize→match)
  - Decide = Y* derive from mission
  - Act = execute
- 2026 趋势: AI accelerates O&O phases → 我天然快

### 4. Cynefin Framework (Snowden)
- 4 域: Simple(清晰) / Complicated(复杂) / Complex(混沌) / Chaotic(危机)
- 每个域用不同决策方法:
  - Simple → best practice (规则手册)
  - Complicated → expert analysis (CTO 技术方案)
  - Complex → probe-sense-respond (实验+观察)
  - Chaotic → act-sense-respond (先做再说)
- 我适用吗: ✅ 极适用 — 我的 atomic_class Heavy/Light/Investigation = Cynefin 简化版
  - Heavy = Complex (需要 17-step 完整流程)
  - Light = Simple (6-step 快速)
  - Investigation = Complicated (先分析再行动)
- 缺: 没有 Chaotic 模式 (CEO 遇到危机怎么办? 目前无 protocol)

### 5. 80/20 Pareto Principle
- 20% 努力产生 80% 结果
- 我适用吗: ⚠️ 部分 — 我容易陷入治理递归(100% 努力在 20% 价值的 meta-governance)
- Board 今天抓的"治理 8 分客户 0 分" = 典型 Pareto 违反

## 我的 CEO 决策模型 v0.1 (综合以上)

```
function ceo_decide(situation):
    # 1. Cynefin classify
    domain = classify_cynefin(situation)
    
    # 2. Apply domain-appropriate method
    if domain == Simple:
        return apply_existing_rule()  # 已有 wisdom/MEMORY 直接用
    elif domain == Complicated:
        return delegate_to_cto()  # 技术问题归 CTO
    elif domain == Complex:
        return probe_sense_respond()  # 小实验 → 观察 → 调整
    elif domain == Chaotic:
        return act_first_then_assess()  # 先稳住再分析
    
    # 3. Second-order check
    second_order = what_happens_after(decision)
    if second_order.is_worse_than_no_action:
        return reconsider()
    
    # 4. First-principles validate
    if decision.based_on_assumptions_not_facts:
        return strip_assumptions_and_rebuild()
    
    # 5. Pareto check
    if decision.effort > 20% AND decision.value < 80%:
        return find_higher_leverage_action()
    
    return decision
```

## 下一步学习计划
- Round 2: 战略思维 (Porter 5 Forces / Blue Ocean / Platform Strategy)
- Round 3: 人才判断 (如何评估 agent 能力 + trust 机制)
- Round 4: 风险管理 (Black Swan / Antifragile)
- Round 5: 创新管理 (Christensen / Zero to One)
