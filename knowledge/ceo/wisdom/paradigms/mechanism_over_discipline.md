---
name: Mechanism > Discipline (靠制度不靠自律)
type: paradigm
discovered: 2026-04-16
trigger: CEO 全 session 反复违反自己写的 5-tuple 规则，直到 hook 真拦才停；Board "不要靠自律管理公司，要靠机制"
depth: foundational
---

## Claim
任何需要 agent 记住才能执行的规则，最终一定会被忘记。正确做法：把规则编入 hook/script/cron 自动执行，agent 忘不忘都不影响。

## Evidence
- CEO 自己写了 MEMORY rule `feedback_ceo_reply_must_be_5tuple`，然后整个 session 前半段没用 5-tuple
- CEO 写了 `feedback_god_view_before_build`，然后 CZL-113/114/115 全造轮子
- CEO 写了 `feedback_no_deferred_dispatch_promise`，然后多次 "下波派 X" 没同轮 spawn
- 规律：MEMORY rule = 社会压力 = 最终遗忘率 100%

## Reasoning Chain
1. Agent 每 session 重生 → 规则必须重新加载 → 加载了也不保证执行
2. Hook/script = 无条件执行 → 不靠 agent 记忆 → 执行率 100%
3. 人类公司也一样：法律（强制） > 道德（自律） > 倡议（可选）
4. 类比：安全带法律 vs "请系安全带"提示 → 法律效果 100x

## Counterfactual
If keep self-discipline only: violation rate stays ~50% (today's empirical), eventually drift to 100%
If mechanism enforced: violation rate → 0% (hook blocks before output)

## Application
CEO 发现自己在写 MEMORY rule 而不是写 hook/script → STOP → 问 "能自动化吗？" → YES → 写 hook → NO → 才写 MEMORY rule
每条 MEMORY rule 都应有对应的"升级路径"：MEMORY → FG rule → hook enforce → auto-fix

## Connections
→ feedback_team_enforce_asymmetry (shipped ≠ live)
→ action_model_v2 Phase C auto (CZL-133 automated trust/writeback/cascade)
→ whitelist_over_blacklist (whitelist = mechanism; blacklist = detection = still needs discipline to act on)
→ 手动 vs 自动化矩阵 (11 items: 5 automated, 4 P0, 2 P1)
