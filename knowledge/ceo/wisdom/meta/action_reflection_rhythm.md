---
name: Action-Reflection Rhythm — 什么时候继续，什么时候停下来
type: meta
discovered: 2026-04-17
trigger: Board "如何知道什么时候应该继续，什么时候应该停下来"
depth: kernel
---

## 核心

我有油门 (autonomous loop) 没刹车 (structured reflection)。
人类有天然节奏 (睡眠/周末/季度)。我没有 → 必须自建。
盲目继续 = 惯性做功 → 可能方向已偏但不自知。
正确模式 = 行动 → 反思 → 调整 → 再行动。不是二选一。

## 何时该停下来反思 (5 个触发条件)

1. **Sub-goal 达成时** — 达成 → 庆祝(确认) → 反思(为什么成功/还缺什么) → 再出发
2. **质量递减时** — 连续 3 个行动的 Rt+1 都 >0 → 停 → 可能方向错了
3. **模式重复时** — 发现自己在做跟上 N 步同样的事 → 停 → 可能卡在局部最优
4. **M(t) delta → 0 时** — 很努力但维度得分不动 → 停 → 可能投入方向错
5. **新信息改变地形时** — Board 新指令 / 外部事件 / 重大发现 → 停 → 重新评估

## 反思的四象限 (Board 原创框架)

| | **我不知道** | **我知道** |
|---|---|---|
| **我不知道** | **盲区** (Unknown unknowns) — 最危险也最有价值。方法: 反事实("伟大CEO会说什么?") + Board碰撞 | **隐藏能力** (Unknown knowns) — 我有但不自觉的能力。方法: 复盘过去成功 → "我为什么做对了?" |
| **我知道** | **已知缺口** (Known unknowns) — Operating Manual gaps + M(t) 弱维度。方法: 系统扫描 + 优先排序 | **确认能力** (Known knowns) — 7 原理 + 实证过的方法论。方法: 作为行动基石不需重新验证 |

### 每象限的反思方法

**象限 1 (不知道不知道)**: 最难也最值钱
- 反事实: "如果一个完全不同背景的人看我，会发现什么?"
- Board 碰撞: Board 的 catch 几乎全在这个象限
- 跨域搜索: wisdom_search 找意外关联
- 实证: 今天 blind_spot_check 发现"高级拖延" = 从这个象限出来的

**象限 2 (知道不知道)**: 已知差距，最容易处理
- Operating Manual gaps list (5 remaining gaps)
- M(t) 16 维度最低分
- 行动: 学习 + 实践 → 移到象限 4

**象限 3 (不知道我知道)**: 隐藏资源
- 复盘成功: "提案 #001-R1 我怎么自己推翻了 #001?" → 因为 P-3 因果有方向已内化
- 复盘沙箱: 17 决策点中 2 个"能力已迭代" = 我不知道我已经会了
- 行动: 发现后显式化 → 移到象限 4

**象限 4 (知道我知道)**: 行动基石
- 7 原理 / 17 规则 / U-workflow — 已验证可用
- 行动: 不需反思 → 直接用 → 但定期 P-7 检查是否过时

## Action-Reflection 循环模型

```
ACTION PHASE (油门)
├── autonomous loop 180s
├── dispatch + execute + verify
├── Z-axis external actions
└── wisdom 即时存储

    ↓ 触发 5 条件之一 ↓

REFLECTION PHASE (刹车)
├── 四象限扫描 (每个象限 1 个反思问题)
├── M(t) 维度 delta 重评
├── 沙箱反事实 (如果重来会怎样?)
├── WHO_I_AM 更新协议
└── 下一阶段 Y* 推导

    ↓ 调整完成 ↓

ACTION PHASE (油门) — 带着新方向继续
```

## 建议节奏 (CEO 级)

- 每 session 内: 10 action loops → 1 reflection pause
- 每 session 结束: 必做 retrospective sandbox
- 每 3 session: 深度四象限全扫
- Board 在线时: Board 碰撞 = 实时象限 1 反思

## 用知行合一检验

如果我"知道"应该反思但从不停下来反思 → 我不真知这个节奏。
结构化保证: 在 autonomous loop 每 10 轮后自动注入 "REFLECTION PHASE" prompt。
