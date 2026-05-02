# E11 Duplicate / Overlap Cluster Report

Clusters below are discovered from inventory fingerprints, not taken as the prompt ontology.

## Discovery Notes
- clusters_found_from_evidence: yes
- prompt_seed_categories_used_as_search_terms_only: yes
- found_but_not_named_in_prompt: `cluster_incubated_company_runtime` and repository-delivery/commercial-completion semantics inside `cluster_closure_status_semantics`.
- expected_but_not_found: none; all owner examples had some evidence, though field/brain was mapped rather than destructively routed.
- false_positives_rejected: repeated Markdown report sections are harmless renderer duplication unless they alter lifecycle or approval semantics.

## cluster_target_lifecycle: Target candidate/proposal/approval lifecycle
- relation_type: conflicting_approval_semantics
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: True
- conflict_risk: high
- why_overlap: E10, E8/E9 validation, operations JSON, and ystar-company approval packets all represent target or approval states; proposal-only targets can be confused with approved contact targets without a lifecycle router.
- canonical_owner_recommendation: bridge-labs owns business target lifecycle; Y-star-gov owns external-action permission semantics; gov-mcp exposes gateway checks.
- adapter_router_recommendation: Implement target_lifecycle_router and make proposal states non-contactable.
- immediate_code_consolidation_safe: True
- migration_strategy: Keep E8/E9/E10 modules as adapters; route future E11/E12 contact through canonical lifecycle states.

### Evidence Members
- fp_0002: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:E9ExternalValidationManifest / approval, approved, feedback, field, manifest, U
- fp_0003: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_from_dict / approval, approved, feedback, field, manifest, U
- fp_0004: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:load_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0005: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:_placeholder / approval, approved, feedback, field, manifest, U
- fp_0006: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:validate_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0007: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_allows_action / approval, approved, feedback, field, manifest, U
- fp_0008: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:render_e9_manifest_template / approval, approved, feedback, field, manifest, U
- fp_0009: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:write_e9_manifest_template / approval, approved, feedback, field, manifest, U

## cluster_evidence_signal_ladder: Evidence, feedback, and paid-signal ladder
- relation_type: conflicting_signal_semantics
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: True
- conflict_risk: high
- why_overlap: Reports and modules use public evidence, external pattern evidence, target discovery evidence, validation feedback, and paid signal for different claims; routing is needed to prevent public discovery from becoming validation or paid-pilot readiness.
- canonical_owner_recommendation: bridge-labs owns market/evidence claim ladder; CIEU governs durable learning; owner decides commercial escalation.
- adapter_router_recommendation: Implement evidence_signal_router.
- immediate_code_consolidation_safe: True
- migration_strategy: Use typed evidence levels and forbid upward claims without matching evidence level.

### Evidence Members
- fp_0001: ystar_bridge_labs:office/mission_command/team_task_builder.py:build_team_tasks / approval, evidence, evidence field, field, mission command, owner decision
- fp_0002: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:E9ExternalValidationManifest / approval, approved, feedback, field, manifest, U
- fp_0003: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_from_dict / approval, approved, feedback, field, manifest, U
- fp_0004: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:load_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0005: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:_placeholder / approval, approved, feedback, field, manifest, U
- fp_0006: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:validate_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0007: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_allows_action / approval, approved, feedback, field, manifest, U
- fp_0008: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:render_e9_manifest_template / approval, approved, feedback, field, manifest, U

## cluster_action_authorization_chain: External action authorization chain
- relation_type: cross_repo_adapter
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: True
- conflict_risk: critical
- why_overlap: Bridge-labs risk tiers, Y-star-gov permission tiers, gov-mcp preflight tools, manifests, execution gates, ledgers, and receipts all govern side effects; a facade is needed so future validation cannot bypass formal governance.
- canonical_owner_recommendation: Y-star-gov owns deterministic policy; gov-mcp owns gateway exposure; bridge-labs owns business intent and execution packet assembly.
- adapter_router_recommendation: Implement action_authorization_router.
- immediate_code_consolidation_safe: True
- migration_strategy: Bridge-labs can call/represent Y-star-gov and gov-mcp decisions without modifying those repos in E11.

### Evidence Members
- fp_0001: ystar_bridge_labs:office/mission_command/team_task_builder.py:build_team_tasks / approval, evidence, evidence field, field, mission command, owner decision
- fp_0002: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:E9ExternalValidationManifest / approval, approved, feedback, field, manifest, U
- fp_0003: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_from_dict / approval, approved, feedback, field, manifest, U
- fp_0004: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:load_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0005: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:_placeholder / approval, approved, feedback, field, manifest, U
- fp_0006: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:validate_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0007: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_allows_action / approval, approved, feedback, field, manifest, U
- fp_0008: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:render_e9_manifest_template / approval, approved, feedback, field, manifest, U

## cluster_learning_writeback_gate: Report, method, dream, brain, and CIEU learning paths
- relation_type: conflicting_writeback_semantics
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: True
- conflict_risk: critical
- why_overlap: Reports propose learning, method kernel stores durable principles, dream cycles propose diffs, brain stores cognitive graph/activation, and CIEU carries prediction delta. Direct report-to-brain learning would bypass review gates.
- canonical_owner_recommendation: CIEU/Y-star-gov owns prediction-delta eligibility; Aiden Brain owns graph state; bridge-labs reports are proposal-only.
- adapter_router_recommendation: Implement learning_writeback_router.
- immediate_code_consolidation_safe: True
- migration_strategy: All persistent learning must be report-only until CIEU/review gate approves brain/memory writeback.

### Evidence Members
- fp_0002: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:E9ExternalValidationManifest / approval, approved, feedback, field, manifest, U
- fp_0003: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_from_dict / approval, approved, feedback, field, manifest, U
- fp_0004: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:load_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0005: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:_placeholder / approval, approved, feedback, field, manifest, U
- fp_0006: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:validate_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0007: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_allows_action / approval, approved, feedback, field, manifest, U
- fp_0008: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:render_e9_manifest_template / approval, approved, feedback, field, manifest, U
- fp_0009: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:write_e9_manifest_template / approval, approved, feedback, field, manifest, U

## cluster_closure_status_semantics: Closure status and completion semantics
- relation_type: conflicting_status_semantics
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: True
- conflict_risk: high
- why_overlap: E milestones distinguish discovery complete, validation complete, paid-signal readiness, repository delivery, and blocked statuses. Without routing, local completion can be mistaken for commercial validation completion.
- canonical_owner_recommendation: bridge-labs CZL owns mission closure semantics; repository status remains delivery-only; commercial validation needs feedback/ledger evidence.
- adapter_router_recommendation: Implement closure_status_router.
- immediate_code_consolidation_safe: True
- migration_strategy: Add status-family checks for discovery, validation, paid signal, revenue, blocked, and repository delivery.

### Evidence Members
- fp_0002: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:E9ExternalValidationManifest / approval, approved, feedback, field, manifest, U
- fp_0003: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_from_dict / approval, approved, feedback, field, manifest, U
- fp_0004: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:load_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0005: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:_placeholder / approval, approved, feedback, field, manifest, U
- fp_0006: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:validate_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0007: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_allows_action / approval, approved, feedback, field, manifest, U
- fp_0008: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:render_e9_manifest_template / approval, approved, feedback, field, manifest, U
- fp_0009: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:write_e9_manifest_template / approval, approved, feedback, field, manifest, U

## cluster_counterfactual_protocol: Counterfactual and disconfirmation protocol
- relation_type: lifecycle_overlap
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: True
- conflict_risk: medium
- why_overlap: Counterfactual language appears in method kernel, opportunity evaluation, market evaluation, validation packets, and tests. A router should source the canonical protocol from method-kernel semantics instead of stage-local wording.
- canonical_owner_recommendation: Method kernel owns durable counterfactual protocol; stage modules adapt it to opportunity, market, execution, revenue, governance, or learning contexts.
- adapter_router_recommendation: Implement counterfactual_router.
- immediate_code_consolidation_safe: True
- migration_strategy: Keep stage-specific disconfirmation tests but route protocol labels through the method kernel.

### Evidence Members
- fp_0011: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:E10RevenuePathScore / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0012: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_presence_score / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0013: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_reachability / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0014: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_contact_risk / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0015: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_owner_burden / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0016: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_recommended_mode / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0017: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:score_e10_candidate / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0018: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:rank_e10_shortest_revenue_paths / approval, disconfirming, evidence, feedback, opportunity, paid signal

## cluster_field_brain_cognitive_runtime: Field/activation/brain cognitive runtime
- relation_type: adjacent_stage_adapter
- repos_involved: gov_mcp, y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: False
- conflict_risk: medium
- why_overlap: Aiden Brain, dream diffs, field-functional archaeology, world-value field, and activation/Hebbian concepts overlap as cognitive-field mechanisms, but not all are harmful duplicates. Integration mapping is safer than destructive consolidation.
- canonical_owner_recommendation: Aiden Brain owns graph/activation state; ystar-company remains incubation source; bridge-labs owns interpretation reports; CIEU gates persistent learning.
- adapter_router_recommendation: No destructive router; cover through learning_writeback_router and integration map.
- immediate_code_consolidation_safe: False
- migration_strategy: Treat field-functional assets as interpretation/incubation until backflowed through CIEU-gated learning.

### Evidence Members
- fp_0001: ystar_bridge_labs:office/mission_command/team_task_builder.py:build_team_tasks / approval, evidence, evidence field, field, mission command, owner decision
- fp_0002: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:E9ExternalValidationManifest / approval, approved, feedback, field, manifest, U
- fp_0003: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_from_dict / approval, approved, feedback, field, manifest, U
- fp_0004: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:load_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0005: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:_placeholder / approval, approved, feedback, field, manifest, U
- fp_0006: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:validate_e9_validation_manifest / approval, approved, feedback, field, manifest, U
- fp_0007: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:e9_manifest_allows_action / approval, approved, feedback, field, manifest, U
- fp_0008: ystar_bridge_labs:office/mission_command/e9_validation_manifest.py:render_e9_manifest_template / approval, approved, feedback, field, manifest, U

## cluster_incubated_company_runtime: ystar-company incubated commercial/runtime mechanisms
- relation_type: adjacent_stage_adapter
- repos_involved: y_star_gov, ystar_bridge_labs, ystar_company
- harmful_duplicate: False
- conflict_risk: medium
- why_overlap: ystar-company contains scheduler, commercial loop, runtime packets, public research adapters, approval packets, and no-action receipts that overlap bridge-labs E6-E10 but are incubation artifacts with a very dirty runtime state.
- canonical_owner_recommendation: bridge-labs owns current E-series commercial runtime; ystar-company remains incubation/reference unless separately backflowed.
- adapter_router_recommendation: No code router in E11; document cross-repo backflow plan.
- immediate_code_consolidation_safe: False
- migration_strategy: Extract patterns later, do not read private runtime DB/log contents or mutate ystar-company.

### Evidence Members
- fp_0011: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:E10RevenuePathScore / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0012: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_presence_score / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0013: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_reachability / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0014: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_contact_risk / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0015: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_owner_burden / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0016: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:_recommended_mode / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0017: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:score_e10_candidate / approval, disconfirming, evidence, feedback, opportunity, paid signal
- fp_0018: ystar_bridge_labs:office/mission_command/e10_shortest_revenue_path_scorer.py:rank_e10_shortest_revenue_paths / approval, disconfirming, evidence, feedback, opportunity, paid signal
