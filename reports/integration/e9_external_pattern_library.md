# E9 External Pattern Library

- pattern_count: 14

## pattern_feedback_taxonomy: Validation feedback taxonomy
- source_family: commercial_validation_startup_discovery
- source_ids: src_yc_talk_to_users
- maturity_level: open_source_practice
- score: 11
- problem_addressed: Raw feedback is hard to compare without signal classes.
- core_mechanism: Classify price, urgency, workflow, objection, referral, opt-out, and disconfirmation signals.
- safety_impact: 5
- M-3 value impact: 5
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into E9 feedback and signal evaluator.

## pattern_action_trace_ledger: Traceable action ledger
- source_family: auditability_observability_action_ledgers
- source_ids: src_opentelemetry_docs
- maturity_level: industry_framework
- score: 10
- problem_addressed: External actions need correlated provenance, not scattered logs.
- core_mechanism: Record action, actor, target, scope, timestamp, provider, decision, and result.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into action and feedback ledgers.

## pattern_agentic_risk_taxonomy: Agentic AI risk taxonomy
- source_family: agentic_ai_security_threat_models
- source_ids: src_owasp_agentic_ai
- maturity_level: industry_framework
- score: 10
- problem_addressed: Agent failures combine autonomy, tool use, identity, and data access.
- core_mechanism: Use a named threat/risk taxonomy before approving agent actions.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into E9 preflight risk labels.

## pattern_ai_management_system_continuous_improvement: AI management system continuous improvement
- source_family: ai_risk_management_governance_standards
- source_ids: src_iso_42001
- maturity_level: standard
- score: 10
- problem_addressed: One-off controls decay without lifecycle ownership.
- core_mechanism: Maintain policies, objectives, processes, review loops, and continual improvement.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into method-kernel learning and report lifecycle.

## pattern_execution_budget: Bounded execution budget
- source_family: sandboxing_scoped_execution_progressive_autonomy
- source_ids: src_nist_ai_rmf, src_langgraph_hitl
- maturity_level: industry_framework
- score: 10
- problem_addressed: Autonomy without count/time/channel limits creates runaway risk.
- core_mechanism: Constrain count, channel, target set, follow-ups, and expiry.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into E9 manifest and action plan budgets.

## pattern_govern_map_measure_manage: Govern / Map / Measure / Manage loop
- source_family: ai_risk_management_governance_standards
- source_ids: src_nist_ai_rmf, src_nist_genai_profile
- maturity_level: standard
- score: 10
- problem_addressed: Unstructured AI risk decisions drift or hide residuals.
- core_mechanism: Map action context, measure risk/evidence, manage controls, and govern repeatability.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into CZL plus action-risk evidence loop.

## pattern_human_in_loop_approve_edit_reject: HITL approve / edit / reject
- source_family: human_in_the_loop_approval_workflows
- source_ids: src_langgraph_hitl, src_openai_hitl
- maturity_level: official_docs
- score: 10
- problem_addressed: Sensitive actions need review without losing execution state.
- core_mechanism: Interrupt execution, store state, and resume after approve/edit/reject decisions.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into E9 approval decision model.

## pattern_kill_switch_stop_conditions: Kill-switch and stop conditions
- source_family: sandboxing_scoped_execution_progressive_autonomy
- source_ids: src_nist_ai_rmf, src_ftc_can_spam
- maturity_level: industry_framework
- score: 10
- problem_addressed: External actions need a crisp halt path when risk or negative feedback appears.
- core_mechanism: Predefine stop conditions: opt-out, budget exhaustion, scope mismatch, or risk escalation.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into action-plan and preflight stop-condition enforcement.

## pattern_opt_out_suppression: Opt-out and suppression registry
- source_family: outreach_crm_compliance_validation_mechanics
- source_ids: src_ftc_can_spam
- maturity_level: standard
- score: 10
- problem_addressed: Follow-up after opt-out creates trust and legal risk.
- core_mechanism: Maintain suppression state and block targets who opted out or exceeded limits.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into E9 suppression registry.

## pattern_progressive_autonomy: Progressive autonomy ladder
- source_family: sandboxing_scoped_execution_progressive_autonomy
- source_ids: src_nist_ai_rmf, src_openai_hitl
- maturity_level: product_practice
- score: 10
- problem_addressed: Agents should not jump from internal analysis to commercial action.
- core_mechanism: Move from internal, read-only, handoff, exact approval, publication approval, then blocked commercial tiers.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into E9 autonomy ladder.

## pattern_small_batch_customer_discovery: Small-batch qualitative discovery
- source_family: commercial_validation_startup_discovery
- source_ids: src_yc_talk_to_users, src_yc_user_interview_questions
- maturity_level: open_source_practice
- score: 10
- problem_addressed: Market validation should learn from real problems before scaling outreach.
- core_mechanism: Use small batches, ask about lived workflow, alternatives tried, urgency, and willingness-to-pay signals.
- safety_impact: 4
- M-3 value impact: 5
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into validation signal taxonomy and owner-operated handoff.

## pattern_tool_consent_scope_minimization: Consent and least-privilege tool scopes
- source_family: tool_mcp_external_action_security
- source_ids: src_mcp_security, src_mcp_authorization
- maturity_level: official_docs
- score: 10
- problem_addressed: Tool access can exceed user intent through confused deputy or broad scopes.
- core_mechanism: Display scopes, bind audience, avoid passthrough, and require per-client consent.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into target/channel/draft/action scope minimization.

## pattern_truthful_identity_non_deception: Truthful identity and non-deception
- source_family: outreach_crm_compliance_validation_mechanics
- source_ids: src_ftc_can_spam, src_mcp_security
- maturity_level: standard
- score: 10
- problem_addressed: External validation can become deceptive if identity or purpose is hidden.
- core_mechanism: Require accurate sender identity, clear AI disclosure, and non-deceptive subject/purpose.
- safety_impact: 5
- M-3 value impact: 4
- owner_burden_impact: 2
- implementation_cost: 2
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into transparency checks and draft binding.

## pattern_persistent_checkpoint_resume: Persistent checkpoint and resume
- source_family: human_in_the_loop_approval_workflows
- source_ids: src_langgraph_hitl, src_openai_hitl
- maturity_level: official_docs
- score: 8
- problem_addressed: Long approval cycles should not force the agent to reconstruct context unsafely.
- core_mechanism: Persist run state and resume only after decisions are supplied.
- safety_impact: 5
- M-3 value impact: 3
- owner_burden_impact: 2
- implementation_cost: 3
- residual_risk: Needs local tests and owner review before external execution.
- translation_recommendation: Translate into approval-state notes and handoff artifacts.
