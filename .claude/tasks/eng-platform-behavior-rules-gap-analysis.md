# Behavior Rules Gap Analysis
**Date**: 2026-04-11
**Agent**: eng-platform (Ryan Park)
**Task**: Scan all governance docs for unenforced rules

---

## Current Status: 10 Rules Implemented in boundary_enforcer.py

**DENY rules (block execution):**
1. `autonomous_mission_requires_article_11` - Autonomous missions need 7-layer construction
2. `must_dispatch_via_cto` - CEO cannot spawn eng-* directly

**WARNING rules (log but don't block):**
3. `verification_before_assertion` - Cannot assert impossibility without verification
4. `root_cause_fix_required` - Bug fixes must have prevention actions
5. `document_requires_execution_plan` - Policy docs must be followed by execution
6. `no_fabrication` - Cannot cite data without verification
7. `counterfactual_before_major_decision` - Major decisions need counterfactual
8. `must_check_health_on_session_start` - First 5 calls include health check
9. `completion_requires_cieu_audit` - Task completion must audit CIEU for Rt=0
10. `extract_board_values_on_session_close` - Extract Board values on session close (not checked in runtime)

---

## MISSING RULES FROM GOVERNANCE DOCS

### From agent-behavior-rules-spec.md (NOT YET IMPLEMENTED):

**CTO:**
- `pre_commit_requires_test` - commit前必须跑测试全过
- `source_first_fixes` - bug fix必须在Y-star-gov源码做，不能改site-packages
- `fix_log_required` - 每次fix后写reports/cto_fix_log.md

**CEO:**
- `directive_decompose_within_minutes: 10` - Board指令10分钟内分解
- `session_close_required` - session结束必须运行session_close_yml.py
- `twin_evolution_on_board_session` - Board参与的session必须运行twin_evolution

**Secretary:**
- `weekly_audit_required` - 每周一审计6岗位义务履约率
- `audit_day: "monday"`
- `dna_distillation_requires_sources` - DNA蒸馏必须附来源

**CMO:**
- `content_length_check` - 发布前检查平台字数限制
- `board_approval_before_publish` - 外部发布需Board批准

**CFO:**
- No new rules beyond existing `no_fabrication`
- `data_source_required` already covered by `no_fabrication`

**CSO:**
- `real_conversation_count` - 日报必须包含真实外部对话数量

---

### From AGENTS.md Constitutional Rules:

**Universal (all agents):**
- `禁止出选择题` - No multiple choice questions (cannot be code-enforced, LLM behavior)
- `session_boot_required` - Must run session_boot_yml.py (obligation system handles this)
- `restart_now_compliance` - Must comply with RESTART_NOW signals (outside hook scope)

**CEO-specific:**
- `k9_inbox_check_frequency` - Must check K9 inbox at session start + every 3-4 interactions
- `directive_tracker_update_on_session_end` - Update DIRECTIVE_TRACKER.md status
- `board_briefing_required` - Write human-readable briefing to BOARD_PENDING.md

**CTO-specific:**
- `pre_change_health_check` - Must run `ystar check-impact` before modifying critical files
- `post_change_verification` - Must run `ystar doctor --layer1` after git commit
- `release_verify_after_push` - Must run `ystar release-verify` after push to main
- `pypi_publish_requires_checks` - Must verify before PyPI upload

**All Engineering (CTO + 4 eng-*):**
- `test_gate_before_commit` - All tests must pass before commit
- `silent_exception_forbidden` - Every except block must log context

---

### From WORKING_STYLE.md:

**Level 2/3 directives:**
- `precheck_required_for_level_2_3` - Level 2/3 directives need gov_precheck (this is for gov_precheck tool, not boundary_enforcer)

---

## TECHNICAL FEASIBILITY ANALYSIS

### Can Implement Now (Hook Runtime):

1. **pre_commit_requires_test** - Check if Bash command contains "git commit" without prior test run
2. **source_first_fixes** - Deny Write/Edit to site-packages paths
3. **directive_decompose_within_minutes** - Track time from directive receipt to DIRECTIVE_TRACKER.md write
4. **content_length_check** - Check Write content length against platform limits
5. **board_approval_before_publish** - Deny Write to outreach/ without approval marker
6. **real_conversation_count** - Check Write to daily reports contains conversation count

### Should Be Obligation (Not Hook):

7. **fix_log_required** - Obligation timeout after fix completion
8. **session_close_required** - Obligation at session end
9. **twin_evolution_on_board_session** - Obligation when Board active
10. **weekly_audit_required** - Weekly obligation
11. **k9_inbox_check_frequency** - Obligation triggered by time/interaction count
12. **directive_tracker_update_on_session_end** - Session-end obligation

### Cannot Code-Enforce (LLM Behavior):

13. **禁止出选择题** - Requires LLM output analysis
14. **dna_distillation_requires_sources** - Requires content understanding
15. **board_briefing_quality** - Requires content understanding

### Already Handled Elsewhere:

16. **test_gate_before_commit** - Pre-commit hook in git (not Y*gov hook)
17. **pre_change_health_check** - CLI workflow, not hook
18. **post_change_verification** - CLI workflow, not hook
19. **release_verify_after_push** - CLI workflow, not hook

---

## IMPLEMENTATION PLAN

### Phase 1: Add 6 New Hook Rules (This Session)

1. `pre_commit_requires_test` (CTO + eng-*) - DENY
2. `source_first_fixes` (CTO + eng-*) - DENY
3. `directive_decompose_timeout` (CEO) - WARNING
4. `content_length_check` (CMO) - WARNING
5. `board_approval_before_publish` (CMO, CSO) - DENY
6. `real_conversation_count_required` (CSO) - WARNING

### Phase 2: Document Obligations (Next Session)

- Fix log obligation
- Session close obligation
- Twin evolution obligation
- Weekly audit obligation
- K9 inbox check obligation

---

## DECISION: IMPLEMENT PHASE 1 NOW

Adding 6 new enforceable rules to boundary_enforcer.py.
