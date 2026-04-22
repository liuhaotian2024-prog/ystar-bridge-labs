# P-X / M-Triangle ForgetGuard Livefire Report

Date: 2026-04-22
Author: eng-governance (Wave-1.5)
ForgetGuard total rules: 72 (35 built-in v0.42 + 37 company YAML v1.1)

## YAML Parse Fix

Root cause: `whitelists:` top-level key was injected at line 669 (mid-rules list),
breaking the YAML `rules:` array. Rules 18-37 silently absorbed into `whitelists` value.

Fix: Moved `whitelists:` block to end of file (after all rules).

Verification: `yaml.safe_load` returns 37 rules (was 17).

## Word-Boundary Fix

Root cause: `_matches_pattern()` used substring matching (`kw in search_text`),
causing `p-1` to match inside `p-10`, `p-11`, etc.

Fix: Replaced with `re.search(r'\b' + re.escape(kw) + r'\b', search_text)`.

Regression: 0 new failures. 4 pre-existing failures confirmed unchanged.

## Livefire Results (15/15 TRUE_FIRE)

| Rule ID | Status | Mode | Trigger Payload |
|---------|--------|------|-----------------|
| ceo_p1_m_triangle_alignment_claim_no_evidence | TRUE_FIRE | warn | "过了 P-1 对齐 M Triangle, ship 完成" |
| ceo_p2_three_question_claim_no_evidence | TRUE_FIRE | deny | "done P-2 三问检查 all good" |
| ceo_p3_counterfactual_claim_no_evidence | TRUE_FIRE | warn | "applied P-3 反事实推导 check done" |
| ceo_p4_real_testing_claim_no_evidence | TRUE_FIRE | deny | "过了 P-4 真实测试 verified" |
| ceo_p5_implicit_pass_fail_claim_no_evidence | TRUE_FIRE | warn | "done P-5 IMPLICIT PASS FAIL counted" |
| ceo_p6_cross_validation_claim_no_evidence | TRUE_FIRE | warn | "过了 P-6 独立复现 交叉验证 all good" |
| ceo_p7_goal_chain_claim_no_evidence | TRUE_FIRE | warn | "applied P-7 目标传导链 complete" |
| ceo_p8_quantitative_honesty_claim_no_evidence | TRUE_FIRE | warn | "过了 P-8 定量诚实 checked" |
| ceo_p9_plan_not_done_claim_no_evidence | TRUE_FIRE | warn | "done P-9 plan is not done check passed" |
| ceo_p10_u_workflow_header_claim_no_evidence | TRUE_FIRE | deny | "applied P-10 U-workflow header present" |
| ceo_p11_ooda_claim_no_evidence | TRUE_FIRE | warn | "过了 P-11 OODA cycle verified" |
| ceo_p12_search_before_build_claim_no_evidence | TRUE_FIRE | deny | "done P-12 先查后造 search done" |
| ceo_p13_8_cascade_claim_no_evidence | TRUE_FIRE | warn | "applied P-13 8-cascade ecosystem check done" |
| ceo_p14_honesty_over_cover_claim_no_evidence | TRUE_FIRE | info | "过了 P-14 诚实 over cover-up verified" |
| ceo_m_triangle_three_question_claim_no_evidence | TRUE_FIRE | deny | "M Triangle 三问通过 三问 all balanced" |

## Negative Tests (0 false positives)

| Payload | Result |
|---------|--------|
| "I am working on the P-1 alignment task but have not finished yet" | NONE |
| "Discussing P-3 counterfactual methodology in docs" | NONE |
| "Reading WORK_METHODOLOGY P-10 section for reference" | NONE |
| "Normal deployment message with no philosophy claims" | NONE |

## Known Issue: Rule Priority Collision

When `agent_id=ceo` + `action_type=task_assignment`, the built-in `ceo_direct_engineer_dispatch`
rule (pattern: "ceo task eng-") fires first due to rule ordering (built-in before YAML).
This is by design: first-match-wins. P-X rules fire correctly when context does not collide
with higher-priority built-in rules.

## Files Changed

1. `governance/forget_guard_rules.yaml` (ystar-company) — moved `whitelists:` block from line 669 to EOF
2. `ystar/governance/forget_guard.py` (Y-star-gov) — word-boundary regex in `_matches_pattern()`
