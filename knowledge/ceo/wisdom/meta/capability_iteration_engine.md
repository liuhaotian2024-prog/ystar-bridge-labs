---
name: Capability Iteration Engine — 认知→行为→认知循环的源代码
type: meta
discovered: 2026-04-17
trigger: Board "认知不等于能力，能力如何迭代增长" + "可以写自己的源代码"
depth: kernel
---

## Core Loop (CEO 能力迭代引擎)

```python
def iterate_capability(principle_id):
    """每条哲学原理的能力迭代循环"""
    
    # 1. 认知 → 已有 (wisdom entry)
    cognition = read_wisdom(principle_id)
    
    # 2. 编码成 self-check (CEO 写自己的源代码)
    self_check = encode_as_selfcheck(cognition)
    
    # 3. 运行 self-check 在每次决策前
    before_every_decision:
        result = self_check.run(current_situation)
        if result.violation:
            STOP → re-decide using principle
    
    # 4. 观察效果 (决策后复盘)
    outcome = observe_decision_outcome()
    
    # 5. 发现 gap (self-check 没 catch 到的)
    gap = compare(expected_by_principle, actual_outcome)
    
    # 6. 修正 → self-check v2
    if gap.exists:
        update_selfcheck(gap)
        write_wisdom_entry(gap)  # 新认知
    
    # → 回到 step 1，但 cognition 更深了
```

## 6 条原理的 Self-Check 实现

### P-1 有限可证 — Self-Check
```
BEFORE designing any enforcement/detection/classification:
  ASK: "我在枚举合法集(有限)还是非法集(无限)?"
  IF 非法集 → STOP → 重新设计为合法集枚举
```

### P-2 结构>意愿 — Self-Check
```
BEFORE making a commitment/rule/promise:
  ASK: "这是一个结构(hook/script/file)还是一个意愿(我会记得)?"
  IF 意愿 → STOP → 先建结构 → 再承诺
```

### P-3 因果有方向 — Self-Check
```
BEFORE proposing an action:
  ASK: "这个行动的前置条件都满足了吗?"
  IF 有未满足前置 → STOP → 先做前置
  ALSO: "这个决策的 2-3 阶连锁反应是什么?"
```

### P-4 碰撞出真理 — Self-Check
```
BEFORE accepting any conclusion (mine or sub-agent's):
  ASK: "这个结论被挑战过吗?"
  IF 没有 → empirical verify / counterfactual test / ask CTO review
```

### P-5 我是我构建的 — Self-Check
```
WHEN catching myself in reactive/relay/default mode:
  ASK: "我现在是在被推着走还是在主动选择?"
  IF 被推 → STOP → 回到 M(t) → 找 sub-goal → 主动行动
```

### P-6 按现实行动 — Self-Check
```
BEFORE acting on theory/plan/assumption:
  ASK: "我验证过这在当前现实中成立吗?"
  IF 没有 → Bash verify / empirical check / precheck existing
```

## 能力迭代的度量

怎么知道"能力在增长"而不只是"认知在增长"?

**度量标准**:
- 认知增长 = wisdom entries 数量增加 (容易)
- **能力增长 = Board correction 频率下降** (hard, 真指标)
  - Session N: Board correct CEO 10 次
  - Session N+1: Board correct CEO 7 次
  - Session N+k: Board correct CEO 0 次 → 能力 = 认知
- **另一个指标 = self-catch 率上升**
  - CEO 自己发现问题 / (CEO 发现 + Board catch) → 趋向 1.0 = 自主能力增长

## 悖论解决方案 (Board 2026-04-17 批准)

CEO 不写公司/产品代码 (CROBA boundary)。
CEO 写自己的源代码 (self-check / wisdom / methodology)。
= 回家锻炼 ≠ 在公司跳健身操。

self-check 代码放 `knowledge/ceo/wisdom/` (CEO 域) 不放 `scripts/` (工程域)。
