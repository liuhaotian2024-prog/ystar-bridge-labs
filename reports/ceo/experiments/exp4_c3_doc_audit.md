---
Phase: C3 — Consultant-Readable Documentation Audit
Date: 2026-04-19
Author: eng-platform (Ryan Park)
Purpose: Inventory of all artifacts a consultant/CTO would need to evaluate Y*gov
---

# C3: Documentation & Artifact Audit for External Review

## 1. Architecture Specifications

| Spec | Path | Lines | Status |
|------|------|-------|--------|
| ARCH-17 Behavioral Governance | `Y-star-gov/docs/arch/arch17_behavioral_governance_spec.md` | 846 | PRESENT |
| ARCH-17 (Labs mirror) | `ystar-company/docs/arch17_behavioral_governance_spec.md` | exists | PRESENT (secondary copy) |
| ARCH-17 (CTO knowledge) | `ystar-company/knowledge/cto/arch17_behavioral_governance_spec.md` | exists | PRESENT (tertiary copy) |
| ARCH-18 Rewrite Guidance | NOT FOUND in `Y-star-gov/docs/arch/` | - | MISSING |

**Note**: ARCH-18 (Rewrite/Guidance spec) was referenced in Board directive but no standalone spec file exists yet. The rewrite functionality is implemented in code (`boundary_enforcer.py` REWRITE transforms) but lacks a formal architecture document.

## 2. Experiment Reports

| Report | Path | Status |
|--------|------|--------|
| Exp 3 Multi-dim Harness | `ystar-company/reports/ceo/experiments/experiment3_multidim_harness.md` | PRESENT |
| Exp 3 B1 (Enforce Rate) | `ystar-company/reports/ceo/experiments/exp3_b1/` | PRESENT (directory) |
| Exp 3 B2 (Lock-Death) | `ystar-company/reports/ceo/experiments/exp3_b2/` | PRESENT (directory) |

## 3. Task Receipts (24 total)

All in `ystar-company/reports/receipts/`:

| Receipt | Task |
|---------|------|
| CZL-ARCH-1.md | Architecture task 1 |
| CZL-ARCH-1-followup.md | Follow-up |
| CZL-ARCH-2.md | Architecture task 2 |
| CZL-ARCH-3.md | Architecture task 3 |
| CZL-ARCH-4.md | Architecture task 4 |
| CZL-ARCH-6.md | Architecture task 6 |
| CZL-ARCH-7.md | Architecture task 7 |
| CZL-ARCH-8.md | Architecture task 8 |
| CZL-ARCH-9.md | Architecture task 9 |
| CZL-ARCH-10.md | Architecture task 10 |
| CZL-ARCH-11a.md | Architecture task 11a |
| CZL-ARCH-11b.md | Architecture task 11b |
| CZL-ARCH-11c.md | Architecture task 11c |
| CZL-ARCH-11d.md | Architecture task 11d |
| CZL-ARCH-14.md | Architecture task 14 |
| CZL-P1-b.md | Phase 1 task b |
| CZL-P1-c.md | Phase 1 task c |
| CZL-P1-d.md | Phase 1 task d |
| CZL-P2-a.md | Phase 2 task a |
| CZL-P2-c-PAUSED.md | Phase 2 task c (paused) |
| CZL-REFACTOR-LABS-NAMES.md | Labs name refactor |
| CZL-WATCHDOG-STUCK.md | Stuck claim watchdog |
| CZL-WIRE-1.md | Wire task 1 |
| CZL-WIRE-2.md | Wire task 2 |

## 4. Demonstrator Scripts

All in `ystar-company/reports/ceo/demonstrators/`:

| Script | Purpose |
|--------|---------|
| exp3_b1_enforce_rate.py | Measure governance enforce deny/allow ratio |
| exp3_b2_lockdeath.py | Detect identity lock-death recurrence |
| goal_1_hook_coverage_measure.py | Measure hook coverage across tool calls |
| goal_1_output.json | Hook coverage measurement output |
| goal_2_next_action_inject_pattern.py | Test next-action injection pattern |
| goal_2_output.txt | Injection pattern output |
| goal_3_rule_lifecycle_scan.py | Scan rule lifecycle completeness |
| goal_3_output.md | Rule lifecycle scan output |
| goal_4_ystar_symbol_liveness.py | Verify Y*gov symbols are live (not dead code) |
| goal_4_output.md | Symbol liveness output |

Additional:
- `ystar-company/tools/cieu/ygva/layer_demo.py` — CIEU layer demonstration
- `ystar-company/tests/demo_rle_e2e.py` — Rule lifecycle E2E demo

## 5. README.md Sufficiency

| Item | Status | Notes |
|------|--------|-------|
| README exists | YES | 841 lines |
| Installation instructions | NEEDS REVIEW | pip install path may need update |
| Quick start | NEEDS REVIEW | ystar doctor / hook-install flow |
| Architecture overview | PARTIAL | References exist but may be outdated |
| License (MIT) | PRESENT | |
| Contributing guide | UNKNOWN | Not checked |

**Grade: B-** — README is substantial (841 lines) but may contain stale references from rapid development. A consultant would benefit from a "start here" section that points to ARCH-17 and the demonstrator scripts.

## 6. Gaps for Consultant Readiness

1. **ARCH-18 spec missing** — Rewrite/Guidance architecture is implemented but undocumented as standalone spec
2. **No single entry-point doc** — Consultant must navigate multiple directories; a "Consultant Start Here" section in README would help
3. **Receipt naming** — CZL-ARCH-N convention is internal; external reviewer needs a mapping to feature names
4. **Experiment reports** — Exp 3 harness exists but Exp 4 (this report) is being created now
