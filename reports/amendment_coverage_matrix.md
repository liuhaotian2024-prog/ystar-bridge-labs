# Amendment Coverage Matrix Audit

**Generated:** amendment_coverage_audit.py at Mon Apr 13 10:51:24 EDT 2026

## Summary

| Metric | Count | % Coverage |
|--------|-------|------------|
| Total Rules | 51 | 100% |
| Remediation Filled | 32 | 62% |
| Has Fulfiller | 1 | 1% |
| Has Test | 51 | 100% |

## Coverage Matrix

| Rule Class | Rule Name | Remediation | Fulfiller | Test | Last Tested |
|------------|-----------|-------------|-----------|------|-------------|
| behavior_rule | `autonomous_mission_requires_article_11` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `board_approval_before_publish` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `completion_requires_cieu_audit` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `content_length_check` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `counterfactual_before_major_decision` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `directive_decompose_within_minutes` | ❌ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `document_requires_execution_plan` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `extract_board_values_on_session_close` | ❌ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `must_check_health_on_session_start` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `must_dispatch_via_cto` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `no_choice_questions` | ❌ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `no_fabrication` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `pre_commit_requires_test` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `real_conversation_count_required` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `role_context` | ❌ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `root_cause_fix_required` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `session_close_required` | ❌ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `source_first_fixes` | ✅ | ❌ | ✅ | 2026-04-13 |
| behavior_rule | `verification_before_assertion` | ✅ | ❌ | ✅ | 2026-04-13 |
| obligation | `autonomous_daily_report` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `directive_acknowledgement` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `gemma_session_daily` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `intent_declaration` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `knowledge_update` | ✅ | ✅ | ✅ | 2026-04-04 |
| obligation | `progress_update` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `task_completion_report` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `theory_library_daily` | ✅ | ❌ | ✅ | 2026-04-04 |
| obligation | `weekly_roadmap_audit` | ✅ | ❌ | ✅ | 2026-04-04 |
| write_boundary | `immutable:AGENTS.md` | ✅ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `immutable:.claude/agents/` | ✅ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `immutable:CLAUDE.md` | ✅ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `immutable:knowledge/secretary/role_definition/` | ✅ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:DIRECTIVE_TRACKER.md` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:memory/session_handoff.md` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:.ystar_active_agent` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:.ystar_session.json` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:AGENTS.md` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:.claude/agents/` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:reports/priority_brief.md` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:memory/boot_packages/` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:memory/boot_packages/history/` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `restricted:governance/SECRETARY_CHARTER.md` | ❌ | ❌ | ✅ | 2026-04-13 |
| write_boundary | `ceo_deny:./src/` | ❌ | ❌ | ✅ | 2026-04-13 |
| delegation | `delegate:board→ceo` | ❌ | ❌ | ✅ | 2026-04-13 |
| delegation | `delegate:ceo→cto` | ❌ | ❌ | ✅ | 2026-04-13 |
| delegation | `delegate:cto→eng-kernel` | ❌ | ❌ | ✅ | 2026-04-13 |
| intent_guard | `intent_guard:governance/` | ✅ | ❌ | ✅ | 2026-04-01 |
| intent_guard | `intent_guard:agents/` | ✅ | ❌ | ✅ | 2026-04-01 |
| intent_guard | `intent_guard:README.md` | ✅ | ❌ | ✅ | 2026-04-01 |
| intent_guard | `intent_guard:scripts/record_intent.py` | ✅ | ❌ | ✅ | 2026-04-01 |
| intent_guard | `intent_guard:scripts/check_intents.py` | ✅ | ❌ | ✅ | 2026-04-01 |

## Gaps: Missing Remediation

- ❌ `directive_decompose_within_minutes` (behavior_rule)
- ❌ `extract_board_values_on_session_close` (behavior_rule)
- ❌ `no_choice_questions` (behavior_rule)
- ❌ `role_context` (behavior_rule)
- ❌ `session_close_required` (behavior_rule)
- ❌ `restricted:DIRECTIVE_TRACKER.md` (write_boundary)
- ❌ `restricted:memory/session_handoff.md` (write_boundary)
- ❌ `restricted:.ystar_active_agent` (write_boundary)
- ❌ `restricted:.ystar_session.json` (write_boundary)
- ❌ `restricted:AGENTS.md` (write_boundary)
- ❌ `restricted:.claude/agents/` (write_boundary)
- ❌ `restricted:reports/priority_brief.md` (write_boundary)
- ❌ `restricted:memory/boot_packages/` (write_boundary)
- ❌ `restricted:memory/boot_packages/history/` (write_boundary)
- ❌ `restricted:governance/SECRETARY_CHARTER.md` (write_boundary)
- ❌ `ceo_deny:./src/` (write_boundary)
- ❌ `delegate:board→ceo` (delegation)
- ❌ `delegate:ceo→cto` (delegation)
- ❌ `delegate:cto→eng-kernel` (delegation)

## Gaps: Missing Fulfiller

- ❌ `autonomous_mission_requires_article_11` (behavior_rule)
- ❌ `board_approval_before_publish` (behavior_rule)
- ❌ `completion_requires_cieu_audit` (behavior_rule)
- ❌ `content_length_check` (behavior_rule)
- ❌ `counterfactual_before_major_decision` (behavior_rule)
- ❌ `directive_decompose_within_minutes` (behavior_rule)
- ❌ `document_requires_execution_plan` (behavior_rule)
- ❌ `extract_board_values_on_session_close` (behavior_rule)
- ❌ `must_check_health_on_session_start` (behavior_rule)
- ❌ `must_dispatch_via_cto` (behavior_rule)
- ❌ `no_choice_questions` (behavior_rule)
- ❌ `no_fabrication` (behavior_rule)
- ❌ `pre_commit_requires_test` (behavior_rule)
- ❌ `real_conversation_count_required` (behavior_rule)
- ❌ `role_context` (behavior_rule)
- ❌ `root_cause_fix_required` (behavior_rule)
- ❌ `session_close_required` (behavior_rule)
- ❌ `source_first_fixes` (behavior_rule)
- ❌ `verification_before_assertion` (behavior_rule)
- ❌ `autonomous_daily_report` (obligation)
- ❌ `directive_acknowledgement` (obligation)
- ❌ `gemma_session_daily` (obligation)
- ❌ `intent_declaration` (obligation)
- ❌ `progress_update` (obligation)
- ❌ `task_completion_report` (obligation)
- ❌ `theory_library_daily` (obligation)
- ❌ `weekly_roadmap_audit` (obligation)
- ❌ `immutable:AGENTS.md` (write_boundary)
- ❌ `immutable:.claude/agents/` (write_boundary)
- ❌ `immutable:CLAUDE.md` (write_boundary)
- ❌ `immutable:knowledge/secretary/role_definition/` (write_boundary)
- ❌ `restricted:DIRECTIVE_TRACKER.md` (write_boundary)
- ❌ `restricted:memory/session_handoff.md` (write_boundary)
- ❌ `restricted:.ystar_active_agent` (write_boundary)
- ❌ `restricted:.ystar_session.json` (write_boundary)
- ❌ `restricted:AGENTS.md` (write_boundary)
- ❌ `restricted:.claude/agents/` (write_boundary)
- ❌ `restricted:reports/priority_brief.md` (write_boundary)
- ❌ `restricted:memory/boot_packages/` (write_boundary)
- ❌ `restricted:memory/boot_packages/history/` (write_boundary)
- ❌ `restricted:governance/SECRETARY_CHARTER.md` (write_boundary)
- ❌ `ceo_deny:./src/` (write_boundary)
- ❌ `delegate:board→ceo` (delegation)
- ❌ `delegate:ceo→cto` (delegation)
- ❌ `delegate:cto→eng-kernel` (delegation)
- ❌ `intent_guard:governance/` (intent_guard)
- ❌ `intent_guard:agents/` (intent_guard)
- ❌ `intent_guard:README.md` (intent_guard)
- ❌ `intent_guard:scripts/record_intent.py` (intent_guard)
- ❌ `intent_guard:scripts/check_intents.py` (intent_guard)

## Gaps: Missing Tests

✅ All rules have test coverage

## Next Steps

1. **Remediation Gaps (19)**: Add Remediation() to boundary_enforcer.py or obligation_remediation.py
2. **Fulfiller Gaps (50)**: Add auto-fulfillment logic to obligation_triggers.py or boundary_enforcer.py
3. **Test Gaps (0)**: Add test cases to Y-star-gov/tests/test_*.py

## Notes

- **Remediation**: Structured guidance when rule is violated (AMENDMENT-012)
- **Fulfiller**: Auto-fulfillment code that proactively satisfies obligations (AMENDMENT-012)
- **Test**: Automated test coverage in Y-star-gov test suite
- **Last Tested**: File mtime of test file containing rule name (heuristic)

Write boundaries and delegation chains typically don't have fulfillers (enforcement only).
Obligations should have both remediation AND fulfiller (teach how + auto-fix when possible).
