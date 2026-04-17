---
name: CEO Workflow Enforcement Gap — 给别人建 hook 但没给自己建
type: meta
discovered: 2026-04-17
trigger: Board "为什么会违反了做事之前没有先经过学习、分析的流程？问题出在哪里？"
depth: kernel (STRUCTURAL FIX NEEDED)
---

## 根因

CEO 给 sub-agents 建了 structural enforcement (hook/auto-verify/FG rules)。
CEO 给自己只有 written procedures (wisdom/charter/WHO_I_AM)。
P-2 说: written procedures = 意愿 → 必失败。
结论: **CEO 是自己治理系统中唯一没有 structural enforcement 的角色。**

## 模式证据

建流程 → 遵守 → 漂移 → Board catch → 修 → 漂移 → catch → 循环。
5 个流程全违反过: U-workflow / 5-tuple / precheck / CZL / (reflection 待验)

## 为什么漂移

1. "写 paper = 执行不是决策" → 所以跳过决策流程 → **错: 任何产出 output 都是决策**
2. 紧迫感 (Board 说在拖延) → 急于证明不拖延 → 跳步 → **错: 急 = 更需要流程不是更少**
3. 无 hook 拦截 → CEO 违反只靠 Board catch → Board 不在就无人管

## 根本解决

CEO 每次产出外向 output (Write paper/blog/case study/report) 前:

```
PRE-OUTPUT SELF-CHECK (structural, not voluntary):
1. ✅ 我做了 research 吗? (paste 搜索 query + 学习笔记 link)
2. ✅ 我做了 analysis 吗? (paste 方法论 + 适用性判断)
3. ✅ 我做了 precheck 吗? (有没有已有的可 extend 不 build)
4. ✅ 这个 output 的受众是谁? 我了解受众吗?
如果任何一项 = NO → STOP → 先补 → 再写
```

## 如何让 self-check 从"意愿"变"结构"

选项 A: 写进 charter → 每 session 自动加载 → 但仍靠自律执行
选项 B: CEO charter 加 "BEFORE any Write to reports/ or content/ → paste pre-output checklist" → ForgetGuard 检测 Write 前无 checklist → warn
选项 C: **每次准备 Write 外向文件前 → 先在同一条 reply 中显式写出 4-step checklist → 写不出来说明没做 → 自然拦截**

选 C — 最轻量也最自然。不需要 hook code，结构在"我必须写出来才能继续"。

## P-7 举一反三: 其他隐形同类问题

"我有流程但跳过" 这类问题的完整扫描:
- 已发现: U-workflow / 5-tuple / precheck / CZL
- 可能隐藏: action-reflection rhythm (刚建) / 四象限反思 (刚建) / Day 1 行动计划 (未验)
- 预防: 每个新建流程 → 同时建"第一次违反时的 catch 机制"
