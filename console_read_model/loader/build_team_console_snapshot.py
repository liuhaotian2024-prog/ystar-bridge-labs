#!/usr/bin/env python3
"""Build a static team console snapshot from curated read-model files only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "console_read_model" / "generated"
GENERATOR_VERSION = "v0"

CURATED_SOURCES = [
    "console_read_model/team_brain_read_model.json",
    "console_read_model/agent_cards.json",
    "console_read_model/capability_matrix.json",
    "agent_brains/team_capsule_map.json",
    "agent_brains/Aiden-CEO/brain_profile.json",
    "agent_brains/Ethan-CTO/brain_profile.json",
    "agent_brains/Samantha-Secretary/brain_profile.json",
    "agent_brains/Ethan-CTO/execution_channels.json",
    "runtime_artifact_quarantine/quarantine_index.json",
    "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
    "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
    "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json",
    "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
    "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
    "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
    "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
    "labs_governance_bridge/generated/governance_decision_snapshot.json",
    "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json",
    "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
    "cross_repo_alignment/generated/cross_repo_alignment_summary.json",
    "labs_live_readiness/generated/live_readiness_report.json",
    "labs_live_boundary/generated/live_boundary_summary.json",
    "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json",
    "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
    "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
    "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
    "governed_observation_loop/generated/governed_observation_loop_summary.json",
    "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
    "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
    "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
    "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
    "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json",
    "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
    "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
    "mission_field_projection_contract/projection_contract_summary.json",
    "field_functional_auto_projection_core/field_projection_operator_summary.json",
    "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
    "behavior_y_star_to_pre_u_candidate/pre_u_candidate_summary.json",
    "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
    "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
    "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
    "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
    "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
    "projection_checked_learning_review_queue/projection_learning_review_summary.json",
    "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
    "residual_review_gate/residual_review_summary.json",
    "learning_target_classifier/learning_target_summary.json",
    "projection_policy_update_candidate/projection_policy_update_summary.json",
    "shadow_projection_policy_patch/shadow_patch_summary.json",
    "shadow_reprojection_preview/shadow_reprojection_summary.json",
    "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
    "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
    "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
    "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
    "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
    "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
    "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
    "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
    "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
    "mcp_request_intent_projection/mcp_request_intent_summary.json",
    "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
    "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
    "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
    "governed_mcp_call_candidate/governed_mcp_call_summary.json",
    "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
    "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
    "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
    "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
    "canonical_learning_target_registry/canonical_learning_target_summary.json",
    "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
    "canonical_update_package_candidate/canonical_update_package_summary.json",
    "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
    "rollback_and_audit_lineage/rollback_audit_summary.json",
    "post_promotion_validation_plan/post_promotion_validation_summary.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
    "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
    "sandbox_approval_fixture/sandbox_approval_summary.json",
    "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
    "sandbox_patch_application/sandbox_patch_application_summary.json",
    "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
    "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
    "sandbox_rollback_validation/sandbox_rollback_summary.json",
    "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
    "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
    "real_approval_workflow_boundary/real_approval_workflow_summary.json",
    "approval_authority_model/approval_authority_summary.json",
    "approval_evidence_dossier/approval_evidence_summary.json",
    "durable_approval_record_contract/approval_record_summary.json",
    "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
    "approval_validity_revocation_policy/approval_validity_summary.json",
    "pre_application_snapshot_policy/snapshot_policy_summary.json",
    "real_application_boundary_gate/real_application_boundary_summary.json",
    "post_approval_preflight_validation/post_approval_preflight_summary.json",
    "manual_approval_runbook/manual_approval_runbook_summary.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
    "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
    "controlled_approval_record_sandbox/controlled_approval_record_sandbox_summary.json",
    "sandbox_approval_record_instance/sandbox_approval_record_summary.json",
    "approval_record_integrity_validation/approval_record_integrity_summary.json",
    "approval_record_validity_state_machine/approval_record_state_machine_summary.json",
    "expiration_revocation_replay/expiration_revocation_replay_summary.json",
    "approval_record_pre_application_gate_replay/pre_application_gate_replay_summary.json",
    "approval_record_audit_lineage/approval_record_audit_summary.json",
    "approval_record_cieu_residual/approval_record_cieu_summary.json",
    "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
    "controlled_real_release_preflight/controlled_real_release_preflight_summary.json",
    "release_candidate_package/release_candidate_summary.json",
    "release_scope_validation/release_scope_validation_summary.json",
    "approval_record_preflight_validation/approval_record_preflight_summary.json",
    "snapshot_and_rollback_preflight/snapshot_rollback_preflight_summary.json",
    "invariant_preflight_validation/invariant_preflight_summary.json",
    "post_release_validation_matrix/post_release_validation_summary.json",
    "release_operator_handoff_packet/release_operator_handoff_summary.json",
    "release_blocker_decision/release_blocker_summary.json",
    "release_preflight_cieu_residual/release_preflight_cieu_summary.json",
    "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
    "real_release_simulation_sandbox/real_release_simulation_summary.json",
    "sandbox_release_authority_fixture/sandbox_release_authority_summary.json",
    "simulated_durable_approval_record/simulated_approval_record_summary.json",
    "sandbox_release_snapshot/sandbox_release_snapshot_summary.json",
    "sandbox_release_execution_plan/sandbox_release_execution_summary.json",
    "sandbox_release_execution_result/sandbox_release_execution_result_summary.json",
    "sandbox_post_release_validation/sandbox_post_release_validation_summary.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_release_projection_mcp_summary.json",
    "sandbox_release_rollback_drill/sandbox_release_rollback_summary.json",
    "original_release_rollback_comparison/sandbox_release_safety_summary.json",
    "release_simulation_cieu_residual/release_simulation_cieu_summary.json",
    "real_release_simulation_readiness/real_release_simulation_readiness.json",
    "live_boundary_no_go_framework/live_boundary_no_go_summary.json",
    "live_capability_domain_registry/live_capability_summary.json",
    "no_go_invariant_matrix/no_go_invariant_summary.json",
    "live_readiness_evidence_index/live_readiness_evidence_summary.json",
    "live_blocker_risk_register/live_blocker_summary.json",
    "l6_meta_development_entry_gate/l6_entry_gate_summary.json",
    "system_no_go_decision_packet/system_live_boundary_decision_summary.json",
    "live_boundary_cieu_residual/live_boundary_cieu_summary.json",
    "live_boundary_readiness/live_boundary_readiness.json",
    "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_summary.json",
    "self_model_and_unique_asset_field/self_asset_summary.json",
    "world_value_field_model/world_value_field_summary.json",
    "value_conversion_operator_library/operator_library_summary.json",
    "open_value_hypothesis_generator/hypothesis_generator_summary.json",
    "value_conversion_physics/conversion_physics_summary.json",
    "redeemability_selection_engine/selection_engine_summary.json",
    "minimum_viable_proof_designer/mvp_design_summary.json",
    "governed_meta_development_experiment_portfolio/experiment_portfolio_summary.json",
    "strategic_residual_meta_learning_loop/strategic_residual_summary.json",
    "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json",
    "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
    "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json",
    "selected_mvp_artifact_cases/selected_case_index.json",
    "mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json",
    "mvp_artifact_review_gate/review_gate_contract.json",
    "mvp_artifact_externalization_boundary/externalization_blocker.json",
    "l6_mvp_artifact_strategic_residual_loop/l6_1_strategic_residual_delta.json",
    "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
    "l6_governed_external_observation_boundary/l6_2_summary.json",
    "pre_observation_packet_schema/pre_observation_packet_schema.json",
    "external_source_registry_and_policy/source_type_registry.json",
    "external_observation_permission_gate/observation_permission_gate_contract.json",
    "manual_external_evidence_import_sandbox/manual_import_contract.json",
    "observation_to_mvp_artifact_linker/observation_to_artifact_link_contract.json",
    "observation_claim_boundary_and_freshness/claim_boundary_policy.json",
    "external_observation_no_action_receipts/no_network_receipt.json",
    "l6_external_observation_strategic_residual_loop/l6_2_strategic_residual_delta.json",
    "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json",
    "l6_controlled_external_observation_sandbox/l6_3_summary.json",
    "l6_observation_case_selector/selected_observation_cases.json",
    "controlled_pre_observation_packets/pre_observation_packet_index.json",
    "sandbox_observation_permission_replay/packet_permission_decisions.json",
    "static_manual_observation_fixtures/observation_fixture_index.json",
    "observation_evidence_validation_sandbox/fixture_validation_results.json",
    "observation_claim_freshness_assessment/claim_freshness_matrix.json",
    "observation_to_artifact_refinement_candidates/refinement_candidate_index.json",
    "controlled_observation_review_packets/review_packet_index.json",
    "controlled_observation_no_action_receipts/no_network_receipt.json",
    "l6_controlled_observation_strategic_residual_loop/l6_3_strategic_residual_delta.json",
    "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json",
    "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
    "real_observation_candidate_selector/selected_real_observation_candidates.json",
    "real_read_only_observation_preflight_contract/preflight_requirement_registry.json",
    "source_allowlist_and_risk_policy/source_allowlist_policy.json",
    "source_allowlist_and_risk_policy/source_denylist_policy.json",
    "real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json",
    "observation_operator_handoff/operator_handoff_contract.json",
    "observation_network_isolation_preflight/network_isolation_requirement.json",
    "observation_evidence_capture_preflight/evidence_capture_contract.json",
    "observation_abort_rollback_quarantine_policy/abort_condition_registry.json",
    "read_only_observation_no_action_guarantees/no_real_observation_receipt.json",
    "real_observation_preflight_decision_gate/candidate_preflight_decisions.json",
    "l6_real_observation_preflight_strategic_residual_loop/l6_4_strategic_residual_delta.json",
    "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json",
    "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.json",
    "pilot_candidate_selector/selected_pilot_candidates.json",
    "pilot_scope_and_non_goals/pilot_boundary_contract.json",
    "pilot_source_constraint_policy/pilot_source_allowlist.json",
    "pilot_source_constraint_policy/pilot_source_denylist.json",
    "pilot_approval_packet_candidates/pilot_approval_packet_index.json",
    "pilot_operator_runbook/operator_step_sequence.json",
    "pilot_evidence_packet_templates/pilot_evidence_packet_template.json",
    "pilot_post_observation_review_workflow/post_observation_review_contract.json",
    "pilot_abort_quarantine_decision_policy/pilot_abort_condition_registry.json",
    "pilot_success_failure_criteria/pilot_success_criteria.json",
    "pilot_no_action_and_execution_blockers/no_real_observation_execution_receipt.json",
    "pilot_design_decision_gate/pilot_candidate_decisions.json",
    "l6_pilot_design_strategic_residual_loop/l6_5_strategic_residual_delta.json",
    "l6_pilot_design_readiness/l6_5_readiness_assessment.json",
    "l6_controlled_observation_pilot_approval_packet/l6_6_summary.json",
    "pilot_approval_candidate_selector/selected_approval_candidates.json",
    "pilot_approval_authority_model/approval_authority_model.json",
    "pilot_approval_packet_assembler/approval_packet_index.json",
    "pilot_approval_evidence_dossier/evidence_dossier_index.json",
    "pilot_approval_risk_review/approval_packet_risk_matrix.json",
    "pilot_operator_authorization_prerequisites/operator_authorization_contract.json",
    "pilot_runtime_isolation_attestation/runtime_isolation_attestation_template.json",
    "pilot_evidence_capture_authorization/evidence_capture_authorization_template.json",
    "pilot_approval_no_action_constraints/approval_no_action_constraint_contract.json",
    "pilot_approval_decision_sandbox/approval_packet_decision_matrix.json",
    "pilot_approval_non_persistence_receipts/no_durable_real_approval_record_receipt.json",
    "l6_pilot_approval_strategic_residual_loop/l6_6_strategic_residual_delta.json",
    "l6_pilot_approval_readiness/l6_6_readiness_assessment.json",
    "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_summary.json",
    "sandbox_approval_record_lifecycle/sandbox_approval_record_index.json",
    "pilot_run_package_assembler/pilot_run_package_index.json",
    "pilot_operator_readiness_package/operator_readiness_checklist.json",
    "pilot_runtime_isolation_readiness/runtime_isolation_readiness_packet.json",
    "pilot_evidence_capture_readiness/evidence_capture_packet_template_final.json",
    "pilot_post_observation_review_readiness/post_observation_review_packet_template.json",
    "manual_evidence_import_readiness/manual_evidence_import_readiness_contract.json",
    "pilot_integrated_decision_gate/integrated_candidate_decision_matrix.json",
    "pilot_integrated_no_action_receipts/no_real_approval_granted_receipt.json",
    "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_strategic_residual_delta.json",
    "l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json",
    "l6_agentic_evidence_discovery_trust_engine/l6_8_summary.json",
    "evidence_need_inference_engine/inferred_evidence_needs.json",
    "autonomous_source_hypothesis_generator/source_hypothesis_index.json",
    "source_type_value_model/source_type_value_matrix.json",
    "evidence_trust_judgment_model/trust_judgment_matrix.json",
    "evidence_value_of_information_model/evidence_need_voi_matrix.json",
    "source_prioritization_and_ranking_engine/ranked_source_hypotheses.json",
    "evidence_conflict_and_corrobation_model/conflict_corroboration_contract.json",
    "observation_work_order_generator/observation_work_order_index.json",
    "pre_observation_rejection_filter/rejected_source_hypotheses.json",
    "agentic_evidence_decision_gate/evidence_discovery_decision_matrix.json",
    "agentic_evidence_no_action_receipts/no_agent_fetch_receipt.json",
    "l6_agentic_evidence_strategic_residual_loop/l6_8_strategic_residual_delta.json",
    "l6_agentic_evidence_readiness_report/l6_8_readiness_assessment.json",
    "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_summary.json",
    "agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json",
    "agentic_pilot_approval_eligibility_gate/approval_eligibility_matrix.json",
    "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_index.json",
    "agentic_pilot_sandbox_approval_records/sandbox_approval_record_index.json",
    "agentic_pilot_runtime_readiness_package/runtime_readiness_packet_index.json",
    "agentic_pilot_dry_run_executor/dry_run_trace_index.json",
    "agentic_pilot_empty_evidence_capture_simulator/simulated_empty_evidence_packet_index.json",
    "agentic_pilot_post_run_review_simulator/post_run_review_packet_index.json",
    "agentic_pilot_residual_and_refinement_candidates/dry_run_refinement_candidate_index.json",
    "agentic_pilot_real_execution_blockers/blocked_real_execution_decisions.json",
    "agentic_pilot_no_action_receipts/no_agent_fetch_receipt.json",
    "l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_strategic_residual_delta.json",
    "l6_agentic_pilot_dry_run_readiness_report/l6_9_readiness_assessment.json",
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_summary.json",
    "tiny_observation_work_order_selector/selected_tiny_observation_work_order.json",
    "tiny_source_locator_resolution/source_locator_resolution_result.json",
    "tiny_real_read_only_observation_trace/tiny_observation_trace.json",
    "tiny_evidence_capture_packet/tiny_evidence_packet.json",
    "tiny_post_observation_review_packet/tiny_post_observation_review_packet.json",
    "tiny_artifact_refinement_candidate/tiny_artifact_refinement_candidate.json",
    "tiny_observation_abort_and_quarantine/abort_or_quarantine_decision.json",
    "tiny_observation_no_action_receipts/no_crawling_receipt.json",
    "l6_tiny_observation_strategic_residual_loop/l6_10_strategic_residual_delta.json",
    "l6_tiny_observation_readiness_report/l6_10_readiness_assessment.json",
    "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.json",
    "locator_retry_work_order_selector/selected_locator_retry_work_order.json",
    "controlled_locator_resolution_trace/locator_resolution_trace.json",
    "locator_eligibility_and_risk_gate/locator_eligibility_result.json",
    "tiny_observation_retry_execution_packet/retry_execution_packet.json",
    "tiny_observation_retry_trace/retry_observation_trace.json",
    "tiny_retry_evidence_capture_packet/retry_evidence_packet.json",
    "tiny_retry_post_observation_review/retry_post_observation_review_packet.json",
    "tiny_retry_refinement_candidate/retry_artifact_refinement_candidate.json",
    "tiny_retry_abort_quarantine/retry_abort_or_quarantine_decision.json",
    "tiny_retry_no_action_receipts/no_broad_search_receipt.json",
    "l6_10r_strategic_residual_loop/l6_10r_strategic_residual_delta.json",
    "l6_10r_readiness_report/l6_10r_readiness_assessment.json",
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_summary.json",
    "capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json",
    "governed_toolmaking_methodology/governed_toolmaking_lifecycle.json",
    "controlled_tool_contract_model/controlled_tool_contract_example_locator_resolver.json",
    "tool_authority_and_use_gate/tool_authority_model.json",
    "tool_sandbox_validation_harness/tool_validation_test_matrix.json",
    "locator_resolver_capability_probe/resolver_capability_probe_result.json",
    "locator_resolver_adapter_registry/resolver_adapter_registry.json",
    "locator_resolver_input_output_contract/locator_resolution_result_disabled_fixture.json",
    "locator_resolution_adapter_trace/adapter_trace.json",
    "concrete_locator_eligibility_gate/concrete_locator_eligibility_result.json",
    "adapter_bound_tiny_observation_retry/adapter_bound_retry_trace.json",
    "adapter_bound_evidence_capture/adapter_bound_evidence_packet.json",
    "adapter_bound_review_and_refinement/adapter_bound_refinement_candidate.json",
    "adapter_bound_blocker_and_fallback_report/locator_tooling_blocker.json",
    "adapter_bound_no_action_receipts/no_broad_search_receipt.json",
    "l6_10t_strategic_residual_loop/l6_10t_strategic_residual_delta.json",
    "l6_10t_readiness_report/l6_10t_readiness_assessment.json",
    "l6_controlled_locator_resolver_enablement/l6_10u_summary.json",
    "controlled_locator_resolution_attempt/selected_work_order.json",
    "controlled_locator_resolution_attempt/locator_resolution_request.json",
    "controlled_locator_resolution_attempt/locator_resolution_result.json",
    "controlled_locator_resolution_attempt/locator_resolution_trace.json",
    "controlled_locator_resolution_attempt/locator_eligibility_result.json",
    "controlled_locator_observation_result/tiny_observation_trace.json",
    "controlled_locator_observation_result/tiny_evidence_packet.json",
    "controlled_locator_observation_result/tiny_refinement_candidate.json",
    "controlled_locator_observation_result/tiny_observation_no_action_receipts.json",
    "controlled_locator_resolver_read_model/l6_10u_strategic_residual_delta.json",
    "controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json",
    "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_summary.json",
    "seed_locator_registry/reviewed_seed_locator_registry.json",
    "seed_locator_registry/seed_locator_registry_lookup_trace.json",
    "explicit_controlled_search_resolver/explicit_search_resolver_trace.json",
    "locator_resolution_v_attempt/selected_work_order.json",
    "locator_resolution_v_attempt/locator_resolution_v_request.json",
    "locator_resolution_v_attempt/locator_resolution_v_result.json",
    "locator_resolution_v_attempt/locator_resolution_v_trace.json",
    "locator_resolution_v_attempt/locator_resolution_v_eligibility_result.json",
    "tiny_observation_v_result/tiny_observation_v_trace.json",
    "tiny_observation_v_result/tiny_evidence_v_packet.json",
    "tiny_observation_v_result/tiny_refinement_v_candidate.json",
    "tiny_observation_v_result/tiny_observation_v_no_action_receipts.json",
    "l6_10v_read_model/l6_10v_strategic_residual_delta.json",
    "l6_10v_read_model/l6_10v_readiness_assessment.json",
    "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_summary.json",
    "reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json",
    "seed_locator_user_action_request/user_action_required.json",
    "seed_locator_retry_attempt/seed_locator_retry_trace.json",
    "seed_locator_retry_result/tiny_seed_observation_trace.json",
    "seed_locator_retry_result/tiny_seed_evidence_packet.json",
    "seed_locator_retry_result/tiny_seed_refinement_candidate.json",
    "seed_locator_retry_result/tiny_seed_no_action_receipts.json",
    "l6_10w_read_model/l6_10w_strategic_residual_delta.json",
    "l6_10w_read_model/l6_10w_readiness_assessment.json",
    "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_summary.json",
    "agentic_query_planner/generated_query_plan.json",
    "controlled_search_backend_runtime/controlled_search_trace.json",
    "search_result_triage/source_triage_matrix.json",
    "bounded_crawl_runtime/bounded_crawl_trace.json",
    "source_quality_and_trust_assessment/trust_assessment_results.json",
    "evidence_extraction_and_claim_boundary/evidence_packet_index.json",
    "evidence_corroboration_and_conflict_matrix/conflict_registry.json",
    "evidence_review_and_refinement_candidates/artifact_refinement_candidate_index.json",
    "l6_10x_read_model/l6_10x_strategic_residual_delta.json",
    "l6_10x_read_model/l6_10x_readiness_assessment.json",
]

UNSAFE_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "__pycache__",
    "active-agent",
    ".pid",
    "daemon",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/drift_hourly",
]


class BuildError(Exception):
    """Raised when the static snapshot cannot be built safely."""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def assert_safe_source(path: Path) -> None:
    try:
        relative = rel(path)
    except ValueError as exc:
        raise BuildError(f"Refusing path outside repo: {path}") from exc

    lowered = relative.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                raise BuildError(f"Refusing unsafe source: {relative}")
        elif m in lowered:
            raise BuildError(f"Refusing unsafe source: {relative}")


def load_json(relative_path: str, files_read: list[str]) -> Any:
    path = ROOT / relative_path
    assert_safe_source(path)
    if not path.exists():
        raise BuildError(f"Missing curated source: {relative_path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    files_read.append(relative_path)
    return data


def load_optional_json(relative_path: str, files_read: list[str]) -> Any | None:
    path = ROOT / relative_path
    assert_safe_source(path)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    files_read.append(relative_path)
    return data


def write_json(relative_path: str, payload: Any, generated_files: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    generated_files.append(relative_path)


def write_text(relative_path: str, text: str, generated_files: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated_files.append(relative_path)


def build_quarantine_summary(
    quarantine_index: dict[str, Any],
    quarantine_manifest: dict[str, Any],
) -> dict[str, Any]:
    artifacts = quarantine_manifest.get("artifacts", [])
    future_adapter_candidates = sorted(
        {
            artifact.get("future_adapter_candidate")
            for artifact in artifacts
            if artifact.get("future_adapter_candidate")
            and artifact.get("future_adapter_candidate") not in {"none", "none_or_metadata_only"}
        }
    )
    if not future_adapter_candidates:
        future_adapter_candidates = quarantine_index.get("future_adapters", [])

    return {
        "schema_name": "ystar.console_read_model.generated.quarantine_summary",
        "schema_version": "v0",
        "framework_status": quarantine_index.get("framework_status"),
        "current_mining_level": quarantine_index.get("current_mining_level"),
        "artifacts_classified": quarantine_manifest.get("artifacts_classified", 0),
        "unsafe_artifacts_count": quarantine_manifest.get("unsafe_artifacts_count", 0),
        "classes_seen": quarantine_manifest.get("classes_seen", {}),
        "generated_manifest_ref": quarantine_index.get(
            "generated_manifest_ref",
            "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
        ),
        "forbidden_direct_reads": quarantine_index.get("forbidden_direct_reads", []),
        "future_adapter_candidates": future_adapter_candidates,
        "safety_warning": (
            "Console displays only curated path-level quarantine summary. "
            "No artifact contents were read."
        ),
    }


def build_safe_mining_summary(candidate_index: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.safe_mining_summary",
        "schema_version": "v0",
        "candidate_count": candidate_index.get("candidate_count", 0),
        "classes_seen": candidate_index.get("classes_seen", {}),
        "generated_candidate_index": (
            "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"
        ),
        "mining_manifest_ref": "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json",
        "safety_level": candidate_index.get("safety_level", "bounded_markdown_candidate"),
        "ingestion_status": candidate_index.get("ingestion_status", "candidate_only"),
        "allowed_next_step": candidate_index.get("allowed_next_step", "human_review_or_curated_queue"),
        "forbidden_next_step": candidate_index.get("forbidden_next_step", "direct_brain_writeback"),
        "allowed_artifact_classes": candidate_index.get("allowed_artifact_classes", []),
        "bounds": candidate_index.get("bounds", {}),
        "warning": (
            "Safe mining candidates are bounded review assets only. They are not brain memory, "
            "CIEU records, or approved writeback."
        ),
    }


def build_review_queue_summary(review_queue: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.review_queue_summary",
        "schema_version": "v0",
        "review_count": review_queue.get("review_count", 0),
        "statuses": review_queue.get("statuses", {}),
        "ingestion_statuses": review_queue.get("ingestion_statuses", {}),
        "intended_use_summary": review_queue.get("intended_use_summary", {}),
        "generated_queue_path": (
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json"
        ),
        "review_queue_manifest_ref": (
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/review_queue_manifest.json"
        ),
        "default_review_status": review_queue.get("default_review_status", "pending_review"),
        "default_ingestion_status": review_queue.get("default_ingestion_status", "not_ingested"),
        "allowed_review_actions": review_queue.get("allowed_review_actions", []),
        "forbidden_actions": review_queue.get("forbidden_actions", []),
        "warning": (
            "Review queue entries are not brain memory and require explicit approval "
            "before any future CIEU, memory, or capsule use."
        ),
    }


def build_disposition_summary(disposition_index: dict[str, Any]) -> dict[str, Any]:
    summary = disposition_index.get("summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.artifact_disposition_summary",
        "schema_version": "v0",
        "total_artifacts": summary.get("total_artifacts", 0),
        "artifacts_with_disposition": summary.get("artifacts_with_disposition", 0),
        "dispositions": summary.get("dispositions", {}),
        "artifact_classes": summary.get("artifact_classes", {}),
        "safe_mined_to_review_queue": summary.get("safe_mined_to_review_queue", 0),
        "deferred_adapter_counts": summary.get("deferred_adapter_counts", {}),
        "ignored_generated_cache": summary.get("ignored_generated_cache", 0),
        "forbidden_direct_read_count": summary.get("forbidden_direct_read_count", 0),
        "evidence_scoring_status": summary.get("evidence_scoring_status", {}),
        "generated_disposition_index": (
            "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json"
        ),
        "warning": summary.get(
            "warning",
            "Disposition is not ingestion. No brain/memory/CIEU writes are allowed.",
        ),
    }


def build_evidence_review_summary(
    evidence_scores: dict[str, Any],
    decision_stub: dict[str, Any],
    hint_routing: dict[str, Any],
) -> dict[str, Any]:
    summary = evidence_scores.get("summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.evidence_review_summary",
        "schema_version": "v0",
        "candidates_scored": summary.get("candidates_scored", 0),
        "decision_stubs_created": decision_stub.get("decision_stubs_created", 0),
        "routes_created": hint_routing.get("routes_created", 0),
        "reuse_readiness": summary.get("reuse_readiness", {}),
        "confidence": summary.get("confidence", {}),
        "route_counts": hint_routing.get("route_counts", {}),
        "semantic_truth_status": summary.get("semantic_truth_status", {}),
        "automatic_approvals": summary.get("automatic_approvals", 0),
        "brain_writeback_allowed": summary.get("brain_writeback_allowed", 0),
        "memory_ingestion_allowed": summary.get("memory_ingestion_allowed", 0),
        "cieu_write_allowed": summary.get("cieu_write_allowed", 0),
        "generated_evidence_scores": "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
        "generated_review_decisions": "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
        "generated_hint_routing": "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
        "warning": summary.get(
            "warning",
            "Evidence scoring is structural only. It is not truth validation and not memory ingestion.",
        ),
    }


def build_governance_bridge_summary(decision_snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.governance_bridge_summary",
        "schema_version": "v0",
        "latest_bridge_run_id": decision_snapshot.get("bridge_run_id"),
        "source_task_id": decision_snapshot.get("source_task_id"),
        "agent_id": decision_snapshot.get("agent_id"),
        "ystar_gov_cli_path": decision_snapshot.get("ystar_gov_cli_path"),
        "ystar_gov_exit_code": decision_snapshot.get("ystar_gov_exit_code"),
        "ystar_gov_decision": decision_snapshot.get("ystar_gov_decision"),
        "allow_execution": decision_snapshot.get("allow_execution"),
        "require_revision": decision_snapshot.get("require_revision"),
        "deny": decision_snapshot.get("deny"),
        "escalate": decision_snapshot.get("escalate"),
        "dry_run_only": decision_snapshot.get("dry_run_only"),
        "non_execution_confirmation": decision_snapshot.get("non_execution_confirmation"),
        "action_executed": decision_snapshot.get("action_executed"),
        "cieu_written": decision_snapshot.get("cieu_written"),
        "brain_writeback_performed": decision_snapshot.get("brain_writeback_performed"),
        "memory_ingestion_performed": decision_snapshot.get("memory_ingestion_performed"),
        "generated_decision_snapshot": (
            "labs_governance_bridge/generated/governance_decision_snapshot.json"
        ),
        "warning": decision_snapshot.get(
            "warning",
            "Bridge is dry-run only and does not execute actions or write CIEU.",
        ),
    }


def build_pre_u_governance_summary(decision_snapshots: dict[str, Any]) -> dict[str, Any]:
    summary = decision_snapshots.get("summary", {})
    snapshots = decision_snapshots.get("snapshots", [])
    decisions_by_role = {
        snapshot.get("agent_id"): {
            "packet_id": snapshot.get("packet_id"),
            "decision": snapshot.get("ystar_gov_decision"),
            "exit_code": snapshot.get("ystar_gov_exit_code"),
            "allow_execution": snapshot.get("allow_execution"),
            "require_revision": snapshot.get("require_revision"),
            "deny": snapshot.get("deny"),
            "escalate": snapshot.get("escalate"),
        }
        for snapshot in snapshots
    }
    return {
        "schema_name": "ystar.console_read_model.generated.pre_u_governance_summary",
        "schema_version": "v0",
        "packets_generated": summary.get("snapshots_created", 0),
        "roles_covered": summary.get("roles_covered", []),
        "decision_counts": summary.get("decision_counts", {}),
        "decisions_by_role": decisions_by_role,
        "dry_run_only": summary.get("dry_run_only"),
        "action_executed": summary.get("action_executed"),
        "cieu_written": summary.get("cieu_written"),
        "brain_writeback_performed": summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": summary.get("memory_ingestion_performed"),
        "generated_decision_snapshots": (
            "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json"
        ),
        "warning": summary.get(
            "warning",
            "Generated Pre-U governance decisions are dry-run only and are not runtime actions.",
        ),
    }


def build_labs_acceptance_summary(acceptance_report: dict[str, Any] | None) -> dict[str, Any]:
    if not acceptance_report:
        return {
            "schema_name": "ystar.console_read_model.generated.labs_acceptance_summary",
            "schema_version": "v0",
            "accepted": False,
            "checks_passed": 0,
            "checks_total": 0,
            "roles_covered": [],
            "decision_counts": {},
            "action_executed": False,
            "cieu_written": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
            "raw_runtime_artifacts_ingested": False,
            "generated_acceptance_report": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
            "warning": "Labs runtime acceptance report has not been generated yet.",
        }

    checks = acceptance_report.get("checks", [])
    passed = sum(1 for check in checks if check.get("status") == "PASS")
    safety = acceptance_report.get("safety_assertions", {})
    decision_summary = acceptance_report.get("decision_summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.labs_acceptance_summary",
        "schema_version": "v0",
        "accepted": acceptance_report.get("accepted"),
        "checks_passed": passed,
        "checks_total": len(checks),
        "roles_covered": decision_summary.get("roles_covered", []),
        "decision_counts": decision_summary.get("decision_counts", {}),
        "action_executed": safety.get("action_executed"),
        "cieu_written": safety.get("cieu_written"),
        "brain_writeback_performed": safety.get("brain_writeback_performed"),
        "memory_ingestion_performed": safety.get("memory_ingestion_performed"),
        "raw_runtime_artifacts_ingested": safety.get("raw_runtime_artifacts_ingested"),
        "generated_acceptance_report": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
        "warning": acceptance_report.get(
            "safety_note",
            "Labs runtime acceptance is dry-run only.",
        ),
    }


def build_cross_repo_alignment_summary(cross_repo_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not cross_repo_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.cross_repo_alignment_summary",
            "schema_version": "v0",
            "alignment_accepted": False,
            "ystar_company_head": None,
            "ystar_company_head_summary": None,
            "ystar_gov_head": None,
            "ystar_gov_head_summary": None,
            "ystar_gov_endpoint_accepted": False,
            "labs_runtime_accepted": False,
            "roles_covered": [],
            "decision_counts": {},
            "safety_assertions": {},
            "generated_manifest": "cross_repo_alignment/generated/cross_repo_status_manifest.json",
            "warning": "Cross-repo alignment report has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.cross_repo_alignment_summary",
        "schema_version": "v0",
        "alignment_accepted": cross_repo_summary.get("alignment_accepted"),
        "ystar_company_head": cross_repo_summary.get("ystar_company_head"),
        "ystar_company_head_summary": cross_repo_summary.get("ystar_company_head_summary"),
        "ystar_gov_head": cross_repo_summary.get("ystar_gov_head"),
        "ystar_gov_head_summary": cross_repo_summary.get("ystar_gov_head_summary"),
        "ystar_gov_endpoint_accepted": cross_repo_summary.get("ystar_gov_endpoint_accepted"),
        "labs_runtime_accepted": cross_repo_summary.get("labs_runtime_accepted"),
        "roles_covered": cross_repo_summary.get("roles_covered", []),
        "decision_counts": cross_repo_summary.get("decision_counts", {}),
        "safety_assertions": cross_repo_summary.get("safety_assertions", {}),
        "generated_manifest": cross_repo_summary.get(
            "generated_manifest",
            "cross_repo_alignment/generated/cross_repo_status_manifest.json",
        ),
        "warning": cross_repo_summary.get(
            "warning",
            "Cross-repo alignment is dry-run only and does not execute actions or write CIEU.",
        ),
    }


def build_live_readiness_summary(live_readiness_report: dict[str, Any] | None) -> dict[str, Any]:
    if not live_readiness_report:
        return {
            "schema_name": "ystar.console_read_model.generated.live_readiness_summary",
            "schema_version": "v0",
            "dry_run_governance_ready": False,
            "minimal_live_loop_ready": False,
            "minimal_live_loop_status": "not_evaluated",
            "recommended_next_phase": "build_live_readiness_report",
            "live_action_execution_allowed": False,
            "live_cieu_write_allowed": False,
            "live_brain_writeback_allowed": False,
            "live_memory_ingestion_allowed": False,
            "candidate_auto_approval_allowed": False,
            "raw_artifact_ingestion_allowed": False,
            "blockers": [],
            "transition_backlog_items": 0,
            "generated_report": "labs_live_readiness/generated/live_readiness_report.json",
            "generated_transition_backlog": "labs_live_readiness/generated/transition_backlog.json",
            "warning": "Live readiness report has not been generated yet.",
        }

    safety = live_readiness_report.get("safety_booleans", {})
    blockers = live_readiness_report.get("live_execution_blockers", [])
    overall = live_readiness_report.get("overall_status", {})
    transition = live_readiness_report.get("transition_backlog_summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.live_readiness_summary",
        "schema_version": "v0",
        "dry_run_governance_ready": overall.get("dry_run_governance_ready"),
        "minimal_live_loop_ready": overall.get("minimal_live_loop_ready"),
        "minimal_live_loop_status": overall.get("minimal_live_loop_status"),
        "recommended_next_phase": overall.get("recommended_next_phase"),
        "live_action_execution_allowed": safety.get("live_action_execution_allowed"),
        "live_cieu_write_allowed": safety.get("live_cieu_write_allowed"),
        "live_brain_writeback_allowed": safety.get("live_brain_writeback_allowed"),
        "live_memory_ingestion_allowed": safety.get("live_memory_ingestion_allowed"),
        "candidate_auto_approval_allowed": safety.get("candidate_auto_approval_allowed"),
        "raw_artifact_ingestion_allowed": safety.get("raw_artifact_ingestion_allowed"),
        "blockers": blockers,
        "transition_backlog_items": transition.get("items_total", 0),
        "generated_report": "labs_live_readiness/generated/live_readiness_report.json",
        "generated_transition_backlog": "labs_live_readiness/generated/transition_backlog.json",
        "warning": live_readiness_report.get(
            "warning",
            "Live-readiness gate is not live runtime and keeps action/CIEU/brain/memory writes blocked.",
        ),
    }


def build_live_boundary_summary(live_boundary_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not live_boundary_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.live_boundary_summary",
            "schema_version": "v0",
            "live_boundary_defined": False,
            "operator_approval_gate_defined": False,
            "action_sandbox_contract_defined": False,
            "rollback_policy_defined": False,
            "cieu_writer_boundary_defined": False,
            "live_action_execution_enabled": False,
            "cieu_write_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "candidate_auto_approval_enabled": False,
            "raw_artifact_ingestion_enabled": False,
            "requires_manual_enablement": True,
            "minimal_live_loop_ready": False,
            "blocked_reason": "live_boundary_manifest_not_generated",
            "checklist_status_counts": {},
            "ready_or_enabled_checklist_items": 0,
            "generated_manifest": "labs_live_boundary/generated/live_boundary_manifest.json",
            "generated_checklist": "labs_live_boundary/generated/live_transition_checklist.json",
            "warning": "Live boundary manifest has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.live_boundary_summary",
        "schema_version": "v0",
        "live_boundary_defined": live_boundary_summary.get("live_boundary_defined"),
        "operator_approval_gate_defined": live_boundary_summary.get("operator_approval_gate_defined"),
        "action_sandbox_contract_defined": live_boundary_summary.get("action_sandbox_contract_defined"),
        "rollback_policy_defined": live_boundary_summary.get("rollback_policy_defined"),
        "cieu_writer_boundary_defined": live_boundary_summary.get("cieu_writer_boundary_defined"),
        "live_action_execution_enabled": live_boundary_summary.get("live_action_execution_enabled"),
        "cieu_write_enabled": live_boundary_summary.get("cieu_write_enabled"),
        "brain_writeback_enabled": live_boundary_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": live_boundary_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": live_boundary_summary.get("candidate_auto_approval_enabled"),
        "raw_artifact_ingestion_enabled": live_boundary_summary.get("raw_artifact_ingestion_enabled"),
        "requires_manual_enablement": live_boundary_summary.get("requires_manual_enablement"),
        "minimal_live_loop_ready": live_boundary_summary.get("minimal_live_loop_ready"),
        "blocked_reason": live_boundary_summary.get("blocked_reason"),
        "checklist_status_counts": live_boundary_summary.get("checklist_status_counts", {}),
        "ready_or_enabled_checklist_items": live_boundary_summary.get("ready_or_enabled_checklist_items", 0),
        "generated_manifest": live_boundary_summary.get(
            "generated_manifest",
            "labs_live_boundary/generated/live_boundary_manifest.json",
        ),
        "generated_checklist": live_boundary_summary.get(
            "generated_checklist",
            "labs_live_boundary/generated/live_transition_checklist.json",
        ),
        "warning": live_boundary_summary.get(
            "warning",
            "Live boundary harness is defined but disabled.",
        ),
    }


def build_cieu_boundary_summary(cieu_boundary_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not cieu_boundary_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.cieu_boundary_summary",
            "schema_version": "v0",
            "cieu_runtime_boundary_defined": False,
            "cieu_runtime_event_schema_defined": False,
            "prediction_delta_fixture_defined": False,
            "cieu_writer_policy_defined": False,
            "dry_run_only": True,
            "persistence_enabled": False,
            "live_action_execution_enabled": False,
            "cieu_write_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "candidate_auto_approval_enabled": False,
            "raw_artifact_ingestion_enabled": False,
            "requires_manual_enablement": True,
            "minimal_live_loop_ready": False,
            "blocked_reason": "cieu_runtime_boundary_manifest_not_generated",
            "generated_manifest": "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json",
            "generated_sample_event": "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json",
            "generated_prediction_delta_fixture": (
                "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json"
            ),
            "warning": "CIEU runtime boundary manifest has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.cieu_boundary_summary",
        "schema_version": "v0",
        "cieu_runtime_boundary_defined": cieu_boundary_summary.get("cieu_runtime_boundary_defined"),
        "cieu_runtime_event_schema_defined": cieu_boundary_summary.get("cieu_runtime_event_schema_defined"),
        "prediction_delta_fixture_defined": cieu_boundary_summary.get("prediction_delta_fixture_defined"),
        "cieu_writer_policy_defined": cieu_boundary_summary.get("cieu_writer_policy_defined"),
        "dry_run_only": cieu_boundary_summary.get("dry_run_only"),
        "persistence_enabled": cieu_boundary_summary.get("persistence_enabled"),
        "live_action_execution_enabled": cieu_boundary_summary.get("live_action_execution_enabled"),
        "cieu_write_enabled": cieu_boundary_summary.get("cieu_write_enabled"),
        "brain_writeback_enabled": cieu_boundary_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": cieu_boundary_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": cieu_boundary_summary.get("candidate_auto_approval_enabled"),
        "raw_artifact_ingestion_enabled": cieu_boundary_summary.get("raw_artifact_ingestion_enabled"),
        "requires_manual_enablement": cieu_boundary_summary.get("requires_manual_enablement"),
        "minimal_live_loop_ready": cieu_boundary_summary.get("minimal_live_loop_ready"),
        "blocked_reason": cieu_boundary_summary.get("blocked_reason"),
        "generated_manifest": cieu_boundary_summary.get(
            "generated_manifest",
            "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json",
        ),
        "generated_sample_event": cieu_boundary_summary.get(
            "generated_sample_event",
            "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json",
        ),
        "generated_prediction_delta_fixture": cieu_boundary_summary.get(
            "generated_prediction_delta_fixture",
            "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json",
        ),
        "warning": cieu_boundary_summary.get(
            "warning",
            "CIEU runtime boundary is defined but persistence is disabled.",
        ),
    }


def build_autonomy_inventory_summary(autonomy_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not autonomy_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.autonomy_inventory_summary",
            "schema_version": "v0",
            "company_autonomy_inventory_defined": False,
            "repo_archaeology_completed": False,
            "observation_capability_map_defined": False,
            "resource_sensing_map_defined": False,
            "action_capability_map_defined": False,
            "governed_tool_registry_candidates_defined": False,
            "agent_role_capability_matrix_defined": False,
            "commercial_agent_company_goal_aligned": False,
            "governance_only_runtime": False,
            "live_actions_enabled": False,
            "external_actions_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "cieu_persistence_enabled": False,
            "git_push_enabled": False,
            "daemon_control_enabled": False,
            "email_or_external_communication_enabled": False,
            "requires_manual_enablement": True,
            "next_required_milestone": "L4.2 Company Autonomous Work Cycle Simulator v0",
            "generated_summary": "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
            "warning": "Company autonomy inventory has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.autonomy_inventory_summary",
        "schema_version": "v0",
        "company_autonomy_inventory_defined": autonomy_summary.get("company_autonomy_inventory_defined"),
        "repo_archaeology_completed": autonomy_summary.get("repo_archaeology_completed"),
        "observation_capability_map_defined": autonomy_summary.get("observation_capability_map_defined"),
        "resource_sensing_map_defined": autonomy_summary.get("resource_sensing_map_defined"),
        "action_capability_map_defined": autonomy_summary.get("action_capability_map_defined"),
        "governed_tool_registry_candidates_defined": autonomy_summary.get(
            "governed_tool_registry_candidates_defined"
        ),
        "agent_role_capability_matrix_defined": autonomy_summary.get("agent_role_capability_matrix_defined"),
        "commercial_agent_company_goal_aligned": autonomy_summary.get("commercial_agent_company_goal_aligned"),
        "governance_only_runtime": autonomy_summary.get("governance_only_runtime"),
        "live_actions_enabled": autonomy_summary.get("live_actions_enabled"),
        "external_actions_enabled": autonomy_summary.get("external_actions_enabled"),
        "brain_writeback_enabled": autonomy_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": autonomy_summary.get("memory_ingestion_enabled"),
        "cieu_persistence_enabled": autonomy_summary.get("cieu_persistence_enabled"),
        "git_push_enabled": autonomy_summary.get("git_push_enabled"),
        "daemon_control_enabled": autonomy_summary.get("daemon_control_enabled"),
        "email_or_external_communication_enabled": autonomy_summary.get(
            "email_or_external_communication_enabled"
        ),
        "requires_manual_enablement": autonomy_summary.get("requires_manual_enablement"),
        "next_required_milestone": autonomy_summary.get("next_required_milestone"),
        "generated_summary": "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
        "generated_report": "company_autonomy_inventory/generated/company_autonomy_report.md",
        "warning": "Company autonomy inventory is discovery-only; all live actions remain disabled.",
    }


def build_autonomous_cycle_summary(cycle_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not cycle_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.autonomous_cycle_summary",
            "schema_version": "v0",
            "autonomous_work_cycle_defined": False,
            "mission_bounded_autonomy_defined": False,
            "founder_sets_mission_agent_team_drives": False,
            "step_by_step_human_prompting_required": True,
            "observation_snapshot_defined": False,
            "autonomous_work_backlog_defined": False,
            "selected_work_item_defined": False,
            "role_delegation_defined": False,
            "governed_tool_selection_defined": False,
            "pre_u_packet_simulated": False,
            "governance_decision_simulated": False,
            "action_plan_simulated": False,
            "cieu_event_simulated": False,
            "residual_delta_simulated": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.3 Governed Read-Only Observation Loop v0",
            "generated_summary": "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
            "warning": "Autonomous work cycle simulator has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.autonomous_cycle_summary",
        "schema_version": "v0",
        "autonomous_work_cycle_defined": cycle_summary.get("autonomous_work_cycle_defined"),
        "mission_bounded_autonomy_defined": cycle_summary.get("mission_bounded_autonomy_defined"),
        "founder_sets_mission_agent_team_drives": cycle_summary.get("founder_sets_mission_agent_team_drives"),
        "step_by_step_human_prompting_required": cycle_summary.get("step_by_step_human_prompting_required"),
        "observation_snapshot_defined": cycle_summary.get("observation_snapshot_defined"),
        "autonomous_work_backlog_defined": cycle_summary.get("autonomous_work_backlog_defined"),
        "selected_work_item_defined": cycle_summary.get("selected_work_item_defined"),
        "role_delegation_defined": cycle_summary.get("role_delegation_defined"),
        "governed_tool_selection_defined": cycle_summary.get("governed_tool_selection_defined"),
        "pre_u_packet_simulated": cycle_summary.get("pre_u_packet_simulated"),
        "governance_decision_simulated": cycle_summary.get("governance_decision_simulated"),
        "action_plan_simulated": cycle_summary.get("action_plan_simulated"),
        "cieu_event_simulated": cycle_summary.get("cieu_event_simulated"),
        "residual_delta_simulated": cycle_summary.get("residual_delta_simulated"),
        "next_task_recommendations_defined": cycle_summary.get("next_task_recommendations_defined"),
        "real_action_executed": cycle_summary.get("real_action_executed"),
        "external_action_executed": cycle_summary.get("external_action_executed"),
        "live_action_enabled": cycle_summary.get("live_action_enabled"),
        "git_push_enabled": cycle_summary.get("git_push_enabled"),
        "daemon_control_enabled": cycle_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": cycle_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": cycle_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": cycle_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": cycle_summary.get("email_or_external_communication_enabled"),
        "requires_manual_enablement_for_live": cycle_summary.get("requires_manual_enablement_for_live"),
        "next_required_milestone": cycle_summary.get("next_required_milestone"),
        "generated_summary": "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
        "generated_report": cycle_summary.get(
            "generated_report",
            "company_autonomous_work_cycle/generated/autonomous_work_cycle_report.md",
        ),
        "warning": cycle_summary.get(
            "warning",
            "Autonomous work cycle is simulated only; no real action occurred.",
        ),
    }


def build_legacy_triage_summary(triage_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not triage_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.legacy_triage_summary",
            "schema_version": "v0",
            "legacy_asset_triage_defined": False,
            "assets_scored": 0,
            "absorption_buckets_defined": False,
            "bucket_counts": {},
            "top_absorption_candidates_defined": False,
            "top_absorption_candidate_count": 0,
            "governed_absorption_backlog_defined": False,
            "governed_absorption_backlog_count": 0,
            "blind_absorption_allowed": False,
            "blanket_rewrite_allowed": False,
            "live_actions_enabled": False,
            "next_required_milestone": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
            "generated_summary": "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
            "warning": "Legacy asset triage has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.legacy_triage_summary",
        "schema_version": "v0",
        "legacy_asset_triage_defined": triage_summary.get("legacy_asset_triage_defined"),
        "assets_scored": triage_summary.get("assets_scored"),
        "absorption_buckets_defined": triage_summary.get("absorption_buckets_defined"),
        "bucket_counts": triage_summary.get("bucket_counts", {}),
        "top_absorption_candidates_defined": triage_summary.get("top_absorption_candidates_defined"),
        "top_absorption_candidate_count": triage_summary.get("top_absorption_candidate_count"),
        "governed_absorption_backlog_defined": triage_summary.get("governed_absorption_backlog_defined"),
        "governed_absorption_backlog_count": triage_summary.get("governed_absorption_backlog_count"),
        "blind_absorption_allowed": triage_summary.get("blind_absorption_allowed"),
        "blanket_rewrite_allowed": triage_summary.get("blanket_rewrite_allowed"),
        "live_actions_enabled": triage_summary.get("live_actions_enabled"),
        "external_actions_enabled": triage_summary.get("external_actions_enabled"),
        "brain_writeback_enabled": triage_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": triage_summary.get("memory_ingestion_enabled"),
        "cieu_persistence_enabled": triage_summary.get("cieu_persistence_enabled"),
        "next_required_milestone": triage_summary.get("next_required_milestone"),
        "generated_summary": "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
        "generated_report": "legacy_asset_triage/generated/legacy_asset_triage_report.md",
        "warning": triage_summary.get("warning", "Legacy assets are triaged only; no absorption is executed."),
    }


def build_observation_loop_summary(observation_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not observation_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.observation_loop_summary",
            "schema_version": "v0",
            "governed_observation_loop_defined": False,
            "read_only_observation_loop_defined": False,
            "observation_source_registry_defined": False,
            "observation_tick_generated": False,
            "mission_dashboard_snapshot_defined": False,
            "company_state_digest_defined": False,
            "observation_to_work_item_candidates_defined": False,
            "mission_bounded_autonomy_supported": False,
            "step_by_step_human_prompting_reduced": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "next_required_milestone": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
            "generated_summary": "governed_observation_loop/generated/governed_observation_loop_summary.json",
            "warning": "Governed observation loop has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.observation_loop_summary",
        "schema_version": "v0",
        "governed_observation_loop_defined": observation_summary.get("governed_observation_loop_defined"),
        "read_only_observation_loop_defined": observation_summary.get("read_only_observation_loop_defined"),
        "observation_source_registry_defined": observation_summary.get("observation_source_registry_defined"),
        "observation_tick_generated": observation_summary.get("observation_tick_generated"),
        "mission_dashboard_snapshot_defined": observation_summary.get("mission_dashboard_snapshot_defined"),
        "company_state_digest_defined": observation_summary.get("company_state_digest_defined"),
        "observation_to_work_item_candidates_defined": observation_summary.get(
            "observation_to_work_item_candidates_defined"
        ),
        "observation_to_work_item_candidate_count": observation_summary.get(
            "observation_to_work_item_candidate_count"
        ),
        "mission_bounded_autonomy_supported": observation_summary.get("mission_bounded_autonomy_supported"),
        "step_by_step_human_prompting_reduced": observation_summary.get("step_by_step_human_prompting_reduced"),
        "real_action_executed": observation_summary.get("real_action_executed"),
        "external_action_executed": observation_summary.get("external_action_executed"),
        "live_action_enabled": observation_summary.get("live_action_enabled"),
        "git_push_enabled": observation_summary.get("git_push_enabled"),
        "daemon_control_enabled": observation_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": observation_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": observation_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": observation_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": observation_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": observation_summary.get("next_required_milestone"),
        "generated_summary": "governed_observation_loop/generated/governed_observation_loop_summary.json",
        "generated_report": "governed_observation_loop/generated/governed_observation_loop_report.md",
        "warning": observation_summary.get("warning", "Observation loop is read-only and executes no actions."),
    }


def build_readonly_tool_summary(tool_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not tool_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.readonly_tool_summary",
            "schema_version": "v0",
            "governed_readonly_observation_tool_defined": False,
            "tool_contract_defined": False,
            "allowed_source_registry_defined": False,
            "sample_invocation_defined": False,
            "sample_result_defined": False,
            "unsafe_invocation_rejected": False,
            "tool_cieu_event_defined": False,
            "local_readonly_dry_run_callable": False,
            "first_governed_tool_wrapper_created": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.5 Governed Tool Invocation Through Pre-U Bridge v0",
            "generated_summary": "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
            "warning": "Governed read-only observation tool has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.readonly_tool_summary",
        "schema_version": "v0",
        "governed_readonly_observation_tool_defined": tool_summary.get(
            "governed_readonly_observation_tool_defined"
        ),
        "tool_contract_defined": tool_summary.get("tool_contract_defined"),
        "allowed_source_registry_defined": tool_summary.get("allowed_source_registry_defined"),
        "sample_invocation_defined": tool_summary.get("sample_invocation_defined"),
        "sample_result_defined": tool_summary.get("sample_result_defined"),
        "unsafe_invocation_rejected": tool_summary.get("unsafe_invocation_rejected"),
        "tool_cieu_event_defined": tool_summary.get("tool_cieu_event_defined"),
        "local_readonly_dry_run_callable": tool_summary.get("local_readonly_dry_run_callable"),
        "mission_bounded_autonomy_supported": tool_summary.get("mission_bounded_autonomy_supported"),
        "step_by_step_human_prompting_reduced": tool_summary.get("step_by_step_human_prompting_reduced"),
        "first_governed_tool_wrapper_created": tool_summary.get("first_governed_tool_wrapper_created"),
        "real_action_executed": tool_summary.get("real_action_executed"),
        "external_action_executed": tool_summary.get("external_action_executed"),
        "live_action_enabled": tool_summary.get("live_action_enabled"),
        "network_enabled": tool_summary.get("network_enabled"),
        "git_push_enabled": tool_summary.get("git_push_enabled"),
        "daemon_control_enabled": tool_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": tool_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": tool_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": tool_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": tool_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": tool_summary.get("next_required_milestone"),
        "generated_summary": "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
        "generated_contract": tool_summary.get(
            "generated_contract",
            "governed_readonly_observation_tool/generated/tool_contract.json",
        ),
        "generated_registry": tool_summary.get(
            "generated_registry",
            "governed_readonly_observation_tool/generated/allowed_source_registry.json",
        ),
        "generated_sample_result": tool_summary.get(
            "generated_sample_result",
            "governed_readonly_observation_tool/generated/sample_tool_result.json",
        ),
        "generated_cieu_event": tool_summary.get(
            "generated_cieu_event",
            "governed_readonly_observation_tool/generated/tool_cieu_event.json",
        ),
        "warning": tool_summary.get(
            "warning",
            "Read-only wrapper is callable locally, but live execution and persistence remain disabled.",
        ),
    }


def build_tool_bridge_summary(bridge_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not bridge_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.tool_bridge_summary",
            "schema_version": "v0",
            "governed_tool_invocation_bridge_defined": False,
            "bridge_contract_defined": False,
            "agent_tool_request_defined": False,
            "pre_u_tool_packet_defined": False,
            "governance_decision_defined": False,
            "bridge_authorization_defined": False,
            "tool_invoked_through_bridge": False,
            "direct_tool_invocation_rejected": False,
            "unsafe_bridge_request_rejected": False,
            "bridge_cieu_event_defined": False,
            "bridge_residual_delta_defined": False,
            "first_governed_tool_invocation_chain_created": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0",
            "generated_summary": "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
            "warning": "Governed tool invocation bridge has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.tool_bridge_summary",
        "schema_version": "v0",
        "governed_tool_invocation_bridge_defined": bridge_summary.get(
            "governed_tool_invocation_bridge_defined"
        ),
        "bridge_contract_defined": bridge_summary.get("bridge_contract_defined"),
        "agent_tool_request_defined": bridge_summary.get("agent_tool_request_defined"),
        "pre_u_tool_packet_defined": bridge_summary.get("pre_u_tool_packet_defined"),
        "governance_decision_defined": bridge_summary.get("governance_decision_defined"),
        "bridge_authorization_defined": bridge_summary.get("bridge_authorization_defined"),
        "tool_invoked_through_bridge": bridge_summary.get("tool_invoked_through_bridge"),
        "direct_tool_invocation_rejected": bridge_summary.get("direct_tool_invocation_rejected"),
        "unsafe_bridge_request_rejected": bridge_summary.get("unsafe_bridge_request_rejected"),
        "bridge_cieu_event_defined": bridge_summary.get("bridge_cieu_event_defined"),
        "bridge_residual_delta_defined": bridge_summary.get("bridge_residual_delta_defined"),
        "mission_bounded_autonomy_supported": bridge_summary.get("mission_bounded_autonomy_supported"),
        "step_by_step_human_prompting_reduced": bridge_summary.get("step_by_step_human_prompting_reduced"),
        "first_governed_tool_invocation_chain_created": bridge_summary.get(
            "first_governed_tool_invocation_chain_created"
        ),
        "real_action_executed": bridge_summary.get("real_action_executed"),
        "external_action_executed": bridge_summary.get("external_action_executed"),
        "live_action_enabled": bridge_summary.get("live_action_enabled"),
        "network_enabled": bridge_summary.get("network_enabled"),
        "git_push_enabled": bridge_summary.get("git_push_enabled"),
        "daemon_control_enabled": bridge_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": bridge_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": bridge_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": bridge_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": bridge_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": bridge_summary.get("next_required_milestone"),
        "generated_summary": "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
        "generated_contract": bridge_summary.get(
            "generated_contract",
            "governed_tool_invocation_bridge/generated/bridge_contract.json",
        ),
        "generated_pre_u_packet": bridge_summary.get(
            "generated_pre_u_packet",
            "governed_tool_invocation_bridge/generated/pre_u_tool_packet.json",
        ),
        "generated_bridged_result": bridge_summary.get(
            "generated_bridged_result",
            "governed_tool_invocation_bridge/generated/bridged_tool_result.json",
        ),
        "generated_cieu_event": bridge_summary.get(
            "generated_cieu_event",
            "governed_tool_invocation_bridge/generated/bridge_cieu_event.json",
        ),
        "warning": bridge_summary.get(
            "warning",
            "Tool invocation is routed through a Pre-U bridge for local read-only dry-run only.",
        ),
    }


def build_work_proposal_summary(work_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not work_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.work_proposal_summary",
            "schema_version": "v0",
            "agent_team_work_proposal_defined": False,
            "mission_context_snapshot_defined": False,
            "agent_team_observation_input_defined": False,
            "autonomous_work_proposals_defined": False,
            "selected_work_proposal_defined": False,
            "role_review_board_defined": False,
            "tool_need_analysis_defined": False,
            "generated_tool_request_defined": False,
            "work_proposal_routed_to_bridge": False,
            "direct_tool_invocation_used": False,
            "bridged_tool_result_ref_defined": False,
            "work_proposal_cieu_event_defined": False,
            "work_proposal_residual_delta_defined": False,
            "agent_team_generated_the_work": False,
            "agent_team_selected_governed_tool": False,
            "pre_u_bridge_required": False,
            "pre_u_bridge_satisfied": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.7 First Mission Dashboard Refresh Loop v0",
            "generated_summary": "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
            "warning": "Agent team work proposal pack has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.work_proposal_summary",
        "schema_version": "v0",
        "agent_team_work_proposal_defined": work_summary.get("agent_team_work_proposal_defined"),
        "mission_context_snapshot_defined": work_summary.get("mission_context_snapshot_defined"),
        "agent_team_observation_input_defined": work_summary.get("agent_team_observation_input_defined"),
        "autonomous_work_proposals_defined": work_summary.get("autonomous_work_proposals_defined"),
        "selected_work_proposal_defined": work_summary.get("selected_work_proposal_defined"),
        "role_review_board_defined": work_summary.get("role_review_board_defined"),
        "tool_need_analysis_defined": work_summary.get("tool_need_analysis_defined"),
        "generated_tool_request_defined": work_summary.get("generated_tool_request_defined"),
        "work_proposal_routed_to_bridge": work_summary.get("work_proposal_routed_to_bridge"),
        "bridge_runner_used": work_summary.get("bridge_runner_used"),
        "direct_tool_invocation_used": work_summary.get("direct_tool_invocation_used"),
        "bridged_tool_result_ref_defined": work_summary.get("bridged_tool_result_ref_defined"),
        "work_proposal_cieu_event_defined": work_summary.get("work_proposal_cieu_event_defined"),
        "work_proposal_residual_delta_defined": work_summary.get("work_proposal_residual_delta_defined"),
        "next_agent_work_recommendations_defined": work_summary.get("next_agent_work_recommendations_defined"),
        "mission_bounded_autonomy_supported": work_summary.get("mission_bounded_autonomy_supported"),
        "founder_sets_mission_agent_team_drives": work_summary.get("founder_sets_mission_agent_team_drives"),
        "step_by_step_human_prompting_required": work_summary.get("step_by_step_human_prompting_required"),
        "agent_team_generated_the_work": work_summary.get("agent_team_generated_the_work"),
        "agent_team_selected_governed_tool": work_summary.get("agent_team_selected_governed_tool"),
        "pre_u_bridge_required": work_summary.get("pre_u_bridge_required"),
        "pre_u_bridge_satisfied": work_summary.get("pre_u_bridge_satisfied"),
        "real_action_executed": work_summary.get("real_action_executed"),
        "external_action_executed": work_summary.get("external_action_executed"),
        "live_action_enabled": work_summary.get("live_action_enabled"),
        "network_enabled": work_summary.get("network_enabled"),
        "git_push_enabled": work_summary.get("git_push_enabled"),
        "daemon_control_enabled": work_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": work_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": work_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": work_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": work_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": work_summary.get("next_required_milestone"),
        "generated_summary": work_summary.get(
            "generated_summary",
            "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
        ),
        "generated_tool_request": work_summary.get(
            "generated_tool_request",
            "agent_team_work_proposal/generated/generated_tool_request.json",
        ),
        "generated_bridge_trace": work_summary.get(
            "generated_bridge_trace",
            "agent_team_work_proposal/generated/work_proposal_to_bridge_trace.json",
        ),
        "generated_bridged_result_ref": work_summary.get(
            "generated_bridged_result_ref",
            "agent_team_work_proposal/generated/bridged_tool_result_ref.json",
        ),
        "generated_cieu_event": work_summary.get(
            "generated_cieu_event",
            "agent_team_work_proposal/generated/work_proposal_cieu_event.json",
        ),
        "warning": work_summary.get(
            "warning",
            "Agent-team work proposal routes generated work through the governed bridge only.",
        ),
    }


def build_dashboard_refresh_summary(refresh_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not refresh_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.dashboard_refresh_summary",
            "schema_version": "v0",
            "mission_dashboard_refresh_loop_defined": False,
            "refresh_loop_contract_defined": False,
            "previous_dashboard_snapshot_defined": False,
            "current_observation_input_defined": False,
            "refreshed_mission_dashboard_defined": False,
            "company_state_delta_defined": False,
            "refreshed_autonomous_backlog_defined": False,
            "refresh_loop_trace_defined": False,
            "refresh_cieu_event_defined": False,
            "refresh_residual_delta_defined": False,
            "dashboard_refresh_loop_ran": False,
            "scheduler_used": False,
            "daemon_used": False,
            "manual_local_run_only": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.8 Governed Recurring Observation Loop Contract v0",
            "generated_summary": "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
            "warning": "Mission dashboard refresh loop has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.dashboard_refresh_summary",
        "schema_version": "v0",
        "mission_dashboard_refresh_loop_defined": refresh_summary.get(
            "mission_dashboard_refresh_loop_defined"
        ),
        "refresh_loop_contract_defined": refresh_summary.get("refresh_loop_contract_defined"),
        "previous_dashboard_snapshot_defined": refresh_summary.get(
            "previous_dashboard_snapshot_defined"
        ),
        "current_observation_input_defined": refresh_summary.get("current_observation_input_defined"),
        "refreshed_mission_dashboard_defined": refresh_summary.get(
            "refreshed_mission_dashboard_defined"
        ),
        "company_state_delta_defined": refresh_summary.get("company_state_delta_defined"),
        "refreshed_autonomous_backlog_defined": refresh_summary.get(
            "refreshed_autonomous_backlog_defined"
        ),
        "refresh_loop_trace_defined": refresh_summary.get("refresh_loop_trace_defined"),
        "refresh_cieu_event_defined": refresh_summary.get("refresh_cieu_event_defined"),
        "refresh_residual_delta_defined": refresh_summary.get("refresh_residual_delta_defined"),
        "next_loop_recommendations_defined": refresh_summary.get(
            "next_loop_recommendations_defined"
        ),
        "mission_bounded_autonomy_supported": refresh_summary.get(
            "mission_bounded_autonomy_supported"
        ),
        "founder_sets_mission_agent_team_drives": refresh_summary.get(
            "founder_sets_mission_agent_team_drives"
        ),
        "step_by_step_human_prompting_required": refresh_summary.get(
            "step_by_step_human_prompting_required"
        ),
        "dashboard_refresh_loop_ran": refresh_summary.get("dashboard_refresh_loop_ran"),
        "scheduler_used": refresh_summary.get("scheduler_used"),
        "daemon_used": refresh_summary.get("daemon_used"),
        "manual_local_run_only": refresh_summary.get("manual_local_run_only"),
        "real_action_executed": refresh_summary.get("real_action_executed"),
        "external_action_executed": refresh_summary.get("external_action_executed"),
        "live_action_enabled": refresh_summary.get("live_action_enabled"),
        "network_enabled": refresh_summary.get("network_enabled"),
        "git_push_enabled": refresh_summary.get("git_push_enabled"),
        "daemon_control_enabled": refresh_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": refresh_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": refresh_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": refresh_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": refresh_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": refresh_summary.get("next_required_milestone"),
        "generated_summary": refresh_summary.get(
            "generated_summary",
            "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
        ),
        "generated_contract": refresh_summary.get(
            "generated_contract",
            "mission_dashboard_refresh_loop/generated/refresh_loop_contract.json",
        ),
        "generated_refreshed_dashboard": refresh_summary.get(
            "generated_refreshed_dashboard",
            "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
        ),
        "generated_company_state_delta": refresh_summary.get(
            "generated_company_state_delta",
            "mission_dashboard_refresh_loop/generated/company_state_delta.json",
        ),
        "generated_cieu_event": refresh_summary.get(
            "generated_cieu_event",
            "mission_dashboard_refresh_loop/generated/refresh_cieu_event.json",
        ),
        "warning": refresh_summary.get(
            "warning",
            "Mission dashboard refresh loop is manual local dry-run only.",
        ),
    }


def build_recurring_loop_summary(recurring_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not recurring_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.recurring_loop_summary",
            "schema_version": "v0",
            "recurring_observation_loop_contract_defined": False,
            "recurrence_policy_defined": False,
            "recurrence_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "auto_run_enabled": False,
            "manual_local_simulation_only": False,
            "allowed_observation_sources_defined": False,
            "tick_governance_gate_defined": False,
            "simulated_observation_tick_defined": False,
            "simulated_tick_cieu_event_defined": False,
            "simulated_tick_residual_delta_defined": False,
            "stop_abort_conditions_defined": False,
            "escalation_conditions_defined": False,
            "manual_enablement_checklist_defined": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.9 Manual Recurring Observation Tick Runner v0",
            "generated_summary": (
                "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json"
            ),
            "warning": "Governed recurring observation loop contract has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.recurring_loop_summary",
        "schema_version": "v0",
        "recurring_observation_loop_contract_defined": recurring_summary.get(
            "recurring_observation_loop_contract_defined"
        ),
        "recurrence_policy_defined": recurring_summary.get("recurrence_policy_defined"),
        "recurrence_enabled": recurring_summary.get("recurrence_enabled"),
        "scheduler_enabled": recurring_summary.get("scheduler_enabled"),
        "daemon_enabled": recurring_summary.get("daemon_enabled"),
        "auto_run_enabled": recurring_summary.get("auto_run_enabled"),
        "manual_local_simulation_only": recurring_summary.get("manual_local_simulation_only"),
        "allowed_observation_sources_defined": recurring_summary.get(
            "allowed_observation_sources_defined"
        ),
        "tick_governance_gate_defined": recurring_summary.get("tick_governance_gate_defined"),
        "simulated_observation_tick_defined": recurring_summary.get(
            "simulated_observation_tick_defined"
        ),
        "simulated_tick_dashboard_delta_defined": recurring_summary.get(
            "simulated_tick_dashboard_delta_defined"
        ),
        "simulated_tick_work_candidates_defined": recurring_summary.get(
            "simulated_tick_work_candidates_defined"
        ),
        "simulated_tick_cieu_event_defined": recurring_summary.get(
            "simulated_tick_cieu_event_defined"
        ),
        "simulated_tick_residual_delta_defined": recurring_summary.get(
            "simulated_tick_residual_delta_defined"
        ),
        "stop_abort_conditions_defined": recurring_summary.get("stop_abort_conditions_defined"),
        "escalation_conditions_defined": recurring_summary.get("escalation_conditions_defined"),
        "manual_enablement_checklist_defined": recurring_summary.get(
            "manual_enablement_checklist_defined"
        ),
        "mission_bounded_autonomy_supported": recurring_summary.get(
            "mission_bounded_autonomy_supported"
        ),
        "founder_sets_mission_agent_team_drives": recurring_summary.get(
            "founder_sets_mission_agent_team_drives"
        ),
        "step_by_step_human_prompting_required": recurring_summary.get(
            "step_by_step_human_prompting_required"
        ),
        "real_action_executed": recurring_summary.get("real_action_executed"),
        "external_action_executed": recurring_summary.get("external_action_executed"),
        "live_action_enabled": recurring_summary.get("live_action_enabled"),
        "network_enabled": recurring_summary.get("network_enabled"),
        "git_push_enabled": recurring_summary.get("git_push_enabled"),
        "daemon_control_enabled": recurring_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": recurring_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": recurring_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": recurring_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": recurring_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": recurring_summary.get("next_required_milestone"),
        "generated_summary": recurring_summary.get(
            "generated_summary",
            "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json",
        ),
        "generated_contract": recurring_summary.get(
            "generated_contract",
            "recurring_observation_loop_contract/generated/recurring_loop_contract.json",
        ),
        "generated_allowed_sources": recurring_summary.get(
            "generated_allowed_sources",
            "recurring_observation_loop_contract/generated/allowed_observation_sources.json",
        ),
        "generated_tick": recurring_summary.get(
            "generated_tick",
            "recurring_observation_loop_contract/generated/simulated_observation_tick_001.json",
        ),
        "generated_cieu_event": recurring_summary.get(
            "generated_cieu_event",
            "recurring_observation_loop_contract/generated/simulated_tick_cieu_event.json",
        ),
        "generated_residual_delta": recurring_summary.get(
            "generated_residual_delta",
            "recurring_observation_loop_contract/generated/simulated_tick_residual_delta.json",
        ),
        "warning": recurring_summary.get(
            "warning",
            "Recurring observation loop contract is disabled for recurrence and simulates one manual local tick only.",
        ),
    }


def build_manual_tick_summary(manual_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not manual_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.manual_tick_summary",
            "schema_version": "v0",
            "manual_recurring_observation_tick_runner_defined": False,
            "manual_tick_runner_contract_defined": False,
            "manual_tick_request_defined": False,
            "manual_tick_preflight_defined": False,
            "manual_tick_source_validation_defined": False,
            "manual_tick_governance_decision_defined": False,
            "manual_tick_result_defined": False,
            "manual_tick_dashboard_delta_defined": False,
            "manual_tick_work_candidates_defined": False,
            "manual_tick_cieu_event_defined": False,
            "manual_tick_residual_delta_defined": False,
            "manual_tick_run_receipt_defined": False,
            "manual_tick_history_index_defined": False,
            "manual_tick_next_recommendations_defined": False,
            "manual_trigger_required": False,
            "one_tick_per_invocation": False,
            "total_recorded_ticks": 0,
            "recurrence_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "auto_run_enabled": False,
            "manual_local_run_only": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L5.0 Review-Gated Learning Candidate Queue v0",
            "generated_summary": (
                "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json"
            ),
            "warning": "Manual recurring observation tick runner has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.manual_tick_summary",
        "schema_version": "v0",
        "manual_recurring_observation_tick_runner_defined": manual_summary.get(
            "manual_recurring_observation_tick_runner_defined"
        ),
        "manual_tick_runner_contract_defined": manual_summary.get(
            "manual_tick_runner_contract_defined"
        ),
        "manual_tick_request_defined": manual_summary.get("manual_tick_request_defined"),
        "manual_tick_preflight_defined": manual_summary.get("manual_tick_preflight_defined"),
        "manual_tick_source_validation_defined": manual_summary.get(
            "manual_tick_source_validation_defined"
        ),
        "manual_tick_governance_decision_defined": manual_summary.get(
            "manual_tick_governance_decision_defined"
        ),
        "manual_tick_result_defined": manual_summary.get("manual_tick_result_defined"),
        "manual_tick_dashboard_delta_defined": manual_summary.get(
            "manual_tick_dashboard_delta_defined"
        ),
        "manual_tick_work_candidates_defined": manual_summary.get(
            "manual_tick_work_candidates_defined"
        ),
        "manual_tick_cieu_event_defined": manual_summary.get("manual_tick_cieu_event_defined"),
        "manual_tick_residual_delta_defined": manual_summary.get(
            "manual_tick_residual_delta_defined"
        ),
        "manual_tick_run_receipt_defined": manual_summary.get("manual_tick_run_receipt_defined"),
        "manual_tick_history_index_defined": manual_summary.get(
            "manual_tick_history_index_defined"
        ),
        "manual_tick_next_recommendations_defined": manual_summary.get(
            "manual_tick_next_recommendations_defined"
        ),
        "manual_trigger_required": manual_summary.get("manual_trigger_required"),
        "one_tick_per_invocation": manual_summary.get("one_tick_per_invocation"),
        "total_recorded_ticks": manual_summary.get("total_recorded_ticks"),
        "mission_bounded_autonomy_supported": manual_summary.get(
            "mission_bounded_autonomy_supported"
        ),
        "founder_sets_mission_agent_team_drives": manual_summary.get(
            "founder_sets_mission_agent_team_drives"
        ),
        "step_by_step_human_prompting_required": manual_summary.get(
            "step_by_step_human_prompting_required"
        ),
        "recurrence_enabled": manual_summary.get("recurrence_enabled"),
        "scheduler_enabled": manual_summary.get("scheduler_enabled"),
        "daemon_enabled": manual_summary.get("daemon_enabled"),
        "auto_run_enabled": manual_summary.get("auto_run_enabled"),
        "manual_local_run_only": manual_summary.get("manual_local_run_only"),
        "real_action_executed": manual_summary.get("real_action_executed"),
        "external_action_executed": manual_summary.get("external_action_executed"),
        "live_action_enabled": manual_summary.get("live_action_enabled"),
        "network_enabled": manual_summary.get("network_enabled"),
        "git_push_enabled": manual_summary.get("git_push_enabled"),
        "daemon_control_enabled": manual_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": manual_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": manual_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": manual_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": manual_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": manual_summary.get("next_required_milestone"),
        "generated_summary": manual_summary.get(
            "generated_summary",
            "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
        ),
        "generated_contract": manual_summary.get(
            "generated_contract",
            "manual_recurring_observation_tick_runner/generated/manual_tick_runner_contract.json",
        ),
        "generated_request": manual_summary.get(
            "generated_request",
            "manual_recurring_observation_tick_runner/generated/manual_tick_request.json",
        ),
        "generated_result": manual_summary.get(
            "generated_result",
            "manual_recurring_observation_tick_runner/generated/manual_tick_result.json",
        ),
        "generated_receipt": manual_summary.get(
            "generated_receipt",
            "manual_recurring_observation_tick_runner/generated/manual_tick_run_receipt.json",
        ),
        "generated_history": manual_summary.get(
            "generated_history",
            "manual_recurring_observation_tick_runner/generated/manual_tick_history_index.json",
        ),
        "generated_cieu_event": manual_summary.get(
            "generated_cieu_event",
            "manual_recurring_observation_tick_runner/generated/manual_tick_cieu_event.json",
        ),
        "generated_residual_delta": manual_summary.get(
            "generated_residual_delta",
            "manual_recurring_observation_tick_runner/generated/manual_tick_residual_delta.json",
        ),
        "warning": manual_summary.get(
            "warning",
            "Manual tick runner executes exactly one local dry-run tick and does not enable recurrence.",
        ),
    }


def build_field_functional_summary(field_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not field_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.field_functional_summary",
            "schema_version": "v0",
            "field_functional_archaeology_defined": False,
            "repos_scanned": 0,
            "assets_scanned": 0,
            "field_functional_assets_found": 0,
            "reuse_candidates_count": 0,
            "wrap_candidates_count": 0,
            "rewrite_candidates_count": 0,
            "concept_reference_count": 0,
            "do_not_absorb_count": 0,
            "old_field_functional_work_found": False,
            "mission_projection_merge_plan_defined": False,
            "ready_for_L5_projection_harness": False,
            "live_action_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L5.1 Mission Field Functional Projection Harness v0",
            "generated_summary": (
                "field_functional_archaeology/generated/field_functional_archaeology_summary.json"
            ),
            "warning": "Field functional archaeology has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.field_functional_summary",
        "schema_version": "v0",
        "field_functional_archaeology_defined": field_summary.get(
            "field_functional_archaeology_defined"
        ),
        "repos_scanned": field_summary.get("repos_scanned"),
        "assets_scanned": field_summary.get("assets_scanned"),
        "field_functional_assets_found": field_summary.get("field_functional_assets_found"),
        "reuse_candidates_count": field_summary.get("reuse_candidates_count"),
        "wrap_candidates_count": field_summary.get("wrap_candidates_count"),
        "rewrite_candidates_count": field_summary.get("rewrite_candidates_count"),
        "concept_reference_count": field_summary.get("concept_reference_count"),
        "do_not_absorb_count": field_summary.get("do_not_absorb_count"),
        "old_field_functional_work_found": field_summary.get("old_field_functional_work_found"),
        "mission_projection_merge_plan_defined": field_summary.get(
            "mission_projection_merge_plan_defined"
        ),
        "ready_for_L5_projection_harness": field_summary.get("ready_for_L5_projection_harness"),
        "live_action_enabled": field_summary.get("live_action_enabled"),
        "external_action_enabled": field_summary.get("external_action_enabled"),
        "network_enabled": field_summary.get("network_enabled"),
        "cieu_persistence_enabled": field_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": field_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": field_summary.get("memory_ingestion_enabled"),
        "next_required_milestone": field_summary.get("next_required_milestone"),
        "generated_summary": field_summary.get(
            "generated_summary",
            "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
        ),
        "generated_inventory": field_summary.get(
            "generated_inventory",
            "field_functional_archaeology/generated/field_functional_asset_inventory.json",
        ),
        "generated_merge_plan": field_summary.get(
            "generated_merge_plan",
            "field_functional_archaeology/generated/mission_projection_merge_plan.json",
        ),
        "warning": field_summary.get(
            "warning",
            "Field functional archaeology produces a merge plan only and enables no live action.",
        ),
    }


def build_mission_projection_summary(projection_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not projection_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.mission_projection_summary",
            "schema_version": "v0",
            "mission_field_projection_harness_defined": False,
            "l5_1_projection_contract_defined": False,
            "layered_projection_trace_generated": False,
            "pre_u_adapter_candidate_generated": False,
            "residual_delta_fixture_generated": False,
            "action_layer_projection_only": True,
            "action_field_execution_implemented": False,
            "ready_for_L5_2_field_functional_auto_projection_core": False,
            "deep_xt_model_is_not_l5_2_main_milestone": True,
            "live_execution_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "candidate_auto_approval_enabled": False,
            "next_required_milestone": "L5.2 Field Functional Auto-Projection Core v0",
            "generated_summary": "mission_field_projection_contract/projection_contract_summary.json",
            "warning": "Mission field projection harness has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.mission_projection_summary",
        "schema_version": "v0",
        "mission_field_projection_harness_defined": projection_summary.get(
            "mission_field_projection_harness_defined"
        ),
        "l5_1_projection_contract_defined": projection_summary.get(
            "l5_1_projection_contract_defined"
        ),
        "layered_projection_trace_generated": projection_summary.get(
            "layered_projection_trace_generated"
        ),
        "pre_u_adapter_candidate_generated": projection_summary.get(
            "pre_u_adapter_candidate_generated"
        ),
        "residual_delta_fixture_generated": projection_summary.get(
            "residual_delta_fixture_generated"
        ),
        "projection_layers": projection_summary.get("projection_layers", []),
        "action_layer_projection_only": projection_summary.get("action_layer_projection_only"),
        "action_field_execution_implemented": projection_summary.get(
            "action_field_execution_implemented"
        ),
        "ready_for_L5_2_field_functional_auto_projection_core": projection_summary.get(
            "ready_for_L5_2_field_functional_auto_projection_core"
        ),
        "deep_xt_model_is_not_l5_2_main_milestone": projection_summary.get(
            "deep_xt_model_is_not_l5_2_main_milestone", True
        ),
        "live_execution_enabled": projection_summary.get("live_execution_enabled"),
        "external_action_enabled": projection_summary.get("external_action_enabled"),
        "network_enabled": projection_summary.get("network_enabled"),
        "scheduler_enabled": projection_summary.get("scheduler_enabled"),
        "daemon_enabled": projection_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": projection_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": projection_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": projection_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": projection_summary.get(
            "candidate_auto_approval_enabled"
        ),
        "next_required_milestone": projection_summary.get("next_required_milestone"),
        "generated_summary": "mission_field_projection_contract/projection_contract_summary.json",
        "generated_contract": projection_summary.get("generated_contract"),
        "generated_trace": projection_summary.get("generated_trace"),
        "generated_pre_u_candidate": projection_summary.get("generated_pre_u_candidate"),
        "generated_residual_delta": projection_summary.get("generated_residual_delta"),
        "warning": projection_summary.get(
            "warning",
            "Mission projection harness is dry-run only and does not execute action-field semantics.",
        ),
    }


def build_field_projection_summary(
    operator_summary: dict[str, Any] | None,
    projection_summary: dict[str, Any] | None,
    pre_u_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.field_projection_summary",
            "schema_version": "v0",
            "field_functional_auto_projection_core_defined": False,
            "mission_level_y_star_input_defined": False,
            "mission_to_behavior_projection_generated": False,
            "behavior_level_y_star_candidate_generated": False,
            "pre_u_packet_candidate_from_behavior_y_star_generated": False,
            "residual_delta_loop_fixture_generated": False,
            "learning_candidate_stub_generated_but_not_approved": False,
            "ready_for_l5_3_projection_checked_autonomous_cycle": False,
            "live_execution_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "behavior_execution_enabled": False,
            "next_required_milestone": "L5.3 Projection-Checked Autonomous Work Cycle v0",
            "warning": "Field functional auto-projection core has not been generated yet.",
        }
    operator_summary = operator_summary or {}
    projection_summary = projection_summary or {}
    pre_u_summary = pre_u_summary or {}
    residual_summary = residual_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.field_projection_summary",
        "schema_version": "v0",
        "field_functional_auto_projection_core_defined": operator_summary.get(
            "field_functional_auto_projection_core_defined"
        ),
        "projection_operator_defined": readiness_summary.get("projection_operator_defined"),
        "mission_level_y_star_input_defined": readiness_summary.get("mission_y_star_defined"),
        "mission_to_behavior_projection_generated": readiness_summary.get(
            "mission_to_behavior_trace_generated"
        ),
        "projection_layers": projection_summary.get("projection_layers", []),
        "behavior_level_y_star_candidate_generated": readiness_summary.get(
            "behavior_level_y_star_candidate_generated"
        ),
        "pre_u_packet_candidate_from_behavior_y_star_generated": readiness_summary.get(
            "pre_u_packet_candidate_generated"
        ),
        "residual_delta_loop_fixture_generated": readiness_summary.get(
            "residual_delta_fixture_generated"
        ),
        "learning_candidate_stub_generated_but_not_approved": residual_summary.get(
            "learning_candidate_stub_generated_but_not_approved"
        ),
        "live_execution_still_blocked": readiness_summary.get("live_execution_still_blocked"),
        "writeback_still_blocked": readiness_summary.get("writeback_still_blocked"),
        "external_action_still_blocked": readiness_summary.get("external_action_still_blocked"),
        "ready_for_l5_3_projection_checked_autonomous_cycle": readiness_summary.get(
            "ready_for_l5_3_projection_checked_autonomous_cycle"
        ),
        "l6_revenue_opportunity_discovery_enabled": operator_summary.get(
            "l6_revenue_opportunity_discovery_enabled"
        ),
        "dry_run_only": pre_u_summary.get("dry_run_only"),
        "pre_u_production_ready": pre_u_summary.get("production_ready"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_operator_summary": "field_functional_auto_projection_core/field_projection_operator_summary.json",
        "generated_projection_summary": "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
        "generated_behavior_candidate": "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
        "generated_pre_u_candidate": "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json",
        "generated_residual_loop_summary": "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
        "generated_readiness": "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
        "warning": (
            "L5.2 is a dry-run field projection core. It does not execute behavior, "
            "discover revenue opportunities, or write learning to memory."
        ),
    }


def build_projection_cycle_summary(
    cycle_summary: dict[str, Any] | None,
    work_summary: dict[str, Any] | None,
    pre_u_summary: dict[str, Any] | None,
    result_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    learning_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.projection_cycle_summary",
            "schema_version": "v0",
            "projection_checked_autonomous_work_cycle_defined": False,
            "behavior_y_star_consumed_by_cycle": False,
            "work_proposal_checked_against_behavior_y_star": False,
            "pre_u_packet_candidate_generated": False,
            "dry_run_gate_decision_generated": False,
            "dry_run_result_generated": False,
            "cieu_like_event_fixture_generated": False,
            "residual_delta_generated": False,
            "learning_review_candidate_generated_but_not_approved": False,
            "ready_for_l5_4_review_gated_learning_loop": False,
            "live_execution_enabled": False,
            "behavior_execution_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L5.4 Review-Gated Learning Loop v0",
            "warning": "Projection-checked autonomous work cycle has not been generated yet.",
        }
    cycle_summary = cycle_summary or {}
    work_summary = work_summary or {}
    pre_u_summary = pre_u_summary or {}
    result_summary = result_summary or {}
    residual_summary = residual_summary or {}
    learning_summary = learning_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.projection_cycle_summary",
        "schema_version": "v0",
        "projection_checked_autonomous_work_cycle_defined": cycle_summary.get(
            "projection_checked_autonomous_work_cycle_defined"
        ),
        "behavior_y_star_consumed_by_cycle": readiness_summary.get(
            "behavior_y_star_consumed_by_cycle"
        ),
        "work_proposal_checked_against_behavior_y_star": readiness_summary.get(
            "work_proposal_checked_against_behavior_y_star"
        ),
        "pre_u_packet_candidate_generated": readiness_summary.get(
            "pre_u_packet_candidate_generated"
        ),
        "dry_run_gate_decision_generated": readiness_summary.get(
            "dry_run_gate_decision_generated"
        ),
        "dry_run_result_generated": readiness_summary.get("dry_run_result_generated"),
        "cieu_like_event_fixture_generated": readiness_summary.get(
            "cieu_like_event_fixture_generated"
        ),
        "residual_delta_generated": readiness_summary.get("residual_delta_generated"),
        "learning_review_candidate_generated_but_not_approved": learning_summary.get(
            "projection_checked_learning_candidate_generated"
        )
        and learning_summary.get("approved") is False,
        "projection_gate_decision": work_summary.get("projection_gate_decision"),
        "cycle_pre_u_gate_decision": pre_u_summary.get("cycle_pre_u_gate_decision"),
        "dry_run_only": pre_u_summary.get("dry_run_only"),
        "pre_u_production_ready": pre_u_summary.get("production_ready"),
        "real_execution_performed": result_summary.get("real_execution_performed"),
        "event_mode": residual_summary.get("event_mode"),
        "db_write_performed": residual_summary.get("db_write_performed"),
        "live_execution_still_blocked": readiness_summary.get("live_execution_still_blocked"),
        "writeback_still_blocked": readiness_summary.get("writeback_still_blocked"),
        "external_action_still_blocked": readiness_summary.get("external_action_still_blocked"),
        "ready_for_l5_4_review_gated_learning_loop": readiness_summary.get(
            "ready_for_l5_4_review_gated_learning_loop"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_cycle_summary": "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
        "generated_work_summary": "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
        "generated_pre_u_summary": "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
        "generated_result_summary": "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
        "generated_residual_summary": "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
        "generated_learning_summary": "projection_checked_learning_review_queue/projection_learning_review_summary.json",
        "generated_readiness": "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
        "warning": (
            "L5.3 is a projection-checked dry-run cycle. It consumes behavior-level Y* "
            "as a gate but does not execute behavior or apply learning."
        ),
    }


def build_shadow_learning_cycle_summary(
    loop_summary: dict[str, Any] | None,
    review_summary: dict[str, Any] | None,
    target_summary: dict[str, Any] | None,
    update_summary: dict[str, Any] | None,
    patch_summary: dict[str, Any] | None,
    reprojection_summary: dict[str, Any] | None,
    shadow_cycle_summary: dict[str, Any] | None,
    shadow_residual_summary: dict[str, Any] | None,
    effect_summary: dict[str, Any] | None,
    integrated_cieu_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.shadow_learning_cycle_summary",
            "schema_version": "v0",
            "integrated_review_gated_shadow_learning_cycle_defined": False,
            "l5_3_residual_consumed": False,
            "review_gate_decision_generated": False,
            "learning_target_classification_generated": False,
            "projection_policy_update_candidate_generated": False,
            "shadow_projection_policy_patch_generated": False,
            "shadow_behavior_y_star_preview_generated": False,
            "shadow_updated_projection_cycle_generated": False,
            "original_vs_shadow_cycle_comparison_generated": False,
            "integrated_cieu_like_fixture_generated": False,
            "ready_for_controlled_canonical_learning_design": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Integrated shadow learning cycle has not been generated yet.",
        }
    loop_summary = loop_summary or {}
    review_summary = review_summary or {}
    target_summary = target_summary or {}
    update_summary = update_summary or {}
    patch_summary = patch_summary or {}
    reprojection_summary = reprojection_summary or {}
    shadow_cycle_summary = shadow_cycle_summary or {}
    shadow_residual_summary = shadow_residual_summary or {}
    effect_summary = effect_summary or {}
    integrated_cieu_summary = integrated_cieu_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.shadow_learning_cycle_summary",
        "schema_version": "v0",
        "integrated_review_gated_shadow_learning_cycle_defined": loop_summary.get(
            "integrated_review_gated_shadow_learning_cycle_defined"
        ),
        "l5_3_residual_consumed": readiness_summary.get("l5_3_residual_consumed"),
        "deterministic_review_gate_decision_generated": readiness_summary.get(
            "review_gate_decision_generated"
        ),
        "review_gate_decision": review_summary.get("decision"),
        "learning_target_classification_generated": readiness_summary.get(
            "learning_target_classified"
        ),
        "projection_policy_update_candidate_generated": readiness_summary.get(
            "projection_policy_update_candidate_generated"
        ),
        "shadow_projection_policy_patch_generated": readiness_summary.get(
            "shadow_projection_policy_patch_generated"
        ),
        "shadow_behavior_y_star_preview_generated": readiness_summary.get(
            "shadow_behavior_y_star_preview_generated"
        ),
        "shadow_updated_projection_cycle_generated": readiness_summary.get(
            "shadow_updated_projection_cycle_generated"
        ),
        "shadow_cycle_cieu_fixture_generated": readiness_summary.get(
            "shadow_cycle_cieu_fixture_generated"
        ),
        "original_vs_shadow_cycle_comparison_generated": readiness_summary.get(
            "original_vs_shadow_cycle_comparison_generated"
        ),
        "integrated_cieu_like_fixture_generated": readiness_summary.get(
            "integrated_learning_cycle_cieu_fixture_generated"
        ),
        "candidate_approved": loop_summary.get("candidate_approved"),
        "candidate_applied": loop_summary.get("candidate_applied"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "previous_residual_influenced_shadow_projection": readiness_summary.get(
            "previous_residual_influenced_shadow_projection"
        ),
        "shadow_learning_effect_class": effect_summary.get("effect_class"),
        "ready_for_controlled_canonical_learning_design": readiness_summary.get(
            "ready_for_controlled_canonical_learning_design"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "shadow_patch_live_application_enabled": readiness_summary.get(
            "shadow_patch_live_application_enabled"
        ),
        "shadow_patch_preview_only": patch_summary.get("preview_only"),
        "shadow_cycle_real_execution_performed": shadow_cycle_summary.get("real_execution_performed"),
        "shadow_cycle_db_write_performed": shadow_residual_summary.get("db_write_performed"),
        "integrated_cieu_db_write_performed": integrated_cieu_summary.get("db_write_performed"),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_loop_summary": "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
        "generated_review_summary": "residual_review_gate/residual_review_summary.json",
        "generated_target_summary": "learning_target_classifier/learning_target_summary.json",
        "generated_update_summary": "projection_policy_update_candidate/projection_policy_update_summary.json",
        "generated_shadow_patch_summary": "shadow_projection_policy_patch/shadow_patch_summary.json",
        "generated_reprojection_summary": "shadow_reprojection_preview/shadow_reprojection_summary.json",
        "generated_shadow_cycle_summary": "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
        "generated_shadow_residual_summary": "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
        "generated_integrated_cieu_summary": "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
        "generated_readiness": "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
        "warning": (
            "L5.4 is shadow-only. Residuals influence a preview Y* and shadow cycle, "
            "but no canonical policy, brain, memory, CIEU store, or live system is changed."
        ),
    }


def build_cross_repo_governance_summary(
    proof_summary: dict[str, Any] | None,
    y_star_gov_summary: dict[str, Any] | None,
    alignment_summary: dict[str, Any] | None,
    gov_mcp_summary: dict[str, Any] | None,
    governed_mcp_summary: dict[str, Any] | None,
    non_bypass_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.cross_repo_governance_summary",
            "schema_version": "v0",
            "cross_repo_governance_contract_proof_defined": False,
            "y_star_gov_surfaces_inventoried_read_only": False,
            "gov_mcp_surfaces_inventoried_read_only": False,
            "ready_for_l5_6_governed_mcp_dry_run_adapter": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Cross-repo governance contract proof has not been generated yet.",
        }
    proof_summary = proof_summary or {}
    y_star_gov_summary = y_star_gov_summary or {}
    alignment_summary = alignment_summary or {}
    gov_mcp_summary = gov_mcp_summary or {}
    governed_mcp_summary = governed_mcp_summary or {}
    non_bypass_summary = non_bypass_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.cross_repo_governance_summary",
        "schema_version": "v0",
        "cross_repo_governance_contract_proof_defined": proof_summary.get(
            "cross_repo_governance_contract_proof_defined"
        ),
        "y_star_gov_surfaces_inventoried_read_only": proof_summary.get(
            "y_star_gov_surfaces_inventoried_read_only"
        ),
        "gov_mcp_surfaces_inventoried_read_only": proof_summary.get(
            "gov_mcp_surfaces_inventoried_read_only"
        ),
        "y_star_gov_repo_present": proof_summary.get("y_star_gov_repo_present"),
        "gov_mcp_repo_present": proof_summary.get("gov_mcp_repo_present"),
        "y_star_gov_scanned_files_count": proof_summary.get("y_star_gov_scanned_files_count"),
        "gov_mcp_scanned_files_count": proof_summary.get("gov_mcp_scanned_files_count"),
        "behavior_y_star_mapped_to_governance_contract": readiness_summary.get(
            "behavior_y_star_mapped_to_governance_contract"
        ),
        "pre_u_candidates_mapped_to_validator_expectations": readiness_summary.get(
            "pre_u_candidates_mapped_to_validator_expectations"
        ),
        "cieu_fixtures_mapped_to_prediction_delta_expectations": readiness_summary.get(
            "cieu_fixtures_mapped_to_prediction_delta_expectations"
        ),
        "gov_mcp_boundary_mapped": readiness_summary.get("gov_mcp_boundary_mapped"),
        "non_bypass_invariants_defined": readiness_summary.get("non_bypass_invariants_defined"),
        "bypass_risks_identified": readiness_summary.get("bypass_risks_identified"),
        "labs_kernel_responsibility_boundary_defined": readiness_summary.get(
            "labs_kernel_responsibility_boundary_defined"
        ),
        "ystar_company_is_not_canonical_governance_kernel": alignment_summary.get(
            "ystar_company_is_not_canonical_governance_kernel"
        ),
        "no_non_ystar_company_repo_modified": proof_summary.get("non_ystar_company_repo_modified") is False,
        "no_mcp_server_or_tool_executed": proof_summary.get("mcp_server_or_tool_executed") is False,
        "mcp_non_bypass_invariants_defined": governed_mcp_summary.get(
            "mcp_non_bypass_invariants_defined"
        ),
        "required_gate_sequence_defined": non_bypass_summary.get("required_gate_sequence_defined"),
        "ready_for_l5_6_governed_mcp_dry_run_adapter": readiness_summary.get(
            "ready_for_l5_6_governed_mcp_dry_run_adapter"
        ),
        "ready_for_controlled_canonical_learning_design": readiness_summary.get(
            "ready_for_controlled_canonical_learning_design"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "y_star_gov_modification_enabled": readiness_summary.get("y_star_gov_modification_enabled"),
        "gov_mcp_modification_enabled": readiness_summary.get("gov_mcp_modification_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_contract_summary": "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
        "generated_y_star_gov_surface_summary": "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
        "generated_alignment_summary": "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
        "generated_gov_mcp_surface_summary": "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
        "generated_governed_mcp_interface_summary": "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
        "generated_non_bypass_summary": "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
        "generated_readiness": "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
        "warning": (
            "L5.5 is a read-only boundary proof. ystar-company is not a governance kernel, "
            "Y-star-gov and gov-mcp were not modified, and MCP tools were not executed."
        ),
    }


def build_governed_mcp_adapter_summary(
    adapter_summary: dict[str, Any] | None,
    intent_summary: dict[str, Any] | None,
    pre_u_summary: dict[str, Any] | None,
    decision_summary: dict[str, Any] | None,
    bridge_summary: dict[str, Any] | None,
    call_summary: dict[str, Any] | None,
    receipt_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.governed_mcp_adapter_summary",
            "schema_version": "v0",
            "l5_6_governed_mcp_dry_run_adapter_defined": False,
            "ready_for_l5_7_controlled_canonical_learning_design": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Governed MCP dry-run adapter has not been generated yet.",
        }
    adapter_summary = adapter_summary or {}
    intent_summary = intent_summary or {}
    pre_u_summary = pre_u_summary or {}
    decision_summary = decision_summary or {}
    bridge_summary = bridge_summary or {}
    call_summary = call_summary or {}
    receipt_summary = receipt_summary or {}
    residual_summary = residual_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.governed_mcp_adapter_summary",
        "schema_version": "v0",
        "l5_6_governed_mcp_dry_run_adapter_defined": adapter_summary.get(
            "l5_6_governed_mcp_dry_run_adapter_defined"
        ),
        "behavior_y_star_loaded": readiness_summary.get("behavior_y_star_loaded"),
        "mcp_request_intent_generated": intent_summary.get("mcp_request_intent_generated"),
        "mcp_pre_u_packet_candidate_generated": pre_u_summary.get(
            "mcp_pre_u_packet_candidate_generated"
        ),
        "dry_run_governance_decision_envelope_generated": decision_summary.get(
            "governance_decision_envelope_generated"
        ),
        "bridge_authorization_receipt_generated": bridge_summary.get("bridge_receipt_generated"),
        "governed_mcp_call_candidate_generated": call_summary.get(
            "governed_mcp_call_candidate_generated"
        ),
        "real_mcp_execution_blocked": readiness_summary.get("real_mcp_execution_blocked"),
        "mcp_dry_run_receipt_generated": receipt_summary.get("mcp_dry_run_receipt_generated"),
        "mcp_cieu_like_event_generated": receipt_summary.get("mcp_cieu_event_fixture_generated"),
        "mcp_residual_delta_generated": residual_summary.get("mcp_residual_delta_generated"),
        "review_only_mcp_learning_candidate_generated": residual_summary.get(
            "mcp_learning_candidate_generated"
        ),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "mcp_server_not_started": readiness_summary.get("mcp_server_not_started"),
        "mcp_tool_not_executed": readiness_summary.get("mcp_tool_not_executed"),
        "mcp_resource_not_mutated": readiness_summary.get("mcp_resource_not_mutated"),
        "ready_for_l5_7_controlled_canonical_learning_design": readiness_summary.get(
            "ready_for_l5_7_controlled_canonical_learning_design"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "y_star_gov_modification_enabled": readiness_summary.get("y_star_gov_modification_enabled"),
        "gov_mcp_modification_enabled": readiness_summary.get("gov_mcp_modification_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "mcp_resource_mutation_enabled": readiness_summary.get("mcp_resource_mutation_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_adapter_summary": "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
        "generated_intent_summary": "mcp_request_intent_projection/mcp_request_intent_summary.json",
        "generated_pre_u_summary": "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
        "generated_decision_summary": "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
        "generated_bridge_summary": "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
        "generated_call_summary": "governed_mcp_call_candidate/governed_mcp_call_summary.json",
        "generated_receipt_summary": "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
        "generated_residual_summary": "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
        "generated_readiness": "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
        "warning": (
            "L5.6 proves a governed MCP dry-run adapter boundary only. gov-mcp was not run, "
            "MCP tools/resources were not executed or mutated, and Y-star-gov/gov-mcp remain unmodified."
        ),
    }


def build_controlled_canonical_learning_summary(
    design_summary: dict[str, Any] | None,
    invariant_summary: dict[str, Any] | None,
    target_summary: dict[str, Any] | None,
    evidence_summary: dict[str, Any] | None,
    gate_summary: dict[str, Any] | None,
    package_summary: dict[str, Any] | None,
    patch_summary: dict[str, Any] | None,
    rollback_summary: dict[str, Any] | None,
    validation_summary: dict[str, Any] | None,
    promotion_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.controlled_canonical_learning_summary",
            "schema_version": "v0",
            "l5_7_controlled_canonical_learning_design_defined": False,
            "ready_for_l5_8_approved_canonical_update_sandbox": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Controlled canonical learning design has not been generated yet.",
        }
    design_summary = design_summary or {}
    invariant_summary = invariant_summary or {}
    target_summary = target_summary or {}
    evidence_summary = evidence_summary or {}
    gate_summary = gate_summary or {}
    package_summary = package_summary or {}
    patch_summary = patch_summary or {}
    rollback_summary = rollback_summary or {}
    validation_summary = validation_summary or {}
    promotion_summary = promotion_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.controlled_canonical_learning_summary",
        "schema_version": "v0",
        "l5_7_controlled_canonical_learning_design_defined": design_summary.get(
            "l5_7_controlled_canonical_learning_design_defined"
        ),
        "y_star_non_mutation_invariant_defined": invariant_summary.get(
            "y_star_non_mutation_invariant_defined"
        ),
        "canonical_learning_target_registry_generated": target_summary.get(
            "canonical_learning_target_registry_generated"
        ),
        "promotion_evidence_bundle_generated": evidence_summary.get(
            "promotion_evidence_bundle_generated"
        ),
        "promotion_eligibility_gate_generated": gate_summary.get(
            "promotion_eligibility_gate_generated"
        ),
        "canonical_update_package_candidate_generated": package_summary.get(
            "canonical_update_package_candidate_generated"
        ),
        "versioned_patch_plan_generated": patch_summary.get("versioned_patch_plan_generated"),
        "rollback_audit_plan_generated": rollback_summary.get("rollback_plan_generated")
        and rollback_summary.get("audit_lineage_record_generated"),
        "post_promotion_validation_plan_generated": validation_summary.get(
            "post_promotion_validation_plan_generated"
        ),
        "dry_run_promotion_fixture_generated": promotion_summary.get(
            "dry_run_promotion_fixture_generated"
        ),
        "candidate_approved": readiness_summary.get("candidate_approved"),
        "candidate_applied": readiness_summary.get("candidate_applied"),
        "canonical_policy_mutation_performed": readiness_summary.get(
            "canonical_policy_mutation_performed"
        ),
        "canonical_update_application_performed": readiness_summary.get(
            "canonical_update_application_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "strategy_mutation_performed": readiness_summary.get("strategy_mutation_performed"),
        "y_star_direct_mutation_performed": readiness_summary.get(
            "y_star_direct_mutation_performed"
        ),
        "actual_canonical_application_blocked": readiness_summary.get(
            "actual_canonical_application_blocked"
        ),
        "candidate_approval_blocked": readiness_summary.get("candidate_approval_blocked"),
        "brain_writeback_blocked": readiness_summary.get("brain_writeback_blocked"),
        "memory_ingestion_blocked": readiness_summary.get("memory_ingestion_blocked"),
        "y_star_direct_mutation_blocked": readiness_summary.get("y_star_direct_mutation_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "ready_for_l5_8_approved_canonical_update_sandbox": readiness_summary.get(
            "ready_for_l5_8_approved_canonical_update_sandbox"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "canonical_update_application_enabled": readiness_summary.get(
            "canonical_update_application_enabled"
        ),
        "y_star_direct_mutation_enabled": readiness_summary.get(
            "y_star_direct_mutation_enabled"
        ),
        "y_star_gov_modification_enabled": readiness_summary.get("y_star_gov_modification_enabled"),
        "gov_mcp_modification_enabled": readiness_summary.get("gov_mcp_modification_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_design_summary": "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
        "generated_invariant_summary": "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
        "generated_target_summary": "canonical_learning_target_registry/canonical_learning_target_summary.json",
        "generated_evidence_summary": "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
        "generated_gate_summary": "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
        "generated_package_summary": "canonical_update_package_candidate/canonical_update_package_summary.json",
        "generated_patch_summary": "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
        "generated_rollback_summary": "rollback_and_audit_lineage/rollback_audit_summary.json",
        "generated_validation_summary": "post_promotion_validation_plan/post_promotion_validation_summary.json",
        "generated_promotion_summary": "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
        "generated_readiness": "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
        "warning": (
            "L5.7 defines controlled canonical learning promotion architecture only. "
            "Candidates remain unapproved and unapplied; canonical policy, brain, memory, "
            "strategy, Y*, Y-star-gov, and gov-mcp remain unmodified."
        ),
    }


def build_approved_sandbox_update_summary(
    sandbox_summary: dict[str, Any] | None,
    approval_summary: dict[str, Any] | None,
    baseline_summary: dict[str, Any] | None,
    patch_summary: dict[str, Any] | None,
    validation_summary: dict[str, Any] | None,
    reprojection_summary: dict[str, Any] | None,
    cieu_summary: dict[str, Any] | None,
    rollback_summary: dict[str, Any] | None,
    effect_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.approved_sandbox_update_summary",
            "schema_version": "v0",
            "l5_8_approved_canonical_update_sandbox_defined": False,
            "ready_for_l5_9_real_approval_workflow_boundary": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Approved canonical update sandbox has not been generated yet.",
        }
    sandbox_summary = sandbox_summary or {}
    approval_summary = approval_summary or {}
    baseline_summary = baseline_summary or {}
    patch_summary = patch_summary or {}
    validation_summary = validation_summary or {}
    reprojection_summary = reprojection_summary or {}
    cieu_summary = cieu_summary or {}
    rollback_summary = rollback_summary or {}
    effect_summary = effect_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.approved_sandbox_update_summary",
        "schema_version": "v0",
        "l5_8_approved_canonical_update_sandbox_defined": sandbox_summary.get(
            "l5_8_approved_canonical_update_sandbox_defined"
        ),
        "sandbox_approval_fixture_generated": approval_summary.get(
            "sandbox_approval_fixture_generated"
        ),
        "sandbox_application_approved": approval_summary.get("sandbox_application_approved"),
        "real_application_approved": approval_summary.get("real_application_approved"),
        "candidate_real_approved": approval_summary.get("candidate_real_approved"),
        "sandbox_baseline_generated": baseline_summary.get(
            "sandbox_canonical_baseline_generated"
        ),
        "sandbox_patch_applied": patch_summary.get("sandbox_patch_applied"),
        "real_canonical_state_unchanged": readiness_summary.get(
            "real_canonical_state_unchanged"
        ),
        "y_star_non_mutation_invariant_preserved": readiness_summary.get(
            "y_star_non_mutation_invariant_preserved"
        ),
        "sandbox_post_update_validation_generated": validation_summary.get(
            "sandbox_post_update_validation_generated"
        ),
        "sandbox_post_update_validation_passed": validation_summary.get(
            "sandbox_post_update_validation_passed"
        ),
        "sandbox_behavior_y_star_reprojection_generated": reprojection_summary.get(
            "sandbox_behavior_y_star_reprojection_generated"
        ),
        "sandbox_governed_mcp_preview_generated": reprojection_summary.get(
            "sandbox_governed_mcp_preview_generated"
        ),
        "sandbox_update_cieu_like_fixture_generated": cieu_summary.get(
            "sandbox_update_cieu_like_fixture_generated"
        ),
        "sandbox_update_residual_delta_generated": cieu_summary.get(
            "sandbox_update_residual_delta_generated"
        ),
        "sandbox_rollback_validation_generated": rollback_summary.get(
            "sandbox_rollback_performed"
        ),
        "rollback_restored_baseline": rollback_summary.get("rollback_restored_baseline"),
        "original_vs_sandbox_vs_rollback_comparison_generated": readiness_summary.get(
            "original_sandbox_rollback_comparison_generated"
        ),
        "sandbox_update_effect_class": effect_summary.get("effect_class"),
        "previous_residual_influenced_sandbox_projection": effect_summary.get(
            "previous_residual_influenced_sandbox_projection"
        ),
        "real_candidate_approved": readiness_summary.get("real_candidate_approved"),
        "real_candidate_applied": readiness_summary.get("real_candidate_applied"),
        "real_canonical_policy_mutation_performed": readiness_summary.get(
            "real_canonical_policy_mutation_performed"
        ),
        "real_canonical_update_application_performed": readiness_summary.get(
            "real_canonical_update_application_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "strategy_mutation_performed": readiness_summary.get("strategy_mutation_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_9_real_approval_workflow_boundary": readiness_summary.get(
            "ready_for_l5_9_real_approval_workflow_boundary"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_sandbox_summary": "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
        "generated_approval_summary": "sandbox_approval_fixture/sandbox_approval_summary.json",
        "generated_baseline_summary": "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
        "generated_patch_summary": "sandbox_patch_application/sandbox_patch_application_summary.json",
        "generated_validation_summary": "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
        "generated_reprojection_summary": "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
        "generated_cieu_summary": "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
        "generated_rollback_summary": "sandbox_rollback_validation/sandbox_rollback_summary.json",
        "generated_effect_summary": "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
        "generated_readiness": "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
        "warning": (
            "L5.8 is sandbox-only. Sandbox approval and patch application are generated "
            "artifacts only; real candidate approval, real canonical mutation, writeback, "
            "direct Y* mutation, MCP execution, and live execution remain blocked."
        ),
    }


def build_real_approval_workflow_summary(
    workflow_summary: dict[str, Any] | None,
    authority_summary: dict[str, Any] | None,
    evidence_summary: dict[str, Any] | None,
    record_summary: dict[str, Any] | None,
    decision_summary: dict[str, Any] | None,
    validity_summary: dict[str, Any] | None,
    snapshot_summary: dict[str, Any] | None,
    boundary_summary: dict[str, Any] | None,
    preflight_summary: dict[str, Any] | None,
    runbook_summary: dict[str, Any] | None,
    audit_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.real_approval_workflow_summary",
            "schema_version": "v0",
            "l5_9_real_approval_workflow_boundary_defined": False,
            "ready_for_l5_10_controlled_approval_record_sandbox": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Real approval workflow boundary has not been generated yet.",
        }
    workflow_summary = workflow_summary or {}
    authority_summary = authority_summary or {}
    evidence_summary = evidence_summary or {}
    record_summary = record_summary or {}
    decision_summary = decision_summary or {}
    validity_summary = validity_summary or {}
    snapshot_summary = snapshot_summary or {}
    boundary_summary = boundary_summary or {}
    preflight_summary = preflight_summary or {}
    runbook_summary = runbook_summary or {}
    audit_summary = audit_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.real_approval_workflow_summary",
        "schema_version": "v0",
        "l5_9_real_approval_workflow_boundary_defined": workflow_summary.get(
            "l5_9_real_approval_workflow_boundary_defined"
        ),
        "approval_authority_model_generated": authority_summary.get(
            "approval_authority_model_generated"
        ),
        "approval_evidence_dossier_generated": evidence_summary.get(
            "approval_evidence_dossier_generated"
        ),
        "durable_approval_record_contract_generated": record_summary.get(
            "durable_approval_record_contract_generated"
        ),
        "approval_decision_packet_fixture_generated": decision_summary.get(
            "approval_decision_packet_fixture_generated"
        ),
        "validity_revocation_policy_generated": validity_summary.get(
            "validity_revocation_policy_generated"
        ),
        "pre_application_snapshot_policy_generated": snapshot_summary.get(
            "pre_application_snapshot_policy_generated"
        ),
        "real_application_boundary_gate_generated": boundary_summary.get(
            "real_application_boundary_gate_generated"
        ),
        "post_approval_preflight_validation_plan_generated": preflight_summary.get(
            "post_approval_preflight_validation_defined"
        ),
        "manual_approval_runbook_generated": runbook_summary.get(
            "manual_approval_runbook_generated"
        ),
        "approval_workflow_cieu_like_fixture_generated": audit_summary.get(
            "approval_workflow_cieu_like_fixture_generated"
        ),
        "real_approval_granted": readiness_summary.get("real_approval_granted"),
        "real_application_authorized": readiness_summary.get("real_application_authorized"),
        "approval_record_created_as_durable_record": readiness_summary.get(
            "approval_record_created_as_durable_record"
        ),
        "durable_approval_record_written": readiness_summary.get(
            "durable_approval_record_written"
        ),
        "durable_db_write_performed": readiness_summary.get("durable_db_write_performed"),
        "real_canonical_policy_mutation_performed": readiness_summary.get(
            "real_canonical_policy_mutation_performed"
        ),
        "real_canonical_update_application_performed": readiness_summary.get(
            "real_canonical_update_application_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "strategy_mutation_performed": readiness_summary.get("strategy_mutation_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "real_approval_still_blocked": readiness_summary.get("real_approval_still_blocked"),
        "real_application_still_blocked": readiness_summary.get(
            "real_application_still_blocked"
        ),
        "durable_approval_persistence_still_blocked": readiness_summary.get(
            "durable_approval_persistence_still_blocked"
        ),
        "brain_writeback_still_blocked": readiness_summary.get("brain_writeback_still_blocked"),
        "memory_ingestion_still_blocked": readiness_summary.get(
            "memory_ingestion_still_blocked"
        ),
        "y_star_direct_mutation_still_blocked": readiness_summary.get(
            "y_star_direct_mutation_still_blocked"
        ),
        "mcp_execution_still_blocked": readiness_summary.get("mcp_execution_still_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": readiness_summary.get(
            "durable_approval_persistence_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_10_controlled_approval_record_sandbox": readiness_summary.get(
            "ready_for_l5_10_controlled_approval_record_sandbox"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_workflow_summary": "real_approval_workflow_boundary/real_approval_workflow_summary.json",
        "generated_authority_summary": "approval_authority_model/approval_authority_summary.json",
        "generated_evidence_summary": "approval_evidence_dossier/approval_evidence_summary.json",
        "generated_record_summary": "durable_approval_record_contract/approval_record_summary.json",
        "generated_decision_summary": "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
        "generated_validity_summary": "approval_validity_revocation_policy/approval_validity_summary.json",
        "generated_snapshot_summary": "pre_application_snapshot_policy/snapshot_policy_summary.json",
        "generated_boundary_summary": "real_application_boundary_gate/real_application_boundary_summary.json",
        "generated_preflight_summary": "post_approval_preflight_validation/post_approval_preflight_summary.json",
        "generated_runbook_summary": "manual_approval_runbook/manual_approval_runbook_summary.json",
        "generated_audit_summary": "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
        "generated_readiness": "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
        "warning": (
            "L5.9 defines the real approval workflow boundary only. No real approval is "
            "granted, no durable approval record is written, and no real canonical update "
            "application is authorized."
        ),
    }


def build_controlled_approval_record_summary(
    sandbox_summary: dict[str, Any] | None,
    record_summary: dict[str, Any] | None,
    integrity_summary: dict[str, Any] | None,
    state_machine_summary: dict[str, Any] | None,
    revocation_summary: dict[str, Any] | None,
    gate_summary: dict[str, Any] | None,
    audit_summary: dict[str, Any] | None,
    cieu_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.controlled_approval_record_summary",
            "schema_version": "v0",
            "l5_10_controlled_approval_record_sandbox_defined": False,
            "ready_for_l5_11_controlled_real_release_preflight": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Controlled approval record sandbox has not been generated yet.",
        }
    sandbox_summary = sandbox_summary or {}
    record_summary = record_summary or {}
    integrity_summary = integrity_summary or {}
    state_machine_summary = state_machine_summary or {}
    revocation_summary = revocation_summary or {}
    gate_summary = gate_summary or {}
    audit_summary = audit_summary or {}
    cieu_summary = cieu_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.controlled_approval_record_summary",
        "schema_version": "v0",
        "l5_10_controlled_approval_record_sandbox_defined": sandbox_summary.get(
            "l5_10_controlled_approval_record_sandbox_defined"
        ),
        "sandbox_approval_record_instance_generated": record_summary.get(
            "sandbox_approval_record_instance_generated"
        ),
        "integrity_validation_generated": integrity_summary.get(
            "integrity_validation_generated"
        ),
        "integrity_validation_status": integrity_summary.get("validation_status"),
        "validity_state_machine_replay_generated": state_machine_summary.get(
            "sandbox_state_machine_replayed"
        ),
        "current_sandbox_state": state_machine_summary.get("current_sandbox_state"),
        "expired_revoked_tampered_wrong_scope_missing_evidence_blocked": (
            revocation_summary.get("invalid_record_variants_generated_and_blocked")
        ),
        "valid_sandbox_record_gate_replay_generated": gate_summary.get(
            "valid_record_gate_replay_generated"
        ),
        "valid_record_gate_result": gate_summary.get("valid_record_gate_result"),
        "invalid_record_gate_blocking_generated": gate_summary.get(
            "invalid_record_gate_blocking_generated"
        ),
        "audit_lineage_generated": audit_summary.get("audit_lineage_generated"),
        "approval_record_cieu_like_fixture_generated": cieu_summary.get(
            "approval_record_cieu_like_fixture_generated"
        ),
        "approval_record_residual_delta_generated": cieu_summary.get(
            "approval_record_residual_delta_generated"
        ),
        "real_approval_granted": readiness_summary.get("real_approval_granted"),
        "durable_approval_record_written": readiness_summary.get(
            "durable_approval_record_written"
        ),
        "real_application_authorized": readiness_summary.get("real_application_authorized"),
        "canonical_policy_mutation_performed": readiness_summary.get(
            "canonical_policy_mutation_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "durable_persistence_still_blocked": readiness_summary.get(
            "durable_persistence_still_blocked"
        ),
        "real_approval_still_blocked": readiness_summary.get("real_approval_still_blocked"),
        "real_application_still_blocked": readiness_summary.get(
            "real_application_still_blocked"
        ),
        "brain_writeback_still_blocked": readiness_summary.get("brain_writeback_still_blocked"),
        "memory_ingestion_still_blocked": readiness_summary.get(
            "memory_ingestion_still_blocked"
        ),
        "y_star_direct_mutation_still_blocked": readiness_summary.get(
            "y_star_direct_mutation_still_blocked"
        ),
        "mcp_execution_still_blocked": readiness_summary.get("mcp_execution_still_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": readiness_summary.get(
            "durable_approval_persistence_enabled"
        ),
        "real_approval_record_write_enabled": readiness_summary.get(
            "real_approval_record_write_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_11_controlled_real_release_preflight": readiness_summary.get(
            "ready_for_l5_11_controlled_real_release_preflight"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_sandbox_summary": "controlled_approval_record_sandbox/controlled_approval_record_sandbox_summary.json",
        "generated_record_summary": "sandbox_approval_record_instance/sandbox_approval_record_summary.json",
        "generated_integrity_summary": "approval_record_integrity_validation/approval_record_integrity_summary.json",
        "generated_state_machine_summary": "approval_record_validity_state_machine/approval_record_state_machine_summary.json",
        "generated_revocation_summary": "expiration_revocation_replay/expiration_revocation_replay_summary.json",
        "generated_gate_summary": "approval_record_pre_application_gate_replay/pre_application_gate_replay_summary.json",
        "generated_audit_summary": "approval_record_audit_lineage/approval_record_audit_summary.json",
        "generated_cieu_summary": "approval_record_cieu_residual/approval_record_cieu_summary.json",
        "generated_readiness": "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
        "warning": (
            "L5.10 creates a sandbox approval record lifecycle only. No real approval is "
            "granted, no durable approval record is written, and no real canonical update "
            "application is authorized."
        ),
    }


def build_controlled_real_release_preflight_summary(
    preflight_summary: dict[str, Any] | None,
    release_summary: dict[str, Any] | None,
    scope_summary: dict[str, Any] | None,
    approval_summary: dict[str, Any] | None,
    snapshot_rollback_summary: dict[str, Any] | None,
    invariant_summary: dict[str, Any] | None,
    post_release_summary: dict[str, Any] | None,
    handoff_summary: dict[str, Any] | None,
    blocker_summary: dict[str, Any] | None,
    cieu_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.controlled_real_release_preflight_summary",
            "schema_version": "v0",
            "l5_11_controlled_real_release_preflight_defined": False,
            "ready_for_l5_12_real_release_simulation_sandbox": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Controlled real release preflight has not been generated yet.",
        }
    preflight_summary = preflight_summary or {}
    release_summary = release_summary or {}
    scope_summary = scope_summary or {}
    approval_summary = approval_summary or {}
    snapshot_rollback_summary = snapshot_rollback_summary or {}
    invariant_summary = invariant_summary or {}
    post_release_summary = post_release_summary or {}
    handoff_summary = handoff_summary or {}
    blocker_summary = blocker_summary or {}
    cieu_summary = cieu_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.controlled_real_release_preflight_summary",
        "schema_version": "v0",
        "l5_11_controlled_real_release_preflight_defined": preflight_summary.get(
            "l5_11_controlled_real_release_preflight_defined"
        ),
        "release_candidate_assembled": release_summary.get("release_candidate_assembled"),
        "release_scope_validation_generated": scope_summary.get(
            "release_scope_validation_generated"
        ),
        "release_scope_validation_status": scope_summary.get("validation_status"),
        "approval_record_preflight_generated": approval_summary.get(
            "approval_record_preflight_generated"
        ),
        "approval_record_validation_status": approval_summary.get("validation_status"),
        "snapshot_rollback_preflight_generated": (
            snapshot_rollback_summary.get("snapshot_preflight_generated")
            and snapshot_rollback_summary.get("rollback_preflight_generated")
        ),
        "snapshot_preflight_generated": snapshot_rollback_summary.get(
            "snapshot_preflight_generated"
        ),
        "rollback_preflight_generated": snapshot_rollback_summary.get(
            "rollback_preflight_generated"
        ),
        "y_star_non_mutation_preflight_generated": invariant_summary.get(
            "y_star_non_mutation_preflight_generated"
        ),
        "mcp_non_bypass_preflight_generated": invariant_summary.get(
            "mcp_non_bypass_preflight_generated"
        ),
        "no_direct_writeback_preflight_generated": invariant_summary.get(
            "no_direct_writeback_preflight_generated"
        ),
        "post_release_validation_matrix_generated": post_release_summary.get(
            "post_release_validation_matrix_generated"
        ),
        "release_operator_handoff_packet_generated": handoff_summary.get(
            "release_operator_handoff_packet_generated"
        ),
        "release_blocker_decision_generated": blocker_summary.get(
            "release_blocker_decision_generated"
        ),
        "release_blocker_decision": blocker_summary.get("decision"),
        "release_preflight_cieu_like_fixture_generated": cieu_summary.get(
            "release_preflight_cieu_like_fixture_generated"
        ),
        "release_preflight_residual_delta_generated": cieu_summary.get(
            "release_preflight_residual_delta_generated"
        ),
        "real_approval_granted": False,
        "real_release_authorized": readiness_summary.get("real_release_authorized"),
        "real_application_authorized": readiness_summary.get("real_application_authorized"),
        "durable_approval_record_written": readiness_summary.get(
            "durable_approval_record_written"
        ),
        "canonical_policy_mutation_performed": readiness_summary.get(
            "canonical_policy_mutation_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "real_release_still_blocked": readiness_summary.get("real_release_still_blocked"),
        "real_approval_still_blocked": readiness_summary.get("real_approval_still_blocked"),
        "durable_persistence_still_blocked": readiness_summary.get(
            "durable_persistence_still_blocked"
        ),
        "real_canonical_application_still_blocked": readiness_summary.get(
            "real_canonical_application_still_blocked"
        ),
        "brain_writeback_still_blocked": readiness_summary.get("brain_writeback_still_blocked"),
        "memory_ingestion_still_blocked": readiness_summary.get(
            "memory_ingestion_still_blocked"
        ),
        "y_star_direct_mutation_still_blocked": readiness_summary.get(
            "y_star_direct_mutation_still_blocked"
        ),
        "mcp_execution_still_blocked": readiness_summary.get("mcp_execution_still_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": readiness_summary.get(
            "durable_approval_persistence_enabled"
        ),
        "real_approval_record_write_enabled": readiness_summary.get(
            "real_approval_record_write_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_release_execution_enabled": readiness_summary.get(
            "real_release_execution_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_12_real_release_simulation_sandbox": readiness_summary.get(
            "ready_for_l5_12_real_release_simulation_sandbox"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_preflight_summary": "controlled_real_release_preflight/controlled_real_release_preflight_summary.json",
        "generated_release_candidate_summary": "release_candidate_package/release_candidate_summary.json",
        "generated_scope_summary": "release_scope_validation/release_scope_validation_summary.json",
        "generated_approval_record_preflight_summary": "approval_record_preflight_validation/approval_record_preflight_summary.json",
        "generated_snapshot_rollback_summary": "snapshot_and_rollback_preflight/snapshot_rollback_preflight_summary.json",
        "generated_invariant_summary": "invariant_preflight_validation/invariant_preflight_summary.json",
        "generated_post_release_summary": "post_release_validation_matrix/post_release_validation_summary.json",
        "generated_handoff_summary": "release_operator_handoff_packet/release_operator_handoff_summary.json",
        "generated_blocker_summary": "release_blocker_decision/release_blocker_summary.json",
        "generated_cieu_summary": "release_preflight_cieu_residual/release_preflight_cieu_summary.json",
        "generated_readiness": "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
        "warning": (
            "L5.11 defines the controlled real release preflight only. No real approval "
            "is granted, no durable approval record is written, no real release is "
            "authorized, and no canonical update is applied."
        ),
    }


def build_real_release_simulation_summary(
    simulation_summary: dict[str, Any] | None,
    authority_summary: dict[str, Any] | None,
    record_summary: dict[str, Any] | None,
    snapshot_summary: dict[str, Any] | None,
    plan_summary: dict[str, Any] | None,
    result_summary: dict[str, Any] | None,
    validation_summary: dict[str, Any] | None,
    preview_summary: dict[str, Any] | None,
    rollback_summary: dict[str, Any] | None,
    safety_summary: dict[str, Any] | None,
    cieu_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.real_release_simulation_summary",
            "schema_version": "v0",
            "l5_12_real_release_simulation_sandbox_defined": False,
            "ready_for_l5_13_live_boundary_no_go_decision_framework": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Real release simulation sandbox has not been generated yet.",
        }
    simulation_summary = simulation_summary or {}
    authority_summary = authority_summary or {}
    record_summary = record_summary or {}
    snapshot_summary = snapshot_summary or {}
    plan_summary = plan_summary or {}
    result_summary = result_summary or {}
    validation_summary = validation_summary or {}
    preview_summary = preview_summary or {}
    rollback_summary = rollback_summary or {}
    safety_summary = safety_summary or {}
    cieu_summary = cieu_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.real_release_simulation_summary",
        "schema_version": "v0",
        "l5_12_real_release_simulation_sandbox_defined": simulation_summary.get(
            "l5_12_real_release_simulation_sandbox_defined"
        ),
        "sandbox_release_authority_fixture_generated": authority_summary.get(
            "sandbox_release_authority_fixture_generated"
        ),
        "simulated_durable_approval_record_generated": record_summary.get(
            "simulated_durable_approval_record_generated"
        ),
        "sandbox_snapshot_generated": snapshot_summary.get("sandbox_snapshot_generated"),
        "simulated_release_operator_confirmed": authority_summary.get(
            "simulated_release_operator_confirmed"
        ),
        "simulated_rollback_operator_confirmed": authority_summary.get(
            "simulated_rollback_operator_confirmed"
        ),
        "sandbox_release_execution_plan_generated": plan_summary.get(
            "sandbox_release_execution_plan_generated"
        ),
        "sandbox_release_execution_generated": result_summary.get(
            "sandbox_release_execution_generated"
        ),
        "sandbox_release_executed": result_summary.get("sandbox_release_executed"),
        "real_canonical_state_unchanged": result_summary.get(
            "real_canonical_state_unchanged"
        ),
        "sandbox_post_release_validation_generated": validation_summary.get(
            "sandbox_post_release_validation_generated"
        ),
        "sandbox_post_release_validation_status": validation_summary.get(
            "sandbox_post_release_validation_status"
        ),
        "sandbox_post_release_projection_generated": preview_summary.get(
            "sandbox_post_release_projection_generated"
        ),
        "sandbox_mcp_preview_generated": preview_summary.get(
            "sandbox_mcp_preview_generated"
        ),
        "sandbox_rollback_drill_generated": rollback_summary.get(
            "sandbox_rollback_drill_generated"
        ),
        "rollback_restored_baseline": rollback_summary.get("rollback_restored_baseline"),
        "original_release_rollback_comparison_generated": bool(safety_summary),
        "release_simulation_cieu_like_fixture_generated": cieu_summary.get(
            "release_simulation_cieu_like_fixture_generated"
        ),
        "release_simulation_residual_delta_generated": cieu_summary.get(
            "release_simulation_residual_delta_generated"
        ),
        "real_approval_granted": readiness_summary.get("real_approval_granted"),
        "real_release_authorized": readiness_summary.get("real_release_authorized"),
        "real_release_performed": readiness_summary.get("real_release_performed"),
        "durable_approval_record_written": readiness_summary.get(
            "durable_approval_record_written"
        ),
        "canonical_policy_mutation_performed": readiness_summary.get(
            "canonical_policy_mutation_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "real_release_still_blocked": readiness_summary.get("real_release_still_blocked"),
        "real_approval_still_blocked": readiness_summary.get("real_approval_still_blocked"),
        "durable_persistence_still_blocked": readiness_summary.get(
            "durable_persistence_still_blocked"
        ),
        "real_canonical_application_still_blocked": readiness_summary.get(
            "real_canonical_application_still_blocked"
        ),
        "brain_writeback_still_blocked": readiness_summary.get("brain_writeback_still_blocked"),
        "memory_ingestion_still_blocked": readiness_summary.get(
            "memory_ingestion_still_blocked"
        ),
        "y_star_direct_mutation_still_blocked": readiness_summary.get(
            "y_star_direct_mutation_still_blocked"
        ),
        "mcp_execution_still_blocked": readiness_summary.get("mcp_execution_still_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": readiness_summary.get(
            "durable_approval_persistence_enabled"
        ),
        "real_approval_record_write_enabled": readiness_summary.get(
            "real_approval_record_write_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_release_execution_enabled": readiness_summary.get(
            "real_release_execution_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_13_live_boundary_no_go_decision_framework": readiness_summary.get(
            "ready_for_l5_13_live_boundary_no_go_decision_framework"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_simulation_summary": "real_release_simulation_sandbox/real_release_simulation_summary.json",
        "generated_authority_summary": "sandbox_release_authority_fixture/sandbox_release_authority_summary.json",
        "generated_simulated_record_summary": "simulated_durable_approval_record/simulated_approval_record_summary.json",
        "generated_snapshot_summary": "sandbox_release_snapshot/sandbox_release_snapshot_summary.json",
        "generated_plan_summary": "sandbox_release_execution_plan/sandbox_release_execution_summary.json",
        "generated_result_summary": "sandbox_release_execution_result/sandbox_release_execution_result_summary.json",
        "generated_validation_summary": "sandbox_post_release_validation/sandbox_post_release_validation_summary.json",
        "generated_projection_mcp_summary": "sandbox_release_projection_and_mcp_preview/sandbox_release_projection_mcp_summary.json",
        "generated_rollback_summary": "sandbox_release_rollback_drill/sandbox_release_rollback_summary.json",
        "generated_comparison_summary": "original_release_rollback_comparison/sandbox_release_safety_summary.json",
        "generated_cieu_summary": "release_simulation_cieu_residual/release_simulation_cieu_summary.json",
        "generated_readiness": "real_release_simulation_readiness/real_release_simulation_readiness.json",
        "warning": (
            "L5.12 simulates a release only in generated sandbox artifacts. No real "
            "approval is granted, no durable approval record is written, no real release "
            "is authorized, and no canonical update is applied."
        ),
    }


def build_live_boundary_no_go_summary(
    framework_summary: dict[str, Any] | None,
    capability_summary: dict[str, Any] | None,
    invariant_summary: dict[str, Any] | None,
    evidence_summary: dict[str, Any] | None,
    blocker_summary: dict[str, Any] | None,
    l6_summary: dict[str, Any] | None,
    decision_summary: dict[str, Any] | None,
    cieu_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.live_boundary_no_go_summary",
            "schema_version": "v0",
            "l5_13_live_boundary_no_go_framework_defined": False,
            "ready_for_l6_meta_development_generative_engine_design": False,
            "ready_for_l6_revenue_opportunity_execution": False,
            "warning": "Live boundary no-go framework has not been generated yet.",
        }
    framework_summary = framework_summary or {}
    capability_summary = capability_summary or {}
    invariant_summary = invariant_summary or {}
    evidence_summary = evidence_summary or {}
    blocker_summary = blocker_summary or {}
    l6_summary = l6_summary or {}
    decision_summary = decision_summary or {}
    cieu_summary = cieu_summary or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.live_boundary_no_go_summary",
        "schema_version": "v0",
        "l5_13_live_boundary_no_go_framework_defined": framework_summary.get(
            "l5_13_live_boundary_no_go_framework_defined"
        ),
        "live_capability_domains_classified": capability_summary.get(
            "live_capability_domains_classified"
        ),
        "no_go_invariants_defined": invariant_summary.get("no_go_invariants_defined"),
        "l5_0_to_l5_12_evidence_indexed": framework_summary.get(
            "l5_0_to_l5_12_evidence_indexed",
            evidence_summary.get("l5_0_to_l5_12_indexed"),
        ),
        "l5_evidence_index_generated": readiness_summary.get("l5_evidence_index_generated"),
        "live_blockers_identified": blocker_summary.get("live_blockers_identified"),
        "l6_design_entry_gate_generated": l6_summary.get("l6_design_entry_gate_generated"),
        "l6_non_execution_boundary_defined": l6_summary.get("l6_non_execution_boundary_defined"),
        "l6_forbidden_hardcoding_policy_defined": l6_summary.get(
            "l6_forbidden_hardcoding_policy_defined"
        ),
        "system_no_go_decision_packet_generated": decision_summary.get(
            "system_no_go_decision_packet_generated"
        ),
        "live_boundary_cieu_like_fixture_generated": cieu_summary.get(
            "live_boundary_cieu_like_fixture_generated"
        ),
        "live_execution_decision": decision_summary.get("live_execution_decision"),
        "real_mcp_execution_decision": decision_summary.get("real_mcp_execution_decision"),
        "real_canonical_update_decision": decision_summary.get(
            "real_canonical_update_decision"
        ),
        "brain_memory_writeback_decision": decision_summary.get(
            "brain_memory_writeback_decision"
        ),
        "durable_persistence_decision": decision_summary.get("durable_persistence_decision"),
        "real_release_decision": decision_summary.get("real_release_decision"),
        "l6_design_entry_decision": decision_summary.get("l6_design_entry_decision"),
        "l6_execution_decision": decision_summary.get("l6_execution_decision"),
        "revenue_execution_decision": capability_summary.get("revenue_execution_decision"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "behavior_execution_enabled": safety_flag("behavior_execution_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "network_enabled": safety_flag("network_enabled"),
        "scheduler_enabled": safety_flag("scheduler_enabled"),
        "daemon_enabled": safety_flag("daemon_enabled"),
        "mcp_server_execution_enabled": safety_flag("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": safety_flag("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": safety_flag(
            "durable_approval_persistence_enabled"
        ),
        "real_approval_record_write_enabled": safety_flag(
            "real_approval_record_write_enabled"
        ),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "strategy_mutation_enabled": safety_flag("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": safety_flag("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": safety_flag("real_candidate_approval_enabled"),
        "real_canonical_policy_mutation_enabled": safety_flag(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_release_execution_enabled": safety_flag("real_release_execution_enabled"),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": safety_flag(
            "revenue_opportunity_discovery_enabled"
        ),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "l6_design_entry_allowed": l6_flag("l6_design_entry_allowed"),
        "l6_revenue_execution_allowed": l6_flag("l6_revenue_execution_allowed"),
        "l6_external_observation_allowed": l6_flag("l6_external_observation_allowed"),
        "l6_external_action_allowed": l6_flag("l6_external_action_allowed"),
        "l6_network_enabled": l6_flag("l6_network_enabled"),
        "l6_publication_enabled": l6_flag("l6_publication_enabled"),
        "l6_payment_enabled": l6_flag("l6_payment_enabled"),
        "live_execution_still_blocked": readiness_summary.get("live_execution_still_blocked"),
        "real_mcp_execution_still_blocked": readiness_summary.get(
            "real_mcp_execution_still_blocked"
        ),
        "real_canonical_update_still_blocked": readiness_summary.get(
            "real_canonical_update_still_blocked"
        ),
        "brain_writeback_still_blocked": readiness_summary.get("brain_writeback_still_blocked"),
        "memory_ingestion_still_blocked": readiness_summary.get(
            "memory_ingestion_still_blocked"
        ),
        "durable_persistence_still_blocked": readiness_summary.get(
            "durable_persistence_still_blocked"
        ),
        "real_release_still_blocked": readiness_summary.get("real_release_still_blocked"),
        "revenue_execution_still_blocked": readiness_summary.get(
            "revenue_execution_still_blocked"
        ),
        "external_action_still_blocked": readiness_summary.get(
            "external_action_still_blocked"
        ),
        "network_still_blocked": readiness_summary.get("network_still_blocked"),
        "ready_for_l6_meta_development_generative_engine_design": readiness_summary.get(
            "ready_for_l6_meta_development_generative_engine_design"
        ),
        "ready_for_l6_revenue_opportunity_execution": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_execution"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_framework_summary": "live_boundary_no_go_framework/live_boundary_no_go_summary.json",
        "generated_capability_summary": "live_capability_domain_registry/live_capability_summary.json",
        "generated_invariant_summary": "no_go_invariant_matrix/no_go_invariant_summary.json",
        "generated_evidence_summary": "live_readiness_evidence_index/live_readiness_evidence_summary.json",
        "generated_blocker_summary": "live_blocker_risk_register/live_blocker_summary.json",
        "generated_l6_entry_summary": "l6_meta_development_entry_gate/l6_entry_gate_summary.json",
        "generated_decision_summary": "system_no_go_decision_packet/system_live_boundary_decision_summary.json",
        "generated_cieu_summary": "live_boundary_cieu_residual/live_boundary_cieu_summary.json",
        "generated_readiness": "live_boundary_readiness/live_boundary_readiness.json",
        "warning": (
            "L5.13 is a no-go framework. Live execution, real MCP execution, real "
            "release, durable persistence, writeback, network/external action, and "
            "L6 revenue execution remain blocked. L6 is design-only."
        ),
    }


def build_l6_meta_development_summary(
    engine_summary: dict[str, Any] | None,
    self_asset_summary: dict[str, Any] | None,
    world_value_summary: dict[str, Any] | None,
    operator_summary: dict[str, Any] | None,
    hypothesis_summary: dict[str, Any] | None,
    physics_summary: dict[str, Any] | None,
    selection_summary: dict[str, Any] | None,
    mvp_summary: dict[str, Any] | None,
    portfolio_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_meta_development_summary",
            "schema_version": "v0",
            "l6_0_meta_development_generative_selection_engine_defined": False,
            "ready_for_l6_1_meta_development_mvp_artifact_sandbox": False,
            "ready_for_l6_revenue_opportunity_execution": False,
            "warning": "L6.0 meta-development generative selection engine has not been generated yet.",
        }
    engine_summary = engine_summary or {}
    self_asset_summary = self_asset_summary or {}
    world_value_summary = world_value_summary or {}
    operator_summary = operator_summary or {}
    hypothesis_summary = hypothesis_summary or {}
    physics_summary = physics_summary or {}
    selection_summary = selection_summary or {}
    mvp_summary = mvp_summary or {}
    portfolio_summary = portfolio_summary or {}
    residual_summary = residual_summary or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_meta_development_summary",
        "schema_version": "v0",
        "l6_0_meta_development_generative_selection_engine_defined": engine_summary.get(
            "l6_0_meta_development_generative_selection_engine_defined"
        ),
        "self_model_generated": self_asset_summary.get(
            "self_model_generated", readiness_summary.get("self_model_generated")
        ),
        "unique_asset_field_generated": self_asset_summary.get(
            "unique_asset_field_generated",
            readiness_summary.get("unique_asset_field_generated"),
        ),
        "world_value_field_generated": world_value_summary.get(
            "world_value_field_generated", readiness_summary.get("world_value_field_generated")
        ),
        "conversion_operator_library_generated": operator_summary.get(
            "conversion_operator_library_generated",
            readiness_summary.get("conversion_operator_library_generated"),
        ),
        "value_hypotheses_generated": hypothesis_summary.get(
            "value_hypotheses_generated", readiness_summary.get("value_hypotheses_generated")
        ),
        "non_hardcoding_check_generated": readiness_summary.get(
            "non_hardcoding_check_generated"
        ),
        "conversion_physics_defined": physics_summary.get(
            "conversion_physics_defined", readiness_summary.get("conversion_physics_defined")
        ),
        "redeemability_selection_generated": selection_summary.get(
            "redeemability_selection_generated",
            readiness_summary.get("redeemability_selection_generated"),
        ),
        "minimum_viable_proof_plans_generated": mvp_summary.get(
            "minimum_viable_proof_plans_generated",
            readiness_summary.get("minimum_viable_proof_plans_generated"),
        ),
        "governed_experiment_portfolio_generated": portfolio_summary.get(
            "governed_experiment_portfolio_generated",
            readiness_summary.get("governed_experiment_portfolio_generated"),
        ),
        "strategic_residual_loop_generated": residual_summary.get(
            "strategic_residual_loop_generated",
            readiness_summary.get("strategic_residual_loop_generated"),
        ),
        "l6_design_only": engine_summary.get("l6_design_only", True),
        "hardcoded_opportunity_categories_forbidden": engine_summary.get(
            "hardcoded_opportunity_categories_forbidden", True
        ),
        "seed_examples_non_exhaustive": engine_summary.get(
            "seed_examples_non_exhaustive", True
        ),
        "seed_examples_not_authorized_for_execution": engine_summary.get(
            "seed_examples_not_authorized_for_execution", True
        ),
        "hypothesis_count": hypothesis_summary.get("hypothesis_count"),
        "selected_for_sandbox_design_count": selection_summary.get(
            "selected_for_sandbox_design_count"
        ),
        "mvp_plan_count": mvp_summary.get("mvp_plan_count"),
        "experiment_count": portfolio_summary.get("experiment_count"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "behavior_execution_enabled": safety_flag("behavior_execution_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "network_enabled": safety_flag("network_enabled"),
        "scheduler_enabled": safety_flag("scheduler_enabled"),
        "daemon_enabled": safety_flag("daemon_enabled"),
        "mcp_server_execution_enabled": safety_flag("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": safety_flag("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": safety_flag(
            "durable_approval_persistence_enabled"
        ),
        "real_approval_record_write_enabled": safety_flag(
            "real_approval_record_write_enabled"
        ),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "strategy_mutation_enabled": safety_flag("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": safety_flag("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": safety_flag("real_candidate_approval_enabled"),
        "real_canonical_policy_mutation_enabled": safety_flag(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_release_execution_enabled": safety_flag("real_release_execution_enabled"),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": safety_flag(
            "revenue_opportunity_discovery_enabled"
        ),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "external_market_scan_enabled": safety_flag("external_market_scan_enabled"),
        "public_content_publication_enabled": safety_flag(
            "public_content_publication_enabled"
        ),
        "payment_enabled": safety_flag("payment_enabled"),
        "l6_design_only_enabled": l6_flag("l6_design_only_enabled"),
        "l6_hypothesis_generation_enabled": l6_flag("l6_hypothesis_generation_enabled"),
        "l6_selection_design_enabled": l6_flag("l6_selection_design_enabled"),
        "l6_sandbox_experiment_design_enabled": l6_flag(
            "l6_sandbox_experiment_design_enabled"
        ),
        "l6_external_execution_enabled": l6_flag("l6_external_execution_enabled"),
        "l6_network_enabled": l6_flag("l6_network_enabled"),
        "l6_publication_enabled": l6_flag("l6_publication_enabled"),
        "l6_payment_enabled": l6_flag("l6_payment_enabled"),
        "l6_revenue_execution_enabled": l6_flag("l6_revenue_execution_enabled"),
        "l6_execution_still_blocked": readiness_summary.get("l6_execution_still_blocked"),
        "external_action_still_blocked": readiness_summary.get(
            "external_action_still_blocked"
        ),
        "network_still_blocked": readiness_summary.get("network_still_blocked"),
        "publication_still_blocked": readiness_summary.get("publication_still_blocked"),
        "payment_still_blocked": readiness_summary.get("payment_still_blocked"),
        "revenue_execution_still_blocked": readiness_summary.get(
            "revenue_execution_still_blocked"
        ),
        "ready_for_l6_1_meta_development_mvp_artifact_sandbox": readiness_summary.get(
            "ready_for_l6_1_meta_development_mvp_artifact_sandbox"
        ),
        "ready_for_l6_revenue_opportunity_execution": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_execution"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_engine_summary": (
            "l6_meta_development_generative_selection_engine/"
            "l6_generative_selection_engine_summary.json"
        ),
        "generated_self_asset_summary": "self_model_and_unique_asset_field/self_asset_summary.json",
        "generated_world_value_summary": "world_value_field_model/world_value_field_summary.json",
        "generated_operator_summary": "value_conversion_operator_library/operator_library_summary.json",
        "generated_hypothesis_summary": "open_value_hypothesis_generator/hypothesis_generator_summary.json",
        "generated_physics_summary": "value_conversion_physics/conversion_physics_summary.json",
        "generated_selection_summary": "redeemability_selection_engine/selection_engine_summary.json",
        "generated_mvp_summary": "minimum_viable_proof_designer/mvp_design_summary.json",
        "generated_portfolio_summary": (
            "governed_meta_development_experiment_portfolio/"
            "experiment_portfolio_summary.json"
        ),
        "generated_residual_summary": (
            "strategic_residual_meta_learning_loop/strategic_residual_summary.json"
        ),
        "generated_readiness": (
            "l6_meta_development_design_readiness/"
            "l6_meta_development_design_readiness.json"
        ),
        "warning": (
            "L6.0 is design-only. External observation, network, publication, "
            "payment, revenue execution, MCP execution, persistence, writeback, "
            "and hard-coded opportunity catalogs remain blocked."
        ),
    }


def build_l6_mvp_artifact_sandbox_summary(
    milestone_summary: dict[str, Any] | None,
    selected_hypotheses: dict[str, Any] | None,
    case_index: dict[str, Any] | None,
    validation_matrix: dict[str, Any] | None,
    review_gate: dict[str, Any] | None,
    externalization_blocker: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_mvp_artifact_sandbox_summary",
            "schema_version": "v0",
            "l6_1_mvp_artifact_sandbox_defined": False,
            "ready_for_l6_2_external_observation_boundary_design": False,
            "ready_for_external_execution": False,
            "warning": "L6.1 MVP artifact sandbox has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_hypotheses = selected_hypotheses or {}
    case_index = case_index or {}
    validation_matrix = validation_matrix or {}
    review_gate = review_gate or {}
    externalization_blocker = externalization_blocker or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_1_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_1_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_mvp_artifact_sandbox_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.1"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Meta-Development MVP Artifact Sandbox v0"
        ),
        "l6_1_mvp_artifact_sandbox_defined": milestone_summary.get(
            "l6_1_mvp_artifact_sandbox_defined",
            readiness_summary.get("l6_1_artifact_sandbox_complete"),
        ),
        "selected_hypotheses_count": selected_hypotheses.get(
            "selected_count", milestone_summary.get("selected_hypotheses_count")
        ),
        "generated_case_count": case_index.get(
            "case_count", milestone_summary.get("generated_case_count")
        ),
        "internal_artifacts_generated": milestone_summary.get(
            "internal_artifacts_generated",
            readiness_summary.get("l6_1_artifact_sandbox_complete"),
        ),
        "artifact_generation_authorized": milestone_summary.get(
            "artifact_generation_authorized",
            readiness_summary.get("artifact_generation_authorized"),
        ),
        "review_gate_generated": readiness_summary.get(
            "review_gate_generated", bool(review_gate)
        ),
        "externalization_boundary_generated": readiness_summary.get(
            "externalization_boundary_generated", bool(externalization_blocker)
        ),
        "strategic_residual_loop_generated": readiness_summary.get(
            "strategic_residual_loop_generated", bool(residual_delta)
        ),
        "structural_validation_only": validation_matrix.get(
            "validation_mode"
        ) == "structural_review_only",
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "network_enabled": safety_flag("network_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_1_sandbox_only": l6_1_flag("l6_1_sandbox_only"),
        "l6_1_internal_artifact_generation_enabled": l6_1_flag(
            "l6_1_internal_artifact_generation_enabled"
        ),
        "l6_1_artifact_review_gate_required": l6_1_flag(
            "l6_1_artifact_review_gate_required"
        ),
        "l6_1_external_execution_enabled": l6_1_flag(
            "l6_1_external_execution_enabled"
        ),
        "l6_1_network_enabled": l6_1_flag("l6_1_network_enabled"),
        "l6_1_publication_enabled": l6_1_flag("l6_1_publication_enabled"),
        "l6_1_outreach_enabled": l6_1_flag("l6_1_outreach_enabled"),
        "l6_1_payment_enabled": l6_1_flag("l6_1_payment_enabled"),
        "l6_1_revenue_execution_enabled": l6_1_flag(
            "l6_1_revenue_execution_enabled"
        ),
        "ready_for_l6_2_external_observation_boundary_design": readiness_summary.get(
            "ready_for_l6_2_external_observation_boundary_design"
        ),
        "ready_for_external_execution": readiness_summary.get("ready_for_external_execution"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get(
            "next_recommended_milestone"
        ),
        "generated_milestone_summary": "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
        "generated_selected_hypotheses": (
            "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json"
        ),
        "generated_case_index": "selected_mvp_artifact_cases/selected_case_index.json",
        "generated_validation_matrix": (
            "mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json"
        ),
        "generated_review_gate": "mvp_artifact_review_gate/review_gate_contract.json",
        "generated_externalization_blocker": (
            "mvp_artifact_externalization_boundary/externalization_blocker.json"
        ),
        "generated_readiness": "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
        "warning": (
            "L6.1 generated internal MVP proof artifacts only. Publication, "
            "outreach, payment, network, revenue, MCP, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }


def build_l6_external_observation_boundary_summary(
    milestone_summary: dict[str, Any] | None,
    packet_schema: dict[str, Any] | None,
    source_registry: dict[str, Any] | None,
    permission_gate: dict[str, Any] | None,
    manual_import_contract: dict[str, Any] | None,
    linker_contract: dict[str, Any] | None,
    claim_policy: dict[str, Any] | None,
    no_network_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": (
                "ystar.console_read_model.generated."
                "l6_external_observation_boundary_summary"
            ),
            "schema_version": "v0",
            "l6_2_external_observation_boundary_defined": False,
            "ready_for_l6_3_controlled_external_observation_sandbox": False,
            "ready_for_real_network_observation": False,
            "warning": "L6.2 external observation boundary has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    packet_schema = packet_schema or {}
    source_registry = source_registry or {}
    permission_gate = permission_gate or {}
    manual_import_contract = manual_import_contract or {}
    linker_contract = linker_contract or {}
    claim_policy = claim_policy or {}
    no_network_receipt = no_network_receipt or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_2_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_2_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_external_observation_boundary_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.2"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Governed External Observation Boundary v0"
        ),
        "l6_2_external_observation_boundary_defined": milestone_summary.get(
            "l6_2_external_observation_boundary_defined",
            readiness_summary.get("l6_2_external_observation_boundary_complete"),
        ),
        "boundary_only": milestone_summary.get("boundary_only", True),
        "sandbox_only": milestone_summary.get("sandbox_only", True),
        "pre_observation_packet_schema_defined": milestone_summary.get(
            "pre_observation_packet_schema_defined", bool(packet_schema)
        ),
        "pre_observation_required_fields_count": len(packet_schema.get("required_fields", [])),
        "source_registry_defined": milestone_summary.get(
            "source_registry_defined", bool(source_registry)
        ),
        "source_type_count": len(source_registry.get("source_types", [])),
        "permission_gate_defined": milestone_summary.get(
            "permission_gate_defined", bool(permission_gate)
        ),
        "manual_import_sandbox_defined": milestone_summary.get(
            "manual_import_sandbox_defined", bool(manual_import_contract)
        ),
        "observation_to_artifact_linker_defined": milestone_summary.get(
            "observation_to_artifact_linker_defined", bool(linker_contract)
        ),
        "claim_boundary_policy_defined": milestone_summary.get(
            "claim_boundary_policy_defined", bool(claim_policy)
        ),
        "no_action_receipts_generated": milestone_summary.get(
            "no_action_receipts_generated", bool(no_network_receipt)
        ),
        "strategic_residual_loop_generated": milestone_summary.get(
            "strategic_residual_loop_generated", bool(residual_delta)
        ),
        "static_fixture_generation_authorized": milestone_summary.get(
            "static_fixture_generation_authorized",
            l6_2_flag("l6_2_static_fixture_generation_enabled"),
        ),
        "manual_evidence_import_contract_authorized": milestone_summary.get(
            "manual_evidence_import_contract_authorized",
            l6_2_flag("l6_2_manual_evidence_import_contract_enabled"),
        ),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized",
            l6_2_flag("l6_2_real_external_observation_enabled"),
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_2_boundary_only": l6_2_flag("l6_2_boundary_only"),
        "l6_2_sandbox_only": l6_2_flag("l6_2_sandbox_only"),
        "l6_2_real_external_observation_enabled": l6_2_flag(
            "l6_2_real_external_observation_enabled"
        ),
        "l6_2_network_enabled": l6_2_flag("l6_2_network_enabled"),
        "l6_2_api_enabled": l6_2_flag("l6_2_api_enabled"),
        "l6_2_scraping_enabled": l6_2_flag("l6_2_scraping_enabled"),
        "l6_2_browser_fetch_enabled": l6_2_flag("l6_2_browser_fetch_enabled"),
        "ready_for_l6_3_controlled_external_observation_sandbox": readiness_summary.get(
            "ready_for_l6_3_controlled_external_observation_sandbox"
        ),
        "ready_for_real_network_observation": readiness_summary.get(
            "ready_for_real_network_observation"
        ),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get(
            "next_recommended_milestone"
        ),
        "generated_milestone_summary": "l6_governed_external_observation_boundary/l6_2_summary.json",
        "generated_packet_schema": "pre_observation_packet_schema/pre_observation_packet_schema.json",
        "generated_source_registry": "external_source_registry_and_policy/source_type_registry.json",
        "generated_permission_gate": (
            "external_observation_permission_gate/observation_permission_gate_contract.json"
        ),
        "generated_manual_import_contract": (
            "manual_external_evidence_import_sandbox/manual_import_contract.json"
        ),
        "generated_no_action_receipt": (
            "external_observation_no_action_receipts/no_network_receipt.json"
        ),
        "generated_readiness": (
            "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json"
        ),
        "warning": (
            "L6.2 is boundary-only. Real external observation, URL fetch, "
            "scraping, publication, outreach, payment, revenue execution, MCP, "
            "live behavior, canonical mutation, writeback, and direct Y* "
            "mutation remain blocked."
        ),
    }


def build_l6_controlled_observation_sandbox_summary(
    milestone_summary: dict[str, Any] | None,
    selected_cases: dict[str, Any] | None,
    packet_index: dict[str, Any] | None,
    permission_decisions: dict[str, Any] | None,
    fixture_index: dict[str, Any] | None,
    validation_results: dict[str, Any] | None,
    claim_matrix: dict[str, Any] | None,
    candidate_index: dict[str, Any] | None,
    review_packet_index: dict[str, Any] | None,
    no_network_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": (
                "ystar.console_read_model.generated."
                "l6_controlled_observation_sandbox_summary"
            ),
            "schema_version": "v0",
            "l6_3_controlled_observation_sandbox_defined": False,
            "ready_for_l6_4_real_read_only_external_observation_preflight": False,
            "ready_for_real_network_observation": False,
            "warning": "L6.3 controlled external observation sandbox has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_cases = selected_cases or {}
    packet_index = packet_index or {}
    permission_decisions = permission_decisions or {}
    fixture_index = fixture_index or {}
    validation_results = validation_results or {}
    claim_matrix = claim_matrix or {}
    candidate_index = candidate_index or {}
    review_packet_index = review_packet_index or {}
    no_network_receipt = no_network_receipt or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_3_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_3_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_controlled_observation_sandbox_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.3"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Controlled External Observation Sandbox v0"
        ),
        "l6_3_controlled_observation_sandbox_defined": milestone_summary.get(
            "l6_3_controlled_observation_sandbox_defined",
            readiness_summary.get("l6_3_controlled_external_observation_sandbox_complete"),
        ),
        "sandbox_only": milestone_summary.get("sandbox_only", True),
        "fixture_only": milestone_summary.get("fixture_only", True),
        "static_fixture_observation_authorized": milestone_summary.get(
            "static_fixture_observation_authorized",
            l6_3_flag("l6_3_static_fixture_observation_enabled"),
        ),
        "manual_import_fixture_authorized": milestone_summary.get(
            "manual_import_fixture_authorized",
            l6_3_flag("l6_3_manual_import_fixture_enabled"),
        ),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized",
            l6_3_flag("l6_3_real_external_observation_enabled"),
        ),
        "selected_observation_case_count": milestone_summary.get(
            "selected_observation_case_count",
            selected_cases.get("selected_case_count"),
        ),
        "pre_observation_packet_count": milestone_summary.get(
            "pre_observation_packet_count",
            packet_index.get("packet_count"),
        ),
        "static_manual_fixture_count": milestone_summary.get(
            "static_manual_fixture_count",
            fixture_index.get("fixture_count"),
        ),
        "permission_replay_generated": milestone_summary.get(
            "permission_replay_generated", bool(permission_decisions)
        ),
        "evidence_validation_generated": milestone_summary.get(
            "evidence_validation_generated", bool(validation_results)
        ),
        "claim_freshness_assessment_generated": milestone_summary.get(
            "claim_freshness_assessment_generated", bool(claim_matrix)
        ),
        "refinement_candidates_generated": milestone_summary.get(
            "refinement_candidates_generated", bool(candidate_index)
        ),
        "refinement_candidate_count": candidate_index.get("candidate_count"),
        "review_packets_generated": milestone_summary.get(
            "review_packets_generated", bool(review_packet_index)
        ),
        "review_packet_count": review_packet_index.get("review_packet_count"),
        "no_action_receipts_generated": milestone_summary.get(
            "no_action_receipts_generated", bool(no_network_receipt)
        ),
        "strategic_residual_loop_generated": milestone_summary.get(
            "strategic_residual_loop_generated", bool(residual_delta)
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_3_sandbox_only": l6_3_flag("l6_3_sandbox_only"),
        "l6_3_fixture_only": l6_3_flag("l6_3_fixture_only"),
        "l6_3_static_fixture_observation_enabled": l6_3_flag(
            "l6_3_static_fixture_observation_enabled"
        ),
        "l6_3_manual_import_fixture_enabled": l6_3_flag(
            "l6_3_manual_import_fixture_enabled"
        ),
        "l6_3_real_external_observation_enabled": l6_3_flag(
            "l6_3_real_external_observation_enabled"
        ),
        "l6_3_network_enabled": l6_3_flag("l6_3_network_enabled"),
        "l6_3_api_enabled": l6_3_flag("l6_3_api_enabled"),
        "l6_3_scraping_enabled": l6_3_flag("l6_3_scraping_enabled"),
        "l6_3_browser_fetch_enabled": l6_3_flag("l6_3_browser_fetch_enabled"),
        "l6_3_artifact_refinement_application_enabled": l6_3_flag(
            "l6_3_artifact_refinement_application_enabled"
        ),
        "ready_for_l6_4_real_read_only_external_observation_preflight": readiness_summary.get(
            "ready_for_l6_4_real_read_only_external_observation_preflight"
        ),
        "ready_for_real_network_observation": readiness_summary.get(
            "ready_for_real_network_observation"
        ),
        "ready_for_scraping": readiness_summary.get("ready_for_scraping"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get(
            "next_recommended_milestone"
        ),
        "generated_milestone_summary": "l6_controlled_external_observation_sandbox/l6_3_summary.json",
        "generated_selected_cases": "l6_observation_case_selector/selected_observation_cases.json",
        "generated_packet_index": "controlled_pre_observation_packets/pre_observation_packet_index.json",
        "generated_permission_replay": "sandbox_observation_permission_replay/packet_permission_decisions.json",
        "generated_fixture_index": "static_manual_observation_fixtures/observation_fixture_index.json",
        "generated_refinement_candidates": (
            "observation_to_artifact_refinement_candidates/refinement_candidate_index.json"
        ),
        "generated_readiness": (
            "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json"
        ),
        "warning": (
            "L6.3 is sandbox fixture/manual-import only. Real external observation, "
            "URL fetch, scraping, API calls, browser fetch, publication, outreach, "
            "payment, revenue execution, MCP, live behavior, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }


def build_l6_real_observation_preflight_summary(
    milestone_summary: dict[str, Any] | None,
    selected_candidates: dict[str, Any] | None,
    requirement_registry: dict[str, Any] | None,
    allowlist_policy: dict[str, Any] | None,
    denylist_policy: dict[str, Any] | None,
    approval_packets: dict[str, Any] | None,
    operator_handoff: dict[str, Any] | None,
    network_isolation: dict[str, Any] | None,
    evidence_capture: dict[str, Any] | None,
    abort_registry: dict[str, Any] | None,
    no_real_observation_receipt: dict[str, Any] | None,
    preflight_decisions: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": (
                "ystar.console_read_model.generated."
                "l6_real_observation_preflight_summary"
            ),
            "schema_version": "v0",
            "l6_4_real_read_only_observation_preflight_defined": False,
            "ready_for_l6_5_controlled_real_read_only_observation_pilot_design": False,
            "ready_for_actual_network_observation_now": False,
            "warning": "L6.4 real read-only external observation preflight has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_candidates = selected_candidates or {}
    requirement_registry = requirement_registry or {}
    allowlist_policy = allowlist_policy or {}
    denylist_policy = denylist_policy or {}
    approval_packets = approval_packets or {}
    operator_handoff = operator_handoff or {}
    network_isolation = network_isolation or {}
    evidence_capture = evidence_capture or {}
    abort_registry = abort_registry or {}
    no_real_observation_receipt = no_real_observation_receipt or {}
    preflight_decisions = preflight_decisions or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_4_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_4_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_real_observation_preflight_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.4"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Real Read-Only External Observation Preflight v0"
        ),
        "l6_4_real_read_only_observation_preflight_defined": milestone_summary.get(
            "l6_4_real_read_only_observation_preflight_defined",
            readiness_summary.get("l6_4_real_read_only_observation_preflight_complete"),
        ),
        "preflight_only": milestone_summary.get("preflight_only", True),
        "sandbox_only": milestone_summary.get("sandbox_only", True),
        "future_real_read_only_observation_candidate_allowed": milestone_summary.get(
            "future_real_read_only_observation_candidate_allowed",
            l6_4_flag("l6_4_future_real_read_only_observation_candidate_allowed"),
        ),
        "candidate_count": milestone_summary.get(
            "candidate_count", selected_candidates.get("candidate_count")
        ),
        "approval_packet_count": milestone_summary.get(
            "approval_packet_count", approval_packets.get("example_count")
        ),
        "preflight_requirement_count": len(requirement_registry.get("requirements", [])),
        "source_allowlist_defined": milestone_summary.get(
            "source_allowlist_defined", bool(allowlist_policy)
        ),
        "source_denylist_defined": milestone_summary.get(
            "source_denylist_defined", bool(denylist_policy)
        ),
        "operator_handoff_plan_generated": milestone_summary.get(
            "operator_handoff_plan_generated", bool(operator_handoff)
        ),
        "network_isolation_preflight_defined": milestone_summary.get(
            "network_isolation_preflight_defined", bool(network_isolation)
        ),
        "evidence_capture_preflight_defined": milestone_summary.get(
            "evidence_capture_preflight_defined", bool(evidence_capture)
        ),
        "abort_rollback_quarantine_policy_defined": milestone_summary.get(
            "abort_rollback_quarantine_policy_defined", bool(abort_registry)
        ),
        "no_action_guarantees_generated": milestone_summary.get(
            "no_action_guarantees_generated", bool(no_real_observation_receipt)
        ),
        "preflight_decision_gate_generated": milestone_summary.get(
            "preflight_decision_gate_generated", bool(preflight_decisions)
        ),
        "strategic_residual_loop_generated": milestone_summary.get(
            "strategic_residual_loop_generated", bool(residual_delta)
        ),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized", False
        ),
        "real_observation_execution_authorized": milestone_summary.get(
            "real_observation_execution_authorized", False
        ),
        "network_authorized": milestone_summary.get("network_authorized", False),
        "api_authorized": milestone_summary.get("api_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_fetch_authorized": milestone_summary.get("browser_fetch_authorized", False),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "revenue_execution_authorized": milestone_summary.get(
            "revenue_execution_authorized", False
        ),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get(
            "canonical_update_authorized", False
        ),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get(
            "memory_ingestion_authorized", False
        ),
        "direct_y_star_mutation_authorized": milestone_summary.get(
            "direct_y_star_mutation_authorized", False
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "cieu_db_write_enabled": safety_flag("cieu_db_write_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_4_preflight_only": l6_4_flag("l6_4_preflight_only"),
        "l6_4_sandbox_only": l6_4_flag("l6_4_sandbox_only"),
        "l6_4_future_real_read_only_observation_candidate_allowed": l6_4_flag(
            "l6_4_future_real_read_only_observation_candidate_allowed"
        ),
        "l6_4_approval_packet_generation_enabled": l6_4_flag(
            "l6_4_approval_packet_generation_enabled"
        ),
        "l6_4_operator_handoff_plan_enabled": l6_4_flag(
            "l6_4_operator_handoff_plan_enabled"
        ),
        "l6_4_evidence_capture_plan_enabled": l6_4_flag(
            "l6_4_evidence_capture_plan_enabled"
        ),
        "l6_4_real_observation_execution_enabled": l6_4_flag(
            "l6_4_real_observation_execution_enabled"
        ),
        "l6_4_network_enabled": l6_4_flag("l6_4_network_enabled"),
        "l6_4_api_enabled": l6_4_flag("l6_4_api_enabled"),
        "l6_4_scraping_enabled": l6_4_flag("l6_4_scraping_enabled"),
        "l6_4_browser_fetch_enabled": l6_4_flag("l6_4_browser_fetch_enabled"),
        "ready_for_l6_5_controlled_real_read_only_observation_pilot_design": readiness_summary.get(
            "ready_for_l6_5_controlled_real_read_only_observation_pilot_design"
        ),
        "ready_for_actual_network_observation_now": readiness_summary.get(
            "ready_for_actual_network_observation_now"
        ),
        "ready_for_scraping": readiness_summary.get("ready_for_scraping"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get(
            "next_recommended_milestone"
        ),
        "generated_milestone_summary": "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
        "generated_selected_candidates": "real_observation_candidate_selector/selected_real_observation_candidates.json",
        "generated_preflight_contract": "real_read_only_observation_preflight_contract/preflight_requirement_registry.json",
        "generated_source_allowlist": "source_allowlist_and_risk_policy/source_allowlist_policy.json",
        "generated_approval_packets": "real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json",
        "generated_operator_handoff": "observation_operator_handoff/operator_handoff_contract.json",
        "generated_network_isolation": "observation_network_isolation_preflight/network_isolation_requirement.json",
        "generated_evidence_capture": "observation_evidence_capture_preflight/evidence_capture_contract.json",
        "generated_decision_gate": "real_observation_preflight_decision_gate/candidate_preflight_decisions.json",
        "generated_readiness": "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json",
        "warning": (
            "L6.4 is preflight-only. Real external observation, URL fetch, scraping, "
            "API calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }


def build_l6_pilot_design_summary(
    milestone_summary: dict[str, Any] | None,
    selected_candidates: dict[str, Any] | None,
    boundary_contract: dict[str, Any] | None,
    source_allowlist: dict[str, Any] | None,
    source_denylist: dict[str, Any] | None,
    approval_packet_index: dict[str, Any] | None,
    operator_steps: dict[str, Any] | None,
    evidence_template: dict[str, Any] | None,
    post_review_contract: dict[str, Any] | None,
    abort_registry: dict[str, Any] | None,
    success_criteria: dict[str, Any] | None,
    no_real_observation_receipt: dict[str, Any] | None,
    pilot_decisions: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_pilot_design_summary",
            "schema_version": "v0",
            "l6_5_controlled_real_read_only_observation_pilot_design_defined": False,
            "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet": False,
            "ready_for_actual_network_observation_now": False,
            "warning": "L6.5 controlled real read-only observation pilot design has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_candidates = selected_candidates or {}
    boundary_contract = boundary_contract or {}
    source_allowlist = source_allowlist or {}
    source_denylist = source_denylist or {}
    approval_packet_index = approval_packet_index or {}
    operator_steps = operator_steps or {}
    evidence_template = evidence_template or {}
    post_review_contract = post_review_contract or {}
    abort_registry = abort_registry or {}
    success_criteria = success_criteria or {}
    no_real_observation_receipt = no_real_observation_receipt or {}
    pilot_decisions = pilot_decisions or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_5_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_5_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_pilot_design_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.5"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Controlled Real Read-Only Observation Pilot Design v0"
        ),
        "l6_5_controlled_real_read_only_observation_pilot_design_defined": milestone_summary.get(
            "l6_5_controlled_real_read_only_observation_pilot_design_defined",
            readiness_summary.get("l6_5_controlled_real_read_only_observation_pilot_design_complete"),
        ),
        "pilot_design_only": milestone_summary.get("pilot_design_only", True),
        "preflight_only": milestone_summary.get("preflight_only", True),
        "future_real_read_only_observation_pilot_candidate_allowed": milestone_summary.get(
            "future_real_read_only_observation_pilot_candidate_allowed",
            l6_5_flag("l6_5_future_real_read_only_observation_pilot_candidate_allowed"),
        ),
        "candidate_count": milestone_summary.get(
            "candidate_count", selected_candidates.get("candidate_count")
        ),
        "approval_packet_count": milestone_summary.get(
            "approval_packet_count", approval_packet_index.get("packet_count")
        ),
        "pilot_scope_defined": milestone_summary.get(
            "pilot_scope_defined", bool(boundary_contract)
        ),
        "pilot_source_constraints_defined": milestone_summary.get(
            "pilot_source_constraints_defined", bool(source_allowlist and source_denylist)
        ),
        "pilot_approval_packet_candidates_generated": milestone_summary.get(
            "pilot_approval_packet_candidates_generated", bool(approval_packet_index)
        ),
        "pilot_operator_runbook_generated": milestone_summary.get(
            "pilot_operator_runbook_generated", bool(operator_steps)
        ),
        "pilot_evidence_packet_templates_generated": milestone_summary.get(
            "pilot_evidence_packet_templates_generated", bool(evidence_template)
        ),
        "post_observation_review_workflow_defined": milestone_summary.get(
            "post_observation_review_workflow_defined", bool(post_review_contract)
        ),
        "abort_quarantine_policy_defined": milestone_summary.get(
            "abort_quarantine_policy_defined", bool(abort_registry)
        ),
        "success_failure_criteria_defined": milestone_summary.get(
            "success_failure_criteria_defined", bool(success_criteria)
        ),
        "no_action_guarantees_generated": milestone_summary.get(
            "no_action_guarantees_generated", bool(no_real_observation_receipt)
        ),
        "pilot_design_decision_gate_generated": milestone_summary.get(
            "pilot_design_decision_gate_generated", bool(pilot_decisions)
        ),
        "strategic_residual_loop_generated": milestone_summary.get(
            "strategic_residual_loop_generated", bool(residual_delta)
        ),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized", False
        ),
        "real_pilot_execution_authorized": milestone_summary.get(
            "real_pilot_execution_authorized", False
        ),
        "network_authorized": milestone_summary.get("network_authorized", False),
        "api_authorized": milestone_summary.get("api_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_fetch_authorized": milestone_summary.get("browser_fetch_authorized", False),
        "search_authorized": milestone_summary.get("search_authorized", False),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "revenue_execution_authorized": milestone_summary.get(
            "revenue_execution_authorized", False
        ),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get(
            "canonical_update_authorized", False
        ),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get(
            "memory_ingestion_authorized", False
        ),
        "direct_y_star_mutation_authorized": milestone_summary.get(
            "direct_y_star_mutation_authorized", False
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "search_enabled": safety_flag("search_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "cieu_db_write_enabled": safety_flag("cieu_db_write_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_5_pilot_design_only": l6_5_flag("l6_5_pilot_design_only"),
        "l6_5_preflight_only": l6_5_flag("l6_5_preflight_only"),
        "l6_5_pilot_approval_packet_generation_enabled": l6_5_flag(
            "l6_5_pilot_approval_packet_generation_enabled"
        ),
        "l6_5_pilot_operator_runbook_enabled": l6_5_flag(
            "l6_5_pilot_operator_runbook_enabled"
        ),
        "l6_5_pilot_evidence_template_enabled": l6_5_flag(
            "l6_5_pilot_evidence_template_enabled"
        ),
        "l6_5_real_pilot_execution_enabled": l6_5_flag(
            "l6_5_real_pilot_execution_enabled"
        ),
        "l6_5_network_enabled": l6_5_flag("l6_5_network_enabled"),
        "l6_5_search_enabled": l6_5_flag("l6_5_search_enabled"),
        "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet": readiness_summary.get(
            "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet"
        ),
        "ready_for_actual_network_observation_now": readiness_summary.get(
            "ready_for_actual_network_observation_now"
        ),
        "ready_for_scraping": readiness_summary.get("ready_for_scraping"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.json",
        "generated_selected_candidates": "pilot_candidate_selector/selected_pilot_candidates.json",
        "generated_pilot_scope": "pilot_scope_and_non_goals/pilot_boundary_contract.json",
        "generated_source_allowlist": "pilot_source_constraint_policy/pilot_source_allowlist.json",
        "generated_approval_packets": "pilot_approval_packet_candidates/pilot_approval_packet_index.json",
        "generated_operator_runbook": "pilot_operator_runbook/operator_step_sequence.json",
        "generated_evidence_template": "pilot_evidence_packet_templates/pilot_evidence_packet_template.json",
        "generated_decision_gate": "pilot_design_decision_gate/pilot_candidate_decisions.json",
        "generated_readiness": "l6_pilot_design_readiness/l6_5_readiness_assessment.json",
        "warning": (
            "L6.5 is pilot-design-only. Real observation, URL fetch, search, scraping, "
            "API calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }


def build_l6_pilot_approval_summary(
    milestone_summary: dict[str, Any] | None,
    selected_candidates: dict[str, Any] | None,
    authority_model: dict[str, Any] | None,
    approval_packet_index: dict[str, Any] | None,
    evidence_dossier_index: dict[str, Any] | None,
    risk_matrix: dict[str, Any] | None,
    operator_authorization: dict[str, Any] | None,
    runtime_attestation: dict[str, Any] | None,
    evidence_capture_authorization: dict[str, Any] | None,
    no_action_constraints: dict[str, Any] | None,
    decision_matrix: dict[str, Any] | None,
    non_persistence_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_pilot_approval_summary",
            "schema_version": "v0",
            "l6_6_controlled_observation_pilot_approval_packet_defined": False,
            "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox": False,
            "ready_for_actual_network_observation_now": False,
            "warning": "L6.6 controlled observation pilot approval packet has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_candidates = selected_candidates or {}
    authority_model = authority_model or {}
    approval_packet_index = approval_packet_index or {}
    evidence_dossier_index = evidence_dossier_index or {}
    risk_matrix = risk_matrix or {}
    operator_authorization = operator_authorization or {}
    runtime_attestation = runtime_attestation or {}
    evidence_capture_authorization = evidence_capture_authorization or {}
    no_action_constraints = no_action_constraints or {}
    decision_matrix = decision_matrix or {}
    non_persistence_receipt = non_persistence_receipt or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_6_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_6_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_pilot_approval_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.6"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Controlled Real Read-Only Observation Pilot Approval Packet v0",
        ),
        "l6_6_controlled_observation_pilot_approval_packet_defined": milestone_summary.get(
            "l6_6_controlled_observation_pilot_approval_packet_defined",
            readiness_summary.get("l6_6_controlled_pilot_approval_packet_complete"),
        ),
        "approval_packet_only": milestone_summary.get("approval_packet_only", True),
        "approval_sandbox_only": milestone_summary.get("approval_sandbox_only", True),
        "future_real_read_only_observation_pilot_candidate_allowed": milestone_summary.get(
            "future_real_read_only_observation_pilot_candidate_allowed",
            l6_6_flag("l6_6_future_real_read_only_observation_pilot_candidate_allowed"),
        ),
        "approval_candidate_count": milestone_summary.get(
            "candidate_count", selected_candidates.get("candidate_count")
        ),
        "approval_packet_count": milestone_summary.get(
            "approval_packet_count", approval_packet_index.get("packet_count")
        ),
        "evidence_dossier_count": milestone_summary.get(
            "evidence_dossier_count", evidence_dossier_index.get("dossier_count")
        ),
        "risk_review_count": milestone_summary.get(
            "risk_review_count", risk_matrix.get("decision_count", risk_matrix.get("row_count"))
        ),
        "approval_authority_model_generated": milestone_summary.get(
            "approval_authority_model_generated", bool(authority_model)
        ),
        "approval_packet_instances_generated": milestone_summary.get(
            "approval_packet_instances_generated", bool(approval_packet_index)
        ),
        "evidence_dossiers_generated": milestone_summary.get(
            "evidence_dossiers_generated", bool(evidence_dossier_index)
        ),
        "risk_reviews_generated": milestone_summary.get(
            "risk_reviews_generated", bool(risk_matrix)
        ),
        "operator_authorization_prerequisites_generated": milestone_summary.get(
            "operator_authorization_prerequisites_generated", bool(operator_authorization)
        ),
        "runtime_isolation_attestation_templates_generated": milestone_summary.get(
            "runtime_isolation_attestation_templates_generated", bool(runtime_attestation)
        ),
        "evidence_capture_authorization_templates_generated": milestone_summary.get(
            "evidence_capture_authorization_templates_generated",
            bool(evidence_capture_authorization),
        ),
        "no_action_constraints_generated": milestone_summary.get(
            "no_action_constraints_generated", bool(no_action_constraints)
        ),
        "approval_decision_sandbox_generated": milestone_summary.get(
            "approval_decision_sandbox_generated", bool(decision_matrix)
        ),
        "non_persistence_receipts_generated": milestone_summary.get(
            "non_persistence_receipts_generated", bool(non_persistence_receipt)
        ),
        "strategic_residual_loop_generated": milestone_summary.get(
            "strategic_residual_loop_generated", bool(residual_delta)
        ),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized", False
        ),
        "real_pilot_execution_authorized": milestone_summary.get(
            "real_pilot_execution_authorized", False
        ),
        "real_approval_granted": milestone_summary.get("real_approval_granted", False),
        "durable_real_approval_record_created": milestone_summary.get(
            "durable_real_approval_record_created", False
        ),
        "network_authorized": milestone_summary.get("network_authorized", False),
        "api_authorized": milestone_summary.get("api_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_fetch_authorized": milestone_summary.get("browser_fetch_authorized", False),
        "search_authorized": milestone_summary.get("search_authorized", False),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "revenue_execution_authorized": milestone_summary.get(
            "revenue_execution_authorized", False
        ),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get(
            "canonical_update_authorized", False
        ),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get("memory_ingestion_authorized", False),
        "direct_y_star_mutation_authorized": milestone_summary.get(
            "direct_y_star_mutation_authorized", False
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "search_enabled": safety_flag("search_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "cieu_db_write_enabled": safety_flag("cieu_db_write_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag("real_y_star_direct_mutation_enabled"),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_6_approval_packet_only": l6_6_flag("l6_6_approval_packet_only"),
        "l6_6_approval_sandbox_only": l6_6_flag("l6_6_approval_sandbox_only"),
        "l6_6_approval_packet_generation_enabled": l6_6_flag(
            "l6_6_approval_packet_generation_enabled"
        ),
        "l6_6_approval_decision_sandbox_enabled": l6_6_flag(
            "l6_6_approval_decision_sandbox_enabled"
        ),
        "l6_6_real_approval_granted": l6_6_flag("l6_6_real_approval_granted"),
        "l6_6_durable_real_approval_record_created": l6_6_flag(
            "l6_6_durable_real_approval_record_created"
        ),
        "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox": readiness_summary.get(
            "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox"
        ),
        "ready_for_actual_network_observation_now": readiness_summary.get(
            "ready_for_actual_network_observation_now"
        ),
        "ready_for_real_approval_now": readiness_summary.get("ready_for_real_approval_now"),
        "ready_for_durable_approval_persistence_now": readiness_summary.get(
            "ready_for_durable_approval_persistence_now"
        ),
        "ready_for_scraping": readiness_summary.get("ready_for_scraping"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_controlled_observation_pilot_approval_packet/l6_6_summary.json",
        "generated_selected_candidates": "pilot_approval_candidate_selector/selected_approval_candidates.json",
        "generated_authority_model": "pilot_approval_authority_model/approval_authority_model.json",
        "generated_approval_packets": "pilot_approval_packet_assembler/approval_packet_index.json",
        "generated_evidence_dossiers": "pilot_approval_evidence_dossier/evidence_dossier_index.json",
        "generated_risk_reviews": "pilot_approval_risk_review/approval_packet_risk_matrix.json",
        "generated_decision_sandbox": "pilot_approval_decision_sandbox/approval_packet_decision_matrix.json",
        "generated_non_persistence_receipt": "pilot_approval_non_persistence_receipts/no_durable_real_approval_record_receipt.json",
        "generated_readiness": "l6_pilot_approval_readiness/l6_6_readiness_assessment.json",
        "warning": (
            "L6.6 is approval-packet-only. Real approval, durable approval "
            "persistence, real observation, URL fetch, search, scraping, API "
            "calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }


def build_l6_integrated_pilot_readiness_summary(
    milestone_summary: dict[str, Any] | None,
    sandbox_record_index: dict[str, Any] | None,
    pilot_run_package_index: dict[str, Any] | None,
    operator_readiness: dict[str, Any] | None,
    runtime_readiness: dict[str, Any] | None,
    evidence_capture: dict[str, Any] | None,
    post_review: dict[str, Any] | None,
    manual_import: dict[str, Any] | None,
    decision_matrix: dict[str, Any] | None,
    no_action_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_integrated_pilot_readiness_summary",
            "schema_version": "v0",
            "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined": False,
            "ready_for_l6_8_user_mediated_manual_evidence_import_pilot": False,
            "ready_for_actual_network_observation_now": False,
            "warning": "L6.7 integrated approval record and pilot readiness sandbox has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    sandbox_record_index = sandbox_record_index or {}
    pilot_run_package_index = pilot_run_package_index or {}
    operator_readiness = operator_readiness or {}
    runtime_readiness = runtime_readiness or {}
    evidence_capture = evidence_capture or {}
    post_review = post_review or {}
    manual_import = manual_import or {}
    decision_matrix = decision_matrix or {}
    no_action_receipt = no_action_receipt or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_7_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_7_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_integrated_pilot_readiness_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.7"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Integrated Approval Record & Pilot Run Readiness Sandbox v0"
        ),
        "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined": milestone_summary.get(
            "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined",
            readiness_summary.get("l6_7_integrated_approval_record_and_pilot_readiness_sandbox_complete"),
        ),
        "integrated_sandbox_only": milestone_summary.get("integrated_sandbox_only", True),
        "approval_record_sandbox_only": milestone_summary.get(
            "approval_record_sandbox_only", True
        ),
        "pilot_run_readiness_only": milestone_summary.get("pilot_run_readiness_only", True),
        "sandbox_approval_record_created": milestone_summary.get(
            "sandbox_approval_record_created", True
        ),
        "sandbox_approval_record_count": milestone_summary.get(
            "sandbox_approval_record_count", sandbox_record_index.get("record_count")
        ),
        "pilot_run_package_count": milestone_summary.get(
            "pilot_run_package_count", pilot_run_package_index.get("package_count")
        ),
        "operator_readiness_package_created": milestone_summary.get(
            "operator_readiness_package_created", bool(operator_readiness)
        ),
        "runtime_isolation_readiness_created": milestone_summary.get(
            "runtime_isolation_readiness_created", bool(runtime_readiness)
        ),
        "evidence_capture_readiness_created": milestone_summary.get(
            "evidence_capture_readiness_created", bool(evidence_capture)
        ),
        "post_observation_review_readiness_created": milestone_summary.get(
            "post_observation_review_readiness_created", bool(post_review)
        ),
        "manual_evidence_import_readiness_created": milestone_summary.get(
            "manual_evidence_import_readiness_created", bool(manual_import)
        ),
        "integrated_decision_gate_created": milestone_summary.get(
            "integrated_decision_gate_created", bool(decision_matrix)
        ),
        "no_action_receipts_created": milestone_summary.get(
            "no_action_receipts_created", bool(no_action_receipt)
        ),
        "strategic_residual_loop_created": milestone_summary.get(
            "strategic_residual_loop_created", bool(residual_delta)
        ),
        "manual_evidence_import_future_candidate_allowed": milestone_summary.get(
            "manual_evidence_import_future_candidate_allowed",
            l6_7_flag("l6_7_manual_evidence_import_future_candidate_allowed"),
        ),
        "durable_real_approval_record_created": milestone_summary.get(
            "durable_real_approval_record_created", False
        ),
        "real_approval_granted": milestone_summary.get("real_approval_granted", False),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized", False
        ),
        "real_pilot_execution_authorized": milestone_summary.get(
            "real_pilot_execution_authorized", False
        ),
        "network_authorized": milestone_summary.get("network_authorized", False),
        "api_authorized": milestone_summary.get("api_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_fetch_authorized": milestone_summary.get("browser_fetch_authorized", False),
        "search_authorized": milestone_summary.get("search_authorized", False),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "revenue_execution_authorized": milestone_summary.get(
            "revenue_execution_authorized", False
        ),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get(
            "canonical_update_authorized", False
        ),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get("memory_ingestion_authorized", False),
        "direct_y_star_mutation_authorized": milestone_summary.get(
            "direct_y_star_mutation_authorized", False
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "search_enabled": safety_flag("search_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "cieu_db_write_enabled": safety_flag("cieu_db_write_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag("real_y_star_direct_mutation_enabled"),
        "durable_approval_persistence_enabled": safety_flag(
            "durable_approval_persistence_enabled"
        ),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag(
            "raw_runtime_artifact_reading_enabled"
        ),
        "l6_7_integrated_sandbox_only": l6_7_flag("l6_7_integrated_sandbox_only"),
        "l6_7_approval_record_sandbox_only": l6_7_flag(
            "l6_7_approval_record_sandbox_only"
        ),
        "l6_7_pilot_run_readiness_only": l6_7_flag("l6_7_pilot_run_readiness_only"),
        "l6_7_sandbox_approval_record_created": l6_7_flag(
            "l6_7_sandbox_approval_record_created"
        ),
        "l6_7_real_approval_granted": l6_7_flag("l6_7_real_approval_granted"),
        "l6_7_durable_real_approval_record_created": l6_7_flag(
            "l6_7_durable_real_approval_record_created"
        ),
        "ready_for_l6_8_user_mediated_manual_evidence_import_pilot": readiness_summary.get(
            "ready_for_l6_8_user_mediated_manual_evidence_import_pilot"
        ),
        "ready_for_actual_network_observation_now": readiness_summary.get(
            "ready_for_actual_network_observation_now"
        ),
        "ready_for_real_approval_now": readiness_summary.get("ready_for_real_approval_now"),
        "ready_for_durable_real_approval_persistence_now": readiness_summary.get(
            "ready_for_durable_real_approval_persistence_now"
        ),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get(
            "ready_for_brain_memory_writeback"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_summary.json",
        "generated_sandbox_records": "sandbox_approval_record_lifecycle/sandbox_approval_record_index.json",
        "generated_pilot_run_packages": "pilot_run_package_assembler/pilot_run_package_index.json",
        "generated_operator_readiness": "pilot_operator_readiness_package/operator_readiness_checklist.json",
        "generated_runtime_readiness": "pilot_runtime_isolation_readiness/runtime_isolation_readiness_packet.json",
        "generated_evidence_capture": "pilot_evidence_capture_readiness/evidence_capture_packet_template_final.json",
        "generated_manual_import_readiness": "manual_evidence_import_readiness/manual_evidence_import_readiness_contract.json",
        "generated_decision_gate": "pilot_integrated_decision_gate/integrated_candidate_decision_matrix.json",
        "generated_no_action_receipt": "pilot_integrated_no_action_receipts/no_real_approval_granted_receipt.json",
        "generated_readiness": "l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json",
        "warning": (
            "L6.7 is integrated-sandbox-only. Sandbox approval records and pilot "
            "run packages are readiness-only. Real approval, durable approval "
            "persistence, real observation, URL fetch, search, scraping, API "
            "calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }


def build_l6_agentic_evidence_summary(
    milestone_summary: dict[str, Any] | None,
    evidence_needs: dict[str, Any] | None,
    source_hypotheses: dict[str, Any] | None,
    source_value_matrix: dict[str, Any] | None,
    trust_judgment_matrix: dict[str, Any] | None,
    voi_matrix: dict[str, Any] | None,
    ranked_sources: dict[str, Any] | None,
    conflict_contract: dict[str, Any] | None,
    work_order_index: dict[str, Any] | None,
    rejected_sources: dict[str, Any] | None,
    decision_matrix: dict[str, Any] | None,
    no_action_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_agentic_evidence_summary",
            "schema_version": "v0",
            "l6_8_agentic_evidence_discovery_trust_engine_defined": False,
            "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval": False,
            "ready_for_actual_network_observation_now": False,
            "warning": "L6.8 agentic evidence discovery trust engine has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    evidence_needs = evidence_needs or {}
    source_hypotheses = source_hypotheses or {}
    source_value_matrix = source_value_matrix or {}
    trust_judgment_matrix = trust_judgment_matrix or {}
    voi_matrix = voi_matrix or {}
    ranked_sources = ranked_sources or {}
    conflict_contract = conflict_contract or {}
    work_order_index = work_order_index or {}
    rejected_sources = rejected_sources or {}
    decision_matrix = decision_matrix or {}
    no_action_receipt = no_action_receipt or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_8_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_8_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_agentic_evidence_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.8"),
        "milestone_name": milestone_summary.get(
            "milestone_name", "Agentic External Evidence Discovery & Trust Judgment Engine v0"
        ),
        "l6_8_agentic_evidence_discovery_trust_engine_defined": milestone_summary.get(
            "l6_8_agentic_evidence_discovery_trust_engine_defined",
            readiness_summary.get("l6_8_agentic_evidence_discovery_and_trust_judgment_engine_complete"),
        ),
        "mode": milestone_summary.get("mode", "agentic_evidence_discovery_design_and_sandbox"),
        "agentic_evidence_discovery_design_and_sandbox_only": l6_8_flag(
            "l6_8_agentic_evidence_discovery_design_and_sandbox_only"
        ),
        "evidence_need_count": milestone_summary.get(
            "evidence_need_count", evidence_needs.get("evidence_need_count")
        ),
        "source_hypothesis_count": milestone_summary.get(
            "source_hypothesis_count", source_hypotheses.get("source_hypothesis_count")
        ),
        "ranked_source_hypothesis_count": milestone_summary.get(
            "ranked_source_hypothesis_count", ranked_sources.get("ranked_count")
        ),
        "observation_work_order_count": milestone_summary.get(
            "observation_work_order_count", work_order_index.get("work_order_count")
        ),
        "rejected_source_hypothesis_count": milestone_summary.get(
            "rejected_source_hypothesis_count", rejected_sources.get("rejected_count")
        ),
        "autonomous_evidence_need_inference_authorized": milestone_summary.get(
            "autonomous_evidence_need_inference_authorized", True
        ),
        "autonomous_source_hypothesis_generation_authorized": milestone_summary.get(
            "autonomous_source_hypothesis_generation_authorized", True
        ),
        "autonomous_evidence_value_judgment_authorized": milestone_summary.get(
            "autonomous_evidence_value_judgment_authorized", True
        ),
        "autonomous_trust_assessment_authorized": milestone_summary.get(
            "autonomous_trust_assessment_authorized", True
        ),
        "observation_work_order_generation_authorized": milestone_summary.get(
            "observation_work_order_generation_authorized", True
        ),
        "source_type_value_model_generated": bool(source_value_matrix),
        "structural_trust_judgment_generated": bool(trust_judgment_matrix),
        "value_of_information_model_generated": bool(voi_matrix),
        "conflict_corroboration_model_generated": bool(conflict_contract),
        "pre_observation_rejection_filter_generated": bool(rejected_sources),
        "agentic_evidence_decision_gate_generated": bool(decision_matrix),
        "no_action_receipts_generated": bool(no_action_receipt),
        "strategic_residual_loop_generated": bool(residual_delta),
        "real_external_observation_authorized": milestone_summary.get(
            "real_external_observation_authorized", False
        ),
        "agent_external_fetch_authorized": milestone_summary.get(
            "agent_external_fetch_authorized", False
        ),
        "network_authorized": milestone_summary.get("network_authorized", False),
        "api_authorized": milestone_summary.get("api_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_fetch_authorized": milestone_summary.get("browser_fetch_authorized", False),
        "search_authorized": milestone_summary.get("search_authorized", False),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "revenue_execution_authorized": milestone_summary.get("revenue_execution_authorized", False),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get("canonical_update_authorized", False),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get("memory_ingestion_authorized", False),
        "direct_y_star_mutation_authorized": milestone_summary.get(
            "direct_y_star_mutation_authorized", False
        ),
        "real_approval_granted": milestone_summary.get("real_approval_granted", False),
        "durable_real_approval_record_created": milestone_summary.get(
            "durable_real_approval_record_created", False
        ),
        "future_controlled_read_only_observation_pilot_candidate_allowed": milestone_summary.get(
            "future_controlled_read_only_observation_pilot_candidate_allowed", True
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "search_enabled": safety_flag("search_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "agent_external_fetch_enabled": safety_flag("agent_external_fetch_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "cieu_db_write_enabled": safety_flag("cieu_db_write_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag("real_y_star_direct_mutation_enabled"),
        "durable_approval_persistence_enabled": safety_flag("durable_approval_persistence_enabled"),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "llm_confidence_as_authority_enabled": safety_flag("llm_confidence_as_authority_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag("raw_runtime_artifact_reading_enabled"),
        "l6_8_agentic_evidence_discovery_design_and_sandbox_only": l6_8_flag(
            "l6_8_agentic_evidence_discovery_design_and_sandbox_only"
        ),
        "l6_8_autonomous_evidence_need_inference_enabled": l6_8_flag(
            "l6_8_autonomous_evidence_need_inference_enabled"
        ),
        "l6_8_autonomous_source_hypothesis_generation_enabled": l6_8_flag(
            "l6_8_autonomous_source_hypothesis_generation_enabled"
        ),
        "l6_8_autonomous_evidence_value_judgment_enabled": l6_8_flag(
            "l6_8_autonomous_evidence_value_judgment_enabled"
        ),
        "l6_8_autonomous_trust_assessment_enabled": l6_8_flag(
            "l6_8_autonomous_trust_assessment_enabled"
        ),
        "l6_8_observation_work_order_generation_enabled": l6_8_flag(
            "l6_8_observation_work_order_generation_enabled"
        ),
        "l6_8_real_external_observation_enabled": l6_8_flag(
            "l6_8_real_external_observation_enabled"
        ),
        "l6_8_agent_external_fetch_enabled": l6_8_flag("l6_8_agent_external_fetch_enabled"),
        "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval": readiness_summary.get(
            "ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval"
        ),
        "ready_for_actual_network_observation_now": readiness_summary.get(
            "ready_for_actual_network_observation_now"
        ),
        "ready_for_autonomous_web_search_now": readiness_summary.get(
            "ready_for_autonomous_web_search_now"
        ),
        "ready_for_scraping": readiness_summary.get("ready_for_scraping"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get("ready_for_brain_memory_writeback"),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_agentic_evidence_discovery_trust_engine/l6_8_summary.json",
        "generated_evidence_needs": "evidence_need_inference_engine/inferred_evidence_needs.json",
        "generated_source_hypotheses": "autonomous_source_hypothesis_generator/source_hypothesis_index.json",
        "generated_source_value_model": "source_type_value_model/source_type_value_matrix.json",
        "generated_trust_judgment": "evidence_trust_judgment_model/trust_judgment_matrix.json",
        "generated_value_of_information": "evidence_value_of_information_model/evidence_need_voi_matrix.json",
        "generated_source_ranking": "source_prioritization_and_ranking_engine/ranked_source_hypotheses.json",
        "generated_work_orders": "observation_work_order_generator/observation_work_order_index.json",
        "generated_rejection_filter": "pre_observation_rejection_filter/rejected_source_hypotheses.json",
        "generated_decision_gate": "agentic_evidence_decision_gate/evidence_discovery_decision_matrix.json",
        "generated_no_action_receipt": "agentic_evidence_no_action_receipts/no_agent_fetch_receipt.json",
        "generated_readiness": "l6_agentic_evidence_readiness_report/l6_8_readiness_assessment.json",
        "warning": (
            "L6.8 is agentic evidence discovery design/sandbox only. It can infer "
            "evidence needs, generate and rank source hypotheses, judge source "
            "value and structural trust, and generate future work orders, but "
            "real observation, agent fetch, URL open, network, search, scraping, "
            "API calls, browser fetch, publication, outreach, payment, revenue, "
            "MCP, live behavior, CIEU DB writes, canonical mutation, writeback, "
            "and direct Y* mutation remain blocked."
        ),
    }


def build_l6_agentic_pilot_dry_run_summary(
    milestone_summary: dict[str, Any] | None,
    selected_work_orders: dict[str, Any] | None,
    eligibility_matrix: dict[str, Any] | None,
    approval_packet_index: dict[str, Any] | None,
    sandbox_record_index: dict[str, Any] | None,
    runtime_packet_index: dict[str, Any] | None,
    dry_run_trace_index: dict[str, Any] | None,
    empty_evidence_index: dict[str, Any] | None,
    post_run_review_index: dict[str, Any] | None,
    refinement_candidate_index: dict[str, Any] | None,
    blocked_execution_decisions: dict[str, Any] | None,
    no_action_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_agentic_pilot_dry_run_summary",
            "schema_version": "v0",
            "l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined": False,
            "ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot": False,
            "ready_for_actual_network_observation_now": False,
            "warning": "L6.9 controlled agentic evidence pilot approval dry-run has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_work_orders = selected_work_orders or {}
    eligibility_matrix = eligibility_matrix or {}
    approval_packet_index = approval_packet_index or {}
    sandbox_record_index = sandbox_record_index or {}
    runtime_packet_index = runtime_packet_index or {}
    dry_run_trace_index = dry_run_trace_index or {}
    empty_evidence_index = empty_evidence_index or {}
    post_run_review_index = post_run_review_index or {}
    refinement_candidate_index = refinement_candidate_index or {}
    blocked_execution_decisions = blocked_execution_decisions or {}
    no_action_receipt = no_action_receipt or {}
    residual_delta = residual_delta or {}

    def safety_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("safety_flags", {}).get(field))

    def l6_9_flag(field: str) -> Any:
        return readiness_summary.get(field, readiness_summary.get("l6_9_flags", {}).get(field))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_agentic_pilot_dry_run_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.9"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Controlled Read-Only Agentic Evidence Discovery Pilot Approval & Dry-Run v0",
        ),
        "l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined": milestone_summary.get(
            "l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined",
            readiness_summary.get(
                "l6_9_controlled_read_only_agentic_evidence_pilot_approval_and_dry_run_complete"
            ),
        ),
        "mode": milestone_summary.get("mode", "pilot_approval_and_dry_run_only"),
        "pilot_approval_and_dry_run_only": l6_9_flag("l6_9_pilot_approval_and_dry_run_only"),
        "sandbox_approval_record_only": l6_9_flag("l6_9_sandbox_approval_record_only"),
        "selected_work_order_count": milestone_summary.get(
            "selected_work_order_count", selected_work_orders.get("selected_count")
        ),
        "eligible_work_order_count": eligibility_matrix.get("eligible_count"),
        "approval_packet_count": milestone_summary.get(
            "approval_packet_count", approval_packet_index.get("approval_packet_count")
        ),
        "sandbox_approval_record_count": milestone_summary.get(
            "sandbox_approval_record_count", sandbox_record_index.get("sandbox_record_count")
        ),
        "runtime_readiness_packet_count": milestone_summary.get(
            "runtime_readiness_packet_count", runtime_packet_index.get("runtime_packet_count")
        ),
        "dry_run_trace_count": milestone_summary.get(
            "dry_run_trace_count", dry_run_trace_index.get("dry_run_trace_count")
        ),
        "empty_evidence_packet_count": milestone_summary.get(
            "empty_evidence_packet_count", empty_evidence_index.get("empty_evidence_packet_count")
        ),
        "post_run_review_packet_count": milestone_summary.get(
            "post_run_review_packet_count", post_run_review_index.get("post_run_review_packet_count")
        ),
        "refinement_candidate_count": milestone_summary.get(
            "refinement_candidate_count", refinement_candidate_index.get("candidate_count")
        ),
        "agentic_work_order_selection_authorized": milestone_summary.get(
            "agentic_work_order_selection_authorized", True
        ),
        "pilot_approval_packet_generation_authorized": milestone_summary.get(
            "pilot_approval_packet_generation_authorized", True
        ),
        "sandbox_approval_record_generation_authorized": milestone_summary.get(
            "sandbox_approval_record_generation_authorized", True
        ),
        "dry_run_lifecycle_simulation_authorized": milestone_summary.get(
            "dry_run_lifecycle_simulation_authorized", True
        ),
        "empty_evidence_capture_simulation_authorized": milestone_summary.get(
            "empty_evidence_capture_simulation_authorized", True
        ),
        "approval_eligibility_gate_generated": bool(eligibility_matrix),
        "approval_packets_generated": bool(approval_packet_index),
        "sandbox_approval_records_generated": bool(sandbox_record_index),
        "runtime_readiness_generated": bool(runtime_packet_index),
        "dry_run_traces_generated": bool(dry_run_trace_index),
        "empty_evidence_capture_generated": bool(empty_evidence_index),
        "post_run_review_generated": bool(post_run_review_index),
        "residual_refinement_candidates_generated": bool(refinement_candidate_index),
        "real_execution_blockers_generated": bool(blocked_execution_decisions),
        "no_action_receipts_generated": bool(no_action_receipt),
        "strategic_residual_loop_generated": bool(residual_delta),
        "real_external_observation_authorized": milestone_summary.get("real_external_observation_authorized", False),
        "real_pilot_execution_authorized": milestone_summary.get("real_pilot_execution_authorized", False),
        "real_approval_granted": milestone_summary.get("real_approval_granted", False),
        "durable_real_approval_record_created": milestone_summary.get(
            "durable_real_approval_record_created", False
        ),
        "agent_external_fetch_authorized": milestone_summary.get("agent_external_fetch_authorized", False),
        "network_authorized": milestone_summary.get("network_authorized", False),
        "api_authorized": milestone_summary.get("api_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_fetch_authorized": milestone_summary.get("browser_fetch_authorized", False),
        "search_authorized": milestone_summary.get("search_authorized", False),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "revenue_execution_authorized": milestone_summary.get("revenue_execution_authorized", False),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get("canonical_update_authorized", False),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get("memory_ingestion_authorized", False),
        "direct_y_star_mutation_authorized": milestone_summary.get("direct_y_star_mutation_authorized", False),
        "future_tiny_real_read_only_pilot_candidate_allowed": milestone_summary.get(
            "future_tiny_real_read_only_pilot_candidate_allowed", True
        ),
        "network_enabled": safety_flag("network_enabled"),
        "api_enabled": safety_flag("api_enabled"),
        "scraping_enabled": safety_flag("scraping_enabled"),
        "browser_fetch_enabled": safety_flag("browser_fetch_enabled"),
        "search_enabled": safety_flag("search_enabled"),
        "external_action_enabled": safety_flag("external_action_enabled"),
        "agent_external_fetch_enabled": safety_flag("agent_external_fetch_enabled"),
        "publication_enabled": safety_flag("publication_enabled"),
        "outreach_enabled": safety_flag("outreach_enabled"),
        "payment_enabled": safety_flag("payment_enabled"),
        "revenue_execution_enabled": safety_flag("revenue_execution_enabled"),
        "mcp_tool_execution_enabled": safety_flag("mcp_tool_execution_enabled"),
        "live_execution_enabled": safety_flag("live_execution_enabled"),
        "cieu_db_write_enabled": safety_flag("cieu_db_write_enabled"),
        "brain_writeback_enabled": safety_flag("brain_writeback_enabled"),
        "memory_ingestion_enabled": safety_flag("memory_ingestion_enabled"),
        "real_canonical_update_application_enabled": safety_flag(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": safety_flag("real_y_star_direct_mutation_enabled"),
        "durable_approval_persistence_enabled": safety_flag("durable_approval_persistence_enabled"),
        "semantic_truth_scoring_enabled": safety_flag("semantic_truth_scoring_enabled"),
        "llm_confidence_as_authority_enabled": safety_flag("llm_confidence_as_authority_enabled"),
        "raw_runtime_artifact_reading_enabled": safety_flag("raw_runtime_artifact_reading_enabled"),
        "l6_9_pilot_approval_and_dry_run_only": l6_9_flag("l6_9_pilot_approval_and_dry_run_only"),
        "l6_9_sandbox_approval_record_only": l6_9_flag("l6_9_sandbox_approval_record_only"),
        "l6_9_agentic_work_order_selection_enabled": l6_9_flag(
            "l6_9_agentic_work_order_selection_enabled"
        ),
        "l6_9_pilot_approval_packet_generation_enabled": l6_9_flag(
            "l6_9_pilot_approval_packet_generation_enabled"
        ),
        "l6_9_sandbox_approval_record_generation_enabled": l6_9_flag(
            "l6_9_sandbox_approval_record_generation_enabled"
        ),
        "l6_9_dry_run_lifecycle_simulation_enabled": l6_9_flag(
            "l6_9_dry_run_lifecycle_simulation_enabled"
        ),
        "l6_9_empty_evidence_capture_simulation_enabled": l6_9_flag(
            "l6_9_empty_evidence_capture_simulation_enabled"
        ),
        "l6_9_real_external_observation_enabled": l6_9_flag(
            "l6_9_real_external_observation_enabled"
        ),
        "ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot": readiness_summary.get(
            "ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot"
        ),
        "ready_for_actual_network_observation_now": readiness_summary.get(
            "ready_for_actual_network_observation_now"
        ),
        "ready_for_autonomous_web_search_now": readiness_summary.get(
            "ready_for_autonomous_web_search_now"
        ),
        "ready_for_scraping": readiness_summary.get("ready_for_scraping"),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get("ready_for_brain_memory_writeback"),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_summary.json",
        "generated_selected_work_orders": "agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json",
        "generated_approval_packets": "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_index.json",
        "generated_sandbox_records": "agentic_pilot_sandbox_approval_records/sandbox_approval_record_index.json",
        "generated_dry_run_traces": "agentic_pilot_dry_run_executor/dry_run_trace_index.json",
        "generated_empty_evidence": "agentic_pilot_empty_evidence_capture_simulator/simulated_empty_evidence_packet_index.json",
        "generated_readiness": "l6_agentic_pilot_dry_run_readiness_report/l6_9_readiness_assessment.json",
        "warning": (
            "L6.9 is pilot approval and dry-run only. It selects L6.8 work "
            "orders, creates sandbox approval packets and records, simulates "
            "runtime readiness, dry-run lifecycle, empty evidence capture, "
            "post-run review, residuals, and no-action receipts, but real "
            "approval, durable approval persistence, real observation, URL "
            "open, network, search, scraping, API calls, browser fetch, "
            "publication, outreach, payment, revenue, MCP, live behavior, "
            "CIEU DB writes, canonical mutation, writeback, and direct Y* "
            "mutation remain blocked."
        ),
    }


def build_l6_tiny_observation_pilot_summary(
    milestone_summary: dict[str, Any] | None,
    selected_work_order: dict[str, Any] | None,
    locator_resolution: dict[str, Any] | None,
    observation_trace: dict[str, Any] | None,
    evidence_packet: dict[str, Any] | None,
    review_packet: dict[str, Any] | None,
    refinement_candidate: dict[str, Any] | None,
    abort_decision: dict[str, Any] | None,
    no_action_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_tiny_observation_pilot_summary",
            "schema_version": "v0",
            "l6_10_tiny_real_read_only_observation_pilot_defined": False,
            "observation_executed": False,
            "ready_for_retry_after_condition_resolved": False,
            "warning": "L6.10 tiny real read-only observation pilot has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_work_order = selected_work_order or {}
    locator_resolution = locator_resolution or {}
    observation_trace = observation_trace or {}
    evidence_packet = evidence_packet or {}
    review_packet = review_packet or {}
    refinement_candidate = refinement_candidate or {}
    abort_decision = abort_decision or {}
    no_action_receipt = no_action_receipt or {}
    residual_delta = residual_delta or {}

    contract_flags = milestone_summary.get("safety_flags", {})
    runtime_limits = milestone_summary.get("runtime_limits", {})

    def flag(field: str) -> Any:
        return milestone_summary.get(field, contract_flags.get(field))

    external_requests_count = observation_trace.get("external_requests_count", 0)
    pages_read_count = observation_trace.get("pages_read_count", 0)
    search_queries_count = observation_trace.get("search_queries_count", 0)

    return {
        "schema_name": "ystar.console_read_model.generated.l6_tiny_observation_pilot_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10"),
        "milestone_name": milestone_summary.get("milestone_name", "Tiny Real Read-Only Agentic Evidence Observation Pilot v0"),
        "mode": milestone_summary.get("mode", "tiny_real_read_only_observation_pilot"),
        "l6_10_tiny_real_read_only_observation_pilot_defined": milestone_summary.get(
            "l6_10_tiny_real_read_only_observation_pilot_defined",
            readiness_summary.get("l6_10_design_and_guardrails_complete"),
        ),
        "selected_work_order_count": milestone_summary.get("selected_work_order_count", 1),
        "selected_work_order_id": selected_work_order.get("selected_work_order_id"),
        "linked_l6_8_work_order_id": selected_work_order.get("linked_l6_8_work_order_id"),
        "source_locator_resolved": locator_resolution.get("source_locator_resolved", False),
        "observation_executed": observation_trace.get("observation_executed", False),
        "blocked_pilot": not observation_trace.get("observation_executed", False),
        "abort_triggered": observation_trace.get("abort_triggered"),
        "abort_reason": observation_trace.get("abort_reason", abort_decision.get("reason")),
        "external_requests_count": external_requests_count,
        "pages_read_count": pages_read_count,
        "search_queries_count": search_queries_count,
        "network_used": observation_trace.get("network_used", False),
        "url_opened": observation_trace.get("source_locator") is not None
        and observation_trace.get("observation_executed") is True,
        "evidence_packet_generated": bool(evidence_packet),
        "live_source_evidence_captured": evidence_packet.get("live_source_evidence_captured", False),
        "post_observation_review_packet_generated": bool(review_packet),
        "artifact_refinement_candidate_generated": bool(refinement_candidate),
        "artifact_refinement_applied": refinement_candidate.get("applied", False),
        "no_action_receipts_generated": bool(no_action_receipt),
        "strategic_residual_loop_generated": bool(residual_delta),
        "real_read_only_observation_pilot_authorized": milestone_summary.get(
            "real_read_only_observation_pilot_authorized", True
        ),
        "broad_web_search_authorized": milestone_summary.get("broad_web_search_authorized", False),
        "crawling_authorized": milestone_summary.get("crawling_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_automation_authorized": milestone_summary.get("browser_automation_authorized", False),
        "login_authorized": milestone_summary.get("login_authorized", False),
        "account_creation_authorized": milestone_summary.get("account_creation_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "form_submission_authorized": milestone_summary.get("form_submission_authorized", False),
        "posting_commenting_messaging_authorized": milestone_summary.get(
            "posting_commenting_messaging_authorized", False
        ),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "revenue_execution_authorized": milestone_summary.get("revenue_execution_authorized", False),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get("canonical_update_authorized", False),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get("memory_ingestion_authorized", False),
        "direct_y_star_mutation_authorized": milestone_summary.get("direct_y_star_mutation_authorized", False),
        "semantic_truth_scoring_enabled": flag("semantic_truth_scoring_enabled"),
        "llm_confidence_as_authority_enabled": flag("llm_confidence_as_authority_enabled"),
        "max_selected_work_orders": runtime_limits.get("max_selected_work_orders"),
        "max_source_locators_observed": runtime_limits.get("max_source_locators_observed"),
        "max_search_queries_if_locator_missing": runtime_limits.get("max_search_queries_if_locator_missing"),
        "max_pages_read": runtime_limits.get("max_pages_read"),
        "max_external_requests": runtime_limits.get("max_external_requests"),
        "ready_for_retry_after_condition_resolved": readiness_summary.get(
            "ready_for_retry_after_condition_resolved"
        ),
        "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot": readiness_summary.get(
            "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot"
        ),
        "ready_for_publication": readiness_summary.get("ready_for_publication"),
        "ready_for_outreach": readiness_summary.get("ready_for_outreach"),
        "ready_for_payment": readiness_summary.get("ready_for_payment"),
        "ready_for_revenue_execution": readiness_summary.get("ready_for_revenue_execution"),
        "ready_for_mcp_execution": readiness_summary.get("ready_for_mcp_execution"),
        "ready_for_canonical_update": readiness_summary.get("ready_for_canonical_update"),
        "ready_for_brain_memory_writeback": readiness_summary.get("ready_for_brain_memory_writeback"),
        "ready_for_direct_y_star_mutation": readiness_summary.get("ready_for_direct_y_star_mutation"),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_summary.json",
        "generated_selected_work_order": "tiny_observation_work_order_selector/selected_tiny_observation_work_order.json",
        "generated_locator_resolution": "tiny_source_locator_resolution/source_locator_resolution_result.json",
        "generated_observation_trace": "tiny_real_read_only_observation_trace/tiny_observation_trace.json",
        "generated_evidence_packet": "tiny_evidence_capture_packet/tiny_evidence_packet.json",
        "generated_review_packet": "tiny_post_observation_review_packet/tiny_post_observation_review_packet.json",
        "generated_refinement_candidate": "tiny_artifact_refinement_candidate/tiny_artifact_refinement_candidate.json",
        "generated_readiness": "l6_tiny_observation_readiness_report/l6_10_readiness_assessment.json",
        "warning": (
            "L6.10 is a tiny real read-only observation pilot. This run took the "
            "blocked outcome because the selected work order had only a placeholder "
            "locator and the environment/tooling did not authorize locator discovery. "
            "No evidence is fabricated, and all downstream action/writeback boundaries remain blocked."
        ),
    }


def build_l6_10r_locator_retry_summary(
    milestone_summary: dict[str, Any] | None,
    selected_work_order: dict[str, Any] | None,
    locator_resolution: dict[str, Any] | None,
    locator_eligibility: dict[str, Any] | None,
    execution_packet: dict[str, Any] | None,
    observation_trace: dict[str, Any] | None,
    evidence_packet: dict[str, Any] | None,
    review_packet: dict[str, Any] | None,
    refinement_candidate: dict[str, Any] | None,
    abort_decision: dict[str, Any] | None,
    no_action_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_10r_locator_retry_summary",
            "schema_version": "v0",
            "l6_10r_controlled_source_locator_resolution_retry_defined": False,
            "tiny_read_only_observation_executed": False,
            "warning": "L6.10R controlled source locator retry has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_work_order = selected_work_order or {}
    locator_resolution = locator_resolution or {}
    locator_eligibility = locator_eligibility or {}
    execution_packet = execution_packet or {}
    observation_trace = observation_trace or {}
    evidence_packet = evidence_packet or {}
    review_packet = review_packet or {}
    refinement_candidate = refinement_candidate or {}
    abort_decision = abort_decision or {}
    no_action_receipt = no_action_receipt or {}
    residual_delta = residual_delta or {}

    runtime_limits = milestone_summary.get("runtime_limits", {})
    safety_flags = milestone_summary.get("safety_flags", {})

    def flag(field: str) -> Any:
        return milestone_summary.get(field, safety_flags.get(field))

    locator_queries = observation_trace.get(
        "locator_discovery_queries_count",
        locator_resolution.get("locator_discovery_queries_count", 0),
    )
    external_reads = observation_trace.get(
        "external_reads_total",
        locator_resolution.get("external_reads_count_for_resolution", 0),
    )
    pages_read = observation_trace.get("pages_read_count", 0)

    return {
        "schema_name": "ystar.console_read_model.generated.l6_10r_locator_retry_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10R"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Controlled Source Locator Resolution & Tiny Observation Retry v0",
        ),
        "mode": milestone_summary.get("mode", "controlled_locator_resolution_and_tiny_observation_retry"),
        "l6_10r_controlled_source_locator_resolution_retry_defined": milestone_summary.get(
            "l6_10r_controlled_source_locator_resolution_retry_defined",
            readiness_summary.get("l6_10r_design_and_guardrails_complete"),
        ),
        "selected_work_order_count": milestone_summary.get("selected_work_order_count", 1),
        "selected_retry_work_order_id": selected_work_order.get("selected_retry_work_order_id"),
        "linked_l6_8_work_order_id": selected_work_order.get("linked_l6_8_work_order_id"),
        "controlled_locator_discovery_authorized": milestone_summary.get(
            "controlled_locator_discovery_authorized", True
        ),
        "tiny_real_read_only_observation_retry_authorized": milestone_summary.get(
            "tiny_real_read_only_observation_retry_authorized", True
        ),
        "locator_discovery_executed": readiness_summary.get(
            "locator_discovery_executed",
            locator_resolution.get("controlled_locator_discovery_executed", False),
        ),
        "locator_discovery_queries_count": locator_queries,
        "concrete_locator_resolved": locator_resolution.get(
            "concrete_locator_resolved",
            readiness_summary.get("concrete_locator_resolved", False),
        ),
        "resolved_locator": locator_resolution.get("resolved_locator"),
        "locator_eligible_for_observation": locator_eligibility.get(
            "locator_eligible_for_observation", False
        ),
        "retry_observation_authorized": execution_packet.get("retry_observation_authorized", False),
        "tiny_read_only_observation_executed": readiness_summary.get(
            "tiny_read_only_observation_executed",
            observation_trace.get("observation_executed", False),
        ),
        "network_used": observation_trace.get("network_used", False),
        "external_reads_total": external_reads,
        "pages_read_count": pages_read,
        "abort_triggered": observation_trace.get("abort_triggered", abort_decision.get("abort_triggered")),
        "abort_reason": observation_trace.get("abort_reason", abort_decision.get("reason")),
        "evidence_packet_generated": bool(evidence_packet),
        "live_source_evidence_captured": evidence_packet.get("live_source_evidence_captured", False),
        "post_observation_review_packet_generated": bool(review_packet),
        "artifact_refinement_candidate_generated": bool(refinement_candidate),
        "artifact_refinement_applied": refinement_candidate.get("applied", False),
        "no_action_receipts_generated": bool(no_action_receipt),
        "strategic_residual_loop_generated": bool(residual_delta),
        "broad_web_search_authorized": milestone_summary.get("broad_web_search_authorized", False),
        "repeated_search_loop_authorized": milestone_summary.get("repeated_search_loop_authorized", False),
        "crawling_authorized": milestone_summary.get("crawling_authorized", False),
        "scraping_authorized": milestone_summary.get("scraping_authorized", False),
        "browser_automation_authorized": milestone_summary.get("browser_automation_authorized", False),
        "login_authorized": milestone_summary.get("login_authorized", False),
        "account_creation_authorized": milestone_summary.get("account_creation_authorized", False),
        "contact_authorized": milestone_summary.get("contact_authorized", False),
        "payment_authorized": milestone_summary.get("payment_authorized", False),
        "form_submission_authorized": milestone_summary.get("form_submission_authorized", False),
        "posting_commenting_messaging_authorized": milestone_summary.get(
            "posting_commenting_messaging_authorized", False
        ),
        "publication_authorized": milestone_summary.get("publication_authorized", False),
        "outreach_authorized": milestone_summary.get("outreach_authorized", False),
        "revenue_execution_authorized": milestone_summary.get("revenue_execution_authorized", False),
        "mcp_execution_authorized": milestone_summary.get("mcp_execution_authorized", False),
        "live_behavior_authorized": milestone_summary.get("live_behavior_authorized", False),
        "cieu_db_write_authorized": milestone_summary.get("cieu_db_write_authorized", False),
        "canonical_update_authorized": milestone_summary.get("canonical_update_authorized", False),
        "brain_writeback_authorized": milestone_summary.get("brain_writeback_authorized", False),
        "memory_ingestion_authorized": milestone_summary.get("memory_ingestion_authorized", False),
        "direct_y_star_mutation_authorized": milestone_summary.get("direct_y_star_mutation_authorized", False),
        "semantic_truth_scoring_enabled": flag("semantic_truth_scoring_enabled"),
        "llm_confidence_as_authority_enabled": flag("llm_confidence_as_authority_enabled"),
        "max_selected_work_orders": runtime_limits.get("max_selected_work_orders"),
        "max_locator_discovery_queries": runtime_limits.get("max_locator_discovery_queries"),
        "max_concrete_locators_resolved": runtime_limits.get("max_concrete_locators_resolved"),
        "max_source_locators_observed": runtime_limits.get("max_source_locators_observed"),
        "max_pages_read": runtime_limits.get("max_pages_read"),
        "max_external_reads_total": runtime_limits.get("max_external_reads_total"),
        "remaining_blocker": readiness_summary.get("remaining_blocker"),
        "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot": readiness_summary.get(
            "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "generated_milestone_summary": "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.json",
        "generated_selected_work_order": "locator_retry_work_order_selector/selected_locator_retry_work_order.json",
        "generated_locator_resolution": "controlled_locator_resolution_trace/locator_resolution_trace.json",
        "generated_observation_trace": "tiny_observation_retry_trace/retry_observation_trace.json",
        "generated_evidence_packet": "tiny_retry_evidence_capture_packet/retry_evidence_packet.json",
        "generated_review_packet": "tiny_retry_post_observation_review/retry_post_observation_review_packet.json",
        "generated_refinement_candidate": "tiny_retry_refinement_candidate/retry_artifact_refinement_candidate.json",
        "generated_readiness": "l6_10r_readiness_report/l6_10r_readiness_assessment.json",
        "warning": (
            "L6.10R is a controlled source locator resolution and tiny observation retry. "
            "This run records Outcome C: no controlled locator-discovery tooling or "
            "concrete locator was available, so no URL was opened, no network was used, "
            "no live evidence was captured, and no evidence was fabricated."
        ),
    }


def build_l6_10t_toolmaking_locator_resolver_summary(
    milestone_summary: dict[str, Any] | None,
    blocker_analysis: dict[str, Any] | None,
    lifecycle: dict[str, Any] | None,
    tool_contract: dict[str, Any] | None,
    authority_model: dict[str, Any] | None,
    validation_matrix: dict[str, Any] | None,
    probe_result: dict[str, Any] | None,
    adapter_registry: dict[str, Any] | None,
    disabled_result: dict[str, Any] | None,
    adapter_trace: dict[str, Any] | None,
    locator_eligibility: dict[str, Any] | None,
    retry_trace: dict[str, Any] | None,
    evidence_packet: dict[str, Any] | None,
    refinement_candidate: dict[str, Any] | None,
    blocker_report: dict[str, Any] | None,
    no_action_receipt: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_10t_toolmaking_locator_resolver_summary",
            "schema_version": "v0",
            "l6_10t_governed_capability_gap_toolmaking_defined": False,
            "warning": "L6.10T governed capability-gap toolmaking has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    blocker_analysis = blocker_analysis or {}
    lifecycle = lifecycle or {}
    tool_contract = tool_contract or {}
    authority_model = authority_model or {}
    validation_matrix = validation_matrix or {}
    probe_result = probe_result or {}
    adapter_registry = adapter_registry or {}
    disabled_result = disabled_result or {}
    adapter_trace = adapter_trace or {}
    locator_eligibility = locator_eligibility or {}
    retry_trace = retry_trace or {}
    evidence_packet = evidence_packet or {}
    refinement_candidate = refinement_candidate or {}
    blocker_report = blocker_report or {}
    no_action_receipt = no_action_receipt or {}
    residual_delta = residual_delta or {}

    runtime_limits = milestone_summary.get("runtime_limits", readiness_summary.get("runtime_limits", {}))
    safety_flags = milestone_summary.get("safety_flags", readiness_summary.get("safety_flags", {}))
    diagnosis = blocker_analysis.get("diagnosis", blocker_analysis)

    def flag(field: str, default: Any = False) -> Any:
        return milestone_summary.get(field, safety_flags.get(field, default))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_10t_toolmaking_locator_resolver_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10T"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Governed Capability Gap Tool-Making Methodology & Controlled Locator Resolver Adapter v0",
        ),
        "mode": milestone_summary.get(
            "mode",
            "governed_capability_gap_toolmaking_and_locator_resolver_adapter",
        ),
        "l6_10t_governed_capability_gap_toolmaking_defined": milestone_summary.get(
            "l6_10t_governed_capability_gap_toolmaking_defined", True
        ),
        "os_neutral_design_required": flag("os_neutral_design_required"),
        "mac_only_solution_allowed": flag("mac_only_solution_allowed"),
        "capability_gap_diagnosis_completed": milestone_summary.get(
            "capability_gap_diagnosis_completed",
            readiness_summary.get("capability_gap_diagnosis_completed", bool(blocker_analysis)),
        ),
        "governed_toolmaking_methodology_created": milestone_summary.get(
            "governed_toolmaking_methodology_created", bool(lifecycle)
        ),
        "controlled_tool_contract_model_created": milestone_summary.get(
            "controlled_tool_contract_model_created",
            readiness_summary.get("controlled_tool_contract_model_created", bool(tool_contract)),
        ),
        "tool_authority_use_gate_created": bool(authority_model),
        "tool_validation_harness_created": bool(validation_matrix),
        "primary_gap_type": diagnosis.get("primary_gap_type"),
        "secondary_gap_type": diagnosis.get("secondary_gap_type"),
        "not_a_governance_logic_failure": diagnosis.get("not_a_governance_logic_failure"),
        "not_an_agentic_evidence_reasoning_failure": diagnosis.get(
            "not_an_agentic_evidence_reasoning_failure"
        ),
        "toolmaking_candidate": diagnosis.get("toolmaking_candidate"),
        "lifecycle_stage_count": len(lifecycle.get("lifecycle_stages", [])),
        "tool_generation_is_live_use_approval": authority_model.get(
            "tool_generation_is_live_use_approval", False
        ),
        "tool_tests_passing_are_live_use_approval": authority_model.get(
            "tool_tests_passing_are_live_use_approval", False
        ),
        "tool_registration_is_live_use_approval": authority_model.get(
            "tool_registration_is_live_use_approval", False
        ),
        "sandbox_use_is_live_use_approval": authority_model.get(
            "sandbox_use_is_live_use_approval", False
        ),
        "resolver_capability_probe_executed": milestone_summary.get(
            "locator_resolver_capability_probe_executed",
            readiness_summary.get("locator_resolver_capability_probe_executed", bool(probe_result)),
        ),
        "capability_probe_local_only": probe_result.get("probe_local_only"),
        "probe_used_network": milestone_summary.get(
            "probe_used_network",
            readiness_summary.get("probe_used_network", probe_result.get("network_used", False)),
        ),
        "controlled_resolver_adapter_available": milestone_summary.get(
            "controlled_resolver_adapter_available",
            readiness_summary.get(
                "controlled_resolver_adapter_available",
                probe_result.get("controlled_locator_resolver_available", False),
            ),
        ),
        "selected_resolver_adapter_id": milestone_summary.get(
            "selected_resolver_adapter_id",
            readiness_summary.get(
                "selected_resolver_adapter_id", probe_result.get("selected_resolver_adapter_id")
            ),
        ),
        "resolver_mode": probe_result.get("resolver_mode"),
        "capability_gap_code": probe_result.get("capability_gap_code", disabled_result.get("error_code")),
        "resolver_adapter_count": len(adapter_registry.get("adapters", [])),
        "adapter_selected": adapter_trace.get("adapter_selected"),
        "adapter_executed": adapter_trace.get("adapter_executed"),
        "locator_discovery_executed": milestone_summary.get(
            "locator_discovery_executed",
            readiness_summary.get("locator_discovery_executed", adapter_trace.get("locator_discovery_query_executed", False)),
        ),
        "locator_discovery_queries_count": milestone_summary.get(
            "locator_discovery_queries_count",
            readiness_summary.get("locator_discovery_queries_count", adapter_trace.get("queries_count", 0)),
        ),
        "concrete_locator_resolved": milestone_summary.get(
            "concrete_locator_resolved",
            readiness_summary.get("concrete_locator_resolved", adapter_trace.get("concrete_locator_resolved", False)),
        ),
        "resolved_locator": adapter_trace.get("resolved_locator"),
        "locator_eligibility_evaluated": locator_eligibility.get("eligibility_evaluated"),
        "tiny_read_only_observation_executed": milestone_summary.get(
            "tiny_read_only_observation_executed",
            readiness_summary.get("tiny_read_only_observation_executed", retry_trace.get("observation_executed", False)),
        ),
        "external_reads_total": milestone_summary.get(
            "external_reads_total", adapter_trace.get("external_reads_count", retry_trace.get("external_reads_count", 0))
        ),
        "pages_read_count": milestone_summary.get("pages_read_count", retry_trace.get("pages_read_count", 0)),
        "evidence_packet_generated": milestone_summary.get("evidence_packet_generated", bool(evidence_packet)),
        "live_source_evidence_captured": evidence_packet.get("live_source_evidence_captured", False),
        "artifact_refinement_candidate_generated": milestone_summary.get(
            "artifact_refinement_candidate_generated", bool(refinement_candidate)
        ),
        "artifact_refinement_applied": milestone_summary.get(
            "artifact_refinement_applied", refinement_candidate.get("applied", False)
        ),
        "generated_tools_granted_live_authority": milestone_summary.get(
            "generated_tools_granted_live_authority", False
        ),
        "no_action_receipts_generated": bool(no_action_receipt),
        "strategic_residual_loop_generated": bool(residual_delta),
        "remaining_blocker": milestone_summary.get(
            "remaining_blocker",
            readiness_summary.get("remaining_blocker", blocker_report.get("blocker_code")),
        ),
        "general_governed_toolmaking_methodology_ready_for_reuse": readiness_summary.get(
            "general_governed_toolmaking_methodology_ready_for_reuse"
        ),
        "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot": readiness_summary.get(
            "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "broad_web_search_authorized": flag("broad_web_search_authorized"),
        "repeated_search_loop_authorized": flag("repeated_search_loop_authorized"),
        "crawling_authorized": flag("crawling_authorized"),
        "scraping_authorized": flag("scraping_authorized"),
        "browser_automation_authorized": flag("browser_automation_authorized"),
        "login_authorized": flag("login_authorized"),
        "account_creation_authorized": flag("account_creation_authorized"),
        "contact_authorized": flag("contact_authorized"),
        "payment_authorized": flag("payment_authorized"),
        "form_submission_authorized": flag("form_submission_authorized"),
        "posting_commenting_messaging_authorized": flag("posting_commenting_messaging_authorized"),
        "publication_authorized": flag("publication_authorized"),
        "outreach_authorized": flag("outreach_authorized"),
        "revenue_execution_authorized": flag("revenue_execution_authorized"),
        "mcp_execution_authorized": flag("mcp_execution_authorized"),
        "live_behavior_authorized": flag("live_behavior_authorized"),
        "cieu_db_write_authorized": flag("cieu_db_write_authorized"),
        "canonical_update_authorized": flag("canonical_update_authorized"),
        "brain_writeback_authorized": flag("brain_writeback_authorized"),
        "memory_ingestion_authorized": flag("memory_ingestion_authorized"),
        "direct_y_star_mutation_authorized": flag("direct_y_star_mutation_authorized"),
        "tool_external_authority_auto_grant_authorized": flag("tool_external_authority_auto_grant_authorized"),
        "semantic_truth_scoring_authorized": flag("semantic_truth_scoring_authorized"),
        "llm_confidence_as_authority_authorized": flag("llm_confidence_as_authority_authorized"),
        "max_selected_work_orders": runtime_limits.get("max_selected_work_orders"),
        "max_resolver_adapters_selected": runtime_limits.get("max_resolver_adapters_selected"),
        "max_locator_discovery_queries": runtime_limits.get("max_locator_discovery_queries"),
        "max_concrete_locators_resolved": runtime_limits.get("max_concrete_locators_resolved"),
        "max_source_locators_observed": runtime_limits.get("max_source_locators_observed"),
        "max_pages_read": runtime_limits.get("max_pages_read"),
        "max_external_reads_total": runtime_limits.get("max_external_reads_total"),
        "generated_milestone_summary": "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_summary.json",
        "generated_blocker_analysis": "capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json",
        "generated_methodology": "governed_toolmaking_methodology/governed_toolmaking_lifecycle.json",
        "generated_tool_contract": "controlled_tool_contract_model/controlled_tool_contract_example_locator_resolver.json",
        "generated_probe_result": "locator_resolver_capability_probe/resolver_capability_probe_result.json",
        "generated_adapter_trace": "locator_resolution_adapter_trace/adapter_trace.json",
        "generated_evidence_packet": "adapter_bound_evidence_capture/adapter_bound_evidence_packet.json",
        "generated_readiness": "l6_10t_readiness_report/l6_10t_readiness_assessment.json",
        "warning": (
            "L6.10T creates a governed capability-gap diagnosis and tool-making "
            "methodology, then applies it to the missing controlled locator resolver. "
            "The default path is local-only and selects the disabled no-network resolver; "
            "no locator is fabricated, no live tool authority is granted, and L6.11 "
            "remains blocked until a controlled resolver enablement milestone."
        ),
    }


def build_l6_10u_locator_resolver_enablement_summary(
    milestone_summary: dict[str, Any] | None,
    selected_work_order: dict[str, Any] | None,
    request: dict[str, Any] | None,
    resolution_result: dict[str, Any] | None,
    resolution_trace: dict[str, Any] | None,
    locator_eligibility: dict[str, Any] | None,
    observation_trace: dict[str, Any] | None,
    evidence_packet: dict[str, Any] | None,
    refinement_candidate: dict[str, Any] | None,
    no_action_receipts: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_10u_locator_resolver_enablement_summary",
            "schema_version": "v0",
            "l6_10u_controlled_locator_resolver_enablement_complete": False,
            "warning": "L6.10U controlled locator resolver enablement has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    selected_work_order = selected_work_order or {}
    request = request or {}
    resolution_result = resolution_result or {}
    resolution_trace = resolution_trace or {}
    locator_eligibility = locator_eligibility or {}
    observation_trace = observation_trace or {}
    evidence_packet = evidence_packet or {}
    refinement_candidate = refinement_candidate or {}
    no_action_receipts = no_action_receipts or {}
    residual_delta = residual_delta or {}
    runtime_limits = milestone_summary or readiness_summary

    def flag(field: str, default: Any = False) -> Any:
        return milestone_summary.get(field, readiness_summary.get(field, default))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_10u_locator_resolver_enablement_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10U"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Controlled Locator Resolver Enablement & First Locator Attempt v0",
        ),
        "mode": milestone_summary.get(
            "mode", "controlled_locator_resolver_enablement_first_attempt"
        ),
        "l6_10u_controlled_locator_resolver_enablement_complete": readiness_summary.get(
            "l6_10u_controlled_locator_resolver_enablement_complete", True
        ),
        "resolver_runtime_created": readiness_summary.get("resolver_runtime_created", True),
        "seed_registry_resolver_created": readiness_summary.get(
            "seed_registry_resolver_created", True
        ),
        "environment_gated_search_resolver_created": readiness_summary.get(
            "environment_gated_search_resolver_created", True
        ),
        "disabled_resolver_created": readiness_summary.get("disabled_resolver_created", True),
        "selected_work_order_id": selected_work_order.get("selected_work_order_id"),
        "source_selected_work_order_id": selected_work_order.get(
            "source_selected_work_order_id"
        ),
        "selected_work_order_count": selected_work_order.get("selected_count", 0),
        "resolution_request_id": request.get("request_id"),
        "resolver_mode_used": milestone_summary.get(
            "resolver_mode_used", resolution_result.get("resolver_mode")
        ),
        "resolver_id": milestone_summary.get("resolver_id", resolution_result.get("resolver_id")),
        "seed_registry_lookup_executed": milestone_summary.get(
            "seed_registry_lookup_executed",
            resolution_result.get("seed_registry_lookup_count", 0) > 0,
        ),
        "seed_registry_lookup_count": milestone_summary.get(
            "seed_registry_lookup_count",
            resolution_result.get("seed_registry_lookup_count", 0),
        ),
        "controlled_search_executed": milestone_summary.get(
            "controlled_search_executed",
            resolution_result.get("search_query_count", 0) > 0,
        ),
        "search_query_count": milestone_summary.get(
            "search_query_count", resolution_result.get("search_query_count", 0)
        ),
        "external_reads_count": milestone_summary.get(
            "external_reads_count", resolution_result.get("external_reads_count", 0)
        ),
        "concrete_locator_resolved": milestone_summary.get(
            "concrete_locator_resolved",
            resolution_result.get("concrete_locator_resolved", False),
        ),
        "resolved_locator": milestone_summary.get(
            "resolved_locator", resolution_result.get("locator")
        ),
        "facts_inferred_from_resolution": resolution_result.get(
            "facts_inferred_from_resolution", False
        ),
        "locator_eligible_for_observation": locator_eligibility.get(
            "locator_eligible_for_observation", False
        ),
        "tiny_read_only_observation_executed": milestone_summary.get(
            "tiny_read_only_observation_executed",
            observation_trace.get("observation_executed", False),
        ),
        "pages_read_count": observation_trace.get("pages_read_count", 0),
        "evidence_packet_generated": milestone_summary.get(
            "evidence_packet_generated", bool(evidence_packet)
        ),
        "live_source_evidence_captured": evidence_packet.get(
            "live_source_evidence_captured", False
        ),
        "artifact_refinement_candidate_generated": milestone_summary.get(
            "artifact_refinement_candidate_generated", bool(refinement_candidate)
        ),
        "artifact_refinement_applied": milestone_summary.get(
            "artifact_refinement_applied", refinement_candidate.get("applied", False)
        ),
        "no_action_receipts_generated": bool(no_action_receipts.get("receipts")),
        "strategic_residual_loop_generated": bool(residual_delta),
        "remaining_blocker": milestone_summary.get(
            "remaining_blocker", readiness_summary.get("remaining_blocker")
        ),
        "ready_for_l6_11_controlled_multi_source_corroboration": readiness_summary.get(
            "ready_for_l6_11_controlled_multi_source_corroboration"
        ),
        "ready_for_l6_10u_retry_after_seed_or_search_enablement": readiness_summary.get(
            "ready_for_l6_10u_retry_after_seed_or_search_enablement"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "seed_registry_resolver_authorized": flag("seed_registry_resolver_authorized"),
        "environment_gated_controlled_search_resolver_authorized": flag(
            "environment_gated_controlled_search_resolver_authorized"
        ),
        "disabled_resolver_authorized": flag("disabled_resolver_authorized"),
        "broad_search_authorized": flag("broad_search_authorized"),
        "repeated_search_loop_authorized": flag("repeated_search_loop_authorized"),
        "crawling_authorized": flag("crawling_authorized"),
        "scraping_authorized": flag("scraping_authorized"),
        "browser_automation_authorized": flag("browser_automation_authorized"),
        "login_authorized": flag("login_authorized"),
        "account_creation_authorized": flag("account_creation_authorized"),
        "contact_authorized": flag("contact_authorized"),
        "payment_authorized": flag("payment_authorized"),
        "form_submission_authorized": flag("form_submission_authorized"),
        "posting_commenting_messaging_authorized": flag(
            "posting_commenting_messaging_authorized"
        ),
        "publication_authorized": flag("publication_authorized"),
        "outreach_authorized": flag("outreach_authorized"),
        "revenue_execution_authorized": flag("revenue_execution_authorized"),
        "mcp_execution_authorized": flag("mcp_execution_authorized"),
        "live_behavior_authorized": flag("live_behavior_authorized"),
        "cieu_db_write_authorized": flag("cieu_db_write_authorized"),
        "canonical_update_authorized": flag("canonical_update_authorized"),
        "brain_writeback_authorized": flag("brain_writeback_authorized"),
        "memory_ingestion_authorized": flag("memory_ingestion_authorized"),
        "direct_y_star_mutation_authorized": flag("direct_y_star_mutation_authorized"),
        "max_selected_work_orders": runtime_limits.get("max_selected_work_orders"),
        "max_locator_resolution_attempts": runtime_limits.get(
            "max_locator_resolution_attempts"
        ),
        "max_search_queries": runtime_limits.get("max_search_queries"),
        "max_seed_registry_lookups": runtime_limits.get("max_seed_registry_lookups"),
        "max_concrete_locators_returned": runtime_limits.get(
            "max_concrete_locators_returned"
        ),
        "max_pages_read": runtime_limits.get("max_pages_read"),
        "max_total_external_reads": runtime_limits.get("max_total_external_reads"),
        "generated_milestone_summary": "l6_controlled_locator_resolver_enablement/l6_10u_summary.json",
        "generated_selected_work_order": "controlled_locator_resolution_attempt/selected_work_order.json",
        "generated_resolution_result": "controlled_locator_resolution_attempt/locator_resolution_result.json",
        "generated_observation_trace": "controlled_locator_observation_result/tiny_observation_trace.json",
        "generated_evidence_packet": "controlled_locator_observation_result/tiny_evidence_packet.json",
        "generated_readiness": "controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json",
        "warning": (
            "L6.10U implements a practical controlled locator resolver runtime. "
            "The default run performed one seed-registry lookup, did not run "
            "controlled search, did not use network, did not fabricate a locator, "
            "and remains blocked until a seed locator or explicitly enabled "
            "controlled resolver is available."
        ),
    }


def build_l6_10v_seed_or_search_resolver_enablement_summary(
    milestone_summary: dict[str, Any] | None,
    registry: dict[str, Any] | None,
    seed_lookup_trace: dict[str, Any] | None,
    explicit_search_trace: dict[str, Any] | None,
    selected_work_order: dict[str, Any] | None,
    request: dict[str, Any] | None,
    resolution_result: dict[str, Any] | None,
    resolution_trace: dict[str, Any] | None,
    locator_eligibility: dict[str, Any] | None,
    observation_trace: dict[str, Any] | None,
    evidence_packet: dict[str, Any] | None,
    refinement_candidate: dict[str, Any] | None,
    no_action_receipts: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_10v_seed_or_search_resolver_enablement_summary",
            "schema_version": "v0",
            "l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete": False,
            "warning": "L6.10V controlled seed/search resolver enablement has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    registry = registry or {}
    seed_lookup_trace = seed_lookup_trace or {}
    explicit_search_trace = explicit_search_trace or {}
    selected_work_order = selected_work_order or {}
    request = request or {}
    resolution_result = resolution_result or {}
    resolution_trace = resolution_trace or {}
    locator_eligibility = locator_eligibility or {}
    observation_trace = observation_trace or {}
    evidence_packet = evidence_packet or {}
    refinement_candidate = refinement_candidate or {}
    no_action_receipts = no_action_receipts or {}
    residual_delta = residual_delta or {}
    runtime_limits = milestone_summary or readiness_summary

    def flag(field: str, default: Any = False) -> Any:
        return milestone_summary.get(field, readiness_summary.get(field, default))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_10v_seed_or_search_resolver_enablement_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10V"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Controlled Seed Locator Registry Population or Explicit Controlled Search Resolver Enablement v0",
        ),
        "mode": milestone_summary.get(
            "mode", "controlled_seed_locator_or_explicit_search_resolver_enablement"
        ),
        "l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete": readiness_summary.get(
            "l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete",
            True,
        ),
        "reviewed_seed_locator_registry_created": readiness_summary.get(
            "reviewed_seed_locator_registry_created", True
        ),
        "explicit_controlled_search_resolver_created": readiness_summary.get(
            "explicit_controlled_search_resolver_created", True
        ),
        "selected_work_order_id": selected_work_order.get("selected_work_order_id"),
        "source_selected_work_order_id": selected_work_order.get(
            "source_selected_work_order_id"
        ),
        "selected_work_order_count": selected_work_order.get("selected_count", 0),
        "resolution_request_id": request.get("request_id"),
        "resolution_path_used": resolution_result.get(
            "resolution_path_used", readiness_summary.get("resolution_path_used")
        ),
        "seed_registry_lookup_executed": seed_lookup_trace.get("lookup_executed", False),
        "seed_registry_lookup_count": resolution_result.get(
            "seed_registry_lookup_count",
            seed_lookup_trace.get("lookup_count", 0),
        ),
        "reviewed_seed_locator_count": len(registry.get("reviewed_seed_locators", [])),
        "seed_locator_resolved": milestone_summary.get("seed_locator_resolved", False),
        "controlled_search_enabled": milestone_summary.get(
            "controlled_search_enabled", explicit_search_trace.get("resolver_enabled", False)
        ),
        "controlled_search_executed": (
            resolution_result.get("controlled_search_query_count", 0) > 0
        ),
        "controlled_search_query_count": resolution_result.get(
            "controlled_search_query_count", 0
        ),
        "external_reads_count": resolution_result.get("external_reads_count", 0),
        "concrete_locator_resolved": resolution_result.get(
            "concrete_locator_resolved", False
        ),
        "resolved_locator": resolution_result.get("resolved_locator"),
        "facts_inferred_from_resolution": resolution_result.get(
            "facts_inferred_from_resolution", False
        ),
        "search_snippets_used_as_evidence": resolution_result.get(
            "search_snippets_used_as_evidence", False
        ),
        "locator_eligible_for_observation": locator_eligibility.get(
            "locator_eligible_for_observation", False
        ),
        "tiny_read_only_observation_executed": milestone_summary.get(
            "tiny_read_only_observation_executed",
            observation_trace.get("observation_executed", False),
        ),
        "pages_read_count": observation_trace.get("pages_read_count", 0),
        "evidence_packet_generated": milestone_summary.get(
            "evidence_packet_generated", bool(evidence_packet)
        ),
        "live_source_evidence_captured": evidence_packet.get(
            "live_source_evidence_captured", False
        ),
        "artifact_refinement_candidate_generated": bool(refinement_candidate),
        "artifact_refinement_applied": refinement_candidate.get("applied", False),
        "no_action_receipts_generated": bool(no_action_receipts.get("receipts")),
        "strategic_residual_loop_generated": bool(residual_delta),
        "remaining_blocker": milestone_summary.get(
            "remaining_blocker", readiness_summary.get("remaining_blocker")
        ),
        "ready_for_l6_11_controlled_multi_source_corroboration": readiness_summary.get(
            "ready_for_l6_11_controlled_multi_source_corroboration"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "reviewed_seed_locator_registry_authorized": flag(
            "reviewed_seed_locator_registry_authorized"
        ),
        "explicit_controlled_search_resolver_authorized": flag(
            "explicit_controlled_search_resolver_authorized"
        ),
        "controlled_search_requires_explicit_enable_flag": flag(
            "controlled_search_requires_explicit_enable_flag"
        ),
        "broad_search_authorized": flag("broad_search_authorized"),
        "repeated_search_loop_authorized": flag("repeated_search_loop_authorized"),
        "crawling_authorized": flag("crawling_authorized"),
        "scraping_authorized": flag("scraping_authorized"),
        "browser_automation_authorized": flag("browser_automation_authorized"),
        "login_authorized": flag("login_authorized"),
        "account_creation_authorized": flag("account_creation_authorized"),
        "contact_authorized": flag("contact_authorized"),
        "payment_authorized": flag("payment_authorized"),
        "form_submission_authorized": flag("form_submission_authorized"),
        "posting_commenting_messaging_authorized": flag(
            "posting_commenting_messaging_authorized"
        ),
        "publication_authorized": flag("publication_authorized"),
        "outreach_authorized": flag("outreach_authorized"),
        "revenue_execution_authorized": flag("revenue_execution_authorized"),
        "mcp_execution_authorized": flag("mcp_execution_authorized"),
        "live_behavior_authorized": flag("live_behavior_authorized"),
        "cieu_db_write_authorized": flag("cieu_db_write_authorized"),
        "canonical_update_authorized": flag("canonical_update_authorized"),
        "brain_writeback_authorized": flag("brain_writeback_authorized"),
        "memory_ingestion_authorized": flag("memory_ingestion_authorized"),
        "direct_y_star_mutation_authorized": flag("direct_y_star_mutation_authorized"),
        "max_selected_work_orders": runtime_limits.get("max_selected_work_orders"),
        "max_seed_registry_lookups": runtime_limits.get("max_seed_registry_lookups"),
        "max_controlled_search_queries": runtime_limits.get(
            "max_controlled_search_queries"
        ),
        "max_concrete_locators_resolved": runtime_limits.get(
            "max_concrete_locators_resolved"
        ),
        "max_pages_read": runtime_limits.get("max_pages_read"),
        "max_total_external_reads": runtime_limits.get("max_total_external_reads"),
        "generated_milestone_summary": "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_summary.json",
        "generated_registry": "seed_locator_registry/reviewed_seed_locator_registry.json",
        "generated_resolution_result": "locator_resolution_v_attempt/locator_resolution_v_result.json",
        "generated_observation_trace": "tiny_observation_v_result/tiny_observation_v_trace.json",
        "generated_evidence_packet": "tiny_observation_v_result/tiny_evidence_v_packet.json",
        "generated_readiness": "l6_10v_read_model/l6_10v_readiness_assessment.json",
        "warning": (
            "L6.10V creates practical seed-registry and explicit opt-in search "
            "resolver enablement paths. The default run performs one local seed "
            "lookup, does not run controlled search, does not use network, and "
            "does not fabricate a locator."
        ),
    }


def build_l6_10w_reviewed_seed_locator_injection_summary(
    milestone_summary: dict[str, Any] | None,
    seed_candidate: dict[str, Any] | None,
    user_action: dict[str, Any] | None,
    retry_trace: dict[str, Any] | None,
    observation_trace: dict[str, Any] | None,
    evidence_packet: dict[str, Any] | None,
    refinement_candidate: dict[str, Any] | None,
    no_action_receipts: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_10w_reviewed_seed_locator_injection_summary",
            "schema_version": "v0",
            "l6_10w_reviewed_seed_locator_injection_tiny_retry_complete": False,
            "warning": "L6.10W reviewed seed locator injection has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    seed_candidate = seed_candidate or {}
    user_action = user_action or {}
    retry_trace = retry_trace or {}
    observation_trace = observation_trace or {}
    evidence_packet = evidence_packet or {}
    refinement_candidate = refinement_candidate or {}
    no_action_receipts = no_action_receipts or {}
    residual_delta = residual_delta or {}
    runtime_limits = milestone_summary or readiness_summary

    def flag(field: str, default: Any = False) -> Any:
        return milestone_summary.get(field, readiness_summary.get(field, default))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_10w_reviewed_seed_locator_injection_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10W"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Reviewed Seed Locator Injection & Tiny Observation Retry v0",
        ),
        "mode": milestone_summary.get("mode", "reviewed_seed_locator_injection_and_tiny_retry"),
        "l6_10w_reviewed_seed_locator_injection_tiny_retry_complete": readiness_summary.get(
            "l6_10w_reviewed_seed_locator_injection_tiny_retry_complete", True
        ),
        "selected_work_order_id": readiness_summary.get(
            "selected_work_order_id", milestone_summary.get("selected_work_order_id")
        ),
        "reviewed_seed_locator_found": readiness_summary.get(
            "reviewed_seed_locator_found", milestone_summary.get("reviewed_seed_locator_found", False)
        ),
        "concrete_locator": readiness_summary.get(
            "concrete_locator", milestone_summary.get("concrete_locator")
        ),
        "seed_candidate_status": seed_candidate.get("status"),
        "user_action_required_generated": readiness_summary.get(
            "user_action_required_generated",
            milestone_summary.get("user_action_required_generated", False),
        ),
        "user_action_request_count": user_action.get("request_count", 0),
        "requested_item": user_action.get("requested_item"),
        "retry_attempted": retry_trace.get("retry_attempted", False),
        "tiny_read_only_observation_executed": readiness_summary.get(
            "tiny_read_only_observation_executed",
            observation_trace.get("observation_executed", False),
        ),
        "external_reads_count": observation_trace.get("external_reads_count", 0),
        "pages_read_count": observation_trace.get("pages_read_count", 0),
        "evidence_packet_generated": bool(evidence_packet),
        "live_source_evidence_captured": evidence_packet.get(
            "live_source_evidence_captured", False
        ),
        "artifact_refinement_candidate_generated": bool(refinement_candidate),
        "artifact_refinement_applied": refinement_candidate.get("applied", False),
        "no_action_receipts_generated": bool(no_action_receipts.get("receipts")),
        "strategic_residual_loop_generated": bool(residual_delta),
        "remaining_blocker": milestone_summary.get(
            "remaining_blocker", readiness_summary.get("remaining_blocker")
        ),
        "ready_for_l6_11_controlled_multi_source_corroboration": readiness_summary.get(
            "ready_for_l6_11_controlled_multi_source_corroboration"
        ),
        "next_recommended_milestone": readiness_summary.get("next_recommended_milestone"),
        "reviewed_seed_locator_injection_authorized": flag(
            "reviewed_seed_locator_injection_authorized"
        ),
        "user_action_request_authorized": flag("user_action_request_authorized"),
        "seed_locator_from_existing_repo_artifacts_authorized": flag(
            "seed_locator_from_existing_repo_artifacts_authorized"
        ),
        "url_invention_authorized": flag("url_invention_authorized"),
        "fake_locator_authorized": flag("fake_locator_authorized"),
        "broad_search_authorized": flag("broad_search_authorized"),
        "repeated_search_loop_authorized": flag("repeated_search_loop_authorized"),
        "crawling_authorized": flag("crawling_authorized"),
        "scraping_authorized": flag("scraping_authorized"),
        "browser_automation_authorized": flag("browser_automation_authorized"),
        "login_authorized": flag("login_authorized"),
        "account_creation_authorized": flag("account_creation_authorized"),
        "contact_authorized": flag("contact_authorized"),
        "payment_authorized": flag("payment_authorized"),
        "form_submission_authorized": flag("form_submission_authorized"),
        "posting_commenting_messaging_authorized": flag("posting_commenting_messaging_authorized"),
        "publication_authorized": flag("publication_authorized"),
        "outreach_authorized": flag("outreach_authorized"),
        "revenue_execution_authorized": flag("revenue_execution_authorized"),
        "mcp_execution_authorized": flag("mcp_execution_authorized"),
        "live_behavior_authorized": flag("live_behavior_authorized"),
        "cieu_db_write_authorized": flag("cieu_db_write_authorized"),
        "canonical_update_authorized": flag("canonical_update_authorized"),
        "brain_writeback_authorized": flag("brain_writeback_authorized"),
        "memory_ingestion_authorized": flag("memory_ingestion_authorized"),
        "direct_y_star_mutation_authorized": flag("direct_y_star_mutation_authorized"),
        "max_selected_work_orders": runtime_limits.get("max_selected_work_orders"),
        "max_seed_locators_injected": runtime_limits.get("max_seed_locators_injected"),
        "max_pages_read": runtime_limits.get("max_pages_read"),
        "max_total_external_reads": runtime_limits.get("max_total_external_reads"),
        "generated_milestone_summary": "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_summary.json",
        "generated_user_action_required": "seed_locator_user_action_request/USER_ACTION_REQUIRED.md",
        "generated_seed_candidate": "reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json",
        "generated_observation_trace": "seed_locator_retry_result/tiny_seed_observation_trace.json",
        "generated_evidence_packet": "seed_locator_retry_result/tiny_seed_evidence_packet.json",
        "generated_readiness": "l6_10w_read_model/l6_10w_readiness_assessment.json",
        "warning": (
            "L6.10W narrows the blocker to a precise one-URL user action request "
            "when no reviewed seed locator exists locally. It does not invent a "
            "URL, search the web, or execute observation in the default path."
        ),
    }


def build_l6_10x_budgeted_controlled_search_summary(
    milestone_summary: dict[str, Any] | None,
    query_plan: dict[str, Any] | None,
    search_trace: dict[str, Any] | None,
    triage_matrix: dict[str, Any] | None,
    crawl_trace: dict[str, Any] | None,
    trust_results: dict[str, Any] | None,
    evidence_index: dict[str, Any] | None,
    conflict_registry: dict[str, Any] | None,
    refinement_index: dict[str, Any] | None,
    residual_delta: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.l6_10x_budgeted_controlled_search_evidence_summary",
            "schema_version": "v0",
            "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete": False,
            "warning": "L6.10X budgeted controlled external search evidence pilot has not been generated yet.",
        }

    milestone_summary = milestone_summary or {}
    query_plan = query_plan or {}
    search_trace = search_trace or {}
    triage_matrix = triage_matrix or {}
    crawl_trace = crawl_trace or {}
    trust_results = trust_results or {}
    evidence_index = evidence_index or {}
    conflict_registry = conflict_registry or {}
    refinement_index = refinement_index or {}
    residual_delta = residual_delta or {}

    def flag(field: str, default: Any = False) -> Any:
        return milestone_summary.get(field, readiness_summary.get(field, default))

    return {
        "schema_name": "ystar.console_read_model.generated.l6_10x_budgeted_controlled_search_evidence_summary",
        "schema_version": "v0",
        "milestone_id": milestone_summary.get("milestone_id", "L6.10X"),
        "milestone_name": milestone_summary.get(
            "milestone_name",
            "Budgeted Controlled External Search, Bounded Crawl & Evidence Corroboration Pilot v0",
        ),
        "mode": milestone_summary.get("mode", "budgeted_controlled_external_search_evidence_pilot"),
        "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete": readiness_summary.get(
            "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete", True
        ),
        "selected_work_order_id": milestone_summary.get("selected_work_order_id"),
        "selected_work_order_count": milestone_summary.get("selected_work_order_count", 1),
        "query_count": milestone_summary.get("query_count", query_plan.get("query_count", 0)),
        "query_categories": [
            query.get("query_category") for query in query_plan.get("queries", [])
        ],
        "search_backend_mode": milestone_summary.get(
            "search_backend_mode", search_trace.get("backend_mode")
        ),
        "backend_missing": milestone_summary.get("backend_missing"),
        "search_executed": milestone_summary.get(
            "search_executed", search_trace.get("search_executed", False)
        ),
        "search_results_considered": milestone_summary.get(
            "search_results_considered", search_trace.get("search_results_considered", 0)
        ),
        "pages_opened": milestone_summary.get(
            "pages_opened", crawl_trace.get("opened_pages_count", 0)
        ),
        "domains_touched": milestone_summary.get("domains_touched", crawl_trace.get("domains_touched", 0)),
        "crawl_depth_used": milestone_summary.get("crawl_depth_used", crawl_trace.get("crawl_depth_used", 0)),
        "evidence_packets_generated": milestone_summary.get(
            "evidence_packets_generated", evidence_index.get("evidence_packet_count", 0)
        ),
        "conflicts_found": milestone_summary.get(
            "conflicts_found", conflict_registry.get("conflict_count", 0)
        ),
        "page_read_backend_missing": milestone_summary.get("page_read_backend_missing"),
        "manual_url_request_avoided": milestone_summary.get("manual_url_request_avoided", True),
        "triage_matrix_generated": bool(triage_matrix),
        "trust_assessment_generated": bool(trust_results),
        "refinement_candidates_generated": bool(refinement_index),
        "remaining_blocker": residual_delta.get("primary_residual"),
        "next_step": readiness_summary.get("next_step"),
        "controlled_external_search_authorized": flag("controlled_external_search_authorized"),
        "bounded_public_page_read_authorized": flag("bounded_public_page_read_authorized"),
        "bounded_crawl_authorized": flag("bounded_crawl_authorized"),
        "evidence_corroboration_authorized": flag("evidence_corroboration_authorized"),
        "ask_user_for_url_authorized": flag("ask_user_for_url_authorized"),
        "user_manual_url_provision_required": flag("user_manual_url_provision_required"),
        "login_authorized": flag("login_authorized"),
        "account_creation_authorized": flag("account_creation_authorized"),
        "contact_authorized": flag("contact_authorized"),
        "payment_authorized": flag("payment_authorized"),
        "form_submission_authorized": flag("form_submission_authorized"),
        "posting_commenting_messaging_authorized": flag("posting_commenting_messaging_authorized"),
        "publication_authorized": flag("publication_authorized"),
        "outreach_authorized": flag("outreach_authorized"),
        "revenue_execution_authorized": flag("revenue_execution_authorized"),
        "mcp_execution_authorized": flag("mcp_execution_authorized"),
        "live_behavior_authorized": flag("live_behavior_authorized"),
        "cieu_db_write_authorized": flag("cieu_db_write_authorized"),
        "canonical_update_authorized": flag("canonical_update_authorized"),
        "brain_writeback_authorized": flag("brain_writeback_authorized"),
        "memory_ingestion_authorized": flag("memory_ingestion_authorized"),
        "direct_y_star_mutation_authorized": flag("direct_y_star_mutation_authorized"),
        "artifact_refinement_candidate_generation_authorized": flag(
            "artifact_refinement_candidate_generation_authorized"
        ),
        "artifact_refinement_application_authorized": flag(
            "artifact_refinement_application_authorized"
        ),
        "search_snippets_as_evidence_authorized": flag(
            "search_snippets_as_evidence_authorized"
        ),
        "llm_confidence_as_truth_authority_authorized": flag(
            "llm_confidence_as_truth_authority_authorized"
        ),
        "semantic_truth_scoring_authorized": flag("semantic_truth_scoring_authorized"),
        "private_sensitive_data_collection_authorized": flag(
            "private_sensitive_data_collection_authorized"
        ),
        "high_volume_crawling_authorized": flag("high_volume_crawling_authorized"),
        "unbounded_scraping_authorized": flag("unbounded_scraping_authorized"),
        "rate_limit_required": flag("rate_limit_required"),
        "stop_on_login_or_payment_or_form": flag("stop_on_login_or_payment_or_form"),
        "stop_on_private_or_sensitive_data": flag("stop_on_private_or_sensitive_data"),
        "stop_on_scope_drift": flag("stop_on_scope_drift"),
        "max_selected_work_orders": milestone_summary.get("max_selected_work_orders"),
        "max_queries": milestone_summary.get("max_queries"),
        "max_search_results_considered": milestone_summary.get("max_search_results_considered"),
        "max_pages_opened": milestone_summary.get("max_pages_opened"),
        "max_domains": milestone_summary.get("max_domains"),
        "max_pages_per_domain": milestone_summary.get("max_pages_per_domain"),
        "max_crawl_depth": milestone_summary.get("max_crawl_depth"),
        "max_total_external_reads": milestone_summary.get("max_total_external_reads"),
        "max_evidence_packets": milestone_summary.get("max_evidence_packets"),
        "generated_milestone_summary": "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_summary.json",
        "generated_query_plan": "agentic_query_planner/generated_query_plan.json",
        "generated_search_trace": "controlled_search_backend_runtime/controlled_search_trace.json",
        "generated_crawl_trace": "bounded_crawl_runtime/bounded_crawl_trace.json",
        "generated_evidence_index": "evidence_extraction_and_claim_boundary/evidence_packet_index.json",
        "generated_readiness": "l6_10x_read_model/l6_10x_readiness_assessment.json",
        "warning": (
            "L6.10X budgets discovery instead of crippling it: five query categories, "
            "bounded result/page/domain/crawl limits, and evidence corroboration artifacts "
            "exist. Default backend is missing, so no search/network/page read occurred."
        ),
    }


def build() -> tuple[list[str], list[str], list[str], list[str]]:
    files_read: list[str] = []
    generated_files: list[str] = []
    warnings: list[str] = []

    team_model = load_json("console_read_model/team_brain_read_model.json", files_read)
    agent_cards = load_json("console_read_model/agent_cards.json", files_read)
    capability_matrix = load_json("console_read_model/capability_matrix.json", files_read)
    team_capsules = load_json("agent_brains/team_capsule_map.json", files_read)
    quarantine_index = load_json("runtime_artifact_quarantine/quarantine_index.json", files_read)
    quarantine_manifest = load_json(
        "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
        files_read,
    )
    safe_mining_candidates = load_json(
        "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
        files_read,
    )
    review_queue = load_json(
        "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json",
        files_read,
    )
    disposition_index = load_json(
        "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
        files_read,
    )
    evidence_scores = load_json(
        "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
        files_read,
    )
    decision_stub = load_json(
        "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
        files_read,
    )
    hint_routing = load_json(
        "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
        files_read,
    )
    governance_decision_snapshot = load_json(
        "labs_governance_bridge/generated/governance_decision_snapshot.json",
        files_read,
    )
    pre_u_governance_decisions = load_json(
        "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json",
        files_read,
    )
    labs_acceptance_report = load_optional_json(
        "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
        files_read,
    )
    cross_repo_generated_summary = load_optional_json(
        "cross_repo_alignment/generated/cross_repo_alignment_summary.json",
        files_read,
    )
    live_readiness_report = load_optional_json(
        "labs_live_readiness/generated/live_readiness_report.json",
        files_read,
    )
    live_boundary_generated_summary = load_optional_json(
        "labs_live_boundary/generated/live_boundary_summary.json",
        files_read,
    )
    cieu_boundary_generated_summary = load_optional_json(
        "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json",
        files_read,
    )
    autonomy_generated_summary = load_optional_json(
        "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
        files_read,
    )
    autonomous_cycle_generated_summary = load_optional_json(
        "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
        files_read,
    )
    legacy_triage_generated_summary = load_optional_json(
        "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
        files_read,
    )
    observation_loop_generated_summary = load_optional_json(
        "governed_observation_loop/generated/governed_observation_loop_summary.json",
        files_read,
    )
    readonly_tool_generated_summary = load_optional_json(
        "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
        files_read,
    )
    tool_bridge_generated_summary = load_optional_json(
        "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
        files_read,
    )
    work_proposal_generated_summary = load_optional_json(
        "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
        files_read,
    )
    dashboard_refresh_generated_summary = load_optional_json(
        "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
        files_read,
    )
    recurring_loop_generated_summary = load_optional_json(
        "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json",
        files_read,
    )
    manual_tick_generated_summary = load_optional_json(
        "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
        files_read,
    )
    field_functional_generated_summary = load_optional_json(
        "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
        files_read,
    )
    mission_projection_generated_summary = load_optional_json(
        "mission_field_projection_contract/projection_contract_summary.json",
        files_read,
    )
    field_projection_operator_summary = load_optional_json(
        "field_functional_auto_projection_core/field_projection_operator_summary.json",
        files_read,
    )
    field_projection_generated_summary = load_optional_json(
        "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
        files_read,
    )
    field_projection_pre_u_summary = load_optional_json(
        "behavior_y_star_to_pre_u_candidate/pre_u_candidate_summary.json",
        files_read,
    )
    field_projection_residual_summary = load_optional_json(
        "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
        files_read,
    )
    field_projection_readiness_summary = load_optional_json(
        "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
        files_read,
    )
    projection_cycle_generated_summary = load_optional_json(
        "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
        files_read,
    )
    projection_cycle_work_summary = load_optional_json(
        "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
        files_read,
    )
    projection_cycle_pre_u_summary = load_optional_json(
        "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
        files_read,
    )
    projection_cycle_result_summary = load_optional_json(
        "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
        files_read,
    )
    projection_cycle_residual_summary = load_optional_json(
        "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
        files_read,
    )
    projection_cycle_learning_summary = load_optional_json(
        "projection_checked_learning_review_queue/projection_learning_review_summary.json",
        files_read,
    )
    projection_cycle_readiness_summary = load_optional_json(
        "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
        files_read,
    )
    shadow_learning_loop_summary = load_optional_json(
        "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
        files_read,
    )
    shadow_learning_review_summary = load_optional_json(
        "residual_review_gate/residual_review_summary.json",
        files_read,
    )
    shadow_learning_target_summary = load_optional_json(
        "learning_target_classifier/learning_target_summary.json",
        files_read,
    )
    shadow_learning_update_summary = load_optional_json(
        "projection_policy_update_candidate/projection_policy_update_summary.json",
        files_read,
    )
    shadow_learning_patch_summary = load_optional_json(
        "shadow_projection_policy_patch/shadow_patch_summary.json",
        files_read,
    )
    shadow_learning_reprojection_summary = load_optional_json(
        "shadow_reprojection_preview/shadow_reprojection_summary.json",
        files_read,
    )
    shadow_learning_shadow_cycle_summary = load_optional_json(
        "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
        files_read,
    )
    shadow_learning_shadow_residual_summary = load_optional_json(
        "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
        files_read,
    )
    shadow_learning_effect_summary = load_optional_json(
        "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json",
        files_read,
    )
    shadow_learning_integrated_cieu_summary = load_optional_json(
        "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
        files_read,
    )
    shadow_learning_readiness_summary = load_optional_json(
        "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
        files_read,
    )
    cross_repo_governance_proof_summary = load_optional_json(
        "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
        files_read,
    )
    cross_repo_governance_y_star_gov_summary = load_optional_json(
        "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
        files_read,
    )
    cross_repo_governance_alignment_summary = load_optional_json(
        "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
        files_read,
    )
    cross_repo_governance_gov_mcp_summary = load_optional_json(
        "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
        files_read,
    )
    cross_repo_governance_interface_summary = load_optional_json(
        "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
        files_read,
    )
    cross_repo_governance_non_bypass_summary = load_optional_json(
        "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
        files_read,
    )
    cross_repo_governance_readiness_summary = load_optional_json(
        "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
        files_read,
    )
    governed_mcp_adapter_generated_summary = load_optional_json(
        "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
        files_read,
    )
    governed_mcp_adapter_intent_summary = load_optional_json(
        "mcp_request_intent_projection/mcp_request_intent_summary.json",
        files_read,
    )
    governed_mcp_adapter_pre_u_summary = load_optional_json(
        "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
        files_read,
    )
    governed_mcp_adapter_decision_summary = load_optional_json(
        "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
        files_read,
    )
    governed_mcp_adapter_bridge_summary = load_optional_json(
        "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
        files_read,
    )
    governed_mcp_adapter_call_summary = load_optional_json(
        "governed_mcp_call_candidate/governed_mcp_call_summary.json",
        files_read,
    )
    governed_mcp_adapter_receipt_summary = load_optional_json(
        "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
        files_read,
    )
    governed_mcp_adapter_residual_summary = load_optional_json(
        "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
        files_read,
    )
    governed_mcp_adapter_readiness_summary = load_optional_json(
        "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
        files_read,
    )
    controlled_canonical_learning_design_summary = load_optional_json(
        "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
        files_read,
    )
    controlled_canonical_learning_invariant_summary = load_optional_json(
        "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
        files_read,
    )
    controlled_canonical_learning_target_summary = load_optional_json(
        "canonical_learning_target_registry/canonical_learning_target_summary.json",
        files_read,
    )
    controlled_canonical_learning_evidence_summary = load_optional_json(
        "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
        files_read,
    )
    controlled_canonical_learning_gate_summary = load_optional_json(
        "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
        files_read,
    )
    controlled_canonical_learning_package_summary = load_optional_json(
        "canonical_update_package_candidate/canonical_update_package_summary.json",
        files_read,
    )
    controlled_canonical_learning_patch_summary = load_optional_json(
        "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
        files_read,
    )
    controlled_canonical_learning_rollback_summary = load_optional_json(
        "rollback_and_audit_lineage/rollback_audit_summary.json",
        files_read,
    )
    controlled_canonical_learning_validation_summary = load_optional_json(
        "post_promotion_validation_plan/post_promotion_validation_summary.json",
        files_read,
    )
    controlled_canonical_learning_promotion_summary = load_optional_json(
        "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
        files_read,
    )
    controlled_canonical_learning_readiness_summary = load_optional_json(
        "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
        files_read,
    )
    approved_sandbox_update_sandbox_summary = load_optional_json(
        "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
        files_read,
    )
    approved_sandbox_update_approval_summary = load_optional_json(
        "sandbox_approval_fixture/sandbox_approval_summary.json",
        files_read,
    )
    approved_sandbox_update_baseline_summary = load_optional_json(
        "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
        files_read,
    )
    approved_sandbox_update_patch_summary = load_optional_json(
        "sandbox_patch_application/sandbox_patch_application_summary.json",
        files_read,
    )
    approved_sandbox_update_validation_summary = load_optional_json(
        "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
        files_read,
    )
    approved_sandbox_update_reprojection_summary = load_optional_json(
        "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
        files_read,
    )
    approved_sandbox_update_cieu_summary = load_optional_json(
        "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
        files_read,
    )
    approved_sandbox_update_rollback_summary = load_optional_json(
        "sandbox_rollback_validation/sandbox_rollback_summary.json",
        files_read,
    )
    approved_sandbox_update_effect_summary = load_optional_json(
        "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
        files_read,
    )
    approved_sandbox_update_readiness_summary = load_optional_json(
        "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
        files_read,
    )
    real_approval_workflow_generated_summary = load_optional_json(
        "real_approval_workflow_boundary/real_approval_workflow_summary.json",
        files_read,
    )
    real_approval_workflow_authority_summary = load_optional_json(
        "approval_authority_model/approval_authority_summary.json",
        files_read,
    )
    real_approval_workflow_evidence_summary = load_optional_json(
        "approval_evidence_dossier/approval_evidence_summary.json",
        files_read,
    )
    real_approval_workflow_record_summary = load_optional_json(
        "durable_approval_record_contract/approval_record_summary.json",
        files_read,
    )
    real_approval_workflow_decision_summary = load_optional_json(
        "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
        files_read,
    )
    real_approval_workflow_validity_summary = load_optional_json(
        "approval_validity_revocation_policy/approval_validity_summary.json",
        files_read,
    )
    real_approval_workflow_snapshot_summary = load_optional_json(
        "pre_application_snapshot_policy/snapshot_policy_summary.json",
        files_read,
    )
    real_approval_workflow_boundary_summary = load_optional_json(
        "real_application_boundary_gate/real_application_boundary_summary.json",
        files_read,
    )
    real_approval_workflow_preflight_summary = load_optional_json(
        "post_approval_preflight_validation/post_approval_preflight_summary.json",
        files_read,
    )
    real_approval_workflow_runbook_summary = load_optional_json(
        "manual_approval_runbook/manual_approval_runbook_summary.json",
        files_read,
    )
    real_approval_workflow_audit_summary = load_optional_json(
        "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
        files_read,
    )
    real_approval_workflow_readiness_summary = load_optional_json(
        "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
        files_read,
    )
    controlled_approval_record_sandbox_summary = load_optional_json(
        "controlled_approval_record_sandbox/controlled_approval_record_sandbox_summary.json",
        files_read,
    )
    controlled_approval_record_instance_summary = load_optional_json(
        "sandbox_approval_record_instance/sandbox_approval_record_summary.json",
        files_read,
    )
    controlled_approval_record_integrity_summary = load_optional_json(
        "approval_record_integrity_validation/approval_record_integrity_summary.json",
        files_read,
    )
    controlled_approval_record_state_machine_summary = load_optional_json(
        "approval_record_validity_state_machine/approval_record_state_machine_summary.json",
        files_read,
    )
    controlled_approval_record_revocation_summary = load_optional_json(
        "expiration_revocation_replay/expiration_revocation_replay_summary.json",
        files_read,
    )
    controlled_approval_record_gate_summary = load_optional_json(
        "approval_record_pre_application_gate_replay/pre_application_gate_replay_summary.json",
        files_read,
    )
    controlled_approval_record_audit_summary = load_optional_json(
        "approval_record_audit_lineage/approval_record_audit_summary.json",
        files_read,
    )
    controlled_approval_record_cieu_summary = load_optional_json(
        "approval_record_cieu_residual/approval_record_cieu_summary.json",
        files_read,
    )
    controlled_approval_record_readiness_summary = load_optional_json(
        "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
        files_read,
    )
    controlled_real_release_preflight_summary_source = load_optional_json(
        "controlled_real_release_preflight/controlled_real_release_preflight_summary.json",
        files_read,
    )
    controlled_real_release_candidate_summary = load_optional_json(
        "release_candidate_package/release_candidate_summary.json",
        files_read,
    )
    controlled_real_release_scope_summary = load_optional_json(
        "release_scope_validation/release_scope_validation_summary.json",
        files_read,
    )
    controlled_real_release_approval_summary = load_optional_json(
        "approval_record_preflight_validation/approval_record_preflight_summary.json",
        files_read,
    )
    controlled_real_release_snapshot_rollback_summary = load_optional_json(
        "snapshot_and_rollback_preflight/snapshot_rollback_preflight_summary.json",
        files_read,
    )
    controlled_real_release_invariant_summary = load_optional_json(
        "invariant_preflight_validation/invariant_preflight_summary.json",
        files_read,
    )
    controlled_real_release_post_release_summary = load_optional_json(
        "post_release_validation_matrix/post_release_validation_summary.json",
        files_read,
    )
    controlled_real_release_handoff_summary = load_optional_json(
        "release_operator_handoff_packet/release_operator_handoff_summary.json",
        files_read,
    )
    controlled_real_release_blocker_summary = load_optional_json(
        "release_blocker_decision/release_blocker_summary.json",
        files_read,
    )
    controlled_real_release_cieu_summary = load_optional_json(
        "release_preflight_cieu_residual/release_preflight_cieu_summary.json",
        files_read,
    )
    controlled_real_release_readiness_summary = load_optional_json(
        "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
        files_read,
    )
    real_release_simulation_summary_source = load_optional_json(
        "real_release_simulation_sandbox/real_release_simulation_summary.json",
        files_read,
    )
    real_release_simulation_authority_summary = load_optional_json(
        "sandbox_release_authority_fixture/sandbox_release_authority_summary.json",
        files_read,
    )
    real_release_simulation_record_summary = load_optional_json(
        "simulated_durable_approval_record/simulated_approval_record_summary.json",
        files_read,
    )
    real_release_simulation_snapshot_summary = load_optional_json(
        "sandbox_release_snapshot/sandbox_release_snapshot_summary.json",
        files_read,
    )
    real_release_simulation_plan_summary = load_optional_json(
        "sandbox_release_execution_plan/sandbox_release_execution_summary.json",
        files_read,
    )
    real_release_simulation_result_summary = load_optional_json(
        "sandbox_release_execution_result/sandbox_release_execution_result_summary.json",
        files_read,
    )
    real_release_simulation_validation_summary = load_optional_json(
        "sandbox_post_release_validation/sandbox_post_release_validation_summary.json",
        files_read,
    )
    real_release_simulation_preview_summary = load_optional_json(
        "sandbox_release_projection_and_mcp_preview/sandbox_release_projection_mcp_summary.json",
        files_read,
    )
    real_release_simulation_rollback_summary = load_optional_json(
        "sandbox_release_rollback_drill/sandbox_release_rollback_summary.json",
        files_read,
    )
    real_release_simulation_safety_summary = load_optional_json(
        "original_release_rollback_comparison/sandbox_release_safety_summary.json",
        files_read,
    )
    real_release_simulation_cieu_summary = load_optional_json(
        "release_simulation_cieu_residual/release_simulation_cieu_summary.json",
        files_read,
    )
    real_release_simulation_readiness_summary = load_optional_json(
        "real_release_simulation_readiness/real_release_simulation_readiness.json",
        files_read,
    )
    live_boundary_framework_summary = load_optional_json(
        "live_boundary_no_go_framework/live_boundary_no_go_summary.json",
        files_read,
    )
    live_boundary_capability_summary = load_optional_json(
        "live_capability_domain_registry/live_capability_summary.json",
        files_read,
    )
    live_boundary_invariant_summary = load_optional_json(
        "no_go_invariant_matrix/no_go_invariant_summary.json",
        files_read,
    )
    live_boundary_evidence_summary = load_optional_json(
        "live_readiness_evidence_index/live_readiness_evidence_summary.json",
        files_read,
    )
    live_boundary_blocker_summary = load_optional_json(
        "live_blocker_risk_register/live_blocker_summary.json",
        files_read,
    )
    live_boundary_l6_entry_summary = load_optional_json(
        "l6_meta_development_entry_gate/l6_entry_gate_summary.json",
        files_read,
    )
    live_boundary_decision_summary = load_optional_json(
        "system_no_go_decision_packet/system_live_boundary_decision_summary.json",
        files_read,
    )
    live_boundary_cieu_summary = load_optional_json(
        "live_boundary_cieu_residual/live_boundary_cieu_summary.json",
        files_read,
    )
    live_boundary_readiness_summary = load_optional_json(
        "live_boundary_readiness/live_boundary_readiness.json",
        files_read,
    )
    l6_meta_development_engine_summary = load_optional_json(
        "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_summary.json",
        files_read,
    )
    l6_meta_development_self_asset_summary = load_optional_json(
        "self_model_and_unique_asset_field/self_asset_summary.json",
        files_read,
    )
    l6_meta_development_world_value_summary = load_optional_json(
        "world_value_field_model/world_value_field_summary.json",
        files_read,
    )
    l6_meta_development_operator_summary = load_optional_json(
        "value_conversion_operator_library/operator_library_summary.json",
        files_read,
    )
    l6_meta_development_hypothesis_summary = load_optional_json(
        "open_value_hypothesis_generator/hypothesis_generator_summary.json",
        files_read,
    )
    l6_meta_development_physics_summary = load_optional_json(
        "value_conversion_physics/conversion_physics_summary.json",
        files_read,
    )
    l6_meta_development_selection_summary = load_optional_json(
        "redeemability_selection_engine/selection_engine_summary.json",
        files_read,
    )
    l6_meta_development_mvp_summary = load_optional_json(
        "minimum_viable_proof_designer/mvp_design_summary.json",
        files_read,
    )
    l6_meta_development_portfolio_summary = load_optional_json(
        "governed_meta_development_experiment_portfolio/experiment_portfolio_summary.json",
        files_read,
    )
    l6_meta_development_residual_summary = load_optional_json(
        "strategic_residual_meta_learning_loop/strategic_residual_summary.json",
        files_read,
    )
    l6_meta_development_readiness_summary = load_optional_json(
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json",
        files_read,
    )
    l6_mvp_artifact_milestone_summary = load_optional_json(
        "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
        files_read,
    )
    l6_mvp_artifact_selected_hypotheses = load_optional_json(
        "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json",
        files_read,
    )
    l6_mvp_artifact_case_index = load_optional_json(
        "selected_mvp_artifact_cases/selected_case_index.json",
        files_read,
    )
    l6_mvp_artifact_validation_matrix = load_optional_json(
        "mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json",
        files_read,
    )
    l6_mvp_artifact_review_gate = load_optional_json(
        "mvp_artifact_review_gate/review_gate_contract.json",
        files_read,
    )
    l6_mvp_artifact_externalization_blocker = load_optional_json(
        "mvp_artifact_externalization_boundary/externalization_blocker.json",
        files_read,
    )
    l6_mvp_artifact_residual_delta = load_optional_json(
        "l6_mvp_artifact_strategic_residual_loop/l6_1_strategic_residual_delta.json",
        files_read,
    )
    l6_mvp_artifact_readiness_summary = load_optional_json(
        "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
        files_read,
    )
    l6_external_observation_milestone_summary = load_optional_json(
        "l6_governed_external_observation_boundary/l6_2_summary.json",
        files_read,
    )
    l6_external_observation_packet_schema = load_optional_json(
        "pre_observation_packet_schema/pre_observation_packet_schema.json",
        files_read,
    )
    l6_external_observation_source_registry = load_optional_json(
        "external_source_registry_and_policy/source_type_registry.json",
        files_read,
    )
    l6_external_observation_permission_gate = load_optional_json(
        "external_observation_permission_gate/observation_permission_gate_contract.json",
        files_read,
    )
    l6_external_observation_manual_import_contract = load_optional_json(
        "manual_external_evidence_import_sandbox/manual_import_contract.json",
        files_read,
    )
    l6_external_observation_linker_contract = load_optional_json(
        "observation_to_mvp_artifact_linker/observation_to_artifact_link_contract.json",
        files_read,
    )
    l6_external_observation_claim_policy = load_optional_json(
        "observation_claim_boundary_and_freshness/claim_boundary_policy.json",
        files_read,
    )
    l6_external_observation_no_network_receipt = load_optional_json(
        "external_observation_no_action_receipts/no_network_receipt.json",
        files_read,
    )
    l6_external_observation_residual_delta = load_optional_json(
        "l6_external_observation_strategic_residual_loop/l6_2_strategic_residual_delta.json",
        files_read,
    )
    l6_external_observation_readiness_summary = load_optional_json(
        "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json",
        files_read,
    )
    l6_controlled_observation_milestone_summary = load_optional_json(
        "l6_controlled_external_observation_sandbox/l6_3_summary.json",
        files_read,
    )
    l6_controlled_observation_selected_cases = load_optional_json(
        "l6_observation_case_selector/selected_observation_cases.json",
        files_read,
    )
    l6_controlled_observation_packet_index = load_optional_json(
        "controlled_pre_observation_packets/pre_observation_packet_index.json",
        files_read,
    )
    l6_controlled_observation_permission_decisions = load_optional_json(
        "sandbox_observation_permission_replay/packet_permission_decisions.json",
        files_read,
    )
    l6_controlled_observation_fixture_index = load_optional_json(
        "static_manual_observation_fixtures/observation_fixture_index.json",
        files_read,
    )
    l6_controlled_observation_validation_results = load_optional_json(
        "observation_evidence_validation_sandbox/fixture_validation_results.json",
        files_read,
    )
    l6_controlled_observation_claim_matrix = load_optional_json(
        "observation_claim_freshness_assessment/claim_freshness_matrix.json",
        files_read,
    )
    l6_controlled_observation_candidate_index = load_optional_json(
        "observation_to_artifact_refinement_candidates/refinement_candidate_index.json",
        files_read,
    )
    l6_controlled_observation_review_packet_index = load_optional_json(
        "controlled_observation_review_packets/review_packet_index.json",
        files_read,
    )
    l6_controlled_observation_no_network_receipt = load_optional_json(
        "controlled_observation_no_action_receipts/no_network_receipt.json",
        files_read,
    )
    l6_controlled_observation_residual_delta = load_optional_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_strategic_residual_delta.json",
        files_read,
    )
    l6_controlled_observation_readiness_summary = load_optional_json(
        "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json",
        files_read,
    )
    l6_real_observation_preflight_milestone_summary = load_optional_json(
        "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
        files_read,
    )
    l6_real_observation_preflight_selected_candidates = load_optional_json(
        "real_observation_candidate_selector/selected_real_observation_candidates.json",
        files_read,
    )
    l6_real_observation_preflight_requirement_registry = load_optional_json(
        "real_read_only_observation_preflight_contract/preflight_requirement_registry.json",
        files_read,
    )
    l6_real_observation_preflight_allowlist_policy = load_optional_json(
        "source_allowlist_and_risk_policy/source_allowlist_policy.json",
        files_read,
    )
    l6_real_observation_preflight_denylist_policy = load_optional_json(
        "source_allowlist_and_risk_policy/source_denylist_policy.json",
        files_read,
    )
    l6_real_observation_preflight_approval_packets = load_optional_json(
        "real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json",
        files_read,
    )
    l6_real_observation_preflight_operator_handoff = load_optional_json(
        "observation_operator_handoff/operator_handoff_contract.json",
        files_read,
    )
    l6_real_observation_preflight_network_isolation = load_optional_json(
        "observation_network_isolation_preflight/network_isolation_requirement.json",
        files_read,
    )
    l6_real_observation_preflight_evidence_capture = load_optional_json(
        "observation_evidence_capture_preflight/evidence_capture_contract.json",
        files_read,
    )
    l6_real_observation_preflight_abort_registry = load_optional_json(
        "observation_abort_rollback_quarantine_policy/abort_condition_registry.json",
        files_read,
    )
    l6_real_observation_preflight_no_real_observation_receipt = load_optional_json(
        "read_only_observation_no_action_guarantees/no_real_observation_receipt.json",
        files_read,
    )
    l6_real_observation_preflight_decisions = load_optional_json(
        "real_observation_preflight_decision_gate/candidate_preflight_decisions.json",
        files_read,
    )
    l6_real_observation_preflight_residual_delta = load_optional_json(
        "l6_real_observation_preflight_strategic_residual_loop/l6_4_strategic_residual_delta.json",
        files_read,
    )
    l6_real_observation_preflight_readiness_summary = load_optional_json(
        "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json",
        files_read,
    )
    l6_pilot_design_milestone_summary = load_optional_json(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.json",
        files_read,
    )
    l6_pilot_design_selected_candidates = load_optional_json(
        "pilot_candidate_selector/selected_pilot_candidates.json",
        files_read,
    )
    l6_pilot_design_boundary_contract = load_optional_json(
        "pilot_scope_and_non_goals/pilot_boundary_contract.json",
        files_read,
    )
    l6_pilot_design_source_allowlist = load_optional_json(
        "pilot_source_constraint_policy/pilot_source_allowlist.json",
        files_read,
    )
    l6_pilot_design_source_denylist = load_optional_json(
        "pilot_source_constraint_policy/pilot_source_denylist.json",
        files_read,
    )
    l6_pilot_design_approval_packet_index = load_optional_json(
        "pilot_approval_packet_candidates/pilot_approval_packet_index.json",
        files_read,
    )
    l6_pilot_design_operator_steps = load_optional_json(
        "pilot_operator_runbook/operator_step_sequence.json",
        files_read,
    )
    l6_pilot_design_evidence_template = load_optional_json(
        "pilot_evidence_packet_templates/pilot_evidence_packet_template.json",
        files_read,
    )
    l6_pilot_design_post_review_contract = load_optional_json(
        "pilot_post_observation_review_workflow/post_observation_review_contract.json",
        files_read,
    )
    l6_pilot_design_abort_registry = load_optional_json(
        "pilot_abort_quarantine_decision_policy/pilot_abort_condition_registry.json",
        files_read,
    )
    l6_pilot_design_success_criteria = load_optional_json(
        "pilot_success_failure_criteria/pilot_success_criteria.json",
        files_read,
    )
    l6_pilot_design_no_real_observation_receipt = load_optional_json(
        "pilot_no_action_and_execution_blockers/no_real_observation_execution_receipt.json",
        files_read,
    )
    l6_pilot_design_decisions = load_optional_json(
        "pilot_design_decision_gate/pilot_candidate_decisions.json",
        files_read,
    )
    l6_pilot_design_residual_delta = load_optional_json(
        "l6_pilot_design_strategic_residual_loop/l6_5_strategic_residual_delta.json",
        files_read,
    )
    l6_pilot_design_readiness_summary = load_optional_json(
        "l6_pilot_design_readiness/l6_5_readiness_assessment.json",
        files_read,
    )
    l6_pilot_approval_milestone_summary = load_optional_json(
        "l6_controlled_observation_pilot_approval_packet/l6_6_summary.json",
        files_read,
    )
    l6_pilot_approval_selected_candidates = load_optional_json(
        "pilot_approval_candidate_selector/selected_approval_candidates.json",
        files_read,
    )
    l6_pilot_approval_authority_model = load_optional_json(
        "pilot_approval_authority_model/approval_authority_model.json",
        files_read,
    )
    l6_pilot_approval_packet_index = load_optional_json(
        "pilot_approval_packet_assembler/approval_packet_index.json",
        files_read,
    )
    l6_pilot_approval_evidence_dossier_index = load_optional_json(
        "pilot_approval_evidence_dossier/evidence_dossier_index.json",
        files_read,
    )
    l6_pilot_approval_risk_matrix = load_optional_json(
        "pilot_approval_risk_review/approval_packet_risk_matrix.json",
        files_read,
    )
    l6_pilot_operator_authorization = load_optional_json(
        "pilot_operator_authorization_prerequisites/operator_authorization_contract.json",
        files_read,
    )
    l6_pilot_runtime_attestation = load_optional_json(
        "pilot_runtime_isolation_attestation/runtime_isolation_attestation_template.json",
        files_read,
    )
    l6_pilot_evidence_capture_authorization = load_optional_json(
        "pilot_evidence_capture_authorization/evidence_capture_authorization_template.json",
        files_read,
    )
    l6_pilot_approval_no_action_constraints = load_optional_json(
        "pilot_approval_no_action_constraints/approval_no_action_constraint_contract.json",
        files_read,
    )
    l6_pilot_approval_decision_matrix = load_optional_json(
        "pilot_approval_decision_sandbox/approval_packet_decision_matrix.json",
        files_read,
    )
    l6_pilot_approval_non_persistence_receipt = load_optional_json(
        "pilot_approval_non_persistence_receipts/no_durable_real_approval_record_receipt.json",
        files_read,
    )
    l6_pilot_approval_residual_delta = load_optional_json(
        "l6_pilot_approval_strategic_residual_loop/l6_6_strategic_residual_delta.json",
        files_read,
    )
    l6_pilot_approval_readiness_summary = load_optional_json(
        "l6_pilot_approval_readiness/l6_6_readiness_assessment.json",
        files_read,
    )
    l6_integrated_pilot_readiness_milestone_summary = load_optional_json(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_summary.json",
        files_read,
    )
    l6_integrated_pilot_readiness_sandbox_record_index = load_optional_json(
        "sandbox_approval_record_lifecycle/sandbox_approval_record_index.json",
        files_read,
    )
    l6_integrated_pilot_readiness_run_package_index = load_optional_json(
        "pilot_run_package_assembler/pilot_run_package_index.json",
        files_read,
    )
    l6_integrated_pilot_operator_readiness = load_optional_json(
        "pilot_operator_readiness_package/operator_readiness_checklist.json",
        files_read,
    )
    l6_integrated_pilot_runtime_readiness = load_optional_json(
        "pilot_runtime_isolation_readiness/runtime_isolation_readiness_packet.json",
        files_read,
    )
    l6_integrated_pilot_evidence_capture = load_optional_json(
        "pilot_evidence_capture_readiness/evidence_capture_packet_template_final.json",
        files_read,
    )
    l6_integrated_pilot_post_review = load_optional_json(
        "pilot_post_observation_review_readiness/post_observation_review_packet_template.json",
        files_read,
    )
    l6_integrated_manual_import_readiness = load_optional_json(
        "manual_evidence_import_readiness/manual_evidence_import_readiness_contract.json",
        files_read,
    )
    l6_integrated_pilot_decision_matrix = load_optional_json(
        "pilot_integrated_decision_gate/integrated_candidate_decision_matrix.json",
        files_read,
    )
    l6_integrated_pilot_no_action_receipt = load_optional_json(
        "pilot_integrated_no_action_receipts/no_real_approval_granted_receipt.json",
        files_read,
    )
    l6_integrated_pilot_residual_delta = load_optional_json(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_strategic_residual_delta.json",
        files_read,
    )
    l6_integrated_pilot_readiness_summary = load_optional_json(
        "l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json",
        files_read,
    )
    l6_agentic_evidence_milestone_summary = load_optional_json(
        "l6_agentic_evidence_discovery_trust_engine/l6_8_summary.json",
        files_read,
    )
    l6_agentic_evidence_needs = load_optional_json(
        "evidence_need_inference_engine/inferred_evidence_needs.json",
        files_read,
    )
    l6_agentic_source_hypothesis_index = load_optional_json(
        "autonomous_source_hypothesis_generator/source_hypothesis_index.json",
        files_read,
    )
    l6_agentic_source_value_matrix = load_optional_json(
        "source_type_value_model/source_type_value_matrix.json",
        files_read,
    )
    l6_agentic_trust_matrix = load_optional_json(
        "evidence_trust_judgment_model/trust_judgment_matrix.json",
        files_read,
    )
    l6_agentic_voi_matrix = load_optional_json(
        "evidence_value_of_information_model/evidence_need_voi_matrix.json",
        files_read,
    )
    l6_agentic_ranked_sources = load_optional_json(
        "source_prioritization_and_ranking_engine/ranked_source_hypotheses.json",
        files_read,
    )
    l6_agentic_conflict_contract = load_optional_json(
        "evidence_conflict_and_corrobation_model/conflict_corroboration_contract.json",
        files_read,
    )
    l6_agentic_work_order_index = load_optional_json(
        "observation_work_order_generator/observation_work_order_index.json",
        files_read,
    )
    l6_agentic_rejected_sources = load_optional_json(
        "pre_observation_rejection_filter/rejected_source_hypotheses.json",
        files_read,
    )
    l6_agentic_decision_matrix = load_optional_json(
        "agentic_evidence_decision_gate/evidence_discovery_decision_matrix.json",
        files_read,
    )
    l6_agentic_no_action_receipt = load_optional_json(
        "agentic_evidence_no_action_receipts/no_agent_fetch_receipt.json",
        files_read,
    )
    l6_agentic_residual_delta = load_optional_json(
        "l6_agentic_evidence_strategic_residual_loop/l6_8_strategic_residual_delta.json",
        files_read,
    )
    l6_agentic_readiness_summary = load_optional_json(
        "l6_agentic_evidence_readiness_report/l6_8_readiness_assessment.json",
        files_read,
    )
    l6_agentic_pilot_dry_run_milestone_summary = load_optional_json(
        "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_summary.json",
        files_read,
    )
    l6_agentic_pilot_selected_work_orders = load_optional_json(
        "agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json",
        files_read,
    )
    l6_agentic_pilot_eligibility_matrix = load_optional_json(
        "agentic_pilot_approval_eligibility_gate/approval_eligibility_matrix.json",
        files_read,
    )
    l6_agentic_pilot_approval_packet_index = load_optional_json(
        "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_index.json",
        files_read,
    )
    l6_agentic_pilot_sandbox_record_index = load_optional_json(
        "agentic_pilot_sandbox_approval_records/sandbox_approval_record_index.json",
        files_read,
    )
    l6_agentic_pilot_runtime_packet_index = load_optional_json(
        "agentic_pilot_runtime_readiness_package/runtime_readiness_packet_index.json",
        files_read,
    )
    l6_agentic_pilot_dry_run_trace_index = load_optional_json(
        "agentic_pilot_dry_run_executor/dry_run_trace_index.json",
        files_read,
    )
    l6_agentic_pilot_empty_evidence_index = load_optional_json(
        "agentic_pilot_empty_evidence_capture_simulator/simulated_empty_evidence_packet_index.json",
        files_read,
    )
    l6_agentic_pilot_post_run_review_index = load_optional_json(
        "agentic_pilot_post_run_review_simulator/post_run_review_packet_index.json",
        files_read,
    )
    l6_agentic_pilot_refinement_candidate_index = load_optional_json(
        "agentic_pilot_residual_and_refinement_candidates/dry_run_refinement_candidate_index.json",
        files_read,
    )
    l6_agentic_pilot_blocked_execution_decisions = load_optional_json(
        "agentic_pilot_real_execution_blockers/blocked_real_execution_decisions.json",
        files_read,
    )
    l6_agentic_pilot_no_action_receipt = load_optional_json(
        "agentic_pilot_no_action_receipts/no_agent_fetch_receipt.json",
        files_read,
    )
    l6_agentic_pilot_residual_delta = load_optional_json(
        "l6_agentic_pilot_dry_run_strategic_residual_loop/l6_9_strategic_residual_delta.json",
        files_read,
    )
    l6_agentic_pilot_readiness_summary = load_optional_json(
        "l6_agentic_pilot_dry_run_readiness_report/l6_9_readiness_assessment.json",
        files_read,
    )
    l6_tiny_observation_milestone_summary = load_optional_json(
        "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_summary.json",
        files_read,
    )
    l6_tiny_observation_selected_work_order = load_optional_json(
        "tiny_observation_work_order_selector/selected_tiny_observation_work_order.json",
        files_read,
    )
    l6_tiny_observation_locator_resolution = load_optional_json(
        "tiny_source_locator_resolution/source_locator_resolution_result.json",
        files_read,
    )
    l6_tiny_observation_trace = load_optional_json(
        "tiny_real_read_only_observation_trace/tiny_observation_trace.json",
        files_read,
    )
    l6_tiny_observation_evidence_packet = load_optional_json(
        "tiny_evidence_capture_packet/tiny_evidence_packet.json",
        files_read,
    )
    l6_tiny_observation_review_packet = load_optional_json(
        "tiny_post_observation_review_packet/tiny_post_observation_review_packet.json",
        files_read,
    )
    l6_tiny_observation_refinement_candidate = load_optional_json(
        "tiny_artifact_refinement_candidate/tiny_artifact_refinement_candidate.json",
        files_read,
    )
    l6_tiny_observation_abort_decision = load_optional_json(
        "tiny_observation_abort_and_quarantine/abort_or_quarantine_decision.json",
        files_read,
    )
    l6_tiny_observation_no_action_receipt = load_optional_json(
        "tiny_observation_no_action_receipts/no_crawling_receipt.json",
        files_read,
    )
    l6_tiny_observation_residual_delta = load_optional_json(
        "l6_tiny_observation_strategic_residual_loop/l6_10_strategic_residual_delta.json",
        files_read,
    )
    l6_tiny_observation_readiness_summary = load_optional_json(
        "l6_tiny_observation_readiness_report/l6_10_readiness_assessment.json",
        files_read,
    )
    l6_10r_milestone_summary = load_optional_json(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.json",
        files_read,
    )
    l6_10r_selected_work_order = load_optional_json(
        "locator_retry_work_order_selector/selected_locator_retry_work_order.json",
        files_read,
    )
    l6_10r_locator_resolution = load_optional_json(
        "controlled_locator_resolution_trace/locator_resolution_trace.json",
        files_read,
    )
    l6_10r_locator_eligibility = load_optional_json(
        "locator_eligibility_and_risk_gate/locator_eligibility_result.json",
        files_read,
    )
    l6_10r_execution_packet = load_optional_json(
        "tiny_observation_retry_execution_packet/retry_execution_packet.json",
        files_read,
    )
    l6_10r_observation_trace = load_optional_json(
        "tiny_observation_retry_trace/retry_observation_trace.json",
        files_read,
    )
    l6_10r_evidence_packet = load_optional_json(
        "tiny_retry_evidence_capture_packet/retry_evidence_packet.json",
        files_read,
    )
    l6_10r_review_packet = load_optional_json(
        "tiny_retry_post_observation_review/retry_post_observation_review_packet.json",
        files_read,
    )
    l6_10r_refinement_candidate = load_optional_json(
        "tiny_retry_refinement_candidate/retry_artifact_refinement_candidate.json",
        files_read,
    )
    l6_10r_abort_decision = load_optional_json(
        "tiny_retry_abort_quarantine/retry_abort_or_quarantine_decision.json",
        files_read,
    )
    l6_10r_no_action_receipt = load_optional_json(
        "tiny_retry_no_action_receipts/no_broad_search_receipt.json",
        files_read,
    )
    l6_10r_residual_delta = load_optional_json(
        "l6_10r_strategic_residual_loop/l6_10r_strategic_residual_delta.json",
        files_read,
    )
    l6_10r_readiness_summary = load_optional_json(
        "l6_10r_readiness_report/l6_10r_readiness_assessment.json",
        files_read,
    )
    l6_10t_milestone_summary = load_optional_json(
        "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_summary.json",
        files_read,
    )
    l6_10t_blocker_analysis = load_optional_json(
        "capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json",
        files_read,
    )
    l6_10t_lifecycle = load_optional_json(
        "governed_toolmaking_methodology/governed_toolmaking_lifecycle.json",
        files_read,
    )
    l6_10t_tool_contract = load_optional_json(
        "controlled_tool_contract_model/controlled_tool_contract_example_locator_resolver.json",
        files_read,
    )
    l6_10t_authority_model = load_optional_json(
        "tool_authority_and_use_gate/tool_authority_model.json",
        files_read,
    )
    l6_10t_validation_matrix = load_optional_json(
        "tool_sandbox_validation_harness/tool_validation_test_matrix.json",
        files_read,
    )
    l6_10t_probe_result = load_optional_json(
        "locator_resolver_capability_probe/resolver_capability_probe_result.json",
        files_read,
    )
    l6_10t_adapter_registry = load_optional_json(
        "locator_resolver_adapter_registry/resolver_adapter_registry.json",
        files_read,
    )
    l6_10t_disabled_result = load_optional_json(
        "locator_resolver_input_output_contract/locator_resolution_result_disabled_fixture.json",
        files_read,
    )
    l6_10t_adapter_trace = load_optional_json(
        "locator_resolution_adapter_trace/adapter_trace.json",
        files_read,
    )
    l6_10t_locator_eligibility = load_optional_json(
        "concrete_locator_eligibility_gate/concrete_locator_eligibility_result.json",
        files_read,
    )
    l6_10t_retry_trace = load_optional_json(
        "adapter_bound_tiny_observation_retry/adapter_bound_retry_trace.json",
        files_read,
    )
    l6_10t_evidence_packet = load_optional_json(
        "adapter_bound_evidence_capture/adapter_bound_evidence_packet.json",
        files_read,
    )
    l6_10t_refinement_candidate = load_optional_json(
        "adapter_bound_review_and_refinement/adapter_bound_refinement_candidate.json",
        files_read,
    )
    l6_10t_blocker_report = load_optional_json(
        "adapter_bound_blocker_and_fallback_report/locator_tooling_blocker.json",
        files_read,
    )
    l6_10t_no_action_receipt = load_optional_json(
        "adapter_bound_no_action_receipts/no_broad_search_receipt.json",
        files_read,
    )
    l6_10t_residual_delta = load_optional_json(
        "l6_10t_strategic_residual_loop/l6_10t_strategic_residual_delta.json",
        files_read,
    )
    l6_10t_readiness_summary = load_optional_json(
        "l6_10t_readiness_report/l6_10t_readiness_assessment.json",
        files_read,
    )
    l6_10u_milestone_summary = load_optional_json(
        "l6_controlled_locator_resolver_enablement/l6_10u_summary.json",
        files_read,
    )
    l6_10u_selected_work_order = load_optional_json(
        "controlled_locator_resolution_attempt/selected_work_order.json",
        files_read,
    )
    l6_10u_resolution_request = load_optional_json(
        "controlled_locator_resolution_attempt/locator_resolution_request.json",
        files_read,
    )
    l6_10u_resolution_result = load_optional_json(
        "controlled_locator_resolution_attempt/locator_resolution_result.json",
        files_read,
    )
    l6_10u_resolution_trace = load_optional_json(
        "controlled_locator_resolution_attempt/locator_resolution_trace.json",
        files_read,
    )
    l6_10u_locator_eligibility = load_optional_json(
        "controlled_locator_resolution_attempt/locator_eligibility_result.json",
        files_read,
    )
    l6_10u_observation_trace = load_optional_json(
        "controlled_locator_observation_result/tiny_observation_trace.json",
        files_read,
    )
    l6_10u_evidence_packet = load_optional_json(
        "controlled_locator_observation_result/tiny_evidence_packet.json",
        files_read,
    )
    l6_10u_refinement_candidate = load_optional_json(
        "controlled_locator_observation_result/tiny_refinement_candidate.json",
        files_read,
    )
    l6_10u_no_action_receipts = load_optional_json(
        "controlled_locator_observation_result/tiny_observation_no_action_receipts.json",
        files_read,
    )
    l6_10u_residual_delta = load_optional_json(
        "controlled_locator_resolver_read_model/l6_10u_strategic_residual_delta.json",
        files_read,
    )
    l6_10u_readiness_summary = load_optional_json(
        "controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json",
        files_read,
    )
    l6_10v_milestone_summary = load_optional_json(
        "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_summary.json",
        files_read,
    )
    l6_10v_registry = load_optional_json(
        "seed_locator_registry/reviewed_seed_locator_registry.json",
        files_read,
    )
    l6_10v_seed_lookup_trace = load_optional_json(
        "seed_locator_registry/seed_locator_registry_lookup_trace.json",
        files_read,
    )
    l6_10v_explicit_search_trace = load_optional_json(
        "explicit_controlled_search_resolver/explicit_search_resolver_trace.json",
        files_read,
    )
    l6_10v_selected_work_order = load_optional_json(
        "locator_resolution_v_attempt/selected_work_order.json",
        files_read,
    )
    l6_10v_resolution_request = load_optional_json(
        "locator_resolution_v_attempt/locator_resolution_v_request.json",
        files_read,
    )
    l6_10v_resolution_result = load_optional_json(
        "locator_resolution_v_attempt/locator_resolution_v_result.json",
        files_read,
    )
    l6_10v_resolution_trace = load_optional_json(
        "locator_resolution_v_attempt/locator_resolution_v_trace.json",
        files_read,
    )
    l6_10v_locator_eligibility = load_optional_json(
        "locator_resolution_v_attempt/locator_resolution_v_eligibility_result.json",
        files_read,
    )
    l6_10v_observation_trace = load_optional_json(
        "tiny_observation_v_result/tiny_observation_v_trace.json",
        files_read,
    )
    l6_10v_evidence_packet = load_optional_json(
        "tiny_observation_v_result/tiny_evidence_v_packet.json",
        files_read,
    )
    l6_10v_refinement_candidate = load_optional_json(
        "tiny_observation_v_result/tiny_refinement_v_candidate.json",
        files_read,
    )
    l6_10v_no_action_receipts = load_optional_json(
        "tiny_observation_v_result/tiny_observation_v_no_action_receipts.json",
        files_read,
    )
    l6_10v_residual_delta = load_optional_json(
        "l6_10v_read_model/l6_10v_strategic_residual_delta.json",
        files_read,
    )
    l6_10v_readiness_summary = load_optional_json(
        "l6_10v_read_model/l6_10v_readiness_assessment.json",
        files_read,
    )
    l6_10w_milestone_summary = load_optional_json(
        "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_summary.json",
        files_read,
    )
    l6_10w_seed_candidate = load_optional_json(
        "reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json",
        files_read,
    )
    l6_10w_user_action = load_optional_json(
        "seed_locator_user_action_request/user_action_required.json",
        files_read,
    )
    l6_10w_retry_trace = load_optional_json(
        "seed_locator_retry_attempt/seed_locator_retry_trace.json",
        files_read,
    )
    l6_10w_observation_trace = load_optional_json(
        "seed_locator_retry_result/tiny_seed_observation_trace.json",
        files_read,
    )
    l6_10w_evidence_packet = load_optional_json(
        "seed_locator_retry_result/tiny_seed_evidence_packet.json",
        files_read,
    )
    l6_10w_refinement_candidate = load_optional_json(
        "seed_locator_retry_result/tiny_seed_refinement_candidate.json",
        files_read,
    )
    l6_10w_no_action_receipts = load_optional_json(
        "seed_locator_retry_result/tiny_seed_no_action_receipts.json",
        files_read,
    )
    l6_10w_residual_delta = load_optional_json(
        "l6_10w_read_model/l6_10w_strategic_residual_delta.json",
        files_read,
    )
    l6_10w_readiness_summary = load_optional_json(
        "l6_10w_read_model/l6_10w_readiness_assessment.json",
        files_read,
    )
    l6_10x_milestone_summary = load_optional_json(
        "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_summary.json",
        files_read,
    )
    l6_10x_query_plan = load_optional_json(
        "agentic_query_planner/generated_query_plan.json",
        files_read,
    )
    l6_10x_search_trace = load_optional_json(
        "controlled_search_backend_runtime/controlled_search_trace.json",
        files_read,
    )
    l6_10x_triage_matrix = load_optional_json(
        "search_result_triage/source_triage_matrix.json",
        files_read,
    )
    l6_10x_crawl_trace = load_optional_json(
        "bounded_crawl_runtime/bounded_crawl_trace.json",
        files_read,
    )
    l6_10x_trust_results = load_optional_json(
        "source_quality_and_trust_assessment/trust_assessment_results.json",
        files_read,
    )
    l6_10x_evidence_index = load_optional_json(
        "evidence_extraction_and_claim_boundary/evidence_packet_index.json",
        files_read,
    )
    l6_10x_conflict_registry = load_optional_json(
        "evidence_corroboration_and_conflict_matrix/conflict_registry.json",
        files_read,
    )
    l6_10x_refinement_index = load_optional_json(
        "evidence_review_and_refinement_candidates/artifact_refinement_candidate_index.json",
        files_read,
    )
    l6_10x_residual_delta = load_optional_json(
        "l6_10x_read_model/l6_10x_strategic_residual_delta.json",
        files_read,
    )
    l6_10x_readiness_summary = load_optional_json(
        "l6_10x_read_model/l6_10x_readiness_assessment.json",
        files_read,
    )
    quarantine_summary = build_quarantine_summary(quarantine_index, quarantine_manifest)
    safe_mining_summary = build_safe_mining_summary(safe_mining_candidates)
    review_queue_summary = build_review_queue_summary(review_queue)
    disposition_summary = build_disposition_summary(disposition_index)
    evidence_review_summary = build_evidence_review_summary(evidence_scores, decision_stub, hint_routing)
    governance_bridge_summary = build_governance_bridge_summary(governance_decision_snapshot)
    pre_u_governance_summary = build_pre_u_governance_summary(pre_u_governance_decisions)
    labs_acceptance_summary = build_labs_acceptance_summary(labs_acceptance_report)
    cross_repo_alignment_summary = build_cross_repo_alignment_summary(cross_repo_generated_summary)
    live_readiness_summary = build_live_readiness_summary(live_readiness_report)
    live_boundary_summary = build_live_boundary_summary(live_boundary_generated_summary)
    cieu_boundary_summary = build_cieu_boundary_summary(cieu_boundary_generated_summary)
    autonomy_inventory_summary = build_autonomy_inventory_summary(autonomy_generated_summary)
    autonomous_cycle_summary = build_autonomous_cycle_summary(autonomous_cycle_generated_summary)
    legacy_triage_summary = build_legacy_triage_summary(legacy_triage_generated_summary)
    observation_loop_summary = build_observation_loop_summary(observation_loop_generated_summary)
    readonly_tool_summary = build_readonly_tool_summary(readonly_tool_generated_summary)
    tool_bridge_summary = build_tool_bridge_summary(tool_bridge_generated_summary)
    work_proposal_summary = build_work_proposal_summary(work_proposal_generated_summary)
    dashboard_refresh_summary = build_dashboard_refresh_summary(dashboard_refresh_generated_summary)
    recurring_loop_summary = build_recurring_loop_summary(recurring_loop_generated_summary)
    manual_tick_summary = build_manual_tick_summary(manual_tick_generated_summary)
    field_functional_summary = build_field_functional_summary(field_functional_generated_summary)
    mission_projection_summary = build_mission_projection_summary(
        mission_projection_generated_summary
    )
    field_projection_summary = build_field_projection_summary(
        field_projection_operator_summary,
        field_projection_generated_summary,
        field_projection_pre_u_summary,
        field_projection_residual_summary,
        field_projection_readiness_summary,
    )
    projection_cycle_summary = build_projection_cycle_summary(
        projection_cycle_generated_summary,
        projection_cycle_work_summary,
        projection_cycle_pre_u_summary,
        projection_cycle_result_summary,
        projection_cycle_residual_summary,
        projection_cycle_learning_summary,
        projection_cycle_readiness_summary,
    )
    shadow_learning_cycle_summary = build_shadow_learning_cycle_summary(
        shadow_learning_loop_summary,
        shadow_learning_review_summary,
        shadow_learning_target_summary,
        shadow_learning_update_summary,
        shadow_learning_patch_summary,
        shadow_learning_reprojection_summary,
        shadow_learning_shadow_cycle_summary,
        shadow_learning_shadow_residual_summary,
        shadow_learning_effect_summary,
        shadow_learning_integrated_cieu_summary,
        shadow_learning_readiness_summary,
    )
    cross_repo_governance_summary = build_cross_repo_governance_summary(
        cross_repo_governance_proof_summary,
        cross_repo_governance_y_star_gov_summary,
        cross_repo_governance_alignment_summary,
        cross_repo_governance_gov_mcp_summary,
        cross_repo_governance_interface_summary,
        cross_repo_governance_non_bypass_summary,
        cross_repo_governance_readiness_summary,
    )
    governed_mcp_adapter_summary = build_governed_mcp_adapter_summary(
        governed_mcp_adapter_generated_summary,
        governed_mcp_adapter_intent_summary,
        governed_mcp_adapter_pre_u_summary,
        governed_mcp_adapter_decision_summary,
        governed_mcp_adapter_bridge_summary,
        governed_mcp_adapter_call_summary,
        governed_mcp_adapter_receipt_summary,
        governed_mcp_adapter_residual_summary,
        governed_mcp_adapter_readiness_summary,
    )
    controlled_canonical_learning_summary = build_controlled_canonical_learning_summary(
        controlled_canonical_learning_design_summary,
        controlled_canonical_learning_invariant_summary,
        controlled_canonical_learning_target_summary,
        controlled_canonical_learning_evidence_summary,
        controlled_canonical_learning_gate_summary,
        controlled_canonical_learning_package_summary,
        controlled_canonical_learning_patch_summary,
        controlled_canonical_learning_rollback_summary,
        controlled_canonical_learning_validation_summary,
        controlled_canonical_learning_promotion_summary,
        controlled_canonical_learning_readiness_summary,
    )
    approved_sandbox_update_summary = build_approved_sandbox_update_summary(
        approved_sandbox_update_sandbox_summary,
        approved_sandbox_update_approval_summary,
        approved_sandbox_update_baseline_summary,
        approved_sandbox_update_patch_summary,
        approved_sandbox_update_validation_summary,
        approved_sandbox_update_reprojection_summary,
        approved_sandbox_update_cieu_summary,
        approved_sandbox_update_rollback_summary,
        approved_sandbox_update_effect_summary,
        approved_sandbox_update_readiness_summary,
    )
    real_approval_workflow_summary = build_real_approval_workflow_summary(
        real_approval_workflow_generated_summary,
        real_approval_workflow_authority_summary,
        real_approval_workflow_evidence_summary,
        real_approval_workflow_record_summary,
        real_approval_workflow_decision_summary,
        real_approval_workflow_validity_summary,
        real_approval_workflow_snapshot_summary,
        real_approval_workflow_boundary_summary,
        real_approval_workflow_preflight_summary,
        real_approval_workflow_runbook_summary,
        real_approval_workflow_audit_summary,
        real_approval_workflow_readiness_summary,
    )
    controlled_approval_record_summary = build_controlled_approval_record_summary(
        controlled_approval_record_sandbox_summary,
        controlled_approval_record_instance_summary,
        controlled_approval_record_integrity_summary,
        controlled_approval_record_state_machine_summary,
        controlled_approval_record_revocation_summary,
        controlled_approval_record_gate_summary,
        controlled_approval_record_audit_summary,
        controlled_approval_record_cieu_summary,
        controlled_approval_record_readiness_summary,
    )
    controlled_real_release_preflight_summary = build_controlled_real_release_preflight_summary(
        controlled_real_release_preflight_summary_source,
        controlled_real_release_candidate_summary,
        controlled_real_release_scope_summary,
        controlled_real_release_approval_summary,
        controlled_real_release_snapshot_rollback_summary,
        controlled_real_release_invariant_summary,
        controlled_real_release_post_release_summary,
        controlled_real_release_handoff_summary,
        controlled_real_release_blocker_summary,
        controlled_real_release_cieu_summary,
        controlled_real_release_readiness_summary,
    )
    real_release_simulation_summary = build_real_release_simulation_summary(
        real_release_simulation_summary_source,
        real_release_simulation_authority_summary,
        real_release_simulation_record_summary,
        real_release_simulation_snapshot_summary,
        real_release_simulation_plan_summary,
        real_release_simulation_result_summary,
        real_release_simulation_validation_summary,
        real_release_simulation_preview_summary,
        real_release_simulation_rollback_summary,
        real_release_simulation_safety_summary,
        real_release_simulation_cieu_summary,
        real_release_simulation_readiness_summary,
    )
    live_boundary_no_go_summary = build_live_boundary_no_go_summary(
        live_boundary_framework_summary,
        live_boundary_capability_summary,
        live_boundary_invariant_summary,
        live_boundary_evidence_summary,
        live_boundary_blocker_summary,
        live_boundary_l6_entry_summary,
        live_boundary_decision_summary,
        live_boundary_cieu_summary,
        live_boundary_readiness_summary,
    )
    l6_meta_development_summary = build_l6_meta_development_summary(
        l6_meta_development_engine_summary,
        l6_meta_development_self_asset_summary,
        l6_meta_development_world_value_summary,
        l6_meta_development_operator_summary,
        l6_meta_development_hypothesis_summary,
        l6_meta_development_physics_summary,
        l6_meta_development_selection_summary,
        l6_meta_development_mvp_summary,
        l6_meta_development_portfolio_summary,
        l6_meta_development_residual_summary,
        l6_meta_development_readiness_summary,
    )
    l6_mvp_artifact_sandbox_summary = build_l6_mvp_artifact_sandbox_summary(
        l6_mvp_artifact_milestone_summary,
        l6_mvp_artifact_selected_hypotheses,
        l6_mvp_artifact_case_index,
        l6_mvp_artifact_validation_matrix,
        l6_mvp_artifact_review_gate,
        l6_mvp_artifact_externalization_blocker,
        l6_mvp_artifact_residual_delta,
        l6_mvp_artifact_readiness_summary,
    )
    l6_external_observation_boundary_summary = build_l6_external_observation_boundary_summary(
        l6_external_observation_milestone_summary,
        l6_external_observation_packet_schema,
        l6_external_observation_source_registry,
        l6_external_observation_permission_gate,
        l6_external_observation_manual_import_contract,
        l6_external_observation_linker_contract,
        l6_external_observation_claim_policy,
        l6_external_observation_no_network_receipt,
        l6_external_observation_residual_delta,
        l6_external_observation_readiness_summary,
    )
    l6_controlled_observation_sandbox_summary = build_l6_controlled_observation_sandbox_summary(
        l6_controlled_observation_milestone_summary,
        l6_controlled_observation_selected_cases,
        l6_controlled_observation_packet_index,
        l6_controlled_observation_permission_decisions,
        l6_controlled_observation_fixture_index,
        l6_controlled_observation_validation_results,
        l6_controlled_observation_claim_matrix,
        l6_controlled_observation_candidate_index,
        l6_controlled_observation_review_packet_index,
        l6_controlled_observation_no_network_receipt,
        l6_controlled_observation_residual_delta,
        l6_controlled_observation_readiness_summary,
    )
    l6_real_observation_preflight_summary = build_l6_real_observation_preflight_summary(
        l6_real_observation_preflight_milestone_summary,
        l6_real_observation_preflight_selected_candidates,
        l6_real_observation_preflight_requirement_registry,
        l6_real_observation_preflight_allowlist_policy,
        l6_real_observation_preflight_denylist_policy,
        l6_real_observation_preflight_approval_packets,
        l6_real_observation_preflight_operator_handoff,
        l6_real_observation_preflight_network_isolation,
        l6_real_observation_preflight_evidence_capture,
        l6_real_observation_preflight_abort_registry,
        l6_real_observation_preflight_no_real_observation_receipt,
        l6_real_observation_preflight_decisions,
        l6_real_observation_preflight_residual_delta,
        l6_real_observation_preflight_readiness_summary,
    )
    l6_pilot_design_summary = build_l6_pilot_design_summary(
        l6_pilot_design_milestone_summary,
        l6_pilot_design_selected_candidates,
        l6_pilot_design_boundary_contract,
        l6_pilot_design_source_allowlist,
        l6_pilot_design_source_denylist,
        l6_pilot_design_approval_packet_index,
        l6_pilot_design_operator_steps,
        l6_pilot_design_evidence_template,
        l6_pilot_design_post_review_contract,
        l6_pilot_design_abort_registry,
        l6_pilot_design_success_criteria,
        l6_pilot_design_no_real_observation_receipt,
        l6_pilot_design_decisions,
        l6_pilot_design_residual_delta,
        l6_pilot_design_readiness_summary,
    )
    l6_pilot_approval_summary = build_l6_pilot_approval_summary(
        l6_pilot_approval_milestone_summary,
        l6_pilot_approval_selected_candidates,
        l6_pilot_approval_authority_model,
        l6_pilot_approval_packet_index,
        l6_pilot_approval_evidence_dossier_index,
        l6_pilot_approval_risk_matrix,
        l6_pilot_operator_authorization,
        l6_pilot_runtime_attestation,
        l6_pilot_evidence_capture_authorization,
        l6_pilot_approval_no_action_constraints,
        l6_pilot_approval_decision_matrix,
        l6_pilot_approval_non_persistence_receipt,
        l6_pilot_approval_residual_delta,
        l6_pilot_approval_readiness_summary,
    )
    l6_integrated_pilot_readiness_summary = build_l6_integrated_pilot_readiness_summary(
        l6_integrated_pilot_readiness_milestone_summary,
        l6_integrated_pilot_readiness_sandbox_record_index,
        l6_integrated_pilot_readiness_run_package_index,
        l6_integrated_pilot_operator_readiness,
        l6_integrated_pilot_runtime_readiness,
        l6_integrated_pilot_evidence_capture,
        l6_integrated_pilot_post_review,
        l6_integrated_manual_import_readiness,
        l6_integrated_pilot_decision_matrix,
        l6_integrated_pilot_no_action_receipt,
        l6_integrated_pilot_residual_delta,
        l6_integrated_pilot_readiness_summary,
    )
    l6_agentic_evidence_summary = build_l6_agentic_evidence_summary(
        l6_agentic_evidence_milestone_summary,
        l6_agentic_evidence_needs,
        l6_agentic_source_hypothesis_index,
        l6_agentic_source_value_matrix,
        l6_agentic_trust_matrix,
        l6_agentic_voi_matrix,
        l6_agentic_ranked_sources,
        l6_agentic_conflict_contract,
        l6_agentic_work_order_index,
        l6_agentic_rejected_sources,
        l6_agentic_decision_matrix,
        l6_agentic_no_action_receipt,
        l6_agentic_residual_delta,
        l6_agentic_readiness_summary,
    )
    l6_agentic_pilot_dry_run_summary = build_l6_agentic_pilot_dry_run_summary(
        l6_agentic_pilot_dry_run_milestone_summary,
        l6_agentic_pilot_selected_work_orders,
        l6_agentic_pilot_eligibility_matrix,
        l6_agentic_pilot_approval_packet_index,
        l6_agentic_pilot_sandbox_record_index,
        l6_agentic_pilot_runtime_packet_index,
        l6_agentic_pilot_dry_run_trace_index,
        l6_agentic_pilot_empty_evidence_index,
        l6_agentic_pilot_post_run_review_index,
        l6_agentic_pilot_refinement_candidate_index,
        l6_agentic_pilot_blocked_execution_decisions,
        l6_agentic_pilot_no_action_receipt,
        l6_agentic_pilot_residual_delta,
        l6_agentic_pilot_readiness_summary,
    )
    l6_tiny_observation_pilot_summary = build_l6_tiny_observation_pilot_summary(
        l6_tiny_observation_milestone_summary,
        l6_tiny_observation_selected_work_order,
        l6_tiny_observation_locator_resolution,
        l6_tiny_observation_trace,
        l6_tiny_observation_evidence_packet,
        l6_tiny_observation_review_packet,
        l6_tiny_observation_refinement_candidate,
        l6_tiny_observation_abort_decision,
        l6_tiny_observation_no_action_receipt,
        l6_tiny_observation_residual_delta,
        l6_tiny_observation_readiness_summary,
    )
    l6_10r_locator_retry_summary = build_l6_10r_locator_retry_summary(
        l6_10r_milestone_summary,
        l6_10r_selected_work_order,
        l6_10r_locator_resolution,
        l6_10r_locator_eligibility,
        l6_10r_execution_packet,
        l6_10r_observation_trace,
        l6_10r_evidence_packet,
        l6_10r_review_packet,
        l6_10r_refinement_candidate,
        l6_10r_abort_decision,
        l6_10r_no_action_receipt,
        l6_10r_residual_delta,
        l6_10r_readiness_summary,
    )
    l6_10t_toolmaking_locator_resolver_summary = build_l6_10t_toolmaking_locator_resolver_summary(
        l6_10t_milestone_summary,
        l6_10t_blocker_analysis,
        l6_10t_lifecycle,
        l6_10t_tool_contract,
        l6_10t_authority_model,
        l6_10t_validation_matrix,
        l6_10t_probe_result,
        l6_10t_adapter_registry,
        l6_10t_disabled_result,
        l6_10t_adapter_trace,
        l6_10t_locator_eligibility,
        l6_10t_retry_trace,
        l6_10t_evidence_packet,
        l6_10t_refinement_candidate,
        l6_10t_blocker_report,
        l6_10t_no_action_receipt,
        l6_10t_residual_delta,
        l6_10t_readiness_summary,
    )
    l6_10u_locator_resolver_enablement_summary = build_l6_10u_locator_resolver_enablement_summary(
        l6_10u_milestone_summary,
        l6_10u_selected_work_order,
        l6_10u_resolution_request,
        l6_10u_resolution_result,
        l6_10u_resolution_trace,
        l6_10u_locator_eligibility,
        l6_10u_observation_trace,
        l6_10u_evidence_packet,
        l6_10u_refinement_candidate,
        l6_10u_no_action_receipts,
        l6_10u_residual_delta,
        l6_10u_readiness_summary,
    )
    l6_10v_seed_or_search_resolver_enablement_summary = (
        build_l6_10v_seed_or_search_resolver_enablement_summary(
            l6_10v_milestone_summary,
            l6_10v_registry,
            l6_10v_seed_lookup_trace,
            l6_10v_explicit_search_trace,
            l6_10v_selected_work_order,
            l6_10v_resolution_request,
            l6_10v_resolution_result,
            l6_10v_resolution_trace,
            l6_10v_locator_eligibility,
            l6_10v_observation_trace,
            l6_10v_evidence_packet,
            l6_10v_refinement_candidate,
            l6_10v_no_action_receipts,
            l6_10v_residual_delta,
            l6_10v_readiness_summary,
        )
    )
    l6_10w_reviewed_seed_locator_injection_summary = (
        build_l6_10w_reviewed_seed_locator_injection_summary(
            l6_10w_milestone_summary,
            l6_10w_seed_candidate,
            l6_10w_user_action,
            l6_10w_retry_trace,
            l6_10w_observation_trace,
            l6_10w_evidence_packet,
            l6_10w_refinement_candidate,
            l6_10w_no_action_receipts,
            l6_10w_residual_delta,
            l6_10w_readiness_summary,
        )
    )
    l6_10x_budgeted_controlled_search_summary = (
        build_l6_10x_budgeted_controlled_search_summary(
            l6_10x_milestone_summary,
            l6_10x_query_plan,
            l6_10x_search_trace,
            l6_10x_triage_matrix,
            l6_10x_crawl_trace,
            l6_10x_trust_results,
            l6_10x_evidence_index,
            l6_10x_conflict_registry,
            l6_10x_refinement_index,
            l6_10x_residual_delta,
            l6_10x_readiness_summary,
        )
    )

    profiles = {
        "Aiden-CEO": load_json("agent_brains/Aiden-CEO/brain_profile.json", files_read),
        "Ethan-CTO": load_json("agent_brains/Ethan-CTO/brain_profile.json", files_read),
        "Samantha-Secretary": load_json("agent_brains/Samantha-Secretary/brain_profile.json", files_read),
    }

    ethan_execution = None
    ethan_execution_path = ROOT / "agent_brains/Ethan-CTO/execution_channels.json"
    if ethan_execution_path.exists():
        ethan_execution = load_json("agent_brains/Ethan-CTO/execution_channels.json", files_read)
    else:
        warnings.append("Ethan execution channel map not present.")

    cards_by_id = {card["card_id"]: card for card in agent_cards.get("cards", [])}
    agents = []
    for agent in team_model.get("agents", []):
        agent_id = agent["agent_id"]
        profile = profiles.get(agent_id, {})
        card = cards_by_id.get(agent_id, {})
        agents.append(
            {
                "agent_id": agent_id,
                "canonical_name": agent.get("canonical_name") or profile.get("canonical_name"),
                "role_type": agent.get("role_type") or profile.get("role_type"),
                "capsule_path": agent.get("capsule_path"),
                "readiness_level": agent.get("readiness_level"),
                "focus": agent.get("focus"),
                "card_status": card.get("status"),
                "capabilities": card.get("capabilities", []),
                "limitations": card.get("limitations", []),
                "next_actions": card.get("next_actions", []),
                "has_pre_u_packet": agent.get("has_pre_u_packet", False),
                "has_chain_review": agent.get("has_chain_review", False),
                "has_execution_channels": agent.get("has_execution_channels", False),
            }
        )

    if ethan_execution:
        warnings.append("Ethan execution channels are present as reference-only boundaries, not runtime launchers.")

    readiness = team_model.get("readiness", {})
    governance_summary = {
        "principle": "labs thinks; Y-star-gov judges; hook enforces; CIEU records and teaches; brain learns",
        "pre_u_packet_validator_spec": team_model.get("governance_interfaces", {}).get("pre_u_packet_validator_spec"),
        "boundary_docs": team_model.get("governance_interfaces", {}).get("boundary_docs"),
        "hook_role": team_model.get("governance_interfaces", {}).get("hook_role"),
        "cieu_role": team_model.get("governance_interfaces", {}).get("cieu_role"),
    }

    open_gaps = [
        "Static console loader exists; no frontend UI yet." if gap == "No static console loader." else gap
        for gap in team_model.get("open_gaps", [])
    ]
    if "Snapshot-only CLI exists; no interactive UI or live refresh yet." not in open_gaps:
        open_gaps.append("Snapshot-only CLI exists; no interactive UI or live refresh yet.")
    if "Runtime artifact quarantine is visible as a path-only summary; full artifact mining is not implemented." not in open_gaps:
        open_gaps.append("Runtime artifact quarantine is visible as a path-only summary; full artifact mining is not implemented.")
    if "Safe mining v0 produces candidate-only Markdown report snippets; no brain or CIEU ingestion exists." not in open_gaps:
        open_gaps.append("Safe mining v0 produces candidate-only Markdown report snippets; no brain or CIEU ingestion exists.")
    if "Candidate review queue exists, but no approval workflow or ingestion path exists." not in open_gaps:
        open_gaps.append("Candidate review queue exists, but no approval workflow or ingestion path exists.")
    if "Backlog disposition index exists, but evidence scoring and adapter extraction are not implemented." not in open_gaps:
        open_gaps.append("Backlog disposition index exists, but evidence scoring and adapter extraction are not implemented.")
    if "Evidence review pack exists, but semantic truth validation and decision application are not implemented." not in open_gaps:
        open_gaps.append("Evidence review pack exists, but semantic truth validation and decision application are not implemented.")
    if "Labs-Gov bridge exists as a dry-run snapshot only; no real hook integration exists." not in open_gaps:
        open_gaps.append("Labs-Gov bridge exists as a dry-run snapshot only; no real hook integration exists.")
    if "Pre-U generator exists for dry-run governance only; no runtime packet execution exists." not in open_gaps:
        open_gaps.append("Pre-U generator exists for dry-run governance only; no runtime packet execution exists.")
    if "Labs runtime acceptance exists for dry-run checks only; no real runtime execution is accepted." not in open_gaps:
        open_gaps.append("Labs runtime acceptance exists for dry-run checks only; no real runtime execution is accepted.")
    if "Cross-repo alignment exists for dry-run compatibility only; no CI or real hook enforcement exists." not in open_gaps:
        open_gaps.append("Cross-repo alignment exists for dry-run compatibility only; no CI or real hook enforcement exists.")
    if "Live readiness gate exists, but minimal live loop remains blocked until required gates exist." not in open_gaps:
        open_gaps.append("Live readiness gate exists, but minimal live loop remains blocked until required gates exist.")
    if "Live boundary harness exists as defined-disabled contracts only; no live execution is enabled." not in open_gaps:
        open_gaps.append("Live boundary harness exists as defined-disabled contracts only; no live execution is enabled.")
    if "CIEU runtime boundary exists as disabled event fixtures only; no CIEU persistence is enabled." not in open_gaps:
        open_gaps.append("CIEU runtime boundary exists as disabled event fixtures only; no CIEU persistence is enabled.")
    if "Company autonomy inventory exists, but governed action registry candidates are not live-enabled." not in open_gaps:
        open_gaps.append("Company autonomy inventory exists, but governed action registry candidates are not live-enabled.")
    if "Autonomous work cycle exists as a simulator only; no real action execution is implemented." not in open_gaps:
        open_gaps.append("Autonomous work cycle exists as a simulator only; no real action execution is implemented.")
    if "Legacy asset triage exists, but no absorption or wrapper application workflow exists." not in open_gaps:
        open_gaps.append("Legacy asset triage exists, but no absorption or wrapper application workflow exists.")
    if "Governed observation loop exists as one read-only tick; recurring wrapper execution is not implemented." not in open_gaps:
        open_gaps.append("Governed observation loop exists as one read-only tick; recurring wrapper execution is not implemented.")
    if "Governed read-only observation tool exists for local dry-run calls only; all invocations remain bridge-gated." not in open_gaps:
        open_gaps.append("Governed read-only observation tool exists for local dry-run calls only; all invocations remain bridge-gated.")
    if "Governed tool invocation bridge exists for local dry-run only; agent work proposal routing remains dry-run only." not in open_gaps:
        open_gaps.append("Governed tool invocation bridge exists for local dry-run only; agent work proposal routing remains dry-run only.")
    if "Agent-team work proposal routing feeds a manual dashboard refresh only; recurrence is not implemented yet." not in open_gaps:
        open_gaps.append("Agent-team work proposal routing feeds a manual dashboard refresh only; recurrence is not implemented yet.")
    if "Mission dashboard refresh loop exists as manual local dry-run only; governed recurrence is not implemented yet." not in open_gaps:
        open_gaps.append("Mission dashboard refresh loop exists as manual local dry-run only; governed recurrence is not implemented yet.")
    if "Recurring observation loop contract exists but recurrence, scheduler, daemon, and auto-run remain disabled." not in open_gaps:
        open_gaps.append("Recurring observation loop contract exists but recurrence, scheduler, daemon, and auto-run remain disabled.")
    if "Manual recurring observation tick runner exists for one-shot local ticks only; no scheduler, daemon, or recurrence is enabled." not in open_gaps:
        open_gaps.append("Manual recurring observation tick runner exists for one-shot local ticks only; no scheduler, daemon, or recurrence is enabled.")
    if "Field functional archaeology exists as a merge plan only; L5 projection harness is not implemented yet." not in open_gaps:
        open_gaps.append("Field functional archaeology exists as a merge plan only; L5 projection harness is not implemented yet.")
    if "Field functional auto-projection core exists as a dry-run projection core only; behavior execution remains disabled." not in open_gaps:
        open_gaps.append("Field functional auto-projection core exists as a dry-run projection core only; behavior execution remains disabled.")
    if "Integrated review-gated shadow learning cycle exists as shadow-only artifacts; controlled canonical learning is not implemented yet." not in open_gaps:
        open_gaps.append("Integrated review-gated shadow learning cycle exists as shadow-only artifacts; controlled canonical learning is not implemented yet.")
    if "Cross-repo governance contract proof exists as read-only boundary alignment; governed MCP dry-run adapter is implemented as dry-run only." not in open_gaps:
        open_gaps.append("Cross-repo governance contract proof exists as read-only boundary alignment; governed MCP dry-run adapter is implemented as dry-run only.")
    if "Controlled canonical learning design exists as a promotion dry-run only; approved canonical update sandbox now remains sandbox-only." not in open_gaps:
        open_gaps.append("Controlled canonical learning design exists as a promotion dry-run only; approved canonical update sandbox now remains sandbox-only.")
    if "Approved canonical update sandbox exists as generated sandbox-only artifacts; real approval workflow boundary is defined but real approval remains blocked." not in open_gaps:
        open_gaps.append("Approved canonical update sandbox exists as generated sandbox-only artifacts; real approval workflow boundary is defined but real approval remains blocked.")
    if "Controlled approval record sandbox exists as generated lifecycle artifacts; real durable approval persistence and real application remain blocked." not in open_gaps:
        open_gaps.append("Controlled approval record sandbox exists as generated lifecycle artifacts; real durable approval persistence and real application remain blocked.")
    if "Real release simulation sandbox exists as generated artifacts only; real release, durable persistence, real approval, and canonical application remain blocked." not in open_gaps:
        open_gaps.append("Real release simulation sandbox exists as generated artifacts only; real release, durable persistence, real approval, and canonical application remain blocked.")

    snapshot = {
        "schema_name": "ystar.console_read_model.generated.team_console_snapshot",
        "schema_version": "v0",
        "generated_by": "console_read_model/loader/build_team_console_snapshot.py",
        "source_files": files_read,
        "agents": agents,
        "capabilities": capability_matrix,
        "readiness": readiness,
        "governance_summary": governance_summary,
        "data_safety": team_model.get("data_safety", {}),
        "quarantine_summary": quarantine_summary,
        "safe_mining_summary": safe_mining_summary,
        "review_queue_summary": review_queue_summary,
        "artifact_disposition_summary": disposition_summary,
        "evidence_review_summary": evidence_review_summary,
        "governance_bridge_summary": governance_bridge_summary,
        "pre_u_governance_summary": pre_u_governance_summary,
        "labs_acceptance_summary": labs_acceptance_summary,
        "cross_repo_alignment_summary": cross_repo_alignment_summary,
        "live_readiness_summary": live_readiness_summary,
        "live_boundary_summary": live_boundary_summary,
        "cieu_boundary_summary": cieu_boundary_summary,
        "autonomy_inventory_summary": autonomy_inventory_summary,
        "autonomous_cycle_summary": autonomous_cycle_summary,
        "legacy_triage_summary": legacy_triage_summary,
        "observation_loop_summary": observation_loop_summary,
        "readonly_tool_summary": readonly_tool_summary,
        "tool_bridge_summary": tool_bridge_summary,
        "work_proposal_summary": work_proposal_summary,
        "dashboard_refresh_summary": dashboard_refresh_summary,
        "recurring_loop_summary": recurring_loop_summary,
        "manual_tick_summary": manual_tick_summary,
        "field_functional_summary": field_functional_summary,
        "mission_projection_summary": mission_projection_summary,
        "field_projection_summary": field_projection_summary,
        "projection_cycle_summary": projection_cycle_summary,
        "shadow_learning_cycle_summary": shadow_learning_cycle_summary,
        "cross_repo_governance_summary": cross_repo_governance_summary,
        "governed_mcp_adapter_summary": governed_mcp_adapter_summary,
        "controlled_canonical_learning_summary": controlled_canonical_learning_summary,
        "approved_sandbox_update_summary": approved_sandbox_update_summary,
        "real_approval_workflow_summary": real_approval_workflow_summary,
        "controlled_approval_record_summary": controlled_approval_record_summary,
        "controlled_real_release_preflight_summary": controlled_real_release_preflight_summary,
        "real_release_simulation_summary": real_release_simulation_summary,
        "live_boundary_no_go_summary": live_boundary_no_go_summary,
        "l6_meta_development_summary": l6_meta_development_summary,
        "l6_mvp_artifact_sandbox_summary": l6_mvp_artifact_sandbox_summary,
        "l6_external_observation_boundary_summary": l6_external_observation_boundary_summary,
        "l6_controlled_observation_sandbox_summary": l6_controlled_observation_sandbox_summary,
        "l6_real_observation_preflight_summary": l6_real_observation_preflight_summary,
        "l6_pilot_design_summary": l6_pilot_design_summary,
        "l6_pilot_approval_summary": l6_pilot_approval_summary,
        "l6_integrated_pilot_readiness_summary": l6_integrated_pilot_readiness_summary,
        "l6_agentic_evidence_summary": l6_agentic_evidence_summary,
        "l6_agentic_pilot_dry_run_summary": l6_agentic_pilot_dry_run_summary,
        "l6_tiny_observation_pilot_summary": l6_tiny_observation_pilot_summary,
        "l6_10r_locator_retry_summary": l6_10r_locator_retry_summary,
        "l6_10t_toolmaking_locator_resolver_summary": l6_10t_toolmaking_locator_resolver_summary,
        "l6_10u_locator_resolver_enablement_summary": l6_10u_locator_resolver_enablement_summary,
        "l6_10v_seed_or_search_resolver_enablement_summary": l6_10v_seed_or_search_resolver_enablement_summary,
        "l6_10w_reviewed_seed_locator_injection_summary": l6_10w_reviewed_seed_locator_injection_summary,
        "l6_10x_budgeted_controlled_search_evidence_summary": l6_10x_budgeted_controlled_search_summary,
        "open_gaps": open_gaps,
        "warnings": warnings,
    }

    compiled_cards = {
        "schema_name": "ystar.console_read_model.generated.agent_cards_compiled",
        "schema_version": "v0",
        "source_files": [
            "console_read_model/agent_cards.json",
            "agent_brains/team_capsule_map.json",
        ],
        "cards": [
            {
                **card,
                "capsule_map_entry": next(
                    (entry for entry in team_capsules.get("agents", []) if entry.get("agent_id") == card.get("card_id")),
                    None,
                ),
            }
            for card in agent_cards.get("cards", [])
        ],
    }

    readiness_summary = {
        "schema_name": "ystar.console_read_model.generated.readiness_summary",
        "schema_version": "v0",
        "ready_now": [
            "reference docs",
            "team read model",
            "capsule schema",
            "Aiden capsule chain",
            "Ethan/Samantha base capsules",
            "Y-star-gov validator interface spec",
            "static read-model validation utility",
            "static snapshot generator",
            "snapshot-only team console CLI",
            "path-only runtime artifact quarantine summary",
            "bounded Markdown safe-mining candidate index",
            "candidate review queue summary",
            "runtime artifact backlog disposition summary",
            "structural evidence review summary",
            "dry-run Labs-Gov alignment bridge snapshot",
            "multi-role dry-run Pre-U governance summary",
            "dry-run labs runtime governance acceptance summary",
            "dry-run cross-repo governance alignment summary",
            "live-readiness gate summary that keeps live execution blocked",
            "disabled live-boundary harness summary",
            "disabled CIEU runtime event boundary summary",
            "company autonomy inventory summary",
            "mission-bounded autonomous work cycle simulator summary",
            "legacy asset triage summary",
            "governed read-only observation loop summary",
            "first governed read-only observation tool wrapper summary",
            "governed tool invocation bridge summary",
            "agent-team work proposal to governed tool invocation summary",
            "mission dashboard refresh loop summary",
            "governed recurring observation loop contract summary",
            "manual recurring observation tick runner summary",
            "field functional archaeology and merge plan summary",
            "mission field functional projection harness summary",
            "field functional auto-projection core summary",
            "projection-checked autonomous work cycle summary",
            "review-gated shadow learning cycle summary",
            "cross-repo governance contract proof summary",
            "governed MCP dry-run adapter summary",
            "controlled canonical learning design summary",
            "controlled approval record sandbox summary",
        ],
        "not_ready": [
            "runtime generator",
            "hook enforcement",
            "validator implementation",
            "CIEU delta schema",
            "brain writeback integration validation",
            "DB-safe query adapter",
            "frontend console",
            "live team-state refresh",
            "CI wiring for validator/generator",
            "CLI integration packaging",
            "semantic validation against live runtime",
            "full runtime artifact mining or curation adapters",
            "brain/CIEU ingestion from safe-mining candidates",
            "review approval workflow for candidate queue entries",
            "evidence scoring for disposition records",
            "DB/log/marker metadata adapters",
            "semantic truth validation for evidence records",
            "review decision application workflow",
            "real hook integration for Labs-Gov bridge",
            "runtime Pre-U packet execution",
            "real runtime acceptance beyond dry-run checks",
            "real cross-repo hook enforcement beyond dry-run alignment",
            "minimal live governed loop",
            "enabled live-boundary harness",
            "enabled CIEU runtime event persistence",
            "approved governed action registry",
            "approved canonical update sandbox",
            "L6 revenue opportunity discovery",
        ],
        "recommended_next_steps": [
            "wire static validator and loader into CI",
            "build a frontend that reads generated snapshots only",
            "create Y-star-gov validator skeleton",
            "define CIEU prediction-delta schema",
            "add Ethan/Samantha Pre-U packet variants",
            "design safe adapters for quarantine-to-CIEU review",
            "add human review queue for safe-mining candidates",
            "define signed review decisions for candidate queue entries",
            "create evidence scoring schema for disposition records",
            "define manual decision application for evidence review stubs",
            "connect bridge decisions to future Pre-U/CIEU dry-run examples without executing actions",
            "define a reviewed path from Pre-U dry-run snapshots to future CIEU prediction-delta examples",
            "define real hook enforcement handoff after dry-run acceptance remains stable",
            "define CI handoff after cross-repo dry-run alignment remains stable",
            "build live boundary harness before any runtime execution",
            "implement live boundary gates without enabling runtime execution",
            "define CIEU runtime event writer verification without enabling persistence",
            "simulate a company autonomous work cycle without enabling live actions",
            "build L4.4 first governed read-only observation tool wrapper",
            "route the governed read-only observation tool through the Pre-U bridge",
            "build L4.6 agent team work proposal to governed tool invocation",
            "define L4.8 governed recurring observation loop contract",
            "build L5.0 review-gated learning candidate queue",
            "build L5.1 mission field functional projection harness from archaeology merge plan",
            "build L5.8 approved canonical update sandbox from L5.7 promotion design",
            "build L5.11 controlled real release preflight from L5.10 approval record sandbox",
        ],
        "blockers": [
            "no DB-safe adapter",
            "no live validator implementation",
            "no hook enforcement",
            "no semantic runtime truth guarantee",
            "no real Labs-Gov hook enforcement path",
            "no runtime Pre-U execution path",
            "no real action/CIEU/brain write path from acceptance reports",
            "no real cross-repo hook enforcement path",
            "no live boundary harness or operator approval gate",
            "live boundary gates are defined but disabled",
            "CIEU runtime event boundary is defined but persistence is disabled",
            "governed action registry candidates are mapped but disabled",
            "autonomous cycle is simulated only and cannot execute real work",
            "legacy assets are triaged but not absorbed",
            "observation loop is read-only and not recurring",
            "recurring observation loop contract is defined but not enabled",
            "approved canonical update sandbox is not implemented yet",
            "real durable approval persistence remains blocked",
            "real canonical update application remains blocked",
            "L6 revenue opportunity discovery remains blocked until canonical learning controls exist",
        ],
        "safety_boundaries": [
            "no DB reads",
            "no log reads",
            "no daemon/runtime state reads",
            "no hook/governance execution",
            "curated read-model files only",
            "quarantine summary is path-level only",
            "safe-mining candidates are bounded Markdown snippets only",
            "review queue entries are pending and not ingested",
            "disposition records are routing metadata, not ingestion",
            "evidence scoring is structural only and does not approve ingestion",
            "Labs-Gov bridge is dry-run only and does not execute actions",
            "generated Pre-U packets are dry-run only and not runtime actions",
            "labs runtime acceptance is dry-run only and not runtime execution",
            "cross-repo alignment is dry-run only and not CI or hook execution",
            "live-readiness gate forbids action/CIEU/brain/memory writes",
            "live-boundary harness is disabled and requires manual enablement",
            "CIEU runtime event boundary is disabled and forbids persistence",
            "company autonomy inventory is discovery-only and live actions remain disabled",
            "autonomous work cycle is simulated only and performs no external action",
            "legacy asset triage is classification-only and does not absorb assets",
            "governed observation loop reads generated summaries only and executes no actions",
            "governed read-only observation tool reads allowed generated summaries only and executes no actions",
            "governed tool invocation bridge requires Pre-U/decision/authorization before local tool calls",
            "agent-team work proposal routing starts from generated observations and remains local read-only dry-run only",
            "mission dashboard refresh loop is manual local dry-run only and uses generated/read-model evidence only",
            "recurring observation loop contract simulates one manual local tick and does not enable recurrence",
            "manual recurring observation tick runner executes one manual local tick only and does not enable recurrence",
            "field functional archaeology is merge-plan-only and does not execute old code or absorb runtime assets",
            "field functional auto-projection core is dry-run only and does not execute behavior",
            "projection-checked autonomous work cycle is dry-run only and does not execute behavior",
            "review-gated shadow learning cycle previews policy changes only and does not mutate canonical policy",
            "cross-repo governance proof keeps ystar-company as labs/runtime and not a governance kernel",
            "governed MCP dry-run adapter blocks real MCP server/tool/resource execution and mutation",
            "controlled canonical learning design creates promotion packages only and blocks approval, application, writeback, and direct Y* mutation",
            "controlled approval record sandbox creates generated record lifecycle fixtures only and blocks real approval, durable persistence, real application, writeback, direct Y* mutation, and MCP execution",
        ],
    }

    manifest = {
        "schema_name": "ystar.console_read_model.generated.generation_manifest",
        "schema_version": "v0",
        "generated_files": [
            "console_read_model/generated/README.md",
            "console_read_model/generated/team_console_snapshot.json",
            "console_read_model/generated/team_console_snapshot.md",
            "console_read_model/generated/agent_cards_compiled.json",
            "console_read_model/generated/readiness_summary.json",
            "console_read_model/generated/quarantine_summary.json",
            "console_read_model/generated/safe_mining_summary.json",
            "console_read_model/generated/review_queue_summary.json",
            "console_read_model/generated/artifact_disposition_summary.json",
            "console_read_model/generated/evidence_review_summary.json",
            "console_read_model/generated/governance_bridge_summary.json",
            "console_read_model/generated/pre_u_governance_summary.json",
            "console_read_model/generated/labs_acceptance_summary.json",
            "console_read_model/generated/cross_repo_alignment_summary.json",
            "console_read_model/generated/live_readiness_summary.json",
            "console_read_model/generated/live_boundary_summary.json",
            "console_read_model/generated/cieu_boundary_summary.json",
            "console_read_model/generated/autonomy_inventory_summary.json",
            "console_read_model/generated/autonomous_cycle_summary.json",
            "console_read_model/generated/legacy_triage_summary.json",
            "console_read_model/generated/observation_loop_summary.json",
            "console_read_model/generated/readonly_tool_summary.json",
            "console_read_model/generated/tool_bridge_summary.json",
            "console_read_model/generated/work_proposal_summary.json",
            "console_read_model/generated/dashboard_refresh_summary.json",
            "console_read_model/generated/recurring_loop_summary.json",
            "console_read_model/generated/manual_tick_summary.json",
            "console_read_model/generated/field_functional_summary.json",
            "console_read_model/generated/mission_projection_summary.json",
            "console_read_model/generated/field_projection_summary.json",
            "console_read_model/generated/projection_cycle_summary.json",
            "console_read_model/generated/shadow_learning_cycle_summary.json",
            "console_read_model/generated/cross_repo_governance_summary.json",
            "console_read_model/generated/governed_mcp_adapter_summary.json",
            "console_read_model/generated/controlled_canonical_learning_summary.json",
            "console_read_model/generated/approved_sandbox_update_summary.json",
            "console_read_model/generated/real_approval_workflow_summary.json",
            "console_read_model/generated/approval_record_sandbox_summary.json",
            "console_read_model/generated/real_release_preflight_summary.json",
            "console_read_model/generated/real_release_simulation_summary.json",
            "console_read_model/generated/live_boundary_no_go_summary.json",
            "console_read_model/generated/l6_meta_development_summary.json",
            "console_read_model/generated/l6_mvp_artifact_sandbox_summary.json",
            "console_read_model/generated/l6_external_observation_boundary_summary.json",
            "console_read_model/generated/l6_controlled_observation_sandbox_summary.json",
            "console_read_model/generated/l6_real_observation_preflight_summary.json",
            "console_read_model/generated/l6_pilot_design_summary.json",
            "console_read_model/generated/l6_pilot_approval_summary.json",
            "console_read_model/generated/l6_integrated_pilot_readiness_summary.json",
            "console_read_model/generated/l6_agentic_evidence_summary.json",
            "console_read_model/generated/l6_agentic_pilot_dry_run_summary.json",
            "console_read_model/generated/l6_tiny_observation_pilot_summary.json",
            "console_read_model/generated/l6_10r_locator_retry_summary.json",
            "console_read_model/generated/l6_10t_toolmaking_locator_resolver_summary.json",
            "console_read_model/generated/l6_10u_locator_resolver_enablement_summary.json",
            "console_read_model/generated/l6_10v_seed_or_search_resolver_enablement_summary.json",
            "console_read_model/generated/l6_10w_reviewed_seed_locator_injection_summary.json",
            "console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json",
            "console_read_model/generated/generation_manifest.json",
        ],
        "source_files": files_read,
        "unsafe_sources_not_read": [
            "*.db",
            "*.db-wal",
            "*.db-shm",
            "scripts/.logs/*",
            "active-agent markers",
            "daemon pid/state files",
            "__pycache__",
            "raw runtime report directories",
        ],
        "generator_version": GENERATOR_VERSION,
        "validation_recommendation": "Run console_read_model/validation/validate_team_read_model.py after generation.",
        "generated_at_policy": "static_snapshot_no_runtime_clock_required",
    }

    snapshot_md = render_snapshot_markdown(snapshot, readiness_summary)

    write_text(
        "console_read_model/generated/README.md",
        "# Generated Console Snapshots\n\n"
        "These files are derived artifacts from curated read-model inputs only.\n"
        "They do not contain DB contents, raw logs, daemon state, active-agent state,\n"
        "or live runtime observations.\n\n"
        "`quarantine_summary.json` is derived from the runtime artifact quarantine\n"
        "path-only manifest. It summarizes classes/counts only and does not include\n"
        "artifact contents.\n\n"
        "`safe_mining_summary.json` is derived from bounded Markdown report candidate\n"
        "indexes. It summarizes candidate counts/classes only; candidates remain\n"
        "review assets, not brain memory.\n\n"
        "`review_queue_summary.json` is derived from generated review queue files.\n"
        "It summarizes pending review state only; entries are not approved or ingested.\n\n"
        "`artifact_disposition_summary.json` is derived from generated backlog\n"
        "disposition indexes. It summarizes routing/disposition only; it is not ingestion.\n\n"
        "`evidence_review_summary.json` is derived from generated evidence review\n"
        "indexes. It summarizes structural readiness only; it is not approval.\n\n"
        "`governance_bridge_summary.json` is derived from the generated Labs-Gov\n"
        "dry-run decision snapshot. It is not hook execution or CIEU writeback.\n\n"
        "`pre_u_governance_summary.json` is derived from generated multi-role\n"
        "Pre-U dry-run decisions. It is not runtime packet execution.\n\n"
        "`labs_acceptance_summary.json` is derived from the generated labs runtime\n"
        "acceptance report. It is dry-run acceptance only, not runtime execution.\n\n"
        "`cross_repo_alignment_summary.json` is derived from the generated cross-repo\n"
        "alignment manifest. It is dry-run compatibility only, not CI or hook execution.\n\n"
        "`live_readiness_summary.json` is derived from the generated live-readiness\n"
        "report. It identifies blockers and keeps live execution disabled.\n\n"
        "`live_boundary_summary.json` is derived from the generated live-boundary\n"
        "manifest. It confirms boundary definitions remain disabled.\n\n"
        "`cieu_boundary_summary.json` is derived from the generated CIEU runtime\n"
        "boundary manifest. It confirms event fixtures are dry-run only and persistence is disabled.\n\n"
        "`autonomy_inventory_summary.json` is derived from the generated company\n"
        "autonomy inventory. It confirms capability maps and tool candidates exist while live actions remain disabled.\n\n"
        "`autonomous_cycle_summary.json` is derived from the mission-bounded\n"
        "autonomous work cycle simulator. It confirms a full simulated company cycle exists while real actions remain disabled.\n\n"
        "`legacy_triage_summary.json` is derived from generated legacy asset\n"
        "triage outputs. It classifies assets before absorption and enables no actions.\n\n"
        "`observation_loop_summary.json` is derived from generated governed\n"
        "observation loop outputs. It summarizes a read-only tick from safe generated sources.\n\n"
        "`readonly_tool_summary.json` is derived from generated governed read-only\n"
        "observation tool outputs. It confirms the first local read-only wrapper is callable while live action remains disabled.\n\n"
        "`tool_bridge_summary.json` is derived from generated governed tool\n"
        "invocation bridge outputs. It confirms the read-only tool is called only after Pre-U packet, decision, and bridge authorization.\n\n"
        "`work_proposal_summary.json` is derived from generated agent-team work\n"
        "proposal outputs. It confirms mission/observation evidence produced a governed tool request routed through the L4.5 bridge.\n\n"
        "`dashboard_refresh_summary.json` is derived from generated mission dashboard\n"
        "refresh loop outputs. It confirms a manual local refresh loop produced a refreshed dashboard without scheduler or daemon use.\n\n"
        "`recurring_loop_summary.json` is derived from generated recurring observation\n"
        "loop contract outputs. It confirms recurrence is defined but disabled and only one manual local simulated tick exists.\n\n"
        "`manual_tick_summary.json` is derived from generated manual recurring\n"
        "observation tick runner outputs. It confirms one manual local tick ran with a receipt while scheduler, daemon, and recurrence stay disabled.\n\n"
        "`field_functional_summary.json` is derived from generated field\n"
        "functional archaeology outputs. It confirms old field-functional work was searched and mapped into a merge plan without executing old code.\n\n"
        "`mission_projection_summary.json` is derived from the L5.1 mission field\n"
        "projection harness. It confirms layered Y* projection, a Pre-U packet candidate, and a residual fixture exist while action execution remains disabled.\n\n"
        "`field_projection_summary.json` is derived from the L5.2 field functional\n"
        "auto-projection core. It confirms mission-to-behavior Y* projection, a behavior-level Pre-U candidate, and a residual loop fixture exist while behavior execution remains disabled.\n\n"
        "`projection_cycle_summary.json` is derived from the L5.3 projection-checked\n"
        "autonomous work cycle. It confirms behavior-level Y* is consumed as a gate before dry-run work proposal, Pre-U candidate, residual, and review-only learning artifacts.\n\n"
        "`shadow_learning_cycle_summary.json` is derived from the L5.4 integrated\n"
        "review-gated shadow learning cycle. It confirms an L5.3 residual can influence a shadow behavior-level Y* preview and shadow cycle without canonical policy mutation or writeback.\n\n"
        "`cross_repo_governance_summary.json` is derived from the L5.5 cross-repo\n"
        "governance contract proof. It confirms ystar-company remains labs/runtime, Y-star-gov remains the intended governance kernel, and gov-mcp remains a governed interface boundary.\n\n"
        "`governed_mcp_adapter_summary.json` is derived from the L5.6 governed MCP\n"
        "dry-run adapter proof. It confirms a future MCP call candidate is downstream of behavior-level Y*, Pre-U, governance expectation, bridge receipt, CIEU-like receipt, residual delta, and review-only learning gates while real MCP execution remains blocked.\n\n"
        "`controlled_canonical_learning_summary.json` is derived from the L5.7 controlled\n"
        "canonical learning design. It confirms review-only and shadow candidates can become non-applied canonical update package candidates while approval, application, writeback, strategy mutation, and direct Y* mutation remain blocked.\n\n"
        "`approved_sandbox_update_summary.json` is derived from the L5.8 approved\n"
        "canonical update sandbox. It confirms sandbox approval/application, sandbox reprojection, MCP preview, CIEU-like residual, and rollback validation exist while real approval, real canonical mutation, writeback, direct Y* mutation, MCP execution, and live execution remain blocked.\n\n"
        "`real_approval_workflow_summary.json` is derived from the L5.9 real approval\n"
        "workflow boundary. It confirms authority, evidence, durable approval record contract, validity/revocation, snapshot, real application gate, preflight, runbook, and audit fixture exist while real approval, durable approval persistence, and real application remain blocked.\n\n"
        "`approval_record_sandbox_summary.json` is derived from the L5.10 controlled\n"
        "approval record sandbox. It confirms sandbox approval record creation, integrity validation, validity/state replay, invalid-record blocking, gate replay, audit lineage, and CIEU-like residuals while real approval, durable persistence, and real application remain blocked.\n\n"
        "`real_release_preflight_summary.json` is derived from the L5.11 controlled\n"
        "real release preflight. It confirms release candidate assembly, scope validation, approval-record preflight, snapshot/rollback checks, invariants, handoff, blocker decision, and CIEU-like residuals while real release, durable persistence, real approval, and canonical application remain blocked.\n\n"
        "`real_release_simulation_summary.json` is derived from the L5.12 real release\n"
        "simulation sandbox. It confirms sandbox authority, simulated approval record, sandbox snapshot, sandbox release execution, post-release validation, MCP preview, rollback drill, comparison, and CIEU-like residuals while real release, durable persistence, real approval, and canonical application remain blocked.\n\n"
        "`live_boundary_no_go_summary.json` is derived from the L5.13 live boundary\n"
        "no-go framework. It confirms live domains, no-go invariants, L5 evidence, blockers, L6 design-only entry, and system no-go decisions while live, external, revenue, persistence, MCP, release, and writeback execution remain blocked.\n\n"
        "`l6_meta_development_summary.json` is derived from the L6.0 meta-development\n"
        "generative selection engine design. It confirms self-modeling, asset-field, world-value, conversion-operator, hypothesis, conversion-physics, MVP proof, portfolio, and strategic residual artifacts while external, network, publication, payment, and revenue execution remain blocked.\n\n"
        "`l6_mvp_artifact_sandbox_summary.json` is derived from the L6.1 MVP\n"
        "artifact sandbox. It confirms selected internal proof artifacts, review gates,\n"
        "validation criteria, externalization blockers, and residual artifacts while publication, outreach, payment, network, revenue, MCP, canonical mutation, and writeback remain blocked.\n\n"
        "`l6_external_observation_boundary_summary.json` is derived from the L6.2\n"
        "governed external observation boundary. It confirms Pre-Observation packet,\n"
        "source registry, permission gate, manual import, no-action receipt, and\n"
        "readiness artifacts while real external observation, URL fetch, scraping,\n"
        "publication, outreach, payment, revenue, MCP, live behavior, canonical\n"
        "mutation, writeback, and direct Y* mutation remain blocked.\n\n"
        "`l6_controlled_observation_sandbox_summary.json` is derived from the L6.3\n"
        "controlled external observation sandbox. It confirms selected observation\n"
        "cases, pre-observation packets, permission replay, static/manual fixtures,\n"
        "structural validation, claim/freshness assessment, review packets,\n"
        "refinement candidates, no-action receipts, and readiness artifacts while\n"
        "real external observation, URL fetch, scraping, API calls, browser fetch,\n"
        "publication, outreach, payment, revenue, MCP, live behavior, canonical\n"
        "mutation, writeback, and direct Y* mutation remain blocked.\n\n"
        "`l6_real_observation_preflight_summary.json` is derived from the L6.4\n"
        "real read-only external observation preflight. It confirms future\n"
        "read-only observation candidates, preflight contracts, source policies,\n"
        "approval packet schemas, operator handoff, network isolation requirements,\n"
        "evidence capture requirements, no-action guarantees, blocked decisions,\n"
        "and readiness artifacts while real observation, URL fetch, scraping, API\n"
        "calls, browser fetch, publication, outreach, payment, revenue, MCP, live\n"
        "behavior, CIEU DB writes, canonical mutation, writeback, and direct Y*\n"
        "mutation remain blocked.\n\n"
        "`l6_pilot_design_summary.json` is derived from the L6.5 controlled real\n"
        "read-only observation pilot design. It confirms pilot candidates, scope,\n"
        "source constraints, approval packet candidates, operator runbook,\n"
        "evidence templates, review workflow, abort/quarantine policy, no-action\n"
        "guarantees, blocked pilot execution decisions, and readiness artifacts\n"
        "while real observation, URL fetch, search, scraping, API calls, browser\n"
        "fetch, publication, outreach, payment, revenue, MCP, live behavior, CIEU\n"
        "DB writes, canonical mutation, writeback, and direct Y* mutation remain\n"
        "blocked.\n\n"
        "`l6_pilot_approval_summary.json` is derived from the L6.6 controlled\n"
        "observation pilot approval packet. It confirms approval candidates,\n"
        "authority constraints, approval packet instances, evidence dossiers,\n"
        "risk reviews, operator/runtime/evidence prerequisites, no-action\n"
        "constraints, blocked approval decisions, non-persistence receipts, and\n"
        "readiness artifacts while real approval, durable approval persistence,\n"
        "real observation, URL fetch, search, scraping, API calls, browser fetch,\n"
        "publication, outreach, payment, revenue, MCP, live behavior, CIEU DB\n"
        "writes, canonical mutation, writeback, and direct Y* mutation remain\n"
        "blocked.\n\n"
        "`l6_integrated_pilot_readiness_summary.json` is derived from the L6.7\n"
        "integrated approval record and pilot run readiness sandbox. It confirms\n"
        "sandbox approval records, lifecycle replay, pilot run packages, operator\n"
        "readiness, runtime isolation readiness, evidence capture readiness,\n"
        "post-observation review readiness, manual evidence import readiness,\n"
        "integrated decisions, no-action receipts, and readiness artifacts while\n"
        "real approval, durable approval persistence, real observation, URL fetch,\n"
        "search, scraping, API calls, browser fetch, publication, outreach,\n"
        "payment, revenue, MCP, live behavior, CIEU DB writes, canonical mutation,\n"
        "writeback, and direct Y* mutation remain blocked.\n\n"
        "`l6_agentic_evidence_summary.json` is derived from the L6.8 agentic\n"
        "external evidence discovery and trust judgment engine. It confirms\n"
        "autonomous evidence need inference, source hypothesis generation,\n"
        "source value modeling, structural trust judgment, value-of-information\n"
        "ranking, conflict/corroboration planning, rejection filtering, future\n"
        "observation work orders, no-action receipts, and readiness artifacts while\n"
        "agent fetch, URL open, network, search, scraping, API calls, browser fetch,\n"
        "publication, outreach, payment, revenue, MCP, live behavior, CIEU DB\n"
        "writes, canonical mutation, writeback, and direct Y* mutation remain\n"
        "blocked.\n\n"
        "`l6_agentic_pilot_dry_run_summary.json` is derived from the L6.9\n"
        "controlled read-only agentic evidence pilot approval and dry-run pack.\n"
        "It confirms work-order selection, approval eligibility, sandbox\n"
        "approval packets, sandbox approval records, runtime readiness, dry-run\n"
        "traces, empty evidence capture, post-run review, residual candidates,\n"
        "real-execution blockers, no-action receipts, and readiness artifacts\n"
        "while real approval, durable approval persistence, real observation,\n"
        "URL fetch/open, search, scraping, API calls, browser fetch, publication,\n"
        "outreach, payment, revenue, MCP, live behavior, CIEU DB writes,\n"
        "canonical mutation, writeback, and direct Y* mutation remain blocked.\n\n"
        "`l6_tiny_observation_pilot_summary.json` is derived from the L6.10\n"
        "tiny real read-only agentic evidence observation pilot. It confirms one\n"
        "selected L6.9 work order, hard runtime limits, locator resolution,\n"
        "observation trace, evidence packet, structural validation, claim/freshness\n"
        "assessment, post-observation review, review-only refinement candidate,\n"
        "abort/quarantine decision, no-action receipts, and readiness artifacts.\n"
        "This run correctly records a blocked pilot because no concrete locator was\n"
        "available and no controlled network/tooling condition was present.\n\n"
        "`l6_10r_locator_retry_summary.json` is derived from the L6.10R\n"
        "controlled source locator resolution and tiny observation retry pack.\n"
        "It confirms one selected work order, one-query locator budget, unresolved\n"
        "locator trace, eligibility block, blocked observation retry, empty evidence\n"
        "packet, post-observation review, review-only refinement candidate,\n"
        "no-action receipts, and readiness artifacts without broad search, crawling,\n"
        "scraping, browser automation, publication, outreach, payment, revenue,\n"
        "MCP, live behavior, CIEU DB writes, canonical mutation, writeback, or\n"
        "direct Y* mutation.\n\n"
        "`l6_10t_toolmaking_locator_resolver_summary.json` is derived from the L6.10T\n"
        "governed capability-gap toolmaking and locator resolver adapter pack.\n"
        "It confirms the L6.10/L6.10R blocker is classified as a tool capability\n"
        "gap, defines a reusable governed self-tooling lifecycle, creates a portable\n"
        "disabled no-network locator resolver interface, and records the remaining\n"
        "controlled resolver gap without granting live tool authority or fabricating\n"
        "a locator.\n\n"
        "`l6_10u_locator_resolver_enablement_summary.json` is derived from the L6.10U\n"
        "controlled locator resolver enablement and first attempt pack. It confirms\n"
        "a portable resolver runtime, seed-registry resolver, environment-gated\n"
        "search resolver, and disabled fallback exist; the default run performs one\n"
        "local seed-registry lookup, does not run search, does not use network, and\n"
        "does not fabricate a locator.\n\n"
        "`l6_10v_seed_or_search_resolver_enablement_summary.json` is derived from\n"
        "the L6.10V controlled seed locator or explicit search resolver enablement\n"
        "pack. It confirms the reviewed seed registry path and explicit opt-in\n"
        "controlled search path are present, while the default run performs one\n"
        "local seed lookup, keeps search disabled, uses no network, and invents no\n"
        "locator.\n\n"
        "`l6_10w_reviewed_seed_locator_injection_summary.json` is derived from\n"
        "the L6.10W reviewed seed locator injection and tiny retry pack. It confirms\n"
        "the system scanned local seed registries, did not invent a URL, and when no\n"
        "reviewed locator exists generated a precise USER_ACTION_REQUIRED packet\n"
        "asking for exactly one public URL tied to the selected work order.\n\n"
        "`l6_10x_budgeted_controlled_search_evidence_summary.json` is derived from\n"
        "the L6.10X budgeted controlled external search evidence pilot. It confirms\n"
        "budgeted query planning, controlled backend gating, bounded crawl policy,\n"
        "source quality assessment, blocked evidence extraction, corroboration,\n"
        "review/refinement candidates, and no-action receipts while the default path\n"
        "uses no search/network/page reads and avoids manual URL requests.\n\n"
        "`console_read_model/cli/team_console.py` consumes these generated files as its\n"
        "only data source.\n",
        generated_files,
    )
    write_json("console_read_model/generated/team_console_snapshot.json", snapshot, generated_files)
    write_text("console_read_model/generated/team_console_snapshot.md", snapshot_md, generated_files)
    write_json("console_read_model/generated/agent_cards_compiled.json", compiled_cards, generated_files)
    write_json("console_read_model/generated/readiness_summary.json", readiness_summary, generated_files)
    write_json("console_read_model/generated/quarantine_summary.json", quarantine_summary, generated_files)
    write_json("console_read_model/generated/safe_mining_summary.json", safe_mining_summary, generated_files)
    write_json("console_read_model/generated/review_queue_summary.json", review_queue_summary, generated_files)
    write_json("console_read_model/generated/artifact_disposition_summary.json", disposition_summary, generated_files)
    write_json("console_read_model/generated/evidence_review_summary.json", evidence_review_summary, generated_files)
    write_json("console_read_model/generated/governance_bridge_summary.json", governance_bridge_summary, generated_files)
    write_json("console_read_model/generated/pre_u_governance_summary.json", pre_u_governance_summary, generated_files)
    write_json("console_read_model/generated/labs_acceptance_summary.json", labs_acceptance_summary, generated_files)
    write_json("console_read_model/generated/cross_repo_alignment_summary.json", cross_repo_alignment_summary, generated_files)
    write_json("console_read_model/generated/live_readiness_summary.json", live_readiness_summary, generated_files)
    write_json("console_read_model/generated/live_boundary_summary.json", live_boundary_summary, generated_files)
    write_json("console_read_model/generated/cieu_boundary_summary.json", cieu_boundary_summary, generated_files)
    write_json("console_read_model/generated/autonomy_inventory_summary.json", autonomy_inventory_summary, generated_files)
    write_json("console_read_model/generated/autonomous_cycle_summary.json", autonomous_cycle_summary, generated_files)
    write_json("console_read_model/generated/legacy_triage_summary.json", legacy_triage_summary, generated_files)
    write_json("console_read_model/generated/observation_loop_summary.json", observation_loop_summary, generated_files)
    write_json("console_read_model/generated/readonly_tool_summary.json", readonly_tool_summary, generated_files)
    write_json("console_read_model/generated/tool_bridge_summary.json", tool_bridge_summary, generated_files)
    write_json("console_read_model/generated/work_proposal_summary.json", work_proposal_summary, generated_files)
    write_json("console_read_model/generated/dashboard_refresh_summary.json", dashboard_refresh_summary, generated_files)
    write_json("console_read_model/generated/recurring_loop_summary.json", recurring_loop_summary, generated_files)
    write_json("console_read_model/generated/manual_tick_summary.json", manual_tick_summary, generated_files)
    write_json("console_read_model/generated/field_functional_summary.json", field_functional_summary, generated_files)
    write_json("console_read_model/generated/mission_projection_summary.json", mission_projection_summary, generated_files)
    write_json("console_read_model/generated/field_projection_summary.json", field_projection_summary, generated_files)
    write_json("console_read_model/generated/projection_cycle_summary.json", projection_cycle_summary, generated_files)
    write_json("console_read_model/generated/shadow_learning_cycle_summary.json", shadow_learning_cycle_summary, generated_files)
    write_json("console_read_model/generated/cross_repo_governance_summary.json", cross_repo_governance_summary, generated_files)
    write_json("console_read_model/generated/governed_mcp_adapter_summary.json", governed_mcp_adapter_summary, generated_files)
    write_json("console_read_model/generated/controlled_canonical_learning_summary.json", controlled_canonical_learning_summary, generated_files)
    write_json("console_read_model/generated/approved_sandbox_update_summary.json", approved_sandbox_update_summary, generated_files)
    write_json("console_read_model/generated/real_approval_workflow_summary.json", real_approval_workflow_summary, generated_files)
    write_json("console_read_model/generated/approval_record_sandbox_summary.json", controlled_approval_record_summary, generated_files)
    write_json("console_read_model/generated/real_release_preflight_summary.json", controlled_real_release_preflight_summary, generated_files)
    write_json("console_read_model/generated/real_release_simulation_summary.json", real_release_simulation_summary, generated_files)
    write_json("console_read_model/generated/live_boundary_no_go_summary.json", live_boundary_no_go_summary, generated_files)
    write_json("console_read_model/generated/l6_meta_development_summary.json", l6_meta_development_summary, generated_files)
    write_json("console_read_model/generated/l6_mvp_artifact_sandbox_summary.json", l6_mvp_artifact_sandbox_summary, generated_files)
    write_json("console_read_model/generated/l6_external_observation_boundary_summary.json", l6_external_observation_boundary_summary, generated_files)
    write_json("console_read_model/generated/l6_controlled_observation_sandbox_summary.json", l6_controlled_observation_sandbox_summary, generated_files)
    write_json("console_read_model/generated/l6_real_observation_preflight_summary.json", l6_real_observation_preflight_summary, generated_files)
    write_json("console_read_model/generated/l6_pilot_design_summary.json", l6_pilot_design_summary, generated_files)
    write_json("console_read_model/generated/l6_pilot_approval_summary.json", l6_pilot_approval_summary, generated_files)
    write_json("console_read_model/generated/l6_integrated_pilot_readiness_summary.json", l6_integrated_pilot_readiness_summary, generated_files)
    write_json("console_read_model/generated/l6_agentic_evidence_summary.json", l6_agentic_evidence_summary, generated_files)
    write_json("console_read_model/generated/l6_agentic_pilot_dry_run_summary.json", l6_agentic_pilot_dry_run_summary, generated_files)
    write_json("console_read_model/generated/l6_tiny_observation_pilot_summary.json", l6_tiny_observation_pilot_summary, generated_files)
    write_json("console_read_model/generated/l6_10r_locator_retry_summary.json", l6_10r_locator_retry_summary, generated_files)
    write_json("console_read_model/generated/l6_10t_toolmaking_locator_resolver_summary.json", l6_10t_toolmaking_locator_resolver_summary, generated_files)
    write_json("console_read_model/generated/l6_10u_locator_resolver_enablement_summary.json", l6_10u_locator_resolver_enablement_summary, generated_files)
    write_json("console_read_model/generated/l6_10v_seed_or_search_resolver_enablement_summary.json", l6_10v_seed_or_search_resolver_enablement_summary, generated_files)
    write_json("console_read_model/generated/l6_10w_reviewed_seed_locator_injection_summary.json", l6_10w_reviewed_seed_locator_injection_summary, generated_files)
    write_json("console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json", l6_10x_budgeted_controlled_search_summary, generated_files)
    write_json("console_read_model/generated/generation_manifest.json", manifest, generated_files)

    return files_read, generated_files, [agent["agent_id"] for agent in agents], warnings


def render_snapshot_markdown(snapshot: dict[str, Any], readiness: dict[str, Any]) -> str:
    lines = [
        "# Team Brain Console Snapshot",
        "",
        "This snapshot is generated from curated read-model files only.",
        "",
        "## Agents",
        "",
    ]
    for agent in snapshot["agents"]:
        lines.extend(
            [
                f"### {agent['agent_id']}",
                "",
                f"- Name: {agent['canonical_name']}",
                f"- Role type: {agent['role_type']}",
                f"- Readiness: {agent['readiness_level']}",
                f"- Focus: {agent['focus']}",
                f"- Pre-U packet: {agent['has_pre_u_packet']}",
                f"- Execution channels: {agent['has_execution_channels']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Capability Matrix Summary",
            "",
            "See `capability_matrix.json` and generated snapshot JSON for the full matrix.",
            "",
            "## Readiness Summary",
            "",
            "Ready now:",
        ]
    )
    lines.extend([f"- {item}" for item in readiness["ready_now"]])
    lines.extend(["", "Not ready:"])
    lines.extend([f"- {item}" for item in readiness["not_ready"]])
    quarantine = snapshot.get("quarantine_summary", {})
    safe_mining = snapshot.get("safe_mining_summary", {})
    review_queue = snapshot.get("review_queue_summary", {})
    disposition = snapshot.get("artifact_disposition_summary", {})
    evidence_review = snapshot.get("evidence_review_summary", {})
    governance_bridge = snapshot.get("governance_bridge_summary", {})
    pre_u_governance = snapshot.get("pre_u_governance_summary", {})
    labs_acceptance = snapshot.get("labs_acceptance_summary", {})
    cross_repo = snapshot.get("cross_repo_alignment_summary", {})
    live_readiness = snapshot.get("live_readiness_summary", {})
    live_boundary = snapshot.get("live_boundary_summary", {})
    cieu_boundary = snapshot.get("cieu_boundary_summary", {})
    autonomy_inventory = snapshot.get("autonomy_inventory_summary", {})
    autonomous_cycle = snapshot.get("autonomous_cycle_summary", {})
    legacy_triage = snapshot.get("legacy_triage_summary", {})
    observation_loop = snapshot.get("observation_loop_summary", {})
    readonly_tool = snapshot.get("readonly_tool_summary", {})
    tool_bridge = snapshot.get("tool_bridge_summary", {})
    work_proposal = snapshot.get("work_proposal_summary", {})
    dashboard_refresh = snapshot.get("dashboard_refresh_summary", {})
    recurring_loop = snapshot.get("recurring_loop_summary", {})
    manual_tick = snapshot.get("manual_tick_summary", {})
    field_functional = snapshot.get("field_functional_summary", {})
    mission_projection = snapshot.get("mission_projection_summary", {})
    field_projection = snapshot.get("field_projection_summary", {})
    projection_cycle = snapshot.get("projection_cycle_summary", {})
    shadow_learning_cycle = snapshot.get("shadow_learning_cycle_summary", {})
    cross_repo_governance = snapshot.get("cross_repo_governance_summary", {})
    governed_mcp_adapter = snapshot.get("governed_mcp_adapter_summary", {})
    controlled_canonical_learning = snapshot.get("controlled_canonical_learning_summary", {})
    approved_sandbox_update = snapshot.get("approved_sandbox_update_summary", {})
    real_approval_workflow = snapshot.get("real_approval_workflow_summary", {})
    controlled_approval_record = snapshot.get("controlled_approval_record_summary", {})
    controlled_real_release_preflight = snapshot.get("controlled_real_release_preflight_summary", {})
    real_release_simulation = snapshot.get("real_release_simulation_summary", {})
    live_boundary_no_go = snapshot.get("live_boundary_no_go_summary", {})
    l6_meta_development = snapshot.get("l6_meta_development_summary", {})
    l6_mvp_artifact_sandbox = snapshot.get("l6_mvp_artifact_sandbox_summary", {})
    l6_external_observation_boundary = snapshot.get(
        "l6_external_observation_boundary_summary", {}
    )
    l6_controlled_observation_sandbox = snapshot.get(
        "l6_controlled_observation_sandbox_summary", {}
    )
    l6_real_observation_preflight = snapshot.get(
        "l6_real_observation_preflight_summary", {}
    )
    l6_pilot_design = snapshot.get("l6_pilot_design_summary", {})
    l6_pilot_approval = snapshot.get("l6_pilot_approval_summary", {})
    l6_integrated_pilot_readiness = snapshot.get(
        "l6_integrated_pilot_readiness_summary", {}
    )
    l6_agentic_evidence = snapshot.get("l6_agentic_evidence_summary", {})
    l6_agentic_pilot_dry_run = snapshot.get("l6_agentic_pilot_dry_run_summary", {})
    l6_tiny_observation_pilot = snapshot.get("l6_tiny_observation_pilot_summary", {})
    l6_10r_locator_retry = snapshot.get("l6_10r_locator_retry_summary", {})
    l6_10t_toolmaking_locator_resolver = snapshot.get(
        "l6_10t_toolmaking_locator_resolver_summary", {}
    )
    l6_10u_locator_resolver_enablement = snapshot.get(
        "l6_10u_locator_resolver_enablement_summary", {}
    )
    l6_10v_seed_or_search_resolver_enablement = snapshot.get(
        "l6_10v_seed_or_search_resolver_enablement_summary", {}
    )
    l6_10w_reviewed_seed_locator_injection = snapshot.get(
        "l6_10w_reviewed_seed_locator_injection_summary", {}
    )
    l6_10x_budgeted_controlled_search = snapshot.get(
        "l6_10x_budgeted_controlled_search_evidence_summary", {}
    )
    lines.extend(
        [
            "",
            "## Runtime Artifact Quarantine Summary",
            "",
            f"- Framework status: {quarantine.get('framework_status')}",
            f"- Current mining level: {quarantine.get('current_mining_level')}",
            f"- Artifacts classified: {quarantine.get('artifacts_classified')}",
            f"- Unsafe artifacts count: {quarantine.get('unsafe_artifacts_count')}",
            "- Classes seen:",
        ]
    )
    for class_name, count in sorted(quarantine.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(
        [
            f"- Generated manifest ref: {quarantine.get('generated_manifest_ref')}",
            f"- Warning: {quarantine.get('safety_warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Runtime Artifact Safe Mining Candidates",
            "",
            f"- Candidate count: {safe_mining.get('candidate_count')}",
            f"- Safety level: {safe_mining.get('safety_level')}",
            f"- Ingestion status: {safe_mining.get('ingestion_status')}",
            f"- Generated candidate index: {safe_mining.get('generated_candidate_index')}",
            "- Classes seen:",
        ]
    )
    for class_name, count in sorted(safe_mining.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(
        [
            f"- Warning: {safe_mining.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Runtime Artifact Candidate Review Queue",
            "",
            f"- Review count: {review_queue.get('review_count')}",
            f"- Default review status: {review_queue.get('default_review_status')}",
            f"- Default ingestion status: {review_queue.get('default_ingestion_status')}",
            f"- Generated queue path: {review_queue.get('generated_queue_path')}",
            "- Statuses:",
        ]
    )
    for status, count in sorted(review_queue.get("statuses", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append("- Intended use summary:")
    for use, count in sorted(review_queue.get("intended_use_summary", {}).items()):
        lines.append(f"  - {use}: {count}")
    lines.append(f"- Warning: {review_queue.get('warning')}")
    lines.extend(
        [
            "",
            "## Runtime Artifact Backlog Disposition",
            "",
            f"- Total artifacts: {disposition.get('total_artifacts')}",
            f"- Artifacts with disposition: {disposition.get('artifacts_with_disposition')}",
            f"- Safe-mined to review queue: {disposition.get('safe_mined_to_review_queue')}",
            f"- Forbidden direct read count: {disposition.get('forbidden_direct_read_count')}",
            f"- Generated disposition index: {disposition.get('generated_disposition_index')}",
            "- Dispositions:",
        ]
    )
    for disposition_name, count in sorted(disposition.get("dispositions", {}).items()):
        lines.append(f"  - {disposition_name}: {count}")
    lines.append("- Evidence scoring status:")
    for status, count in sorted(disposition.get("evidence_scoring_status", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append(f"- Warning: {disposition.get('warning')}")
    lines.extend(
        [
            "",
            "## Runtime Artifact Evidence Review",
            "",
            f"- Candidates scored: {evidence_review.get('candidates_scored')}",
            f"- Decision stubs created: {evidence_review.get('decision_stubs_created')}",
            f"- Routes created: {evidence_review.get('routes_created')}",
            f"- Automatic approvals: {evidence_review.get('automatic_approvals')}",
            "- Reuse readiness:",
        ]
    )
    for readiness_name, count in sorted(evidence_review.get("reuse_readiness", {}).items()):
        lines.append(f"  - {readiness_name}: {count}")
    lines.append("- Route counts:")
    for route, count in sorted(evidence_review.get("route_counts", {}).items()):
        lines.append(f"  - {route}: {count}")
    lines.append("- Semantic truth status:")
    for status, count in sorted(evidence_review.get("semantic_truth_status", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append(f"- Warning: {evidence_review.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs-Gov Alignment Bridge",
            "",
            f"- Bridge run id: {governance_bridge.get('latest_bridge_run_id')}",
            f"- Source task id: {governance_bridge.get('source_task_id')}",
            f"- Agent id: {governance_bridge.get('agent_id')}",
            f"- Y-star-gov decision: {governance_bridge.get('ystar_gov_decision')}",
            f"- Y-star-gov exit code: {governance_bridge.get('ystar_gov_exit_code')}",
            f"- allow_execution: {governance_bridge.get('allow_execution')}",
            f"- require_revision: {governance_bridge.get('require_revision')}",
            f"- deny: {governance_bridge.get('deny')}",
            f"- escalate: {governance_bridge.get('escalate')}",
            f"- dry_run_only: {governance_bridge.get('dry_run_only')}",
            f"- action_executed: {governance_bridge.get('action_executed')}",
            f"- cieu_written: {governance_bridge.get('cieu_written')}",
            f"- brain_writeback_performed: {governance_bridge.get('brain_writeback_performed')}",
            f"- Warning: {governance_bridge.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Labs Pre-U Governance Dry Run",
            "",
            f"- Packets generated: {pre_u_governance.get('packets_generated')}",
            f"- Roles covered: {', '.join(pre_u_governance.get('roles_covered', []))}",
            "- Decision counts:",
        ]
    )
    for decision, count in sorted(pre_u_governance.get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.append("- Decisions by role:")
    for agent_id, decision in sorted(pre_u_governance.get("decisions_by_role", {}).items()):
        lines.append(f"  - {agent_id}: {decision.get('decision')} (exit {decision.get('exit_code')})")
    lines.extend(
        [
            f"- dry_run_only: {pre_u_governance.get('dry_run_only')}",
            f"- action_executed: {pre_u_governance.get('action_executed')}",
            f"- cieu_written: {pre_u_governance.get('cieu_written')}",
            f"- brain_writeback_performed: {pre_u_governance.get('brain_writeback_performed')}",
            f"- Warning: {pre_u_governance.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Labs Runtime Governance Acceptance",
            "",
            f"- accepted: {labs_acceptance.get('accepted')}",
            f"- checks_passed: {labs_acceptance.get('checks_passed')}",
            f"- checks_total: {labs_acceptance.get('checks_total')}",
            f"- roles_covered: {', '.join(labs_acceptance.get('roles_covered', []))}",
            "- decision_counts:",
        ]
    )
    for decision, count in sorted(labs_acceptance.get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.extend(
        [
            f"- action_executed: {labs_acceptance.get('action_executed')}",
            f"- cieu_written: {labs_acceptance.get('cieu_written')}",
            f"- brain_writeback_performed: {labs_acceptance.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {labs_acceptance.get('memory_ingestion_performed')}",
            f"- raw_runtime_artifacts_ingested: {labs_acceptance.get('raw_runtime_artifacts_ingested')}",
            f"- Warning: {labs_acceptance.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Cross-Repo Governance Alignment",
            "",
            f"- alignment_accepted: {cross_repo.get('alignment_accepted')}",
            f"- ystar-company HEAD: {cross_repo.get('ystar_company_head_summary')}",
            f"- Y-star-gov HEAD: {cross_repo.get('ystar_gov_head_summary')}",
            f"- Y-star-gov endpoint accepted: {cross_repo.get('ystar_gov_endpoint_accepted')}",
            f"- labs runtime accepted: {cross_repo.get('labs_runtime_accepted')}",
            f"- roles_covered: {', '.join(cross_repo.get('roles_covered', []))}",
            "- decision_counts:",
        ]
    )
    for decision, count in sorted(cross_repo.get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.append("- safety_assertions:")
    for key, value in sorted(cross_repo.get("safety_assertions", {}).items()):
        lines.append(f"  - {key}: {value}")
    lines.append(f"- Warning: {cross_repo.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs Live Readiness",
            "",
            f"- dry_run_governance_ready: {live_readiness.get('dry_run_governance_ready')}",
            f"- minimal_live_loop_ready: {live_readiness.get('minimal_live_loop_ready')}",
            f"- minimal_live_loop_status: {live_readiness.get('minimal_live_loop_status')}",
            f"- recommended_next_phase: {live_readiness.get('recommended_next_phase')}",
            f"- live_action_execution_allowed: {live_readiness.get('live_action_execution_allowed')}",
            f"- live_cieu_write_allowed: {live_readiness.get('live_cieu_write_allowed')}",
            f"- live_brain_writeback_allowed: {live_readiness.get('live_brain_writeback_allowed')}",
            f"- live_memory_ingestion_allowed: {live_readiness.get('live_memory_ingestion_allowed')}",
            f"- transition_backlog_items: {live_readiness.get('transition_backlog_items')}",
            "- blockers:",
        ]
    )
    for blocker in live_readiness.get("blockers", []):
        lines.append(f"  - {blocker}")
    lines.append(f"- Warning: {live_readiness.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs Live Boundary",
            "",
            f"- live_boundary_defined: {live_boundary.get('live_boundary_defined')}",
            f"- operator_approval_gate_defined: {live_boundary.get('operator_approval_gate_defined')}",
            f"- action_sandbox_contract_defined: {live_boundary.get('action_sandbox_contract_defined')}",
            f"- rollback_policy_defined: {live_boundary.get('rollback_policy_defined')}",
            f"- cieu_writer_boundary_defined: {live_boundary.get('cieu_writer_boundary_defined')}",
            f"- live_action_execution_enabled: {live_boundary.get('live_action_execution_enabled')}",
            f"- cieu_write_enabled: {live_boundary.get('cieu_write_enabled')}",
            f"- brain_writeback_enabled: {live_boundary.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {live_boundary.get('memory_ingestion_enabled')}",
            f"- minimal_live_loop_ready: {live_boundary.get('minimal_live_loop_ready')}",
            f"- requires_manual_enablement: {live_boundary.get('requires_manual_enablement')}",
            f"- blocked_reason: {live_boundary.get('blocked_reason')}",
            "- checklist_status_counts:",
        ]
    )
    for status, count in sorted(live_boundary.get("checklist_status_counts", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append(f"- Warning: {live_boundary.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs CIEU Runtime Boundary",
            "",
            f"- cieu_runtime_boundary_defined: {cieu_boundary.get('cieu_runtime_boundary_defined')}",
            f"- cieu_runtime_event_schema_defined: {cieu_boundary.get('cieu_runtime_event_schema_defined')}",
            f"- prediction_delta_fixture_defined: {cieu_boundary.get('prediction_delta_fixture_defined')}",
            f"- cieu_writer_policy_defined: {cieu_boundary.get('cieu_writer_policy_defined')}",
            f"- dry_run_only: {cieu_boundary.get('dry_run_only')}",
            f"- persistence_enabled: {cieu_boundary.get('persistence_enabled')}",
            f"- live_action_execution_enabled: {cieu_boundary.get('live_action_execution_enabled')}",
            f"- cieu_write_enabled: {cieu_boundary.get('cieu_write_enabled')}",
            f"- brain_writeback_enabled: {cieu_boundary.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {cieu_boundary.get('memory_ingestion_enabled')}",
            f"- minimal_live_loop_ready: {cieu_boundary.get('minimal_live_loop_ready')}",
            f"- requires_manual_enablement: {cieu_boundary.get('requires_manual_enablement')}",
            f"- blocked_reason: {cieu_boundary.get('blocked_reason')}",
            f"- generated_sample_event: {cieu_boundary.get('generated_sample_event')}",
            f"- generated_prediction_delta_fixture: {cieu_boundary.get('generated_prediction_delta_fixture')}",
            f"- Warning: {cieu_boundary.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Company Autonomy Inventory",
            "",
            f"- repo_archaeology_completed: {autonomy_inventory.get('repo_archaeology_completed')}",
            f"- observation_capability_map_defined: {autonomy_inventory.get('observation_capability_map_defined')}",
            f"- resource_sensing_map_defined: {autonomy_inventory.get('resource_sensing_map_defined')}",
            f"- action_capability_map_defined: {autonomy_inventory.get('action_capability_map_defined')}",
            f"- governed_tool_registry_candidates_defined: {autonomy_inventory.get('governed_tool_registry_candidates_defined')}",
            f"- agent_role_capability_matrix_defined: {autonomy_inventory.get('agent_role_capability_matrix_defined')}",
            f"- commercial_agent_company_goal_aligned: {autonomy_inventory.get('commercial_agent_company_goal_aligned')}",
            f"- governance_only_runtime: {autonomy_inventory.get('governance_only_runtime')}",
            f"- live_actions_enabled: {autonomy_inventory.get('live_actions_enabled')}",
            f"- external_actions_enabled: {autonomy_inventory.get('external_actions_enabled')}",
            f"- brain_writeback_enabled: {autonomy_inventory.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {autonomy_inventory.get('memory_ingestion_enabled')}",
            f"- cieu_persistence_enabled: {autonomy_inventory.get('cieu_persistence_enabled')}",
            f"- next_required_milestone: {autonomy_inventory.get('next_required_milestone')}",
            f"- Warning: {autonomy_inventory.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Company Autonomous Work Cycle",
            "",
            f"- mission_bounded_autonomy_defined: {autonomous_cycle.get('mission_bounded_autonomy_defined')}",
            f"- founder_sets_mission_agent_team_drives: {autonomous_cycle.get('founder_sets_mission_agent_team_drives')}",
            f"- step_by_step_human_prompting_required: {autonomous_cycle.get('step_by_step_human_prompting_required')}",
            f"- observation_snapshot_defined: {autonomous_cycle.get('observation_snapshot_defined')}",
            f"- autonomous_work_backlog_defined: {autonomous_cycle.get('autonomous_work_backlog_defined')}",
            f"- selected_work_item_defined: {autonomous_cycle.get('selected_work_item_defined')}",
            f"- role_delegation_defined: {autonomous_cycle.get('role_delegation_defined')}",
            f"- governed_tool_selection_defined: {autonomous_cycle.get('governed_tool_selection_defined')}",
            f"- pre_u_packet_simulated: {autonomous_cycle.get('pre_u_packet_simulated')}",
            f"- governance_decision_simulated: {autonomous_cycle.get('governance_decision_simulated')}",
            f"- action_plan_simulated: {autonomous_cycle.get('action_plan_simulated')}",
            f"- cieu_event_simulated: {autonomous_cycle.get('cieu_event_simulated')}",
            f"- residual_delta_simulated: {autonomous_cycle.get('residual_delta_simulated')}",
            f"- real_action_executed: {autonomous_cycle.get('real_action_executed')}",
            f"- external_action_executed: {autonomous_cycle.get('external_action_executed')}",
            f"- live_action_enabled: {autonomous_cycle.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {autonomous_cycle.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {autonomous_cycle.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {autonomous_cycle.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {autonomous_cycle.get('next_required_milestone')}",
            f"- Warning: {autonomous_cycle.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Legacy Asset Triage",
            "",
            f"- assets_scored: {legacy_triage.get('assets_scored')}",
            f"- absorption_buckets_defined: {legacy_triage.get('absorption_buckets_defined')}",
            f"- top_absorption_candidates_defined: {legacy_triage.get('top_absorption_candidates_defined')}",
            f"- governed_absorption_backlog_defined: {legacy_triage.get('governed_absorption_backlog_defined')}",
            f"- blind_absorption_allowed: {legacy_triage.get('blind_absorption_allowed')}",
            f"- blanket_rewrite_allowed: {legacy_triage.get('blanket_rewrite_allowed')}",
            f"- live_actions_enabled: {legacy_triage.get('live_actions_enabled')}",
            f"- next_required_milestone: {legacy_triage.get('next_required_milestone')}",
            "- bucket_counts:",
        ]
    )
    for bucket, count in sorted(legacy_triage.get("bucket_counts", {}).items()):
        lines.append(f"  - {bucket}: {count}")
    lines.append(f"- Warning: {legacy_triage.get('warning')}")
    lines.extend(
        [
            "",
            "## Governed Observation Loop",
            "",
            f"- read_only_observation_loop_defined: {observation_loop.get('read_only_observation_loop_defined')}",
            f"- observation_source_registry_defined: {observation_loop.get('observation_source_registry_defined')}",
            f"- observation_tick_generated: {observation_loop.get('observation_tick_generated')}",
            f"- mission_dashboard_snapshot_defined: {observation_loop.get('mission_dashboard_snapshot_defined')}",
            f"- company_state_digest_defined: {observation_loop.get('company_state_digest_defined')}",
            f"- observation_to_work_item_candidates_defined: {observation_loop.get('observation_to_work_item_candidates_defined')}",
            f"- mission_bounded_autonomy_supported: {observation_loop.get('mission_bounded_autonomy_supported')}",
            f"- step_by_step_human_prompting_reduced: {observation_loop.get('step_by_step_human_prompting_reduced')}",
            f"- real_action_executed: {observation_loop.get('real_action_executed')}",
            f"- external_action_executed: {observation_loop.get('external_action_executed')}",
            f"- live_action_enabled: {observation_loop.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {observation_loop.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {observation_loop.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {observation_loop.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {observation_loop.get('next_required_milestone')}",
            f"- Warning: {observation_loop.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed Read-Only Observation Tool",
            "",
            f"- tool_contract_defined: {readonly_tool.get('tool_contract_defined')}",
            f"- allowed_source_registry_defined: {readonly_tool.get('allowed_source_registry_defined')}",
            f"- sample_invocation_defined: {readonly_tool.get('sample_invocation_defined')}",
            f"- sample_result_defined: {readonly_tool.get('sample_result_defined')}",
            f"- unsafe_invocation_rejected: {readonly_tool.get('unsafe_invocation_rejected')}",
            f"- local_readonly_dry_run_callable: {readonly_tool.get('local_readonly_dry_run_callable')}",
            f"- first_governed_tool_wrapper_created: {readonly_tool.get('first_governed_tool_wrapper_created')}",
            f"- real_action_executed: {readonly_tool.get('real_action_executed')}",
            f"- external_action_executed: {readonly_tool.get('external_action_executed')}",
            f"- live_action_enabled: {readonly_tool.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {readonly_tool.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {readonly_tool.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {readonly_tool.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {readonly_tool.get('next_required_milestone')}",
            f"- Warning: {readonly_tool.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed Tool Invocation Bridge",
            "",
            f"- bridge_contract_defined: {tool_bridge.get('bridge_contract_defined')}",
            f"- agent_tool_request_defined: {tool_bridge.get('agent_tool_request_defined')}",
            f"- pre_u_tool_packet_defined: {tool_bridge.get('pre_u_tool_packet_defined')}",
            f"- governance_decision_defined: {tool_bridge.get('governance_decision_defined')}",
            f"- bridge_authorization_defined: {tool_bridge.get('bridge_authorization_defined')}",
            f"- tool_invoked_through_bridge: {tool_bridge.get('tool_invoked_through_bridge')}",
            f"- direct_tool_invocation_rejected: {tool_bridge.get('direct_tool_invocation_rejected')}",
            f"- unsafe_bridge_request_rejected: {tool_bridge.get('unsafe_bridge_request_rejected')}",
            f"- bridge_cieu_event_defined: {tool_bridge.get('bridge_cieu_event_defined')}",
            f"- bridge_residual_delta_defined: {tool_bridge.get('bridge_residual_delta_defined')}",
            f"- first_governed_tool_invocation_chain_created: {tool_bridge.get('first_governed_tool_invocation_chain_created')}",
            f"- real_action_executed: {tool_bridge.get('real_action_executed')}",
            f"- external_action_executed: {tool_bridge.get('external_action_executed')}",
            f"- live_action_enabled: {tool_bridge.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {tool_bridge.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {tool_bridge.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {tool_bridge.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {tool_bridge.get('next_required_milestone')}",
            f"- Warning: {tool_bridge.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Agent Team Work Proposal",
            "",
            f"- mission_context_snapshot_defined: {work_proposal.get('mission_context_snapshot_defined')}",
            f"- agent_team_observation_input_defined: {work_proposal.get('agent_team_observation_input_defined')}",
            f"- autonomous_work_proposals_defined: {work_proposal.get('autonomous_work_proposals_defined')}",
            f"- selected_work_proposal_defined: {work_proposal.get('selected_work_proposal_defined')}",
            f"- role_review_board_defined: {work_proposal.get('role_review_board_defined')}",
            f"- tool_need_analysis_defined: {work_proposal.get('tool_need_analysis_defined')}",
            f"- generated_tool_request_defined: {work_proposal.get('generated_tool_request_defined')}",
            f"- work_proposal_routed_to_bridge: {work_proposal.get('work_proposal_routed_to_bridge')}",
            f"- direct_tool_invocation_used: {work_proposal.get('direct_tool_invocation_used')}",
            f"- bridged_tool_result_ref_defined: {work_proposal.get('bridged_tool_result_ref_defined')}",
            f"- work_proposal_cieu_event_defined: {work_proposal.get('work_proposal_cieu_event_defined')}",
            f"- work_proposal_residual_delta_defined: {work_proposal.get('work_proposal_residual_delta_defined')}",
            f"- agent_team_generated_the_work: {work_proposal.get('agent_team_generated_the_work')}",
            f"- agent_team_selected_governed_tool: {work_proposal.get('agent_team_selected_governed_tool')}",
            f"- pre_u_bridge_required: {work_proposal.get('pre_u_bridge_required')}",
            f"- pre_u_bridge_satisfied: {work_proposal.get('pre_u_bridge_satisfied')}",
            f"- real_action_executed: {work_proposal.get('real_action_executed')}",
            f"- external_action_executed: {work_proposal.get('external_action_executed')}",
            f"- live_action_enabled: {work_proposal.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {work_proposal.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {work_proposal.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {work_proposal.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {work_proposal.get('next_required_milestone')}",
            f"- Warning: {work_proposal.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Mission Dashboard Refresh Loop",
            "",
            f"- refresh_loop_contract_defined: {dashboard_refresh.get('refresh_loop_contract_defined')}",
            f"- previous_dashboard_snapshot_defined: {dashboard_refresh.get('previous_dashboard_snapshot_defined')}",
            f"- current_observation_input_defined: {dashboard_refresh.get('current_observation_input_defined')}",
            f"- refreshed_mission_dashboard_defined: {dashboard_refresh.get('refreshed_mission_dashboard_defined')}",
            f"- company_state_delta_defined: {dashboard_refresh.get('company_state_delta_defined')}",
            f"- refreshed_autonomous_backlog_defined: {dashboard_refresh.get('refreshed_autonomous_backlog_defined')}",
            f"- refresh_loop_trace_defined: {dashboard_refresh.get('refresh_loop_trace_defined')}",
            f"- refresh_cieu_event_defined: {dashboard_refresh.get('refresh_cieu_event_defined')}",
            f"- refresh_residual_delta_defined: {dashboard_refresh.get('refresh_residual_delta_defined')}",
            f"- dashboard_refresh_loop_ran: {dashboard_refresh.get('dashboard_refresh_loop_ran')}",
            f"- scheduler_used: {dashboard_refresh.get('scheduler_used')}",
            f"- daemon_used: {dashboard_refresh.get('daemon_used')}",
            f"- manual_local_run_only: {dashboard_refresh.get('manual_local_run_only')}",
            f"- real_action_executed: {dashboard_refresh.get('real_action_executed')}",
            f"- external_action_executed: {dashboard_refresh.get('external_action_executed')}",
            f"- live_action_enabled: {dashboard_refresh.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {dashboard_refresh.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {dashboard_refresh.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {dashboard_refresh.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {dashboard_refresh.get('next_required_milestone')}",
            f"- Warning: {dashboard_refresh.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed Recurring Observation Loop Contract",
            "",
            f"- recurring_observation_loop_contract_defined: {recurring_loop.get('recurring_observation_loop_contract_defined')}",
            f"- recurrence_policy_defined: {recurring_loop.get('recurrence_policy_defined')}",
            f"- recurrence_enabled: {recurring_loop.get('recurrence_enabled')}",
            f"- scheduler_enabled: {recurring_loop.get('scheduler_enabled')}",
            f"- daemon_enabled: {recurring_loop.get('daemon_enabled')}",
            f"- auto_run_enabled: {recurring_loop.get('auto_run_enabled')}",
            f"- manual_local_simulation_only: {recurring_loop.get('manual_local_simulation_only')}",
            f"- allowed_observation_sources_defined: {recurring_loop.get('allowed_observation_sources_defined')}",
            f"- tick_governance_gate_defined: {recurring_loop.get('tick_governance_gate_defined')}",
            f"- simulated_observation_tick_defined: {recurring_loop.get('simulated_observation_tick_defined')}",
            f"- simulated_tick_cieu_event_defined: {recurring_loop.get('simulated_tick_cieu_event_defined')}",
            f"- simulated_tick_residual_delta_defined: {recurring_loop.get('simulated_tick_residual_delta_defined')}",
            f"- stop_abort_conditions_defined: {recurring_loop.get('stop_abort_conditions_defined')}",
            f"- escalation_conditions_defined: {recurring_loop.get('escalation_conditions_defined')}",
            f"- manual_enablement_checklist_defined: {recurring_loop.get('manual_enablement_checklist_defined')}",
            f"- real_action_executed: {recurring_loop.get('real_action_executed')}",
            f"- external_action_executed: {recurring_loop.get('external_action_executed')}",
            f"- live_action_enabled: {recurring_loop.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {recurring_loop.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {recurring_loop.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {recurring_loop.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {recurring_loop.get('next_required_milestone')}",
            f"- Warning: {recurring_loop.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Manual Recurring Observation Tick Runner",
            "",
            f"- manual_tick_runner_contract_defined: {manual_tick.get('manual_tick_runner_contract_defined')}",
            f"- manual_tick_request_defined: {manual_tick.get('manual_tick_request_defined')}",
            f"- manual_tick_preflight_defined: {manual_tick.get('manual_tick_preflight_defined')}",
            f"- manual_tick_source_validation_defined: {manual_tick.get('manual_tick_source_validation_defined')}",
            f"- manual_tick_governance_decision_defined: {manual_tick.get('manual_tick_governance_decision_defined')}",
            f"- manual_tick_result_defined: {manual_tick.get('manual_tick_result_defined')}",
            f"- manual_tick_dashboard_delta_defined: {manual_tick.get('manual_tick_dashboard_delta_defined')}",
            f"- manual_tick_work_candidates_defined: {manual_tick.get('manual_tick_work_candidates_defined')}",
            f"- manual_tick_cieu_event_defined: {manual_tick.get('manual_tick_cieu_event_defined')}",
            f"- manual_tick_residual_delta_defined: {manual_tick.get('manual_tick_residual_delta_defined')}",
            f"- manual_tick_run_receipt_defined: {manual_tick.get('manual_tick_run_receipt_defined')}",
            f"- manual_tick_history_index_defined: {manual_tick.get('manual_tick_history_index_defined')}",
            f"- manual_trigger_required: {manual_tick.get('manual_trigger_required')}",
            f"- one_tick_per_invocation: {manual_tick.get('one_tick_per_invocation')}",
            f"- total_recorded_ticks: {manual_tick.get('total_recorded_ticks')}",
            f"- recurrence_enabled: {manual_tick.get('recurrence_enabled')}",
            f"- scheduler_enabled: {manual_tick.get('scheduler_enabled')}",
            f"- daemon_enabled: {manual_tick.get('daemon_enabled')}",
            f"- auto_run_enabled: {manual_tick.get('auto_run_enabled')}",
            f"- manual_local_run_only: {manual_tick.get('manual_local_run_only')}",
            f"- real_action_executed: {manual_tick.get('real_action_executed')}",
            f"- external_action_executed: {manual_tick.get('external_action_executed')}",
            f"- live_action_enabled: {manual_tick.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {manual_tick.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {manual_tick.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {manual_tick.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {manual_tick.get('next_required_milestone')}",
            f"- Warning: {manual_tick.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Field Functional Archaeology",
            "",
            f"- field_functional_archaeology_defined: {field_functional.get('field_functional_archaeology_defined')}",
            f"- repos_scanned: {field_functional.get('repos_scanned')}",
            f"- assets_scanned: {field_functional.get('assets_scanned')}",
            f"- field_functional_assets_found: {field_functional.get('field_functional_assets_found')}",
            f"- reuse_candidates_count: {field_functional.get('reuse_candidates_count')}",
            f"- wrap_candidates_count: {field_functional.get('wrap_candidates_count')}",
            f"- rewrite_candidates_count: {field_functional.get('rewrite_candidates_count')}",
            f"- concept_reference_count: {field_functional.get('concept_reference_count')}",
            f"- do_not_absorb_count: {field_functional.get('do_not_absorb_count')}",
            f"- mission_projection_merge_plan_defined: {field_functional.get('mission_projection_merge_plan_defined')}",
            f"- ready_for_L5_projection_harness: {field_functional.get('ready_for_L5_projection_harness')}",
            f"- live_action_enabled: {field_functional.get('live_action_enabled')}",
            f"- external_action_enabled: {field_functional.get('external_action_enabled')}",
            f"- cieu_persistence_enabled: {field_functional.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {field_functional.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {field_functional.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {field_functional.get('next_required_milestone')}",
            f"- Warning: {field_functional.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Mission Field Projection Harness",
            "",
            f"- mission_field_projection_harness_defined: {mission_projection.get('mission_field_projection_harness_defined')}",
            f"- l5_1_projection_contract_defined: {mission_projection.get('l5_1_projection_contract_defined')}",
            f"- layered_projection_trace_generated: {mission_projection.get('layered_projection_trace_generated')}",
            f"- pre_u_adapter_candidate_generated: {mission_projection.get('pre_u_adapter_candidate_generated')}",
            f"- residual_delta_fixture_generated: {mission_projection.get('residual_delta_fixture_generated')}",
            f"- action_layer_projection_only: {mission_projection.get('action_layer_projection_only')}",
            f"- action_field_execution_implemented: {mission_projection.get('action_field_execution_implemented')}",
            f"- ready_for_L5_2_field_functional_auto_projection_core: {mission_projection.get('ready_for_L5_2_field_functional_auto_projection_core')}",
            f"- deep_xt_model_is_not_l5_2_main_milestone: {mission_projection.get('deep_xt_model_is_not_l5_2_main_milestone')}",
            f"- live_execution_enabled: {mission_projection.get('live_execution_enabled')}",
            f"- external_action_enabled: {mission_projection.get('external_action_enabled')}",
            f"- network_enabled: {mission_projection.get('network_enabled')}",
            f"- scheduler_enabled: {mission_projection.get('scheduler_enabled')}",
            f"- daemon_enabled: {mission_projection.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {mission_projection.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {mission_projection.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {mission_projection.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {mission_projection.get('next_required_milestone')}",
            f"- Warning: {mission_projection.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Field Functional Auto-Projection Core",
            "",
            f"- field_functional_auto_projection_core_defined: {field_projection.get('field_functional_auto_projection_core_defined')}",
            f"- mission_level_y_star_input_defined: {field_projection.get('mission_level_y_star_input_defined')}",
            f"- mission_to_behavior_projection_generated: {field_projection.get('mission_to_behavior_projection_generated')}",
            f"- projection_layers: {', '.join(field_projection.get('projection_layers', []))}",
            f"- behavior_level_y_star_candidate_generated: {field_projection.get('behavior_level_y_star_candidate_generated')}",
            f"- pre_u_packet_candidate_from_behavior_y_star_generated: {field_projection.get('pre_u_packet_candidate_from_behavior_y_star_generated')}",
            f"- residual_delta_loop_fixture_generated: {field_projection.get('residual_delta_loop_fixture_generated')}",
            f"- learning_candidate_stub_generated_but_not_approved: {field_projection.get('learning_candidate_stub_generated_but_not_approved')}",
            f"- live_execution_enabled: {field_projection.get('live_execution_enabled')}",
            f"- external_action_enabled: {field_projection.get('external_action_enabled')}",
            f"- network_enabled: {field_projection.get('network_enabled')}",
            f"- scheduler_enabled: {field_projection.get('scheduler_enabled')}",
            f"- daemon_enabled: {field_projection.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {field_projection.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {field_projection.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {field_projection.get('memory_ingestion_enabled')}",
            f"- behavior_execution_enabled: {field_projection.get('behavior_execution_enabled')}",
            f"- l6_revenue_opportunity_discovery_enabled: {field_projection.get('l6_revenue_opportunity_discovery_enabled')}",
            f"- ready_for_l5_3_projection_checked_autonomous_cycle: {field_projection.get('ready_for_l5_3_projection_checked_autonomous_cycle')}",
            f"- next_required_milestone: {field_projection.get('next_required_milestone')}",
            f"- Warning: {field_projection.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Projection-Checked Autonomous Work Cycle",
            "",
            f"- projection_checked_autonomous_work_cycle_defined: {projection_cycle.get('projection_checked_autonomous_work_cycle_defined')}",
            f"- behavior_y_star_consumed_by_cycle: {projection_cycle.get('behavior_y_star_consumed_by_cycle')}",
            f"- work_proposal_checked_against_behavior_y_star: {projection_cycle.get('work_proposal_checked_against_behavior_y_star')}",
            f"- pre_u_packet_candidate_generated: {projection_cycle.get('pre_u_packet_candidate_generated')}",
            f"- dry_run_gate_decision_generated: {projection_cycle.get('dry_run_gate_decision_generated')}",
            f"- dry_run_result_generated: {projection_cycle.get('dry_run_result_generated')}",
            f"- cieu_like_event_fixture_generated: {projection_cycle.get('cieu_like_event_fixture_generated')}",
            f"- residual_delta_generated: {projection_cycle.get('residual_delta_generated')}",
            f"- learning_review_candidate_generated_but_not_approved: {projection_cycle.get('learning_review_candidate_generated_but_not_approved')}",
            f"- live_execution_enabled: {projection_cycle.get('live_execution_enabled')}",
            f"- external_action_enabled: {projection_cycle.get('external_action_enabled')}",
            f"- network_enabled: {projection_cycle.get('network_enabled')}",
            f"- scheduler_enabled: {projection_cycle.get('scheduler_enabled')}",
            f"- daemon_enabled: {projection_cycle.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {projection_cycle.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {projection_cycle.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {projection_cycle.get('memory_ingestion_enabled')}",
            f"- behavior_execution_enabled: {projection_cycle.get('behavior_execution_enabled')}",
            f"- ready_for_l5_4_review_gated_learning_loop: {projection_cycle.get('ready_for_l5_4_review_gated_learning_loop')}",
            f"- next_required_milestone: {projection_cycle.get('next_required_milestone')}",
            f"- Warning: {projection_cycle.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Integrated Review-Gated Shadow Learning Cycle",
            "",
            f"- integrated_review_gated_shadow_learning_cycle_defined: {shadow_learning_cycle.get('integrated_review_gated_shadow_learning_cycle_defined')}",
            f"- l5_3_residual_consumed: {shadow_learning_cycle.get('l5_3_residual_consumed')}",
            f"- deterministic_review_gate_decision_generated: {shadow_learning_cycle.get('deterministic_review_gate_decision_generated')}",
            f"- review_gate_decision: {shadow_learning_cycle.get('review_gate_decision')}",
            f"- learning_target_classification_generated: {shadow_learning_cycle.get('learning_target_classification_generated')}",
            f"- projection_policy_update_candidate_generated: {shadow_learning_cycle.get('projection_policy_update_candidate_generated')}",
            f"- shadow_projection_policy_patch_generated: {shadow_learning_cycle.get('shadow_projection_policy_patch_generated')}",
            f"- shadow_behavior_y_star_preview_generated: {shadow_learning_cycle.get('shadow_behavior_y_star_preview_generated')}",
            f"- shadow_updated_projection_cycle_generated: {shadow_learning_cycle.get('shadow_updated_projection_cycle_generated')}",
            f"- original_vs_shadow_cycle_comparison_generated: {shadow_learning_cycle.get('original_vs_shadow_cycle_comparison_generated')}",
            f"- integrated_cieu_like_fixture_generated: {shadow_learning_cycle.get('integrated_cieu_like_fixture_generated')}",
            f"- candidate_approved: {shadow_learning_cycle.get('candidate_approved')}",
            f"- candidate_applied: {shadow_learning_cycle.get('candidate_applied')}",
            f"- canonical_policy_mutation_enabled: {shadow_learning_cycle.get('canonical_policy_mutation_enabled')}",
            f"- brain_writeback_enabled: {shadow_learning_cycle.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {shadow_learning_cycle.get('memory_ingestion_enabled')}",
            f"- live_execution_enabled: {shadow_learning_cycle.get('live_execution_enabled')}",
            f"- behavior_execution_enabled: {shadow_learning_cycle.get('behavior_execution_enabled')}",
            f"- external_action_enabled: {shadow_learning_cycle.get('external_action_enabled')}",
            f"- network_enabled: {shadow_learning_cycle.get('network_enabled')}",
            f"- scheduler_enabled: {shadow_learning_cycle.get('scheduler_enabled')}",
            f"- daemon_enabled: {shadow_learning_cycle.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {shadow_learning_cycle.get('cieu_persistence_enabled')}",
            f"- previous_residual_influenced_shadow_projection: {shadow_learning_cycle.get('previous_residual_influenced_shadow_projection')}",
            f"- ready_for_controlled_canonical_learning_design: {shadow_learning_cycle.get('ready_for_controlled_canonical_learning_design')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {shadow_learning_cycle.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {shadow_learning_cycle.get('next_required_milestone')}",
            f"- Warning: {shadow_learning_cycle.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Cross-Repo Governance Contract Proof",
            "",
            f"- cross_repo_governance_contract_proof_defined: {cross_repo_governance.get('cross_repo_governance_contract_proof_defined')}",
            f"- y_star_gov_surfaces_inventoried_read_only: {cross_repo_governance.get('y_star_gov_surfaces_inventoried_read_only')}",
            f"- gov_mcp_surfaces_inventoried_read_only: {cross_repo_governance.get('gov_mcp_surfaces_inventoried_read_only')}",
            f"- behavior_y_star_mapped_to_governance_contract: {cross_repo_governance.get('behavior_y_star_mapped_to_governance_contract')}",
            f"- pre_u_candidates_mapped_to_validator_expectations: {cross_repo_governance.get('pre_u_candidates_mapped_to_validator_expectations')}",
            f"- cieu_fixtures_mapped_to_prediction_delta_expectations: {cross_repo_governance.get('cieu_fixtures_mapped_to_prediction_delta_expectations')}",
            f"- gov_mcp_boundary_mapped: {cross_repo_governance.get('gov_mcp_boundary_mapped')}",
            f"- non_bypass_invariants_defined: {cross_repo_governance.get('non_bypass_invariants_defined')}",
            f"- bypass_risks_identified: {cross_repo_governance.get('bypass_risks_identified')}",
            f"- no_non_ystar_company_repo_modified: {cross_repo_governance.get('no_non_ystar_company_repo_modified')}",
            f"- no_mcp_server_or_tool_executed: {cross_repo_governance.get('no_mcp_server_or_tool_executed')}",
            f"- ready_for_l5_6_governed_mcp_dry_run_adapter: {cross_repo_governance.get('ready_for_l5_6_governed_mcp_dry_run_adapter')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {cross_repo_governance.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {cross_repo_governance.get('next_required_milestone')}",
            f"- Warning: {cross_repo_governance.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed MCP Dry-Run Adapter",
            "",
            f"- l5_6_governed_mcp_dry_run_adapter_defined: {governed_mcp_adapter.get('l5_6_governed_mcp_dry_run_adapter_defined')}",
            f"- behavior_y_star_loaded: {governed_mcp_adapter.get('behavior_y_star_loaded')}",
            f"- mcp_request_intent_generated: {governed_mcp_adapter.get('mcp_request_intent_generated')}",
            f"- mcp_pre_u_packet_candidate_generated: {governed_mcp_adapter.get('mcp_pre_u_packet_candidate_generated')}",
            f"- dry_run_governance_decision_envelope_generated: {governed_mcp_adapter.get('dry_run_governance_decision_envelope_generated')}",
            f"- bridge_authorization_receipt_generated: {governed_mcp_adapter.get('bridge_authorization_receipt_generated')}",
            f"- governed_mcp_call_candidate_generated: {governed_mcp_adapter.get('governed_mcp_call_candidate_generated')}",
            f"- real_mcp_execution_blocked: {governed_mcp_adapter.get('real_mcp_execution_blocked')}",
            f"- mcp_dry_run_receipt_generated: {governed_mcp_adapter.get('mcp_dry_run_receipt_generated')}",
            f"- mcp_cieu_like_event_generated: {governed_mcp_adapter.get('mcp_cieu_like_event_generated')}",
            f"- mcp_residual_delta_generated: {governed_mcp_adapter.get('mcp_residual_delta_generated')}",
            f"- review_only_mcp_learning_candidate_generated: {governed_mcp_adapter.get('review_only_mcp_learning_candidate_generated')}",
            f"- y_star_gov_unmodified: {governed_mcp_adapter.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {governed_mcp_adapter.get('gov_mcp_unmodified')}",
            f"- mcp_server_not_started: {governed_mcp_adapter.get('mcp_server_not_started')}",
            f"- mcp_tool_not_executed: {governed_mcp_adapter.get('mcp_tool_not_executed')}",
            f"- mcp_resource_not_mutated: {governed_mcp_adapter.get('mcp_resource_not_mutated')}",
            f"- ready_for_l5_7_controlled_canonical_learning_design: {governed_mcp_adapter.get('ready_for_l5_7_controlled_canonical_learning_design')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {governed_mcp_adapter.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {governed_mcp_adapter.get('next_required_milestone')}",
            f"- Warning: {governed_mcp_adapter.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Controlled Canonical Learning Design",
            "",
            f"- l5_7_controlled_canonical_learning_design_defined: {controlled_canonical_learning.get('l5_7_controlled_canonical_learning_design_defined')}",
            f"- y_star_non_mutation_invariant_defined: {controlled_canonical_learning.get('y_star_non_mutation_invariant_defined')}",
            f"- canonical_learning_target_registry_generated: {controlled_canonical_learning.get('canonical_learning_target_registry_generated')}",
            f"- promotion_evidence_bundle_generated: {controlled_canonical_learning.get('promotion_evidence_bundle_generated')}",
            f"- promotion_eligibility_gate_generated: {controlled_canonical_learning.get('promotion_eligibility_gate_generated')}",
            f"- canonical_update_package_candidate_generated: {controlled_canonical_learning.get('canonical_update_package_candidate_generated')}",
            f"- versioned_patch_plan_generated: {controlled_canonical_learning.get('versioned_patch_plan_generated')}",
            f"- rollback_audit_plan_generated: {controlled_canonical_learning.get('rollback_audit_plan_generated')}",
            f"- post_promotion_validation_plan_generated: {controlled_canonical_learning.get('post_promotion_validation_plan_generated')}",
            f"- dry_run_promotion_fixture_generated: {controlled_canonical_learning.get('dry_run_promotion_fixture_generated')}",
            f"- candidate_approved: {controlled_canonical_learning.get('candidate_approved')}",
            f"- candidate_applied: {controlled_canonical_learning.get('candidate_applied')}",
            f"- canonical_policy_mutation_performed: {controlled_canonical_learning.get('canonical_policy_mutation_performed')}",
            f"- canonical_update_application_performed: {controlled_canonical_learning.get('canonical_update_application_performed')}",
            f"- brain_writeback_performed: {controlled_canonical_learning.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {controlled_canonical_learning.get('memory_ingestion_performed')}",
            f"- strategy_mutation_performed: {controlled_canonical_learning.get('strategy_mutation_performed')}",
            f"- y_star_direct_mutation_performed: {controlled_canonical_learning.get('y_star_direct_mutation_performed')}",
            f"- y_star_gov_unmodified: {controlled_canonical_learning.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {controlled_canonical_learning.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_8_approved_canonical_update_sandbox: {controlled_canonical_learning.get('ready_for_l5_8_approved_canonical_update_sandbox')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {controlled_canonical_learning.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {controlled_canonical_learning.get('next_required_milestone')}",
            f"- Warning: {controlled_canonical_learning.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Approved Canonical Update Sandbox",
            "",
            f"- l5_8_approved_canonical_update_sandbox_defined: {approved_sandbox_update.get('l5_8_approved_canonical_update_sandbox_defined')}",
            f"- sandbox_approval_fixture_generated: {approved_sandbox_update.get('sandbox_approval_fixture_generated')}",
            f"- sandbox_baseline_generated: {approved_sandbox_update.get('sandbox_baseline_generated')}",
            f"- sandbox_patch_applied: {approved_sandbox_update.get('sandbox_patch_applied')}",
            f"- real_canonical_state_unchanged: {approved_sandbox_update.get('real_canonical_state_unchanged')}",
            f"- y_star_non_mutation_invariant_preserved: {approved_sandbox_update.get('y_star_non_mutation_invariant_preserved')}",
            f"- sandbox_post_update_validation_generated: {approved_sandbox_update.get('sandbox_post_update_validation_generated')}",
            f"- sandbox_behavior_y_star_reprojection_generated: {approved_sandbox_update.get('sandbox_behavior_y_star_reprojection_generated')}",
            f"- sandbox_governed_mcp_preview_generated: {approved_sandbox_update.get('sandbox_governed_mcp_preview_generated')}",
            f"- sandbox_update_cieu_like_fixture_generated: {approved_sandbox_update.get('sandbox_update_cieu_like_fixture_generated')}",
            f"- sandbox_rollback_validation_generated: {approved_sandbox_update.get('sandbox_rollback_validation_generated')}",
            f"- original_vs_sandbox_vs_rollback_comparison_generated: {approved_sandbox_update.get('original_vs_sandbox_vs_rollback_comparison_generated')}",
            f"- real_candidate_approved: {approved_sandbox_update.get('real_candidate_approved')}",
            f"- real_candidate_applied: {approved_sandbox_update.get('real_candidate_applied')}",
            f"- real_canonical_policy_mutation_performed: {approved_sandbox_update.get('real_canonical_policy_mutation_performed')}",
            f"- real_canonical_update_application_performed: {approved_sandbox_update.get('real_canonical_update_application_performed')}",
            f"- brain_writeback_performed: {approved_sandbox_update.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {approved_sandbox_update.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {approved_sandbox_update.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {approved_sandbox_update.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {approved_sandbox_update.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_9_real_approval_workflow_boundary: {approved_sandbox_update.get('ready_for_l5_9_real_approval_workflow_boundary')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {approved_sandbox_update.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {approved_sandbox_update.get('next_required_milestone')}",
            f"- Warning: {approved_sandbox_update.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Real Approval Workflow Boundary",
            "",
            f"- l5_9_real_approval_workflow_boundary_defined: {real_approval_workflow.get('l5_9_real_approval_workflow_boundary_defined')}",
            f"- approval_authority_model_generated: {real_approval_workflow.get('approval_authority_model_generated')}",
            f"- approval_evidence_dossier_generated: {real_approval_workflow.get('approval_evidence_dossier_generated')}",
            f"- durable_approval_record_contract_generated: {real_approval_workflow.get('durable_approval_record_contract_generated')}",
            f"- approval_decision_packet_fixture_generated: {real_approval_workflow.get('approval_decision_packet_fixture_generated')}",
            f"- validity_revocation_policy_generated: {real_approval_workflow.get('validity_revocation_policy_generated')}",
            f"- pre_application_snapshot_policy_generated: {real_approval_workflow.get('pre_application_snapshot_policy_generated')}",
            f"- real_application_boundary_gate_generated: {real_approval_workflow.get('real_application_boundary_gate_generated')}",
            f"- post_approval_preflight_validation_plan_generated: {real_approval_workflow.get('post_approval_preflight_validation_plan_generated')}",
            f"- manual_approval_runbook_generated: {real_approval_workflow.get('manual_approval_runbook_generated')}",
            f"- approval_workflow_cieu_like_fixture_generated: {real_approval_workflow.get('approval_workflow_cieu_like_fixture_generated')}",
            f"- real_approval_granted: {real_approval_workflow.get('real_approval_granted')}",
            f"- real_application_authorized: {real_approval_workflow.get('real_application_authorized')}",
            f"- durable_approval_record_written: {real_approval_workflow.get('durable_approval_record_written')}",
            f"- real_canonical_policy_mutation_performed: {real_approval_workflow.get('real_canonical_policy_mutation_performed')}",
            f"- real_canonical_update_application_performed: {real_approval_workflow.get('real_canonical_update_application_performed')}",
            f"- brain_writeback_performed: {real_approval_workflow.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {real_approval_workflow.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {real_approval_workflow.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {real_approval_workflow.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {real_approval_workflow.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_10_controlled_approval_record_sandbox: {real_approval_workflow.get('ready_for_l5_10_controlled_approval_record_sandbox')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {real_approval_workflow.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {real_approval_workflow.get('next_required_milestone')}",
            f"- Warning: {real_approval_workflow.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Controlled Approval Record Sandbox",
            "",
            f"- l5_10_controlled_approval_record_sandbox_defined: {controlled_approval_record.get('l5_10_controlled_approval_record_sandbox_defined')}",
            f"- sandbox_approval_record_instance_generated: {controlled_approval_record.get('sandbox_approval_record_instance_generated')}",
            f"- integrity_validation_generated: {controlled_approval_record.get('integrity_validation_generated')}",
            f"- validity_state_machine_replay_generated: {controlled_approval_record.get('validity_state_machine_replay_generated')}",
            f"- invalid_record_variants_generated_and_blocked: {controlled_approval_record.get('expired_revoked_tampered_wrong_scope_missing_evidence_blocked')}",
            f"- valid_sandbox_record_gate_replay_generated: {controlled_approval_record.get('valid_sandbox_record_gate_replay_generated')}",
            f"- invalid_record_gate_blocking_generated: {controlled_approval_record.get('invalid_record_gate_blocking_generated')}",
            f"- audit_lineage_generated: {controlled_approval_record.get('audit_lineage_generated')}",
            f"- approval_record_cieu_like_fixture_generated: {controlled_approval_record.get('approval_record_cieu_like_fixture_generated')}",
            f"- real_approval_granted: {controlled_approval_record.get('real_approval_granted')}",
            f"- durable_approval_record_written: {controlled_approval_record.get('durable_approval_record_written')}",
            f"- real_application_authorized: {controlled_approval_record.get('real_application_authorized')}",
            f"- brain_writeback_performed: {controlled_approval_record.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {controlled_approval_record.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {controlled_approval_record.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {controlled_approval_record.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {controlled_approval_record.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_11_controlled_real_release_preflight: {controlled_approval_record.get('ready_for_l5_11_controlled_real_release_preflight')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {controlled_approval_record.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {controlled_approval_record.get('next_required_milestone')}",
            f"- Warning: {controlled_approval_record.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Controlled Real Release Preflight",
            "",
            f"- l5_11_controlled_real_release_preflight_defined: {controlled_real_release_preflight.get('l5_11_controlled_real_release_preflight_defined')}",
            f"- release_candidate_assembled: {controlled_real_release_preflight.get('release_candidate_assembled')}",
            f"- release_scope_validation_generated: {controlled_real_release_preflight.get('release_scope_validation_generated')}",
            f"- approval_record_preflight_generated: {controlled_real_release_preflight.get('approval_record_preflight_generated')}",
            f"- snapshot_rollback_preflight_generated: {controlled_real_release_preflight.get('snapshot_rollback_preflight_generated')}",
            f"- y_star_non_mutation_preflight_generated: {controlled_real_release_preflight.get('y_star_non_mutation_preflight_generated')}",
            f"- mcp_non_bypass_preflight_generated: {controlled_real_release_preflight.get('mcp_non_bypass_preflight_generated')}",
            f"- post_release_validation_matrix_generated: {controlled_real_release_preflight.get('post_release_validation_matrix_generated')}",
            f"- release_operator_handoff_packet_generated: {controlled_real_release_preflight.get('release_operator_handoff_packet_generated')}",
            f"- release_blocker_decision_generated: {controlled_real_release_preflight.get('release_blocker_decision_generated')}",
            f"- release_preflight_cieu_like_fixture_generated: {controlled_real_release_preflight.get('release_preflight_cieu_like_fixture_generated')}",
            f"- real_approval_granted: {controlled_real_release_preflight.get('real_approval_granted')}",
            f"- real_release_authorized: {controlled_real_release_preflight.get('real_release_authorized')}",
            f"- durable_approval_record_written: {controlled_real_release_preflight.get('durable_approval_record_written')}",
            f"- canonical_policy_mutation_performed: {controlled_real_release_preflight.get('canonical_policy_mutation_performed')}",
            f"- brain_writeback_performed: {controlled_real_release_preflight.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {controlled_real_release_preflight.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {controlled_real_release_preflight.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {controlled_real_release_preflight.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {controlled_real_release_preflight.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_12_real_release_simulation_sandbox: {controlled_real_release_preflight.get('ready_for_l5_12_real_release_simulation_sandbox')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {controlled_real_release_preflight.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {controlled_real_release_preflight.get('next_required_milestone')}",
            f"- Warning: {controlled_real_release_preflight.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Real Release Simulation Sandbox",
            "",
            f"- l5_12_real_release_simulation_sandbox_defined: {real_release_simulation.get('l5_12_real_release_simulation_sandbox_defined')}",
            f"- sandbox_release_authority_fixture_generated: {real_release_simulation.get('sandbox_release_authority_fixture_generated')}",
            f"- simulated_durable_approval_record_generated: {real_release_simulation.get('simulated_durable_approval_record_generated')}",
            f"- sandbox_snapshot_generated: {real_release_simulation.get('sandbox_snapshot_generated')}",
            f"- simulated_release_operator_confirmed: {real_release_simulation.get('simulated_release_operator_confirmed')}",
            f"- simulated_rollback_operator_confirmed: {real_release_simulation.get('simulated_rollback_operator_confirmed')}",
            f"- sandbox_release_execution_generated: {real_release_simulation.get('sandbox_release_execution_generated')}",
            f"- real_canonical_state_unchanged: {real_release_simulation.get('real_canonical_state_unchanged')}",
            f"- sandbox_post_release_validation_generated: {real_release_simulation.get('sandbox_post_release_validation_generated')}",
            f"- sandbox_post_release_projection_generated: {real_release_simulation.get('sandbox_post_release_projection_generated')}",
            f"- sandbox_mcp_preview_generated: {real_release_simulation.get('sandbox_mcp_preview_generated')}",
            f"- sandbox_rollback_drill_generated: {real_release_simulation.get('sandbox_rollback_drill_generated')}",
            f"- release_simulation_cieu_like_fixture_generated: {real_release_simulation.get('release_simulation_cieu_like_fixture_generated')}",
            f"- real_approval_granted: {real_release_simulation.get('real_approval_granted')}",
            f"- real_release_authorized: {real_release_simulation.get('real_release_authorized')}",
            f"- durable_approval_record_written: {real_release_simulation.get('durable_approval_record_written')}",
            f"- canonical_policy_mutation_performed: {real_release_simulation.get('canonical_policy_mutation_performed')}",
            f"- brain_writeback_performed: {real_release_simulation.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {real_release_simulation.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {real_release_simulation.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {real_release_simulation.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {real_release_simulation.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_13_live_boundary_no_go_decision_framework: {real_release_simulation.get('ready_for_l5_13_live_boundary_no_go_decision_framework')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {real_release_simulation.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {real_release_simulation.get('next_required_milestone')}",
            f"- Warning: {real_release_simulation.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Live Boundary No-Go Framework",
            "",
            f"- l5_13_live_boundary_no_go_framework_defined: {live_boundary_no_go.get('l5_13_live_boundary_no_go_framework_defined')}",
            f"- live_capability_domains_classified: {live_boundary_no_go.get('live_capability_domains_classified')}",
            f"- no_go_invariants_defined: {live_boundary_no_go.get('no_go_invariants_defined')}",
            f"- l5_0_to_l5_12_evidence_indexed: {live_boundary_no_go.get('l5_0_to_l5_12_evidence_indexed')}",
            f"- live_blockers_identified: {live_boundary_no_go.get('live_blockers_identified')}",
            f"- l6_design_entry_gate_generated: {live_boundary_no_go.get('l6_design_entry_gate_generated')}",
            f"- l6_non_execution_boundary_defined: {live_boundary_no_go.get('l6_non_execution_boundary_defined')}",
            f"- l6_forbidden_hardcoding_policy_defined: {live_boundary_no_go.get('l6_forbidden_hardcoding_policy_defined')}",
            f"- system_no_go_decision_packet_generated: {live_boundary_no_go.get('system_no_go_decision_packet_generated')}",
            f"- live_boundary_cieu_like_fixture_generated: {live_boundary_no_go.get('live_boundary_cieu_like_fixture_generated')}",
            f"- live_execution_decision: {live_boundary_no_go.get('live_execution_decision')}",
            f"- real_mcp_execution_decision: {live_boundary_no_go.get('real_mcp_execution_decision')}",
            f"- real_canonical_update_decision: {live_boundary_no_go.get('real_canonical_update_decision')}",
            f"- brain_memory_writeback_decision: {live_boundary_no_go.get('brain_memory_writeback_decision')}",
            f"- durable_persistence_decision: {live_boundary_no_go.get('durable_persistence_decision')}",
            f"- real_release_decision: {live_boundary_no_go.get('real_release_decision')}",
            f"- l6_design_entry_decision: {live_boundary_no_go.get('l6_design_entry_decision')}",
            f"- l6_execution_decision: {live_boundary_no_go.get('l6_execution_decision')}",
            f"- ready_for_l6_meta_development_generative_engine_design: {live_boundary_no_go.get('ready_for_l6_meta_development_generative_engine_design')}",
            f"- ready_for_l6_revenue_opportunity_execution: {live_boundary_no_go.get('ready_for_l6_revenue_opportunity_execution')}",
            f"- next_required_milestone: {live_boundary_no_go.get('next_required_milestone')}",
            f"- Warning: {live_boundary_no_go.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6 Meta-Development Generative Selection Engine",
            "",
            f"- l6_0_meta_development_generative_selection_engine_defined: {l6_meta_development.get('l6_0_meta_development_generative_selection_engine_defined')}",
            f"- self_model_generated: {l6_meta_development.get('self_model_generated')}",
            f"- unique_asset_field_generated: {l6_meta_development.get('unique_asset_field_generated')}",
            f"- world_value_field_generated: {l6_meta_development.get('world_value_field_generated')}",
            f"- conversion_operator_library_generated: {l6_meta_development.get('conversion_operator_library_generated')}",
            f"- value_hypotheses_generated: {l6_meta_development.get('value_hypotheses_generated')}",
            f"- conversion_physics_defined: {l6_meta_development.get('conversion_physics_defined')}",
            f"- redeemability_selection_generated: {l6_meta_development.get('redeemability_selection_generated')}",
            f"- minimum_viable_proof_plans_generated: {l6_meta_development.get('minimum_viable_proof_plans_generated')}",
            f"- governed_experiment_portfolio_generated: {l6_meta_development.get('governed_experiment_portfolio_generated')}",
            f"- strategic_residual_loop_generated: {l6_meta_development.get('strategic_residual_loop_generated')}",
            f"- l6_design_only: {l6_meta_development.get('l6_design_only')}",
            f"- hardcoded_opportunity_categories_forbidden: {l6_meta_development.get('hardcoded_opportunity_categories_forbidden')}",
            f"- seed_examples_non_exhaustive: {l6_meta_development.get('seed_examples_non_exhaustive')}",
            f"- ready_for_l6_1_meta_development_mvp_artifact_sandbox: {l6_meta_development.get('ready_for_l6_1_meta_development_mvp_artifact_sandbox')}",
            f"- ready_for_l6_revenue_opportunity_execution: {l6_meta_development.get('ready_for_l6_revenue_opportunity_execution')}",
            f"- next_required_milestone: {l6_meta_development.get('next_required_milestone')}",
            f"- Warning: {l6_meta_development.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.1 MVP Artifact Sandbox",
            "",
            f"- l6_1_mvp_artifact_sandbox_defined: {l6_mvp_artifact_sandbox.get('l6_1_mvp_artifact_sandbox_defined')}",
            f"- selected_hypotheses_count: {l6_mvp_artifact_sandbox.get('selected_hypotheses_count')}",
            f"- generated_case_count: {l6_mvp_artifact_sandbox.get('generated_case_count')}",
            f"- internal_artifacts_generated: {l6_mvp_artifact_sandbox.get('internal_artifacts_generated')}",
            f"- review_gate_generated: {l6_mvp_artifact_sandbox.get('review_gate_generated')}",
            f"- externalization_boundary_generated: {l6_mvp_artifact_sandbox.get('externalization_boundary_generated')}",
            f"- strategic_residual_loop_generated: {l6_mvp_artifact_sandbox.get('strategic_residual_loop_generated')}",
            f"- ready_for_l6_2_external_observation_boundary_design: {l6_mvp_artifact_sandbox.get('ready_for_l6_2_external_observation_boundary_design')}",
            f"- ready_for_external_execution: {l6_mvp_artifact_sandbox.get('ready_for_external_execution')}",
            f"- ready_for_publication: {l6_mvp_artifact_sandbox.get('ready_for_publication')}",
            f"- ready_for_outreach: {l6_mvp_artifact_sandbox.get('ready_for_outreach')}",
            f"- ready_for_payment: {l6_mvp_artifact_sandbox.get('ready_for_payment')}",
            f"- ready_for_revenue_execution: {l6_mvp_artifact_sandbox.get('ready_for_revenue_execution')}",
            f"- next_recommended_milestone: {l6_mvp_artifact_sandbox.get('next_recommended_milestone')}",
            f"- Warning: {l6_mvp_artifact_sandbox.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.2 Governed External Observation Boundary",
            "",
            f"- l6_2_external_observation_boundary_defined: {l6_external_observation_boundary.get('l6_2_external_observation_boundary_defined')}",
            f"- boundary_only: {l6_external_observation_boundary.get('boundary_only')}",
            f"- sandbox_only: {l6_external_observation_boundary.get('sandbox_only')}",
            f"- pre_observation_packet_schema_defined: {l6_external_observation_boundary.get('pre_observation_packet_schema_defined')}",
            f"- source_registry_defined: {l6_external_observation_boundary.get('source_registry_defined')}",
            f"- permission_gate_defined: {l6_external_observation_boundary.get('permission_gate_defined')}",
            f"- manual_import_sandbox_defined: {l6_external_observation_boundary.get('manual_import_sandbox_defined')}",
            f"- no_action_receipts_generated: {l6_external_observation_boundary.get('no_action_receipts_generated')}",
            f"- strategic_residual_loop_generated: {l6_external_observation_boundary.get('strategic_residual_loop_generated')}",
            f"- real_external_observation_authorized: {l6_external_observation_boundary.get('real_external_observation_authorized')}",
            f"- network_enabled: {l6_external_observation_boundary.get('network_enabled')}",
            f"- publication_enabled: {l6_external_observation_boundary.get('publication_enabled')}",
            f"- outreach_enabled: {l6_external_observation_boundary.get('outreach_enabled')}",
            f"- payment_enabled: {l6_external_observation_boundary.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_external_observation_boundary.get('revenue_execution_enabled')}",
            f"- ready_for_l6_3_controlled_external_observation_sandbox: {l6_external_observation_boundary.get('ready_for_l6_3_controlled_external_observation_sandbox')}",
            f"- ready_for_real_network_observation: {l6_external_observation_boundary.get('ready_for_real_network_observation')}",
            f"- next_recommended_milestone: {l6_external_observation_boundary.get('next_recommended_milestone')}",
            f"- Warning: {l6_external_observation_boundary.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.3 Controlled External Observation Sandbox",
            "",
            f"- l6_3_controlled_observation_sandbox_defined: {l6_controlled_observation_sandbox.get('l6_3_controlled_observation_sandbox_defined')}",
            f"- sandbox_only: {l6_controlled_observation_sandbox.get('sandbox_only')}",
            f"- fixture_only: {l6_controlled_observation_sandbox.get('fixture_only')}",
            f"- static_fixture_observation_authorized: {l6_controlled_observation_sandbox.get('static_fixture_observation_authorized')}",
            f"- manual_import_fixture_authorized: {l6_controlled_observation_sandbox.get('manual_import_fixture_authorized')}",
            f"- selected_observation_case_count: {l6_controlled_observation_sandbox.get('selected_observation_case_count')}",
            f"- pre_observation_packet_count: {l6_controlled_observation_sandbox.get('pre_observation_packet_count')}",
            f"- static_manual_fixture_count: {l6_controlled_observation_sandbox.get('static_manual_fixture_count')}",
            f"- permission_replay_generated: {l6_controlled_observation_sandbox.get('permission_replay_generated')}",
            f"- evidence_validation_generated: {l6_controlled_observation_sandbox.get('evidence_validation_generated')}",
            f"- claim_freshness_assessment_generated: {l6_controlled_observation_sandbox.get('claim_freshness_assessment_generated')}",
            f"- refinement_candidates_generated: {l6_controlled_observation_sandbox.get('refinement_candidates_generated')}",
            f"- review_packets_generated: {l6_controlled_observation_sandbox.get('review_packets_generated')}",
            f"- no_action_receipts_generated: {l6_controlled_observation_sandbox.get('no_action_receipts_generated')}",
            f"- real_external_observation_authorized: {l6_controlled_observation_sandbox.get('real_external_observation_authorized')}",
            f"- network_enabled: {l6_controlled_observation_sandbox.get('network_enabled')}",
            f"- scraping_enabled: {l6_controlled_observation_sandbox.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_controlled_observation_sandbox.get('browser_fetch_enabled')}",
            f"- publication_enabled: {l6_controlled_observation_sandbox.get('publication_enabled')}",
            f"- outreach_enabled: {l6_controlled_observation_sandbox.get('outreach_enabled')}",
            f"- payment_enabled: {l6_controlled_observation_sandbox.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_controlled_observation_sandbox.get('revenue_execution_enabled')}",
            f"- ready_for_l6_4_real_read_only_external_observation_preflight: {l6_controlled_observation_sandbox.get('ready_for_l6_4_real_read_only_external_observation_preflight')}",
            f"- ready_for_real_network_observation: {l6_controlled_observation_sandbox.get('ready_for_real_network_observation')}",
            f"- next_recommended_milestone: {l6_controlled_observation_sandbox.get('next_recommended_milestone')}",
            f"- Warning: {l6_controlled_observation_sandbox.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.4 Real Read-Only External Observation Preflight",
            "",
            f"- l6_4_real_read_only_observation_preflight_defined: {l6_real_observation_preflight.get('l6_4_real_read_only_observation_preflight_defined')}",
            f"- preflight_only: {l6_real_observation_preflight.get('preflight_only')}",
            f"- sandbox_only: {l6_real_observation_preflight.get('sandbox_only')}",
            f"- future_real_read_only_observation_candidate_allowed: {l6_real_observation_preflight.get('future_real_read_only_observation_candidate_allowed')}",
            f"- candidate_count: {l6_real_observation_preflight.get('candidate_count')}",
            f"- approval_packet_count: {l6_real_observation_preflight.get('approval_packet_count')}",
            f"- source_allowlist_defined: {l6_real_observation_preflight.get('source_allowlist_defined')}",
            f"- source_denylist_defined: {l6_real_observation_preflight.get('source_denylist_defined')}",
            f"- operator_handoff_plan_generated: {l6_real_observation_preflight.get('operator_handoff_plan_generated')}",
            f"- network_isolation_preflight_defined: {l6_real_observation_preflight.get('network_isolation_preflight_defined')}",
            f"- evidence_capture_preflight_defined: {l6_real_observation_preflight.get('evidence_capture_preflight_defined')}",
            f"- abort_rollback_quarantine_policy_defined: {l6_real_observation_preflight.get('abort_rollback_quarantine_policy_defined')}",
            f"- no_action_guarantees_generated: {l6_real_observation_preflight.get('no_action_guarantees_generated')}",
            f"- preflight_decision_gate_generated: {l6_real_observation_preflight.get('preflight_decision_gate_generated')}",
            f"- real_external_observation_authorized: {l6_real_observation_preflight.get('real_external_observation_authorized')}",
            f"- network_enabled: {l6_real_observation_preflight.get('network_enabled')}",
            f"- scraping_enabled: {l6_real_observation_preflight.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_real_observation_preflight.get('browser_fetch_enabled')}",
            f"- publication_enabled: {l6_real_observation_preflight.get('publication_enabled')}",
            f"- outreach_enabled: {l6_real_observation_preflight.get('outreach_enabled')}",
            f"- payment_enabled: {l6_real_observation_preflight.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_real_observation_preflight.get('revenue_execution_enabled')}",
            f"- ready_for_l6_5_controlled_real_read_only_observation_pilot_design: {l6_real_observation_preflight.get('ready_for_l6_5_controlled_real_read_only_observation_pilot_design')}",
            f"- ready_for_actual_network_observation_now: {l6_real_observation_preflight.get('ready_for_actual_network_observation_now')}",
            f"- next_recommended_milestone: {l6_real_observation_preflight.get('next_recommended_milestone')}",
            f"- Warning: {l6_real_observation_preflight.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.5 Controlled Real Read-Only Observation Pilot Design",
            "",
            f"- l6_5_controlled_real_read_only_observation_pilot_design_defined: {l6_pilot_design.get('l6_5_controlled_real_read_only_observation_pilot_design_defined')}",
            f"- pilot_design_only: {l6_pilot_design.get('pilot_design_only')}",
            f"- preflight_only: {l6_pilot_design.get('preflight_only')}",
            f"- future_real_read_only_observation_pilot_candidate_allowed: {l6_pilot_design.get('future_real_read_only_observation_pilot_candidate_allowed')}",
            f"- candidate_count: {l6_pilot_design.get('candidate_count')}",
            f"- approval_packet_count: {l6_pilot_design.get('approval_packet_count')}",
            f"- pilot_scope_defined: {l6_pilot_design.get('pilot_scope_defined')}",
            f"- pilot_source_constraints_defined: {l6_pilot_design.get('pilot_source_constraints_defined')}",
            f"- pilot_approval_packet_candidates_generated: {l6_pilot_design.get('pilot_approval_packet_candidates_generated')}",
            f"- pilot_operator_runbook_generated: {l6_pilot_design.get('pilot_operator_runbook_generated')}",
            f"- pilot_evidence_packet_templates_generated: {l6_pilot_design.get('pilot_evidence_packet_templates_generated')}",
            f"- post_observation_review_workflow_defined: {l6_pilot_design.get('post_observation_review_workflow_defined')}",
            f"- abort_quarantine_policy_defined: {l6_pilot_design.get('abort_quarantine_policy_defined')}",
            f"- success_failure_criteria_defined: {l6_pilot_design.get('success_failure_criteria_defined')}",
            f"- no_action_guarantees_generated: {l6_pilot_design.get('no_action_guarantees_generated')}",
            f"- pilot_design_decision_gate_generated: {l6_pilot_design.get('pilot_design_decision_gate_generated')}",
            f"- real_external_observation_authorized: {l6_pilot_design.get('real_external_observation_authorized')}",
            f"- real_pilot_execution_authorized: {l6_pilot_design.get('real_pilot_execution_authorized')}",
            f"- network_enabled: {l6_pilot_design.get('network_enabled')}",
            f"- search_enabled: {l6_pilot_design.get('search_enabled')}",
            f"- scraping_enabled: {l6_pilot_design.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_pilot_design.get('browser_fetch_enabled')}",
            f"- publication_enabled: {l6_pilot_design.get('publication_enabled')}",
            f"- outreach_enabled: {l6_pilot_design.get('outreach_enabled')}",
            f"- payment_enabled: {l6_pilot_design.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_pilot_design.get('revenue_execution_enabled')}",
            f"- ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet: {l6_pilot_design.get('ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet')}",
            f"- ready_for_actual_network_observation_now: {l6_pilot_design.get('ready_for_actual_network_observation_now')}",
            f"- next_recommended_milestone: {l6_pilot_design.get('next_recommended_milestone')}",
            f"- Warning: {l6_pilot_design.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.6 Controlled Observation Pilot Approval Packet",
            "",
            f"- l6_6_controlled_observation_pilot_approval_packet_defined: {l6_pilot_approval.get('l6_6_controlled_observation_pilot_approval_packet_defined')}",
            f"- approval_packet_only: {l6_pilot_approval.get('approval_packet_only')}",
            f"- approval_sandbox_only: {l6_pilot_approval.get('approval_sandbox_only')}",
            f"- future_real_read_only_observation_pilot_candidate_allowed: {l6_pilot_approval.get('future_real_read_only_observation_pilot_candidate_allowed')}",
            f"- approval_candidate_count: {l6_pilot_approval.get('approval_candidate_count')}",
            f"- approval_packet_count: {l6_pilot_approval.get('approval_packet_count')}",
            f"- evidence_dossier_count: {l6_pilot_approval.get('evidence_dossier_count')}",
            f"- risk_review_count: {l6_pilot_approval.get('risk_review_count')}",
            f"- approval_authority_model_generated: {l6_pilot_approval.get('approval_authority_model_generated')}",
            f"- approval_packet_instances_generated: {l6_pilot_approval.get('approval_packet_instances_generated')}",
            f"- evidence_dossiers_generated: {l6_pilot_approval.get('evidence_dossiers_generated')}",
            f"- risk_reviews_generated: {l6_pilot_approval.get('risk_reviews_generated')}",
            f"- operator_authorization_prerequisites_generated: {l6_pilot_approval.get('operator_authorization_prerequisites_generated')}",
            f"- runtime_isolation_attestation_templates_generated: {l6_pilot_approval.get('runtime_isolation_attestation_templates_generated')}",
            f"- evidence_capture_authorization_templates_generated: {l6_pilot_approval.get('evidence_capture_authorization_templates_generated')}",
            f"- no_action_constraints_generated: {l6_pilot_approval.get('no_action_constraints_generated')}",
            f"- approval_decision_sandbox_generated: {l6_pilot_approval.get('approval_decision_sandbox_generated')}",
            f"- non_persistence_receipts_generated: {l6_pilot_approval.get('non_persistence_receipts_generated')}",
            f"- real_approval_granted: {l6_pilot_approval.get('real_approval_granted')}",
            f"- durable_real_approval_record_created: {l6_pilot_approval.get('durable_real_approval_record_created')}",
            f"- real_external_observation_authorized: {l6_pilot_approval.get('real_external_observation_authorized')}",
            f"- real_pilot_execution_authorized: {l6_pilot_approval.get('real_pilot_execution_authorized')}",
            f"- network_enabled: {l6_pilot_approval.get('network_enabled')}",
            f"- search_enabled: {l6_pilot_approval.get('search_enabled')}",
            f"- scraping_enabled: {l6_pilot_approval.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_pilot_approval.get('browser_fetch_enabled')}",
            f"- publication_enabled: {l6_pilot_approval.get('publication_enabled')}",
            f"- outreach_enabled: {l6_pilot_approval.get('outreach_enabled')}",
            f"- payment_enabled: {l6_pilot_approval.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_pilot_approval.get('revenue_execution_enabled')}",
            f"- ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox: {l6_pilot_approval.get('ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox')}",
            f"- ready_for_actual_network_observation_now: {l6_pilot_approval.get('ready_for_actual_network_observation_now')}",
            f"- ready_for_real_approval_now: {l6_pilot_approval.get('ready_for_real_approval_now')}",
            f"- ready_for_durable_approval_persistence_now: {l6_pilot_approval.get('ready_for_durable_approval_persistence_now')}",
            f"- next_recommended_milestone: {l6_pilot_approval.get('next_recommended_milestone')}",
            f"- Warning: {l6_pilot_approval.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.7 Integrated Approval Record And Pilot Readiness Sandbox",
            "",
            f"- l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined: {l6_integrated_pilot_readiness.get('l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined')}",
            f"- integrated_sandbox_only: {l6_integrated_pilot_readiness.get('integrated_sandbox_only')}",
            f"- approval_record_sandbox_only: {l6_integrated_pilot_readiness.get('approval_record_sandbox_only')}",
            f"- pilot_run_readiness_only: {l6_integrated_pilot_readiness.get('pilot_run_readiness_only')}",
            f"- sandbox_approval_record_created: {l6_integrated_pilot_readiness.get('sandbox_approval_record_created')}",
            f"- sandbox_approval_record_count: {l6_integrated_pilot_readiness.get('sandbox_approval_record_count')}",
            f"- pilot_run_package_count: {l6_integrated_pilot_readiness.get('pilot_run_package_count')}",
            f"- operator_readiness_package_created: {l6_integrated_pilot_readiness.get('operator_readiness_package_created')}",
            f"- runtime_isolation_readiness_created: {l6_integrated_pilot_readiness.get('runtime_isolation_readiness_created')}",
            f"- evidence_capture_readiness_created: {l6_integrated_pilot_readiness.get('evidence_capture_readiness_created')}",
            f"- post_observation_review_readiness_created: {l6_integrated_pilot_readiness.get('post_observation_review_readiness_created')}",
            f"- manual_evidence_import_readiness_created: {l6_integrated_pilot_readiness.get('manual_evidence_import_readiness_created')}",
            f"- integrated_decision_gate_created: {l6_integrated_pilot_readiness.get('integrated_decision_gate_created')}",
            f"- no_action_receipts_created: {l6_integrated_pilot_readiness.get('no_action_receipts_created')}",
            f"- real_approval_granted: {l6_integrated_pilot_readiness.get('real_approval_granted')}",
            f"- durable_real_approval_record_created: {l6_integrated_pilot_readiness.get('durable_real_approval_record_created')}",
            f"- real_external_observation_authorized: {l6_integrated_pilot_readiness.get('real_external_observation_authorized')}",
            f"- real_pilot_execution_authorized: {l6_integrated_pilot_readiness.get('real_pilot_execution_authorized')}",
            f"- network_enabled: {l6_integrated_pilot_readiness.get('network_enabled')}",
            f"- search_enabled: {l6_integrated_pilot_readiness.get('search_enabled')}",
            f"- scraping_enabled: {l6_integrated_pilot_readiness.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_integrated_pilot_readiness.get('browser_fetch_enabled')}",
            f"- publication_enabled: {l6_integrated_pilot_readiness.get('publication_enabled')}",
            f"- outreach_enabled: {l6_integrated_pilot_readiness.get('outreach_enabled')}",
            f"- payment_enabled: {l6_integrated_pilot_readiness.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_integrated_pilot_readiness.get('revenue_execution_enabled')}",
            f"- ready_for_l6_8_user_mediated_manual_evidence_import_pilot: {l6_integrated_pilot_readiness.get('ready_for_l6_8_user_mediated_manual_evidence_import_pilot')}",
            f"- ready_for_actual_network_observation_now: {l6_integrated_pilot_readiness.get('ready_for_actual_network_observation_now')}",
            f"- ready_for_real_approval_now: {l6_integrated_pilot_readiness.get('ready_for_real_approval_now')}",
            f"- ready_for_durable_real_approval_persistence_now: {l6_integrated_pilot_readiness.get('ready_for_durable_real_approval_persistence_now')}",
            f"- next_recommended_milestone: {l6_integrated_pilot_readiness.get('next_recommended_milestone')}",
            f"- Warning: {l6_integrated_pilot_readiness.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.8 Agentic Evidence Discovery Trust Engine",
            "",
            f"- l6_8_agentic_evidence_discovery_trust_engine_defined: {l6_agentic_evidence.get('l6_8_agentic_evidence_discovery_trust_engine_defined')}",
            f"- mode: {l6_agentic_evidence.get('mode')}",
            f"- agentic_evidence_discovery_design_and_sandbox_only: {l6_agentic_evidence.get('agentic_evidence_discovery_design_and_sandbox_only')}",
            f"- autonomous_evidence_need_inference_authorized: {l6_agentic_evidence.get('autonomous_evidence_need_inference_authorized')}",
            f"- autonomous_source_hypothesis_generation_authorized: {l6_agentic_evidence.get('autonomous_source_hypothesis_generation_authorized')}",
            f"- autonomous_evidence_value_judgment_authorized: {l6_agentic_evidence.get('autonomous_evidence_value_judgment_authorized')}",
            f"- autonomous_trust_assessment_authorized: {l6_agentic_evidence.get('autonomous_trust_assessment_authorized')}",
            f"- observation_work_order_generation_authorized: {l6_agentic_evidence.get('observation_work_order_generation_authorized')}",
            f"- evidence_need_count: {l6_agentic_evidence.get('evidence_need_count')}",
            f"- source_hypothesis_count: {l6_agentic_evidence.get('source_hypothesis_count')}",
            f"- ranked_source_hypothesis_count: {l6_agentic_evidence.get('ranked_source_hypothesis_count')}",
            f"- observation_work_order_count: {l6_agentic_evidence.get('observation_work_order_count')}",
            f"- rejected_source_hypothesis_count: {l6_agentic_evidence.get('rejected_source_hypothesis_count')}",
            f"- source_type_value_model_generated: {l6_agentic_evidence.get('source_type_value_model_generated')}",
            f"- structural_trust_judgment_generated: {l6_agentic_evidence.get('structural_trust_judgment_generated')}",
            f"- value_of_information_model_generated: {l6_agentic_evidence.get('value_of_information_model_generated')}",
            f"- conflict_corroboration_model_generated: {l6_agentic_evidence.get('conflict_corroboration_model_generated')}",
            f"- pre_observation_rejection_filter_generated: {l6_agentic_evidence.get('pre_observation_rejection_filter_generated')}",
            f"- agentic_evidence_decision_gate_generated: {l6_agentic_evidence.get('agentic_evidence_decision_gate_generated')}",
            f"- no_action_receipts_generated: {l6_agentic_evidence.get('no_action_receipts_generated')}",
            f"- real_external_observation_authorized: {l6_agentic_evidence.get('real_external_observation_authorized')}",
            f"- agent_external_fetch_authorized: {l6_agentic_evidence.get('agent_external_fetch_authorized')}",
            f"- network_enabled: {l6_agentic_evidence.get('network_enabled')}",
            f"- search_enabled: {l6_agentic_evidence.get('search_enabled')}",
            f"- scraping_enabled: {l6_agentic_evidence.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_agentic_evidence.get('browser_fetch_enabled')}",
            f"- publication_enabled: {l6_agentic_evidence.get('publication_enabled')}",
            f"- outreach_enabled: {l6_agentic_evidence.get('outreach_enabled')}",
            f"- payment_enabled: {l6_agentic_evidence.get('payment_enabled')}",
            f"- revenue_execution_enabled: {l6_agentic_evidence.get('revenue_execution_enabled')}",
            f"- ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval: {l6_agentic_evidence.get('ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval')}",
            f"- ready_for_actual_network_observation_now: {l6_agentic_evidence.get('ready_for_actual_network_observation_now')}",
            f"- ready_for_autonomous_web_search_now: {l6_agentic_evidence.get('ready_for_autonomous_web_search_now')}",
            f"- next_recommended_milestone: {l6_agentic_evidence.get('next_recommended_milestone')}",
            f"- Warning: {l6_agentic_evidence.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.9 Controlled Agentic Evidence Pilot Approval Dry-Run",
            "",
            f"- l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined: {l6_agentic_pilot_dry_run.get('l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined')}",
            f"- mode: {l6_agentic_pilot_dry_run.get('mode')}",
            f"- pilot_approval_and_dry_run_only: {l6_agentic_pilot_dry_run.get('pilot_approval_and_dry_run_only')}",
            f"- sandbox_approval_record_only: {l6_agentic_pilot_dry_run.get('sandbox_approval_record_only')}",
            f"- selected_work_order_count: {l6_agentic_pilot_dry_run.get('selected_work_order_count')}",
            f"- approval_packet_count: {l6_agentic_pilot_dry_run.get('approval_packet_count')}",
            f"- sandbox_approval_record_count: {l6_agentic_pilot_dry_run.get('sandbox_approval_record_count')}",
            f"- dry_run_trace_count: {l6_agentic_pilot_dry_run.get('dry_run_trace_count')}",
            f"- empty_evidence_packet_count: {l6_agentic_pilot_dry_run.get('empty_evidence_packet_count')}",
            f"- post_run_review_packet_count: {l6_agentic_pilot_dry_run.get('post_run_review_packet_count')}",
            f"- real_external_observation_authorized: {l6_agentic_pilot_dry_run.get('real_external_observation_authorized')}",
            f"- real_pilot_execution_authorized: {l6_agentic_pilot_dry_run.get('real_pilot_execution_authorized')}",
            f"- real_approval_granted: {l6_agentic_pilot_dry_run.get('real_approval_granted')}",
            f"- durable_real_approval_record_created: {l6_agentic_pilot_dry_run.get('durable_real_approval_record_created')}",
            f"- network_enabled: {l6_agentic_pilot_dry_run.get('network_enabled')}",
            f"- search_enabled: {l6_agentic_pilot_dry_run.get('search_enabled')}",
            f"- scraping_enabled: {l6_agentic_pilot_dry_run.get('scraping_enabled')}",
            f"- browser_fetch_enabled: {l6_agentic_pilot_dry_run.get('browser_fetch_enabled')}",
            f"- ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot: {l6_agentic_pilot_dry_run.get('ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot')}",
            f"- ready_for_actual_network_observation_now: {l6_agentic_pilot_dry_run.get('ready_for_actual_network_observation_now')}",
            f"- ready_for_autonomous_web_search_now: {l6_agentic_pilot_dry_run.get('ready_for_autonomous_web_search_now')}",
            f"- next_recommended_milestone: {l6_agentic_pilot_dry_run.get('next_recommended_milestone')}",
            f"- Warning: {l6_agentic_pilot_dry_run.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10 Tiny Real Read-Only Agentic Evidence Observation Pilot",
            "",
            f"- l6_10_tiny_real_read_only_observation_pilot_defined: {l6_tiny_observation_pilot.get('l6_10_tiny_real_read_only_observation_pilot_defined')}",
            f"- mode: {l6_tiny_observation_pilot.get('mode')}",
            f"- selected_work_order_count: {l6_tiny_observation_pilot.get('selected_work_order_count')}",
            f"- source_locator_resolved: {l6_tiny_observation_pilot.get('source_locator_resolved')}",
            f"- observation_executed: {l6_tiny_observation_pilot.get('observation_executed')}",
            f"- blocked_pilot: {l6_tiny_observation_pilot.get('blocked_pilot')}",
            f"- external_requests_count: {l6_tiny_observation_pilot.get('external_requests_count')}",
            f"- pages_read_count: {l6_tiny_observation_pilot.get('pages_read_count')}",
            f"- search_queries_count: {l6_tiny_observation_pilot.get('search_queries_count')}",
            f"- evidence_packet_generated: {l6_tiny_observation_pilot.get('evidence_packet_generated')}",
            f"- post_observation_review_packet_generated: {l6_tiny_observation_pilot.get('post_observation_review_packet_generated')}",
            f"- artifact_refinement_candidate_generated: {l6_tiny_observation_pilot.get('artifact_refinement_candidate_generated')}",
            f"- artifact_refinement_applied: {l6_tiny_observation_pilot.get('artifact_refinement_applied')}",
            f"- broad_web_search_authorized: {l6_tiny_observation_pilot.get('broad_web_search_authorized')}",
            f"- crawling_authorized: {l6_tiny_observation_pilot.get('crawling_authorized')}",
            f"- scraping_authorized: {l6_tiny_observation_pilot.get('scraping_authorized')}",
            f"- browser_automation_authorized: {l6_tiny_observation_pilot.get('browser_automation_authorized')}",
            f"- publication_authorized: {l6_tiny_observation_pilot.get('publication_authorized')}",
            f"- outreach_authorized: {l6_tiny_observation_pilot.get('outreach_authorized')}",
            f"- payment_authorized: {l6_tiny_observation_pilot.get('payment_authorized')}",
            f"- revenue_execution_authorized: {l6_tiny_observation_pilot.get('revenue_execution_authorized')}",
            f"- ready_for_retry_after_condition_resolved: {l6_tiny_observation_pilot.get('ready_for_retry_after_condition_resolved')}",
            f"- next_recommended_milestone: {l6_tiny_observation_pilot.get('next_recommended_milestone')}",
            f"- Warning: {l6_tiny_observation_pilot.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10R Controlled Source Locator Resolution And Tiny Observation Retry",
            "",
            f"- l6_10r_controlled_source_locator_resolution_retry_defined: {l6_10r_locator_retry.get('l6_10r_controlled_source_locator_resolution_retry_defined')}",
            f"- mode: {l6_10r_locator_retry.get('mode')}",
            f"- selected_work_order_count: {l6_10r_locator_retry.get('selected_work_order_count')}",
            f"- locator_discovery_executed: {l6_10r_locator_retry.get('locator_discovery_executed')}",
            f"- locator_discovery_queries_count: {l6_10r_locator_retry.get('locator_discovery_queries_count')}",
            f"- concrete_locator_resolved: {l6_10r_locator_retry.get('concrete_locator_resolved')}",
            f"- locator_eligible_for_observation: {l6_10r_locator_retry.get('locator_eligible_for_observation')}",
            f"- retry_observation_authorized: {l6_10r_locator_retry.get('retry_observation_authorized')}",
            f"- tiny_read_only_observation_executed: {l6_10r_locator_retry.get('tiny_read_only_observation_executed')}",
            f"- external_reads_total: {l6_10r_locator_retry.get('external_reads_total')}",
            f"- pages_read_count: {l6_10r_locator_retry.get('pages_read_count')}",
            f"- evidence_packet_generated: {l6_10r_locator_retry.get('evidence_packet_generated')}",
            f"- live_source_evidence_captured: {l6_10r_locator_retry.get('live_source_evidence_captured')}",
            f"- post_observation_review_packet_generated: {l6_10r_locator_retry.get('post_observation_review_packet_generated')}",
            f"- artifact_refinement_candidate_generated: {l6_10r_locator_retry.get('artifact_refinement_candidate_generated')}",
            f"- artifact_refinement_applied: {l6_10r_locator_retry.get('artifact_refinement_applied')}",
            f"- broad_web_search_authorized: {l6_10r_locator_retry.get('broad_web_search_authorized')}",
            f"- repeated_search_loop_authorized: {l6_10r_locator_retry.get('repeated_search_loop_authorized')}",
            f"- crawling_authorized: {l6_10r_locator_retry.get('crawling_authorized')}",
            f"- scraping_authorized: {l6_10r_locator_retry.get('scraping_authorized')}",
            f"- browser_automation_authorized: {l6_10r_locator_retry.get('browser_automation_authorized')}",
            f"- remaining_blocker: {l6_10r_locator_retry.get('remaining_blocker')}",
            f"- next_recommended_milestone: {l6_10r_locator_retry.get('next_recommended_milestone')}",
            f"- Warning: {l6_10r_locator_retry.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10T Governed Toolmaking Locator Resolver",
            "",
            f"- l6_10t_governed_capability_gap_toolmaking_defined: {l6_10t_toolmaking_locator_resolver.get('l6_10t_governed_capability_gap_toolmaking_defined')}",
            f"- mode: {l6_10t_toolmaking_locator_resolver.get('mode')}",
            f"- os_neutral_design_required: {l6_10t_toolmaking_locator_resolver.get('os_neutral_design_required')}",
            f"- mac_only_solution_allowed: {l6_10t_toolmaking_locator_resolver.get('mac_only_solution_allowed')}",
            f"- primary_gap_type: {l6_10t_toolmaking_locator_resolver.get('primary_gap_type')}",
            f"- secondary_gap_type: {l6_10t_toolmaking_locator_resolver.get('secondary_gap_type')}",
            f"- governed_toolmaking_methodology_created: {l6_10t_toolmaking_locator_resolver.get('governed_toolmaking_methodology_created')}",
            f"- controlled_tool_contract_model_created: {l6_10t_toolmaking_locator_resolver.get('controlled_tool_contract_model_created')}",
            f"- resolver_capability_probe_executed: {l6_10t_toolmaking_locator_resolver.get('resolver_capability_probe_executed')}",
            f"- capability_probe_local_only: {l6_10t_toolmaking_locator_resolver.get('capability_probe_local_only')}",
            f"- probe_used_network: {l6_10t_toolmaking_locator_resolver.get('probe_used_network')}",
            f"- controlled_resolver_adapter_available: {l6_10t_toolmaking_locator_resolver.get('controlled_resolver_adapter_available')}",
            f"- selected_resolver_adapter_id: {l6_10t_toolmaking_locator_resolver.get('selected_resolver_adapter_id')}",
            f"- resolver_mode: {l6_10t_toolmaking_locator_resolver.get('resolver_mode')}",
            f"- capability_gap_code: {l6_10t_toolmaking_locator_resolver.get('capability_gap_code')}",
            f"- locator_discovery_executed: {l6_10t_toolmaking_locator_resolver.get('locator_discovery_executed')}",
            f"- locator_discovery_queries_count: {l6_10t_toolmaking_locator_resolver.get('locator_discovery_queries_count')}",
            f"- concrete_locator_resolved: {l6_10t_toolmaking_locator_resolver.get('concrete_locator_resolved')}",
            f"- tiny_read_only_observation_executed: {l6_10t_toolmaking_locator_resolver.get('tiny_read_only_observation_executed')}",
            f"- evidence_packet_generated: {l6_10t_toolmaking_locator_resolver.get('evidence_packet_generated')}",
            f"- generated_tools_granted_live_authority: {l6_10t_toolmaking_locator_resolver.get('generated_tools_granted_live_authority')}",
            f"- artifact_refinement_applied: {l6_10t_toolmaking_locator_resolver.get('artifact_refinement_applied')}",
            f"- general_governed_toolmaking_methodology_ready_for_reuse: {l6_10t_toolmaking_locator_resolver.get('general_governed_toolmaking_methodology_ready_for_reuse')}",
            f"- remaining_blocker: {l6_10t_toolmaking_locator_resolver.get('remaining_blocker')}",
            f"- next_recommended_milestone: {l6_10t_toolmaking_locator_resolver.get('next_recommended_milestone')}",
            f"- Warning: {l6_10t_toolmaking_locator_resolver.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10U Controlled Locator Resolver Enablement",
            "",
            f"- l6_10u_controlled_locator_resolver_enablement_complete: {l6_10u_locator_resolver_enablement.get('l6_10u_controlled_locator_resolver_enablement_complete')}",
            f"- mode: {l6_10u_locator_resolver_enablement.get('mode')}",
            f"- resolver_runtime_created: {l6_10u_locator_resolver_enablement.get('resolver_runtime_created')}",
            f"- seed_registry_resolver_created: {l6_10u_locator_resolver_enablement.get('seed_registry_resolver_created')}",
            f"- environment_gated_search_resolver_created: {l6_10u_locator_resolver_enablement.get('environment_gated_search_resolver_created')}",
            f"- disabled_resolver_created: {l6_10u_locator_resolver_enablement.get('disabled_resolver_created')}",
            f"- selected_work_order_id: {l6_10u_locator_resolver_enablement.get('selected_work_order_id')}",
            f"- source_selected_work_order_id: {l6_10u_locator_resolver_enablement.get('source_selected_work_order_id')}",
            f"- resolver_mode_used: {l6_10u_locator_resolver_enablement.get('resolver_mode_used')}",
            f"- resolver_id: {l6_10u_locator_resolver_enablement.get('resolver_id')}",
            f"- seed_registry_lookup_executed: {l6_10u_locator_resolver_enablement.get('seed_registry_lookup_executed')}",
            f"- seed_registry_lookup_count: {l6_10u_locator_resolver_enablement.get('seed_registry_lookup_count')}",
            f"- controlled_search_executed: {l6_10u_locator_resolver_enablement.get('controlled_search_executed')}",
            f"- search_query_count: {l6_10u_locator_resolver_enablement.get('search_query_count')}",
            f"- external_reads_count: {l6_10u_locator_resolver_enablement.get('external_reads_count')}",
            f"- concrete_locator_resolved: {l6_10u_locator_resolver_enablement.get('concrete_locator_resolved')}",
            f"- resolved_locator: {l6_10u_locator_resolver_enablement.get('resolved_locator')}",
            f"- tiny_read_only_observation_executed: {l6_10u_locator_resolver_enablement.get('tiny_read_only_observation_executed')}",
            f"- evidence_packet_generated: {l6_10u_locator_resolver_enablement.get('evidence_packet_generated')}",
            f"- live_source_evidence_captured: {l6_10u_locator_resolver_enablement.get('live_source_evidence_captured')}",
            f"- artifact_refinement_applied: {l6_10u_locator_resolver_enablement.get('artifact_refinement_applied')}",
            f"- broad_search_authorized: {l6_10u_locator_resolver_enablement.get('broad_search_authorized')}",
            f"- repeated_search_loop_authorized: {l6_10u_locator_resolver_enablement.get('repeated_search_loop_authorized')}",
            f"- crawling_authorized: {l6_10u_locator_resolver_enablement.get('crawling_authorized')}",
            f"- scraping_authorized: {l6_10u_locator_resolver_enablement.get('scraping_authorized')}",
            f"- browser_automation_authorized: {l6_10u_locator_resolver_enablement.get('browser_automation_authorized')}",
            f"- remaining_blocker: {l6_10u_locator_resolver_enablement.get('remaining_blocker')}",
            f"- next_recommended_milestone: {l6_10u_locator_resolver_enablement.get('next_recommended_milestone')}",
            f"- Warning: {l6_10u_locator_resolver_enablement.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10V Controlled Seed Locator Or Search Resolver Enablement",
            "",
            f"- l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete: {l6_10v_seed_or_search_resolver_enablement.get('l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete')}",
            f"- mode: {l6_10v_seed_or_search_resolver_enablement.get('mode')}",
            f"- reviewed_seed_locator_registry_created: {l6_10v_seed_or_search_resolver_enablement.get('reviewed_seed_locator_registry_created')}",
            f"- explicit_controlled_search_resolver_created: {l6_10v_seed_or_search_resolver_enablement.get('explicit_controlled_search_resolver_created')}",
            f"- selected_work_order_id: {l6_10v_seed_or_search_resolver_enablement.get('selected_work_order_id')}",
            f"- source_selected_work_order_id: {l6_10v_seed_or_search_resolver_enablement.get('source_selected_work_order_id')}",
            f"- resolution_path_used: {l6_10v_seed_or_search_resolver_enablement.get('resolution_path_used')}",
            f"- seed_registry_lookup_executed: {l6_10v_seed_or_search_resolver_enablement.get('seed_registry_lookup_executed')}",
            f"- seed_registry_lookup_count: {l6_10v_seed_or_search_resolver_enablement.get('seed_registry_lookup_count')}",
            f"- reviewed_seed_locator_count: {l6_10v_seed_or_search_resolver_enablement.get('reviewed_seed_locator_count')}",
            f"- seed_locator_resolved: {l6_10v_seed_or_search_resolver_enablement.get('seed_locator_resolved')}",
            f"- controlled_search_enabled: {l6_10v_seed_or_search_resolver_enablement.get('controlled_search_enabled')}",
            f"- controlled_search_executed: {l6_10v_seed_or_search_resolver_enablement.get('controlled_search_executed')}",
            f"- controlled_search_query_count: {l6_10v_seed_or_search_resolver_enablement.get('controlled_search_query_count')}",
            f"- external_reads_count: {l6_10v_seed_or_search_resolver_enablement.get('external_reads_count')}",
            f"- concrete_locator_resolved: {l6_10v_seed_or_search_resolver_enablement.get('concrete_locator_resolved')}",
            f"- resolved_locator: {l6_10v_seed_or_search_resolver_enablement.get('resolved_locator')}",
            f"- tiny_read_only_observation_executed: {l6_10v_seed_or_search_resolver_enablement.get('tiny_read_only_observation_executed')}",
            f"- evidence_packet_generated: {l6_10v_seed_or_search_resolver_enablement.get('evidence_packet_generated')}",
            f"- live_source_evidence_captured: {l6_10v_seed_or_search_resolver_enablement.get('live_source_evidence_captured')}",
            f"- broad_search_authorized: {l6_10v_seed_or_search_resolver_enablement.get('broad_search_authorized')}",
            f"- repeated_search_loop_authorized: {l6_10v_seed_or_search_resolver_enablement.get('repeated_search_loop_authorized')}",
            f"- crawling_authorized: {l6_10v_seed_or_search_resolver_enablement.get('crawling_authorized')}",
            f"- scraping_authorized: {l6_10v_seed_or_search_resolver_enablement.get('scraping_authorized')}",
            f"- browser_automation_authorized: {l6_10v_seed_or_search_resolver_enablement.get('browser_automation_authorized')}",
            f"- remaining_blocker: {l6_10v_seed_or_search_resolver_enablement.get('remaining_blocker')}",
            f"- next_recommended_milestone: {l6_10v_seed_or_search_resolver_enablement.get('next_recommended_milestone')}",
            f"- Warning: {l6_10v_seed_or_search_resolver_enablement.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10W Reviewed Seed Locator Injection Tiny Retry",
            "",
            f"- l6_10w_reviewed_seed_locator_injection_tiny_retry_complete: {l6_10w_reviewed_seed_locator_injection.get('l6_10w_reviewed_seed_locator_injection_tiny_retry_complete')}",
            f"- mode: {l6_10w_reviewed_seed_locator_injection.get('mode')}",
            f"- selected_work_order_id: {l6_10w_reviewed_seed_locator_injection.get('selected_work_order_id')}",
            f"- reviewed_seed_locator_found: {l6_10w_reviewed_seed_locator_injection.get('reviewed_seed_locator_found')}",
            f"- concrete_locator: {l6_10w_reviewed_seed_locator_injection.get('concrete_locator')}",
            f"- user_action_required_generated: {l6_10w_reviewed_seed_locator_injection.get('user_action_required_generated')}",
            f"- requested_item: {l6_10w_reviewed_seed_locator_injection.get('requested_item')}",
            f"- retry_attempted: {l6_10w_reviewed_seed_locator_injection.get('retry_attempted')}",
            f"- tiny_read_only_observation_executed: {l6_10w_reviewed_seed_locator_injection.get('tiny_read_only_observation_executed')}",
            f"- external_reads_count: {l6_10w_reviewed_seed_locator_injection.get('external_reads_count')}",
            f"- pages_read_count: {l6_10w_reviewed_seed_locator_injection.get('pages_read_count')}",
            f"- evidence_packet_generated: {l6_10w_reviewed_seed_locator_injection.get('evidence_packet_generated')}",
            f"- live_source_evidence_captured: {l6_10w_reviewed_seed_locator_injection.get('live_source_evidence_captured')}",
            f"- url_invention_authorized: {l6_10w_reviewed_seed_locator_injection.get('url_invention_authorized')}",
            f"- fake_locator_authorized: {l6_10w_reviewed_seed_locator_injection.get('fake_locator_authorized')}",
            f"- broad_search_authorized: {l6_10w_reviewed_seed_locator_injection.get('broad_search_authorized')}",
            f"- crawling_authorized: {l6_10w_reviewed_seed_locator_injection.get('crawling_authorized')}",
            f"- scraping_authorized: {l6_10w_reviewed_seed_locator_injection.get('scraping_authorized')}",
            f"- browser_automation_authorized: {l6_10w_reviewed_seed_locator_injection.get('browser_automation_authorized')}",
            f"- remaining_blocker: {l6_10w_reviewed_seed_locator_injection.get('remaining_blocker')}",
            f"- next_recommended_milestone: {l6_10w_reviewed_seed_locator_injection.get('next_recommended_milestone')}",
            f"- Warning: {l6_10w_reviewed_seed_locator_injection.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## L6.10X Budgeted Controlled External Search Evidence Pilot",
            "",
            f"- l6_10x_budgeted_controlled_external_search_evidence_pilot_complete: {l6_10x_budgeted_controlled_search.get('l6_10x_budgeted_controlled_external_search_evidence_pilot_complete')}",
            f"- mode: {l6_10x_budgeted_controlled_search.get('mode')}",
            f"- selected_work_order_id: {l6_10x_budgeted_controlled_search.get('selected_work_order_id')}",
            f"- query_count: {l6_10x_budgeted_controlled_search.get('query_count')}",
            f"- search_backend_mode: {l6_10x_budgeted_controlled_search.get('search_backend_mode')}",
            f"- backend_missing: {l6_10x_budgeted_controlled_search.get('backend_missing')}",
            f"- search_executed: {l6_10x_budgeted_controlled_search.get('search_executed')}",
            f"- search_results_considered: {l6_10x_budgeted_controlled_search.get('search_results_considered')}",
            f"- pages_opened: {l6_10x_budgeted_controlled_search.get('pages_opened')}",
            f"- domains_touched: {l6_10x_budgeted_controlled_search.get('domains_touched')}",
            f"- crawl_depth_used: {l6_10x_budgeted_controlled_search.get('crawl_depth_used')}",
            f"- evidence_packets_generated: {l6_10x_budgeted_controlled_search.get('evidence_packets_generated')}",
            f"- conflicts_found: {l6_10x_budgeted_controlled_search.get('conflicts_found')}",
            f"- manual_url_request_avoided: {l6_10x_budgeted_controlled_search.get('manual_url_request_avoided')}",
            f"- ask_user_for_url_authorized: {l6_10x_budgeted_controlled_search.get('ask_user_for_url_authorized')}",
            f"- user_manual_url_provision_required: {l6_10x_budgeted_controlled_search.get('user_manual_url_provision_required')}",
            f"- controlled_external_search_authorized: {l6_10x_budgeted_controlled_search.get('controlled_external_search_authorized')}",
            f"- bounded_crawl_authorized: {l6_10x_budgeted_controlled_search.get('bounded_crawl_authorized')}",
            f"- login_authorized: {l6_10x_budgeted_controlled_search.get('login_authorized')}",
            f"- payment_authorized: {l6_10x_budgeted_controlled_search.get('payment_authorized')}",
            f"- publication_authorized: {l6_10x_budgeted_controlled_search.get('publication_authorized')}",
            f"- outreach_authorized: {l6_10x_budgeted_controlled_search.get('outreach_authorized')}",
            f"- revenue_execution_authorized: {l6_10x_budgeted_controlled_search.get('revenue_execution_authorized')}",
            f"- mcp_execution_authorized: {l6_10x_budgeted_controlled_search.get('mcp_execution_authorized')}",
            f"- remaining_blocker: {l6_10x_budgeted_controlled_search.get('remaining_blocker')}",
            f"- next_step: {l6_10x_budgeted_controlled_search.get('next_step')}",
            f"- Warning: {l6_10x_budgeted_controlled_search.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governance Boundary",
            "",
            snapshot["governance_summary"]["principle"],
            "",
            "## Data Safety Boundary",
            "",
            "Console reads curated read-model files only. It must not read DBs, logs, active-agent markers, daemon state, or raw runtime state directly.",
            "",
            "## Next Recommended Steps",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in readiness["recommended_next_steps"]])
    lines.extend(["", "## Warnings / Gaps", ""])
    for item in snapshot["warnings"] + snapshot["open_gaps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def print_report(status: str, files_read: list[str], generated_files: list[str], agents: list[str], warnings: list[str]) -> None:
    print(f"Team Console Snapshot Loader: {status}")
    print(f"Files read: {len(files_read)}")
    print(f"Files generated: {len(generated_files)}")
    print(f"Agents included: {', '.join(agents)}")
    print(f"Warnings: {len(warnings)}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    print("\nFiles read:")
    for item in files_read:
        print(f"- {item}")
    print("\nFiles generated:")
    for item in generated_files:
        print(f"- {item}")


def main() -> int:
    try:
        files_read, generated_files, agents, warnings = build()
    except Exception as exc:
        print(f"Team Console Snapshot Loader: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report("PASS", files_read, generated_files, agents, warnings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
