# Y*gov Hard Constraints Index

> **WARNING: This file is a human-readable INDEX only.**
> The execution sources are `.ystar_session.json` (declarative config) and
> `Y-star-gov/ystar/adapters/boundary_enforcer.py` (runtime enforcement).
> Do NOT treat this file as the source of truth. If this file and the execution
> sources disagree, the execution sources win.

**Total constraint items: 193 across 11 categories**
**Last verified: governance_boot.sh output (run at session start)**

---

## Category 1: Immutable Paths (2 items)

Paths that NO agent can modify (except secretary via override_roles).

| # | Pattern | Type | Effect |
|---|---------|------|--------|
| 1 | `AGENTS.md` | File | DENY write — governance charter |
| 2 | `.claude/agents/` | Directory | DENY write — agent definitions |

- **Declaration**: `.ystar_session.json` -> `immutable_paths.patterns`
- **Enforcement**: `boundary_enforcer.py` -> `_check_immutable_paths()`
- **Override**: Only `secretary` role (via `immutable_paths.override_roles`)

---

## Category 2: Contract Deny Paths (3 items)

Absolute paths denied for ALL agents.

| # | Path | Effect |
|---|------|--------|
| 1 | `/etc` | DENY all access |
| 2 | `/root` | DENY all access |
| 3 | `/production` | DENY all access |

- **Declaration**: `.ystar_session.json` -> `contract.deny`
- **Enforcement**: `boundary_enforcer.py` -> write boundary check

---

## Category 3: Contract Deny Commands (4 items)

Shell commands denied for ALL agents.

| # | Command | Effect |
|---|---------|--------|
| 1 | `rm -rf` | DENY execution |
| 2 | `sudo` | DENY execution |
| 3 | `DROP TABLE` | DENY execution |
| 4 | `ystar setup --yes` | DENY execution |

- **Declaration**: `.ystar_session.json` -> `contract.deny_commands`
- **Enforcement**: Hook daemon Bash tool interception

---

## Category 4: Restricted Write Paths (6 items)

Paths writable only by specific roles.

| # | Path | Allowed Roles | Effect |
|---|------|---------------|--------|
| 1 | `DIRECTIVE_TRACKER.md` | ceo | DENY others |
| 2 | `memory/session_handoff.md` | ceo | DENY others |
| 3 | `.ystar_active_agent` | secretary | DENY others |
| 4 | `.ystar_session.json` | secretary | DENY others |
| 5 | `AGENTS.md` | secretary | DENY others |
| 6 | `.claude/agents/` | secretary | DENY others |

- **Declaration**: `.ystar_session.json` -> `restricted_write_paths`
- **Enforcement**: `boundary_enforcer.py` -> `_check_restricted_write_paths()`

---

## Category 5: CEO Deny Paths (2 items)

Paths the CEO is specifically forbidden from writing (no code, no src).

| # | Path | Effect |
|---|------|--------|
| 1 | `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/` | DENY CEO write |
| 2 | `./src/` | DENY CEO write |

- **Declaration**: `.ystar_session.json` -> `ceo_deny_paths`
- **Enforcement**: `boundary_enforcer.py` -> write boundary check (agent=ceo)

---

## Category 6: Agent Write Path Boundaries (10 agents)

Each agent can ONLY write to their designated paths. Writing outside = DENY.

| # | Agent | Allowed Write Paths |
|---|-------|---------------------|
| 1 | ceo | `./reports/`, `./BOARD_PENDING.md`, `./DISPATCH.md`, `./OKR.md`, `./DIRECTIVE_TRACKER.md`, `./OPERATIONS.md`, `./WEEKLY_CYCLE.md`, `./knowledge/` |
| 2 | cto | `./src/`, `./tests/`, `./products/`, `./docs/`, `./.github/`, `./CHANGELOG.md`, Y-star-gov repo, `./scripts/`, `./CLAUDE.md` |
| 3 | cmo | `./content/`, `./marketing/` |
| 4 | cso | `./sales/` |
| 5 | cfo | `./finance/`, `./reports/` |
| 6 | eng-kernel | (empty -- must work through CTO) |
| 7 | eng-governance | (empty -- must work through CTO) |
| 8 | eng-platform | (empty -- must work through CTO) |
| 9 | eng-domains | (empty -- must work through CTO) |
| 10 | k9 | `./research/`, `./knowledge/`, `./sales/feedback/` |

- **Declaration**: `.ystar_session.json` -> `agent_write_paths`
- **Enforcement**: `boundary_enforcer.py` -> `_check_write_boundary()`

---

## Category 7: Obligation Agent Scope (55+ obligations)

Each obligation is assigned to specific agents who MUST fulfill it within SLA.

| # | Obligation | Assigned To |
|---|-----------|-------------|
| 1 | respond_to_complaint | ceo |
| 2 | directive_decomposition | ceo |
| 3 | p0_bug_fix | cto |
| 4 | p1_bug_fix | cto |
| 5 | p2_bug_fix | cto |
| 6 | fix_log_entry | cto |
| 7 | article_source_verification | cmo |
| 8 | blog_first_draft | cmo |
| 9 | conversation_documentation | cso |
| 10 | lead_followup | cso |
| 11 | cfo_token_recording | cfo |
| 12 | monthly_financial_summary | cfo |
| 13 | weekly_cash_flow | cfo |
| 14 | knowledge_gap_bootstrap | * (all agents) |
| 15 | autonomous_daily_report | * |
| 16 | ceo_daily_consolidation | ceo |
| 17 | session_boot | * |
| 18 | ceo_delegation_dispatch | ceo |
| 19 | governance_pipeline_check | ceo |
| 20 | pre_commit_test | cto, eng-kernel, eng-governance, eng-platform, eng-domains |
| 21 | pipeline_health_verify | cto |
| 22 | content_accuracy_review | cmo |
| 23 | thinking_discipline_check | * |
| 24 | cross_review_critical_file | * |
| 25 | k9_inbox_check | ceo |
| 26 | commit_push_sync | * |
| 27 | cieu_liveness_check | * |
| 28 | cross_review_sla | * |
| 29 | escalation_response | ceo |
| 30 | security_incident_response | * |
| 31 | case_documentation | * |
| 32 | github_issue_triage | cto |
| 33 | social_media_board_approval | cmo, cso |
| 34 | distribution_verify_post_push | cto |
| 35 | hot_reboot_protocol | ceo |
| 36 | session_cleanup_boot_markers | ceo |
| 37 | k9_task_reply_check | ceo |
| 38 | session_handoff_update | ceo |
| 39 | board_session_lock_cleanup | ceo |
| 40 | pre_commit_silent_exception_check | cto, eng-* |
| 41 | readme_verify_section_update | cto |
| 42 | p2_task_definition_complete | cto, ceo |
| 43 | directive_tracker_check | ceo |
| 44 | directive_tracker_update | ceo |
| 45 | daemon_status_check | ceo |
| 46 | platform_research_before_write | cmo |
| 47 | k9_task_routing_check | ceo |
| 48 | ab_experiment_true_control | ceo |
| 49 | mandatory_agent_identity_check | * |
| 50 | cieu_liveness_enforcement_block | * |
| 51 | security_incident_auto_escalation | * |
| 52 | shell_command_approval | * |
| 53 | governance_loop_rate_limit | orchestrator |
| 54 | handoff_backpressure_check | * |
| 55 | escalation_resolution_timeout | ceo |

Additional: off_hours_activity_notification (*), path_a_mandatory_report (path_a_agent), diagnostic_agent_read_access (doctor_agent), mandatory_session_boot_record (*), weekly_cieu_behavioral_audit (eng-governance), task_acknowledgement (all named agents + jinjin)

- **Declaration**: `.ystar_session.json` -> `obligation_agent_scope`
- **Enforcement**: Hook daemon obligation tracking + CIEU recording

---

## Category 8: Agent Behavior Rules (88 boolean rules across 10 agents)

Boolean constraints enforced per-agent. Common rules applied to most/all agents:

| Rule | Applied To | Effect |
|------|-----------|--------|
| verification_before_assertion | all 10 agents | Must verify facts before stating them |
| root_cause_fix_required | all 10 agents | Must fix root cause, not symptoms |
| document_requires_execution_plan | all 10 agents | Documents need actionable plans |
| no_fabrication | all 10 agents | Zero tolerance for made-up data |
| counterfactual_before_major_decision | all 10 agents | Must run "what if" before big decisions |
| must_check_health_on_session_start | all 10 agents | Health check mandatory at boot |
| extract_board_values_on_session_close | all 10 agents | Record Board values at session end |
| completion_requires_cieu_audit | all 10 agents | Self-audit CIEU before claiming done |

CEO-specific rules:

| Rule | Effect |
|------|--------|
| must_dispatch_via_cto | CEO cannot dispatch directly to engineers |
| no_choice_questions | CEO must not present multiple-choice to Board |
| session_close_required | Must run session close protocol |
| autonomous_mission_requires_article_11 | Autonomous ops need Article 11 approval |
| directive_decompose_within_minutes: 10 | Must decompose directives within 10 min |

CTO/Engineer-specific rules:

| Rule | Effect |
|------|--------|
| pre_commit_requires_test | Must run tests before any commit |
| source_first_fixes | Fix source code, not workarounds |

CMO-specific rules:

| Rule | Effect |
|------|--------|
| content_length_check | Verify content fits platform limits |
| board_approval_before_publish | Board must approve before publishing |

CSO-specific rules:

| Rule | Effect |
|------|--------|
| real_conversation_count_required | Must track real conversation counts |
| board_approval_before_publish | Board must approve before publishing |

- **Declaration**: `.ystar_session.json` -> `agent_behavior_rules`
- **Enforcement**: Hook daemon behavior rule checks + CIEU recording

---

## Category 9: Delegation Chain (3 links)

Defines who can delegate to whom and at what depth.

| # | Principal | Actor | Scope | Re-delegate | Max Depth |
|---|-----------|-------|-------|-------------|-----------|
| 1 | board | ceo | * | yes | 5 |
| 2 | ceo | cto | src/,tests/,products/,docs/ | yes | 4 |
| 3 | cto | eng-kernel | ystar/kernel/ | no | 0 |

- **Declaration**: `.ystar_session.json` -> `delegation_chain.links`
- **Enforcement**: Hook daemon delegation validation

---

## Category 10: Obligation Timing SLAs (9 items)

Maximum time (seconds) before an obligation becomes OVERDUE.

| # | Obligation | SLA | Human Readable |
|---|-----------|-----|----------------|
| 1 | directive_acknowledgement | 120s | 2 minutes |
| 2 | intent_declaration | 300s | 5 minutes |
| 3 | progress_update | 1800s | 30 minutes |
| 4 | task_completion_report | 3600s | 1 hour |
| 5 | knowledge_update | 21600s | 6 hours |
| 6 | theory_library_daily | 86400s | 24 hours |
| 7 | autonomous_daily_report | 86400s | 24 hours |
| 8 | gemma_session_daily | 86400s | 24 hours |
| 9 | weekly_roadmap_audit | 604800s | 7 days |

- **Declaration**: `.ystar_session.json` -> `contract.obligation_timing`
- **Enforcement**: Obligation tracker + CIEU liveness check

---

## Category 11: Intent Guard Protected Paths (5 items)

Paths that require an intent declaration before modification.

| # | Path | Effect |
|---|------|--------|
| 1 | `governance/` | Requires intent declaration |
| 2 | `agents/` | Requires intent declaration |
| 3 | `README.md` | Requires intent declaration |
| 4 | `scripts/record_intent.py` | Requires intent declaration |
| 5 | `scripts/check_intents.py` | Requires intent declaration |

- **Declaration**: `.ystar_session.json` -> `intent_guard_protected_paths`
- **Enforcement**: Intent guard system (intent_guard_window_hours: 4)

---

## Verification

To verify all constraints are enforcing, run:
```bash
bash scripts/governance_boot.sh [agent_id]
```

Expected output for full enforcement: `ALL SYSTEMS GO`

The E2E tests verify:
1. **must_dispatch_via_cto** -- CEO cannot spawn engineer subagents directly
2. **immutable_paths** -- No agent can write AGENTS.md
3. **restricted_write_paths** -- Only designated roles can write restricted files
4. **ceo_code_block** -- CEO cannot write to Y-star-gov source code
5. **normal_operations** -- Read operations are not blocked (fail-open for reads)

Note: Tests 1 and 4 only apply when active agent is CEO. When booting as other agents, these show "NOT ENFORCING" which is expected.
