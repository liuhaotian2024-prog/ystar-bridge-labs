# Sub-Agent Boot Prompt Template

**Constitutional, non-violable, Board 2026-04-15 night, fixes parallel-blindness R3 root cause**  
**Updated 2026-04-16 — Action Model v2 spec integration (Ethan #127 + Maya CZL-129)**

Canonical reference: `governance/action_model_v2.md` §2 (Phase A dispatch) + §3 (Phase C receipt).

## 所有 sub-agent dispatch prompt 必含此 boot context

CEO/CTO 派 sub-agent 时 prompt **必须**含以下 boot context 段（在任务描述之前）：

```
## BOOT CONTEXT — Action Model v2 Phase A (5 steps mandatory, ≤5 tool_uses)

**Atomic class**: [Heavy|Light|Investigation] — declare upfront per governance/action_model_v2.md §3

**Phase A: Pre-Dispatch (5 steps)**

1. Read `.czl_subgoals.json` — 当前 campaign / current_subgoal / 已完成项 / 剩余项
2. **Pre-build routing gate**: If atomic involves writing NEW file in `governance/` or `Y-star-gov/ystar/governance/`, run `python3 scripts/precheck_existing.py <component_name>` BEFORE Write tool. If `matches.count > 0`, atomic MUST be reframed to EXTEND existing file OR justify BUILD_NEW with explicit reason in receipt citing precheck JSON.
3. Run `git log -5 --oneline` — 最近 5 commits 看其他 sub-agent 在干啥 (reduced from 10 per v2 spec)
4. Run `python3 scripts/session_watchdog.py --statusline` — capture AC pre-baseline (compare post-execution in Phase C step 12)
5. Run `pgrep -fl k9_routing_subscriber` — K9 daemon census (verify supervision chain alive)

## Phase C: Post-Dispatch Receipt Requirements

**Heavy atomic (17-step)**: Receipt MUST include 9 Phase C steps:
- **9. Test** — pytest output (if code change) or synthetic compliance/violation cases (if spec change)
- **10. Verification** — empirical paste: `ls -la <artifact>` + `wc -w <spec.md>` + `grep -E '^## ' <spec.md>` (anti-hallucination protocol per CZL-114)
- **11. Experiment** — smoke test on 5-10 sample corpus (synthetic violations for spec, dev dataset for code, staging for config)
- **12. AC delta** — `session_watchdog.py --statusline` again, compare to step 4 baseline. If AC dropped >10 → root-cause investigation queued
- **13. K9 silent-fire audit** — `k9log/auditor.py --repo . --output reports/governance/k9_silent_fire_<atomic_id>.md` (catch false negatives)
- **14. CIEU emit** — explicit `ATOMIC_COMPLETE` (Rt+1=0) or `ATOMIC_FAILED` (Rt+1>0) event with metadata: atomic_id, agent_id, Rt+1, tool_uses, duration, artifact_paths, test_pass_count
- **15. Trust score delta** — update `knowledge/engineer_trust_scores.json`: Rt+1=0 + honest tool_uses → +0.05; Rt+1>0 self-caught → +0.02; CEO-caught → -0.10; hallucinated receipt → -0.20
- **16. Knowledge writeback** — append lesson to `MEMORY/feedback_<topic>.md` (general pattern), code docstring (implementation detail), or `governance/<spec>.md` (governance refinement)
- **17. Cascade trigger** — check Ecosystem Dependency Map (downstream dependencies). If atomic A ships → queue atomic B. Write to `scripts/.cascade_queue.json`

**Light atomic (6-step)**: Receipt MUST include Phase C steps 10 (verification) + 14 (CIEU emit)  
**Investigation atomic (4-step)**: Receipt MUST include Phase C step 14 (CIEU emit with report_path)

## 任务规则
- atomic single deliverable (Iron Rule 0.5)
- **NO git commit/push/add/reset** (CEO manages version control, sub-agent writes only)
- 禁选择题 / 请 Board shell (Iron Rule 0)
- 禁 idle "等指令"
- Receipt MUST be CIEU 5-tuple structured (Y*/Xt/U/Yt+1/Rt+1) ≤300 words
- Tool_uses claimed MUST match metadata exactly (±1 tolerance max, per-call granularity, no "Edit 6x" compression)
```

## Why

R3 根因实证（今晚多次 sub-agent 失败）：
- Ethan #3 不知道 Samantha 加了 .claude/tasks/ 写权 → 出选择题给 Board
- Sofia 不知道 Samantha #2 commit e37f195d → 报 "permission denial"
- CEO Samantha #4/#5 race → AGENTS.md duplicate IRON RULE 0

## ForgetGuard reference

`subagent_boot_no_state_read` rule (W22.1 backlog) 检 sub-agent 起始 N 个 tool_uses 含 .czl_subgoals.json read.
