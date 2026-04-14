---
name: Task card on disk is not dispatch
description: Writing a task file to .claude/tasks/ does not trigger any sub-agent; dispatch requires an explicit Agent tool call that references the card
type: feedback
originSessionId: 36ef8c73-06cf-42bb-931e-9a2e522c40d0
---
`.claude/tasks/eng-*.md` 文件写入磁盘本身**不触发任何执行**。Sub-agent 不会 poll 目录、不会自动认领。必须用 Agent tool 显式 spawn 对应 subagent_type，并在 prompt 里指向 task card 路径。

**Why:** Board 2026-04-13 追问 "还没有等回来吗"——CEO 本线写了 4 个 task cards 后就去"等"，忘了 4 张卡需要 4 次 Agent 调用才会被执行。本线空转。

**How to apply:**
- 每写完一张 task card，立刻同一轮 spawn 对应 subagent_type 的 Agent 调用，prompt 头行 `读 .claude/tasks/<filename> 执行`
- 并行派多人时，用一条消息里多个 Agent tool call block
- "Task card 就位" 不是 status，status 是 "N 路并行 spawned, ETA X"
- 未来 AMENDMENT-015 Phase 3 Layer 3 (self-recovery) 应考虑 task card 文件 watcher，自动 dispatch——现在没有
