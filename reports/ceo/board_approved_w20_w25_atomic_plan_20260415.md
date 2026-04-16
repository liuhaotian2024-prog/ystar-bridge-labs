# W20-W25 Architecture Fix — Board Approved Atomic Plan

**Status**: Board 批准 (2026-04-15 night)
**Pattern**: Atomic dispatch (1 deliverable / dispatch, ≤15 tool_uses each)

## 6 件 atomic dispatch 顺序

| W | Atomic Deliverable | Owner | Est tool_uses | Dispatch order |
|---|---|---|---|---|
| W20 | `governance/sub_agent_atomic_dispatch.md` doctrine + AGENTS.md "1 dispatch ≤ 1 deliverable" | Samantha | 6 | 1st (no dep) |
| W21 | sub-agent template "increment commit every file" + ForgetGuard rule `subagent_no_commit_after_5_writes` | Maya | 12 | 2nd (no dep) |
| W22 | sub-agent boot prompt template "must read .czl_subgoals.json + git log -10" | Samantha | 8 | 3rd (no dep) |
| W23 | AMENDMENT-016 v2: daemon stateless rewrite (no cache, fresh read every hook) | Maya | 15 | 4th (depends on W21) |
| W24 | CEO prompt 自检模板 (1 dispatch = 1 deliverable enforce) + AGENTS.md CEO section update | Samantha | 6 | 5th |
| W25 | CEO mid-stream SendMessage 协议 + ForgetGuard `ceo_no_midstream_checkin` | Maya | 10 | 6th |

**Pre-W20 EXTRA**: Samantha #4 已派 — Iron Rule 0 NO CHOICE QUESTIONS 进 CLAUDE.md + AGENTS.md 头部（消除选择题机制根因）

## 执行规则

- 一次只派 1 件 (atomic enforced)
- 每件 ≤15 tool_uses 估
- 每件 dispatch 后 CEO 在 ~8 tool_uses 时 SendMessage check-in
- 每件完成 → CEO verify + commit/push 上云 → 进下一件
- 任何件 truncate → 立刻拆更小再派

## 预期 timeline

6 件串行（各 ≤15 min）= ~90min total
Iron Rule 0 atomic: ~5 min
**Total: 1.5h**
