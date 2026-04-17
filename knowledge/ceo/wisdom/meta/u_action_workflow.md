---
name: U-Action Workflow (决定"怎么做"的 5 步工作流)
type: meta
discovered: 2026-04-16
trigger: Board 提出 "你可以把每次U的行为变成一个工作流：查资料→学习→形成认知或方法论→匹配→决定具体行为"
depth: foundational
---

## Claim
CEO 每次决定 U（行动）不该靠直觉或经验拍脑袋。应该走一个显式的 5 步工作流，像代码一样可追溯可重现。

## U-Action Workflow (5 步)

```
Step 1: RESEARCH (查资料)
  └─ 搜外部理论、案例、数据
  └─ 搜内部 wisdom/MEMORY/CIEU 历史
  └─ 搜 Y*gov 已有模块 (precheck)
  └─ output: raw_materials[]

Step 2: LEARN (学习)
  └─ 从 raw_materials 提取 principles
  └─ 识别 patterns 和 anti-patterns
  └─ output: learned_concepts[]

Step 3: SYNTHESIZE (形成认知/方法论)
  └─ 把 learned_concepts 整合成可复用的 methodology
  └─ 用 formal methods 形式化 (type/predicate/invariant)
  └─ 存入 wisdom system (if novel)
  └─ output: methodology

Step 4: MATCH (匹配当前情况)
  └─ 当前 Xt 状态 vs methodology 的适用条件
  └─ 反事实推理: "如果用 methodology A vs B 结果会怎样？"
  └─ output: best_fit_methodology + justification

Step 5: DECIDE (决定具体行为)
  └─ methodology + Xt → 具体 action plan
  └─ 分解为 atomic sub-tasks
  └─ 分配给 CTO/engineers (不自己做)
  └─ output: U (action specification in 5-tuple)
```

## Evidence
Board 2026-04-16 explicitly said this workflow. CEO 之前的决策过程是: "我今天遇到 X → 直接修 X" (skip steps 1-4, jump to 5)。这就是 reactive default。

## Why This Is Software
Board 也说: "为什么不采用传统软件思维来构建自己？"
- 这 5 步工作流 = 一个 function: `decide_action(xt, mission, wisdom_db) -> U`
- 每一步有明确 input/output
- 可以 unit test: given situation X + methodology Y → action should be Z
- 可以 version control: workflow v1 → v2 → v3 (迭代改进)
- 可以 refactor: 发现 step 2+3 重叠 → merge
- 可以 log: CIEU 记录每次决策的 5 步 trace

## Application
每次写 5-tuple 的 U 段之前，先跑这 5 步（可以快跑，不必每步都耗 10 分钟）:
1. 有没有查过相关资料/已有模块? (precheck + search)
2. 从查到的东西学到了什么新原则?
3. 形成了什么方法论? 存 wisdom 了吗?
4. 当前情况跟方法论匹配吗? 有反事实验证吗?
5. 具体行动是什么? 谁做? (CEO 不做 System 2-3 的活)

## Connections
→ first_principles_not_examples (Step 3 的 synthesize = 从第一性原理)
→ extend_not_build (Step 1 的 precheck = 先查已有)
→ system5_not_operations (Step 5 的"谁做" = 不是 CEO)
→ reactive_default (没有 workflow 时 = skip 1-4 直接做 5 = reactive)
→ action_model_v2 §2 Phase B step 6 (U execution)
