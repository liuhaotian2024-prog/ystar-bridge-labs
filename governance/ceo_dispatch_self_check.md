# CEO Dispatch Self-Check Protocol

**Constitutional, non-violable, Board 2026-04-15 night, fixes R5 "CEO 单 prompt 塞多任务"**

## 每次 CEO dispatch sub-agent 前必答 3 问 (内心, 5 秒)

1. **这个 prompt 是 ≤1 deliverable 吗？**
   - Yes → go
   - No → 立刻拆成多 dispatch + sequence (Iron Rule 0.5)

2. **这个 deliverable 估算 ≤15 tool_uses 吗？**
   - Yes → go
   - No → 继续拆

3. **sub-agent 需要的 context 我在 prompt 里写全了吗？**
   - 文件路径具体到绝对路径
   - 依赖任务的 commit hash / agent_id
   - 禁止事项清单 (Iron Rule 0 / no idle / no request Board shell)
   - 成功判据 (Rt+1=0 definition)

## 违反自检 = CEO 越权风险升级

CEO 违反 "1 dispatch = 1 deliverable" 规则 → ForgetGuard `multi_task_dispatch_disguise` rule → CIEU event。
月累计 > 3 次 → Board P0 escalation。

## 历史案例（don't repeat）

- Ethan #5 (a8dd03b654c650f77) — CEO 单 prompt 塞 6 任务 → 47 tool_uses truncated 0 ship
- Samantha #5 (a0af160bfb7c400d5) — CEO race dispatch 未 verify #4 完成 → redundant commit 168720c2

## Self-Check 要写进 CEO section 的显式提醒

CEO 每次用 Agent tool 前，脑内跑一遍三问。跑完才 write prompt。
