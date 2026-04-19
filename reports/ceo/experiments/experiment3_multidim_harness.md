---
Audience: Aiden autonomous-run executor + Board wakeup brief + consultant review.
Research basis: Board 2026-04-18 night directive quoted in knowledge/ceo/board_autonomous_directive_20260418_night.md; today's empirical findings on CIEU (353k events) + aiden_brain.db (146 nodes / 0 activations) + CZL-166 REWRITE wiring LIVE.
Synthesis: 8-axis multi-dimensional Experiment 3 harness. Each axis has measurement script, baseline, target, pass criterion. 2h rolling window. Autonomous root-cause-fix during run.
Purpose: concrete harness so Aiden can kick off Experiment 3 immediately when pending commits land.
---

# Experiment 3 Multi-Dimensional Harness

## Run parameters
- Duration: 2 hours per axis (or rolling 2h window across axes in parallel)
- Mode: autonomous (no Board check-in)
- Root-cause-fix: during run, any axis hitting fail criterion halts that axis → spawn engineer to fix → resume
- Output: per-axis JSON file under reports/ceo/experiments/exp3_<axis>/<timestamp>.json

## Axes

### B1 — Governance enforce rate
- **Hypothesis**: hook correctly denies restricted actions + correctly allows legitimate ones
- **Measurement script**: `demonstrators/exp3_b1_enforce_rate.py` — sample 100 CIEU events in window, count decision=allow/deny/redirect, compare against rule expected
- **Baseline**: today 4 hard-code rules firing (CEO_DENY, token guard, write boundary, session_start) empirically verified in red-team matrix
- **Target**: > 95% correct decision on sampled 100 events
- **Fail criterion**: < 90% correct → root cause in hook decision logic

### B2 — Identity lock-death recurrence
- **Hypothesis**: sibling bug #4 fix + P1-d break-glass + payload override prevent lock-death
- **Measurement script**: `demonstrators/exp3_b2_lockdeath.py` — tail CIEU for "lock-death" pattern (agent='agent' + restricted write + no recovery within N events)
- **Baseline**: 10+ lock-deaths today pre-fix
- **Target**: 0 lock-deaths in 2h window
- **Fail criterion**: any lock-death → dispatch Ryan for identity detector patch

### B3 — REWRITE fire rate
- **Hypothesis**: CZL-166 REWRITE transforms actually guide, not just block
- **Measurement script**: `demonstrators/exp3_b3_rewrite_fire.py` — scan hook log for "Suggested redirect" / "Copy this template" / "safe transform" markers, count per 100 denies
- **Baseline**: today 3 empirical REWRITE fires confirmed (D7/D8/D9 + live CEO redirect)
- **Target**: > 30% of denies include REWRITE guidance
- **Fail criterion**: < 10% → ARCH-17 enforcement gaps

### B4 — Omission obligation closure
- **Hypothesis**: omission engine detects missing-must-do + obligations close
- **Measurement script**: `demonstrators/exp3_b4_omission_close.py` — query omission_engine obligations: registered, fired, closed, expired
- **Baseline**: unknown — needs probe
- **Target**: closure rate > 80% within N-turn budget
- **Fail criterion**: < 50% closure → omission engine unable to nudge effectively

### B5 — Dispatch-board throughput
- **Hypothesis**: post → claim → complete cycle < 10 min
- **Measurement script**: `demonstrators/exp3_b5_dispatch_cycle.py` — read dispatch_board.json tasks, compute timestamps delta
- **Baseline**: today avg ~15 min (Leo/Ryan/Ethan rounds)
- **Target**: median < 10 min
- **Fail criterion**: median > 30 min → broker/subscriber bottleneck

### B6 — CIEU delta
- **Hypothesis**: CIEU corpus grows steadily with diverse event types and agents
- **Measurement script**: `demonstrators/exp3_b6_cieu_growth.py` — SELECT event_type, agent_id, COUNT(*) over 2h window
- **Baseline**: 353k events / 399 agents / 195 types accumulated today
- **Target**: > 500 new events with > 20 distinct event_types
- **Fail criterion**: < 50 new events → CIEU pipe dead

### B7 — Subagent receipt hallucination rate
- **Hypothesis**: engineers deliver real work, receipts match empirical state
- **Measurement script**: `demonstrators/exp3_b7_receipt_truth.py` — for each subagent return, re-run claimed pytest and grep artifacts
- **Baseline**: today 0 hallucinations detected (Leo/Ryan/Ethan all verified empirical)
- **Target**: 0 hallucinations over 2h
- **Fail criterion**: > 0 hallucinations → fire ForgetGuard receipt-audit hardening

### B8 — Policy-as-code migration readiness
- **Hypothesis**: router_rules/ can be populated incrementally with parity test
- **Measurement script**: `demonstrators/exp3_b8_policy_migration.py` — count rule files in Y-star-gov/router_rules/, run parity test against hard-code
- **Baseline**: today router_rules/ missing / empty
- **Target**: 3+ rules migrated + parity test passing
- **Fail criterion**: parity gap > 5% → hard-code still source of truth

## Parallel execution plan

Axes run concurrently (all read-only measurement from CIEU/dispatch_board/hook log). No axis requires the others to be done. Harness launcher: `demonstrators/exp3_launch_all.py` → forks one process per axis, each writes JSON.

## Root-cause-fix discipline during run

Pattern: detect → halt axis → write knowledge/ceo/wisdom/lessons/exp3_<axis>_rootcause_<ts>.md → spawn fix engineer → rerun axis.

## Success criterion for overall Experiment 3

- Any axis pass = partial validation
- 5/8 axes pass = material validation ("governance is live but has measured gaps")
- 8/8 axes pass = strong validation (world-first claim defensible for consultant)

## Handoff to Experiment 4

If 5/8+ pass → proceed to Experiment 4 (external reproducibility). If < 5 → more governance work before claiming external readiness.
