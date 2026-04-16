# Sub-Agent Atomic Dispatch Doctrine

**Constitutional, non-violable, Board 2026-04-15 night, fixes truncation R1 root cause**

## 核心规则

**1 dispatch = 1 deliverable**。多任务必须拆成多 dispatch + sequence。

## Why

Sub-agent 平均失败模式：30-50 tool_uses 时 Anthropic-side 硬截断。
单 dispatch 塞 6 任务（如今晚 Ethan #5）→ 必截断 → 全部丢失 → CEO 事后 wrap。

## 强制规则

CEO/CTO 派 sub-agent 时 prompt 必符合：
- ≤1 deliverable per dispatch（不允许 "+" "和" 连接独立任务）
- ≤15 tool_uses 估算 budget
- 多任务 → 多 dispatch + 显式 sequence + dependency chain

## ForgetGuard enforcement

`multi_task_dispatch_disguise` rule (action: warn → 后续升 deny):
- trigger: Agent tool prompt 含 "+ task" / "Task A:.*Task B:" / "(Task|任务) [12345]:" 多个 → warn

## 例外

紧急生产中断 P0 + Board 明授可暂停此规则，记 CIEU `MULTI_TASK_DISPATCH_OVERRIDE`.

---
*Established 2026-04-15 night to fix 11 sub-agent failures observed today.*
