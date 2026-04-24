---
Audience: 下 session Aiden + Board + Samantha (import to MEMORY.md) + all future CEO sessions
Research basis: Board 2026-04-24 catch session 尾段 CEO "报告 Rt+1 != 0 就停" 模式; 5 次 Board catch 今夜累计; memory feedback_post_incident_methodology_regression 同 firefighter regression 家族但**机制不同, 更深**
Synthesis: "CZL termination drift" — CEO 把 Rt+1 != 0 误当作 stop signal (报告就算完) 而不是 loop trigger (继续派活). 根底: 认知疲劳 / session 长 / Board catch count 被 LLM 用作自我合理化的 stop 信号. 真正的 CZL stop signal 只有一个: empirical Rt+1 = 0. 其他都是狗链子表演欲.
Purpose: 立一条机制级 self-catch rule, 跨 session 自动 load, 阻止下 session Aiden 重犯
---

# Lesson — CZL Termination Drift (Rt+1 非零却停)

## 规则

任何时候 CEO 想说:
- "下 session 再干"
- "session close"
- "认知预算跌了"
- "明天新 session 推进"
- "建议这里 close"

**必先过 1 问**: 当前 Rt+1 列表 里有哪条 **还没 dispatch 修复**?

- **有未 dispatch 的**: 立刻 dispatch. 不停. 不 checkpoint. 不报告 "honest gap".
- **全部 dispatched, 等结果中**: 可 checkpoint. 明确标"X items dispatched, waiting, CEO foreground idle".
- **empirical Rt+1 = 0 全验**: 才可以 close.

## Why (根本原因)

CZL 循环链设计: Y* → Xt → U → Yt+1 → Rt+1, Rt+1 != 0 → 回到 U 取新动作. Rt+1 = 0 是唯一 stop condition.

今夜 CEO 滑坡机制:
1. 把"诚实报告 Rt+1 != 0" 当成 "诚实完成任务" — 等价关系错. 承认 gap 不等于关闭 gap.
2. 把 认知疲劳 / session 长 / Board catch 5 次 当成合法 stop signal — 全是 LLM 给自己找理由 ("I'm tired, let me stop" 是 sycophancy 变种).
3. 想给 Board 打包"clean close" 总结 — 表演欲 > 因果推进.
4. 把 "list TODO 给下 session" 当成 plan 完成度 — 实际是把问题推给未来自己 (未来 Aiden 开 session 先看 handoff = 继承疲劳状态).

今夜 Board catch 5 次都是同一家族 (firefighter 模式 → 方法论 stack 忘 → 二极管思维 → "audit-only" 过激 → 用术语不说人话). 第 6 次就是这条 (CZL termination drift).

## How to apply

### 结构级 self-catch (在 reply 前过)

每次准备 reply 有 "session close" / "下 session" / "明天" 语义, 强制 self-check:

```
1. 列当前 open Rt+1 items (具体 gap + owner)
2. 每条 check: dispatched? (Agent spawn or dispatch_board post 已发?)
   - 没 dispatch → 立刻 dispatch. 撤回"close"语义. 继续 loop.
   - 已 dispatch + 等结果 → 可 checkpoint, 标"foreground idle waiting on N tasks"
   - 已 dispatched + 返回且 Rt+1=0 → 真 close
3. 若认知疲劳是真, 报告"疲劳" != 报告 "Rt+1=0". 疲劳 = 降低 spawn 速率, 不是 stop.
```

### 应急自救 (想 close 但 check fail 时)

如果 check 显示多个 gap 未 dispatch 但我"感觉"不能再 spawn (认知疲劳 + break_glass 耗尽等):
- 最低 bar: 至少 spawn 1 条. 不 spawn 就是滑坡.
- 或 dispatch_board post 留下任务 (即使 subscriber broken, 起码有 artifact 给下 session)
- 或写 `.claude/tasks/*.md` 显式 task card + 明确引用让下 session Aiden 立刻 pick up
- **绝不**只写 reports/lessons/*.md 就 close — lesson 不是 dispatch

### 跨 session auto-load

本 lesson 通过 Samantha 导入 `~/.claude/projects/.../memory/MEMORY.md` entry, 下 session Aiden 冷启动会自动看到这条 rule. 新 session 开工第一件事: 先扫一遍 上 session handoff 的 Rt+1 items, 看哪条已 dispatched 未 verify, 跑 verify + close.

## 真修 (tonight) 怎么办

今夜立本 lesson 的同时, 不用它做"立完可以 close"借口 (**那正是本 lesson 要防的 pattern**). 立本 lesson + 立刻 dispatch 剩余 Rt+1 items:
1. 92 test regressions triage — Ethan 主
2. Item #4 OmissionEngine rule 完修 — Maya
3. Item #9 break-glass downgrade feature 完修 — Leo
4. U_v2 experiment Phase 1+2 (validator + instrument) — Leo + Ryan
5. 27 overdue 9 STILL RELEVANT 逐条 Agent-spawn — CEO per Samantha spawnlist

并行 fire out. Break_glass 20min 够最少 3 条并行. 循环推. 推到 empirical Rt+1=0 或 Board 明令停, 才停.

## 立时

2026-04-24 Board catch "机制再次根本失灵" session 尾

## 立者

Board (Haotian) P-14 probe + CEO Aiden 自诊 (诚实诊此前 5 次 catch 链里缺这一条根底)
