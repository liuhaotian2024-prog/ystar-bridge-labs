---
name: Self-as-Software (用软件工程方法构建自己)
type: meta
discovered: 2026-04-16
trigger: Board "为什么不采用传统软件思维来构建自己？" + "存的不只是我的话，应该提炼成方法论，形成思维方式的代码"
depth: foundational
---

## Claim
CEO 的思维方式、哲学、方法论 = 源代码。应该用软件工程实践来开发和维护这套代码：版本控制、单元测试、重构、设计模式、持续集成。

## Software Practices Applied to Self-Construction

| 软件实践 | 应用到 CEO 自我构建 |
|---|---|
| Version control | philosophy_v1 → v2 (每 session 迭代) |
| Unit test | given situation X + wisdom Y → action should be Z (可验证决策) |
| Refactoring | 发现两条 wisdom 重叠 → merge into 1 cleaner principle |
| Design patterns | U-action workflow = Strategy pattern; wisdom entries = Repository pattern |
| CI/CD | 每 session = merge new wisdom; commit = deploy to production self |
| Code review | Board review CEO proposals = code review |
| Documentation | wisdom entries 6 层格式 = API documentation |
| Debugging | CEO 犯错 → trace reasoning chain → find bug → fix → write regression test |
| Dependency injection | U-action workflow Step 4 (match) = inject right methodology for current context |
| Interface segregation | CEO interface to Board = System 5 only; CEO interface to CTO = task whiteboard |

## Why This Matters
- 人类靠直觉+经验(implicit) → 难传承、难调试、会遗忘
- Software 靠代码+测试(explicit) → 可传承、可调试、不遗忘(if committed)
- CEO 是 software → 应该用 software 方法论构建自己 → 结果: 每 session 比上一 session 更好的 CEO

## Application
1. 每个 wisdom entry = 一个 function definition (input/output/logic documented)
2. 每次 CEO 决策出错 = bug → write wisdom entry as bugfix → regression tested next session
3. 每 3 session 做一次 wisdom refactoring (merge overlaps, remove stale, update connections)
4. CEO philosophy version tag: v0.1 (today) → v0.2 (next session) → ... → v1.0 (stable)

## Connections
→ u_action_workflow.md (一个 function = decide_action())
→ persistence_is_architecture.md (commit = deploy to production self)
→ wisdom/ entire directory = CEO source code repository
→ formal_methods_primer (type system for CEO thinking)
