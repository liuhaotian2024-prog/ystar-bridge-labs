# E11 Conflict Risk Matrix

## conflict_01: Target candidate/proposal/approval lifecycle
- affected_cluster: cluster_target_lifecycle
- scenario: E10 proposed target seed is treated as contact approval.
- risk: conflicting_approval_semantics
- likely_impact: Could cause unauthorized customer contact in E12.
- current_evidence: E10, E8/E9 validation, operations JSON, and ystar-company approval packets all represent target or approval states; proposal-only targets can be confused with approved contact targets without a lifecycle router.
- proposed_router_or_fix: target_lifecycle_router
- could_break_E12_external_validation: yes
- could_corrupt_brain_CIEU_learning: no
- severity: high
- owner_decision_required: yes
- exact_next_action: Implement target_lifecycle_router and make proposal states non-contactable.

## conflict_02: Evidence, feedback, and paid-signal ladder
- affected_cluster: cluster_evidence_signal_ladder
- scenario: Public target discovery evidence is treated as validation feedback or paid signal.
- risk: conflicting_signal_semantics
- likely_impact: Could recommend paid pilot without buyer response.
- current_evidence: Reports and modules use public evidence, external pattern evidence, target discovery evidence, validation feedback, and paid signal for different claims; routing is needed to prevent public discovery from becoming validation or paid-pilot readiness.
- proposed_router_or_fix: evidence_signal_router
- could_break_E12_external_validation: yes
- could_corrupt_brain_CIEU_learning: yes
- severity: high
- owner_decision_required: yes
- exact_next_action: Implement evidence_signal_router.

## conflict_03: External action authorization chain
- affected_cluster: cluster_action_authorization_chain
- scenario: Bridge-labs execution gate bypasses Y-star-gov/gov-mcp semantics.
- risk: cross_repo_adapter
- likely_impact: Could execute external action without canonical owner approval.
- current_evidence: Bridge-labs risk tiers, Y-star-gov permission tiers, gov-mcp preflight tools, manifests, execution gates, ledgers, and receipts all govern side effects; a facade is needed so future validation cannot bypass formal governance.
- proposed_router_or_fix: action_authorization_router
- could_break_E12_external_validation: yes
- could_corrupt_brain_CIEU_learning: no
- severity: critical
- owner_decision_required: yes
- exact_next_action: Implement action_authorization_router.

## conflict_04: Report, method, dream, brain, and CIEU learning paths
- affected_cluster: cluster_learning_writeback_gate
- scenario: E reports or dream diffs write directly to brain/CIEU.
- risk: conflicting_writeback_semantics
- likely_impact: Could corrupt persistent learning without prediction-delta validation.
- current_evidence: Reports propose learning, method kernel stores durable principles, dream cycles propose diffs, brain stores cognitive graph/activation, and CIEU carries prediction delta. Direct report-to-brain learning would bypass review gates.
- proposed_router_or_fix: learning_writeback_router
- could_break_E12_external_validation: no
- could_corrupt_brain_CIEU_learning: yes
- severity: critical
- owner_decision_required: yes
- exact_next_action: Implement learning_writeback_router.

## conflict_05: Closure status and completion semantics
- affected_cluster: cluster_closure_status_semantics
- scenario: Discovery complete is interpreted as validation or paid-signal complete.
- risk: conflicting_status_semantics
- likely_impact: Could move E12/E13 into paid-pilot path prematurely.
- current_evidence: E milestones distinguish discovery complete, validation complete, paid-signal readiness, repository delivery, and blocked statuses. Without routing, local completion can be mistaken for commercial validation completion.
- proposed_router_or_fix: closure_status_router
- could_break_E12_external_validation: yes
- could_corrupt_brain_CIEU_learning: no
- severity: high
- owner_decision_required: yes
- exact_next_action: Implement closure_status_router.

## conflict_06: Counterfactual and disconfirmation protocol
- affected_cluster: cluster_counterfactual_protocol
- scenario: Stage-local counterfactual wording drifts from method-kernel protocol.
- risk: lifecycle_overlap
- likely_impact: Could weaken disconfirmation gates.
- current_evidence: Counterfactual language appears in method kernel, opportunity evaluation, market evaluation, validation packets, and tests. A router should source the canonical protocol from method-kernel semantics instead of stage-local wording.
- proposed_router_or_fix: counterfactual_router
- could_break_E12_external_validation: yes
- could_corrupt_brain_CIEU_learning: no
- severity: medium
- owner_decision_required: no
- exact_next_action: Implement counterfactual_router.

## conflict_07: Field/activation/brain cognitive runtime
- affected_cluster: cluster_field_brain_cognitive_runtime
- scenario: Incubated mechanism is mistaken for canonical runtime.
- risk: adjacent_stage_adapter
- likely_impact: Could create unclear ownership or stale behavior.
- current_evidence: Aiden Brain, dream diffs, field-functional archaeology, world-value field, and activation/Hebbian concepts overlap as cognitive-field mechanisms, but not all are harmful duplicates. Integration mapping is safer than destructive consolidation.
- proposed_router_or_fix: backflow plan
- could_break_E12_external_validation: unknown
- could_corrupt_brain_CIEU_learning: unknown
- severity: medium
- owner_decision_required: no
- exact_next_action: No destructive router; cover through learning_writeback_router and integration map.

## conflict_08: ystar-company incubated commercial/runtime mechanisms
- affected_cluster: cluster_incubated_company_runtime
- scenario: Incubated mechanism is mistaken for canonical runtime.
- risk: adjacent_stage_adapter
- likely_impact: Could create unclear ownership or stale behavior.
- current_evidence: ystar-company contains scheduler, commercial loop, runtime packets, public research adapters, approval packets, and no-action receipts that overlap bridge-labs E6-E10 but are incubation artifacts with a very dirty runtime state.
- proposed_router_or_fix: backflow plan
- could_break_E12_external_validation: unknown
- could_corrupt_brain_CIEU_learning: unknown
- severity: medium
- owner_decision_required: no
- exact_next_action: No code router in E11; document cross-repo backflow plan.
