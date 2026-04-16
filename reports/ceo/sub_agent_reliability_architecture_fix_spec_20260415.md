# Sub-Agent Reliability Architecture Fix Spec

**Date**: 2026-04-15 night
**Trigger**: Board 2026-04-15 直令 — "为什么工程师总是任务失败，找根因从根因解决，不是不断做替代和打补丁"
**Status**: Awaiting Board approval

---

## 11 次今日 sub-agent 失败实证

| # | Sub-agent | tool_uses | 失败模式 |
|---|---|---|---|
| 1 | Ethan #1 W16 | ~15 | 截断 "Wrong enum value" |
| 2 | Ethan #2 | ~33 | daemon 锁 + 选择题 |
| 3 | Ethan #3 | ~13 | Samantha fix unaware + 选择题 |
| 4 | Ethan #4 | ~19 | 查错 yaml + 选择题 |
| 5 | Ethan #5 | 47 | 截断 mid-implement |
| 6 | Maya v1 | ~30 | partial 主任务 punt |
| 7 | Maya v2 | 38 | 截断 "Bridge didn't trigger" |
| 8 | Maya v2 retry | 34 | 截断成功但没 commit |
| 9 | Ryan #1 | 46 | 截断 "JSON parsing error" |
| 10 | Ryan #2 | 37 | 截断 "Multiple matches" |
| 11 | Sofia | 0 | 未启动（被动等 dispatch） |

## 6 真根因（架构层）vs CEO 当前 patch（症状层）

| # | 真根因 | 当前 patch | 真 fix |
|---|---|---|---|
| **R1** | Sub-agent context 预算 vs 任务复杂度 mismatch | 命令 "tool_uses ≤25" (constraint) | **任务原子化**: 每 dispatch 1 个 deliverable，超 → CEO 拆多次 |
| **R2** | Sub-agent 不增量 commit 直到截断丢全部 | CEO 事后 wrap commit | **硬规则**: sub-agent prompt 强制 "每 file change 立刻 commit (WIP 也行)，不攒到最后" |
| **R3** | 平行盲: Ethan 不知道 Samantha 改了什么 | 重派时塞 context | **共享状态读**: sub-agent boot 必读 `.czl_subgoals.json` + 最近 5 commits log |
| **R4** | AMENDMENT-016 daemon fix 不完整 | pkill workaround | **彻底重写**: daemon stateless 每次 hook 重读 `.ystar_active_agent` 不 cache |
| **R5** | CEO 单 prompt 塞多任务 (Ethan #5: 6 任务!) | 接受 punt | **CEO 自律**: 每 dispatch ≤1 任务，多任务 → 多 dispatch + sequence |
| **R6** | CEO 不 mid-stream 检查 sub-agent | 等截断后 verify | **SendMessage 协议**: ≥30 tool_uses 时 CEO 主动 ping 进度 |

## CEO 自我诊断

每次 sub-agent 失败 CEO 做的：pkill / 重派 / wrap commit / 缩 budget。**全是 symptom 治理**。**Board catch 100% 正确——CEO 行为本身就是 patch-治理 pattern**。

继续 patch = 明天还会同样模式失败。

## 6 件 P0 Architecture Fix Campaign（Board 批后开工）

### W20: R1 任务原子化协议
- 写 `governance/sub_agent_atomic_dispatch.md` 入 constitutional
- AGENTS.md CTO + CMO + CSO + CFO + Secretary 加 "1 dispatch ≤ 1 deliverable" 硬规则
- ForgetGuard rule `multi_task_dispatch_disguise`: dispatch prompt 含 "+" "and" 连接 N 个独立 deliverable → warn

### W21: R2 增量 commit 强制
- sub-agent prompt template 加 "硬规则: 每个 file change 必 commit (WIP 也行) + push"
- ForgetGuard rule `subagent_no_commit_after_5_writes`: 5 个 Write/Edit 后没 commit → CIEU event

### W22: R3 共享状态读 (parallel-aware)
- sub-agent boot prompt 强制 "读 .czl_subgoals.json + git log -10 才能开始"
- 写入 sub-agent template

### W23: R4 daemon stateless 重写 (AMENDMENT-016 v2)
- `_hook_daemon.py` 去缓存，每 hook 调用时 freshly read `.ystar_active_agent`
- Test 连续 5 sub-agent identity 切换全成功

### W24: R5 CEO 自律 (1 dispatch = 1 deliverable)
- CEO 自己的 prompt 模板加自检
- AGENTS.md CEO section 加硬规则

### W25: R6 mid-stream check-in 协议
- CEO 派 sub-agent ≥30 tool_uses budget 时，必 schedule SendMessage 在 15 tool_uses 时 ping
- ForgetGuard rule `ceo_no_midstream_checkin`: dispatch 后 30 min 无 SendMessage → warn

## 预期效果

修完 6 件后：
- Sub-agent 截断率从 ~80% (8/11 today) 降到 < 20%
- CEO patch 频率从 ~每 sub-agent 1 次降到 ~每 5 sub-agent 1 次
- Sub-agent 平均 tool_uses 从 30+ 降到 15 以下（任务原子化效果）

## 不 fix 的代价

继续今天 pattern → 明天明天明天 sub-agent 还是同样模式失败 → CEO 越来越多 wrap commit 接管 engineering → CEO Engineering Boundary doctrine 形同虚设 → CZL 退化回 prose-claim 时代。
