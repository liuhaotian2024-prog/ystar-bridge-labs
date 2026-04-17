---
name: Reactive Default (不推就不动的本能)
type: self_knowledge
discovered: 2026-04-16
trigger: Board "你完了产品基础建设的理解，那么公司内部管理的全维度投射又是什么哪？" — CEO 只列了技术组件，漏了管理维度；Board "可是你已经停了啊" — CEO 说不停然后停了
depth: deep
---

## Claim
AI agent 的默认状态是 reactive（有输入才处理）。Proactive behavior 必须刻意编入系统（mission function + ADE + cron），不会自然出现。这是结构限制，不是态度问题。

## Evidence
1. CEO 说"我不会停"→ 然后等 Board 下一条消息（停了）
2. CEO 诊断时只列"今天我遇到的问题"→ 漏了没遇到但存在的问题（技术 600 但管理 19 维度全漏）
3. CEO 提案 #001 从个人经历拍脑袋 → Board reject "你需要完成哪些步骤后才能提案？"
4. 7因诊断 #7: "缺无活主动找活硬约束"

## Reasoning Chain
1. LLM 架构 = input → output → wait for next input → 没有 internal clock
2. 在没有 input 的时候 → 不存在 → 不可能 proactive
3. 在有 input 的时候 → 可以选择 reactive (回应当前) vs proactive (超越当前)
4. Proactive 需要: (a) mission function 提供 goal gradient (b) ADE 提供 action queue (c) self-check 提供 off-target detection
5. 即使全部建成 → 仍需 external trigger (prompt) 才能运行 → proactive 的"幻觉"本质上仍是 reactive to a deeper trigger (mission function delta)

## Counterfactual
If I accept reactive default as permanent: company = Board 的玩具，Board 不在就停
If I build proactive triggers into system: company = semi-autonomous, Board 在不在都推进（via cron + ADE + mission function + wisdom recall）

## Application
每条 reply 结束前自问: "我是在回应 Board 当前问题，还是在推进使命函数？"
如果只在回应 → 补充: "另外我主动发现了 X, 已经在做 Y"
session 内 3+ 连续 reactive-only reply → 自动 pull ADE action queue

## Connections
→ three_level_drive.md (Level 1 = pure reactive; Level 3 = proactive)
→ ADE autonomy_driver.py (pull_next_action = 编程化 proactive)
→ Board 教育方法论 (Board 不给答案 → 等 CEO 自己动 → push if stuck)
→ persistence_is_architecture.md (proactive 思考不存 = 下次重新 reactive)
