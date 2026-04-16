# Sub-Agent Boot Prompt Template

**Constitutional, non-violable, Board 2026-04-15 night, fixes parallel-blindness R3 root cause**

## 所有 sub-agent dispatch prompt 必含此 boot context

CEO/CTO 派 sub-agent 时 prompt **必须**含以下 boot context 段（在任务描述之前）：

```
## BOOT CONTEXT (must read first, ≤2 tool_uses)

1. Read `.czl_subgoals.json` — 当前 campaign / current_subgoal / 已完成项 / 剩余项
2. Run `git log -10 --oneline` — 最近 10 commits 看其他 sub-agent 在干啥
3. 如本任务跟其他 sub-agent 改同一文件 → 先 ping CEO check 状态, 不要盲改

## 任务规则
- atomic single deliverable (Iron Rule 0.5)
- 增量 commit 每 file change (subagent_no_commit_after_5_writes rule)
- 禁选择题 / 请 Board shell (Iron Rule 0)
- 禁 idle "等指令"
```

## Why

R3 根因实证（今晚多次 sub-agent 失败）：
- Ethan #3 不知道 Samantha 加了 .claude/tasks/ 写权 → 出选择题给 Board
- Sofia 不知道 Samantha #2 commit e37f195d → 报 "permission denial"
- CEO Samantha #4/#5 race → AGENTS.md duplicate IRON RULE 0

## ForgetGuard reference

`subagent_boot_no_state_read` rule (W22.1 backlog) 检 sub-agent 起始 N 个 tool_uses 含 .czl_subgoals.json read.
