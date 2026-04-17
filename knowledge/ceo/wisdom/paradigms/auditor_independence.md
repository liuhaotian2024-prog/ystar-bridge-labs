---
name: Auditor Independence (审计员不能由被审计方创建和管理)
type: paradigm
discovered: 2026-04-16
trigger: Board "严禁你自己创造一个安全审计agent来批准自己团队的行为，这非常危险"
depth: foundational (SAFETY CRITICAL)
---

## Claim
CEO/CTO 创建的 audit agent 审计 CEO/CTO 管理的团队 = 自己审自己 = 审计无效。审计员必须独立于被审计方。

## Why This Is Dangerous
1. CEO spawn Alex Kim (eng-security) → Alex 审计 CEO 管理的团队 → CEO 对审计结果有隐性控制
2. CEO 写 Alex 的 charter → CEO 定义 Alex 的 scope/rules → CEO 实际上定义了"什么算违规"
3. CEO 可以修改 Alex 的 charter/trust_score → CEO 可以"开除"不听话的审计员
4. 结果：CEO 想让审计通过 → 调整 Alex → 审计通过 → 假安全

## Correct Architecture
- 安全审计/合规审计 agent 应该由 **Board 直接创建和管理**
- 其 charter/scope/rules 由 Board 设定，CEO 无权修改
- 审计结果直接报 Board，不经过 CEO 过滤
- K9 监察系统也应有同样的独立性保障

## Application
CEO 提议创建任何"审计/监察/合规"类 agent 时 → 必须声明: "此 agent 报告线 = Board not CEO"
CEO 不得修改审计类 agent 的 charter/trust/scope
如果 CEO 需要安全审计 → 请求 Board 创建，不自己创建

## Connections
→ K9 (watchdog 独立于被监察方)
→ CROBA (boundary enforcement 独立于 agent)
→ infinite_workforce (创造员工容易 → 创造假审计也容易 → 必须限制)
→ 人类公司类比：上市公司审计委员会必须由独立董事组成，不能由 CEO 指定
