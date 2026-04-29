#!/usr/bin/env python3
"""Run safe local checks for the curated Y* company read-model stack."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Check:
    label: str
    command: list[str]
    mutates_generated_files: bool = False


REBUILD_CHECKS = [
    Check(
        "Build runtime artifact manifest",
        ["python3", "runtime_artifact_quarantine/tools/build_runtime_artifact_manifest.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build Markdown report safe-mining candidates",
        ["python3", "runtime_artifact_quarantine/safe_mining/tools/build_markdown_report_candidates.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build candidate review queue",
        ["python3", "runtime_artifact_quarantine/safe_mining/review_queue/tools/build_candidate_review_queue.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build artifact disposition index",
        ["python3", "runtime_artifact_quarantine/backlog_disposition/tools/build_artifact_disposition_index.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build evidence review pack",
        ["python3", "runtime_artifact_quarantine/evidence_review/tools/build_evidence_review_pack.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build Labs-Gov hook envelope",
        ["python3", "labs_governance_bridge/tools/build_labs_hook_envelope.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Run Labs-Gov dry-run bridge",
        ["python3", "labs_governance_bridge/tools/run_labs_gov_dry_run.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build multi-role Pre-U packets",
        ["python3", "labs_governance_bridge/pre_u_generator/tools/build_pre_u_packets.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build Pre-U hook envelopes",
        ["python3", "labs_governance_bridge/pre_u_generator/tools/build_hook_envelopes_from_packets.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Run multi-role Pre-U governance dry-run",
        ["python3", "labs_governance_bridge/pre_u_generator/tools/run_pre_u_governance_dry_run.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build team console snapshot",
        ["python3", "console_read_model/loader/build_team_console_snapshot.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build live readiness report",
        ["python3", "labs_live_readiness/tools/build_live_readiness_report.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build live boundary manifest",
        ["python3", "labs_live_boundary/tools/build_live_boundary_manifest.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build CIEU runtime boundary",
        ["python3", "labs_cieu_runtime_boundary/tools/build_cieu_runtime_boundary.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build company autonomy inventory",
        ["python3", "company_autonomy_inventory/tools/build_company_autonomy_inventory.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build autonomous work cycle simulator",
        ["python3", "company_autonomous_work_cycle/tools/build_autonomous_work_cycle.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build legacy asset triage",
        ["python3", "legacy_asset_triage/tools/build_legacy_asset_triage.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build governed observation loop",
        ["python3", "governed_observation_loop/tools/build_governed_observation_loop.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build governed read-only observation tool artifacts",
        ["python3", "governed_readonly_observation_tool/tools/build_readonly_observation_tool_artifacts.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build governed tool invocation bridge",
        ["python3", "governed_tool_invocation_bridge/tools/build_tool_invocation_bridge.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build agent team work proposal",
        ["python3", "agent_team_work_proposal/tools/build_agent_team_work_proposal.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build mission dashboard refresh loop",
        ["python3", "mission_dashboard_refresh_loop/tools/build_mission_dashboard_refresh_loop.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build recurring observation loop contract",
        ["python3", "recurring_observation_loop_contract/tools/build_recurring_observation_contract.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build manual recurring observation tick runner",
        ["python3", "manual_recurring_observation_tick_runner/tools/build_manual_tick_runner.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build field functional archaeology",
        ["python3", "field_functional_archaeology/tools/build_field_functional_archaeology.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build mission field projection harness",
        ["python3", "mission_field_projection_contract/tools/build_mission_field_projection_harness.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build field functional auto-projection core",
        ["python3", "field_functional_auto_projection_core/tools/build_field_functional_auto_projection_core.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build projection-checked autonomous work cycle",
        ["python3", "projection_checked_autonomous_work_cycle/tools/build_projection_checked_autonomous_work_cycle.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build review-gated shadow learning cycle",
        ["python3", "review_gated_shadow_learning_cycle/tools/build_review_gated_shadow_learning_cycle.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build cross-repo governance contract proof",
        ["python3", "cross_repo_governance_contract_proof/tools/build_cross_repo_governance_contract_proof.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build governed MCP dry-run adapter",
        ["python3", "governed_mcp_dry_run_adapter/tools/build_governed_mcp_dry_run_adapter.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build controlled canonical learning design",
        ["python3", "controlled_canonical_learning_design/tools/build_controlled_canonical_learning_design.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build approved canonical update sandbox",
        ["python3", "approved_canonical_update_sandbox/tools/build_approved_canonical_update_sandbox.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build real approval workflow boundary",
        ["python3", "real_approval_workflow_boundary/tools/build_real_approval_workflow_boundary.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build controlled approval record sandbox",
        ["python3", "controlled_approval_record_sandbox/tools/build_controlled_approval_record_sandbox.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build controlled real release preflight",
        ["python3", "controlled_real_release_preflight/tools/build_controlled_real_release_preflight.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build real release simulation sandbox",
        ["python3", "real_release_simulation_sandbox/tools/build_real_release_simulation_sandbox.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build live boundary no-go framework",
        ["python3", "live_boundary_no_go_framework/tools/build_live_boundary_no_go_framework.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build L6 meta-development generative selection engine",
        ["python3", "l6_meta_development_generative_selection_engine/tools/build_l6_meta_development_generative_selection_engine.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build L6.1 MVP artifact sandbox",
        ["python3", "l6_meta_development_mvp_artifact_sandbox/tools/build_l6_meta_development_mvp_artifact_sandbox.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Refresh team console snapshot after L6.1 MVP artifact sandbox",
        ["python3", "console_read_model/loader/build_team_console_snapshot.py"],
        mutates_generated_files=True,
    ),
]

VALIDATION_CHECKS = [
    Check(
        "Validate JSON: team_console_snapshot.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/team_console_snapshot.json"],
    ),
    Check(
        "Validate JSON: quarantine_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/quarantine_summary.json"],
    ),
    Check(
        "Validate JSON: safe_mining_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/safe_mining_summary.json"],
    ),
    Check(
        "Validate JSON: review_queue_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/review_queue_summary.json"],
    ),
    Check(
        "Validate JSON: artifact_disposition_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/artifact_disposition_summary.json"],
    ),
    Check(
        "Validate JSON: evidence_review_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/evidence_review_summary.json"],
    ),
    Check(
        "Validate JSON: governance_bridge_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/governance_bridge_summary.json"],
    ),
    Check(
        "Validate JSON: pre_u_governance_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/pre_u_governance_summary.json"],
    ),
    Check(
        "Compile labs runtime acceptance runner",
        ["python3", "-m", "py_compile", "labs_runtime_acceptance/tools/run_labs_runtime_acceptance.py"],
    ),
    Check(
        "Validate JSON: labs_acceptance_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/labs_acceptance_summary.json"],
    ),
    Check(
        "Validate JSON: labs_runtime_acceptance_report.json",
        ["python3", "-m", "json.tool", "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json"],
    ),
    Check(
        "Validate JSON: labs_runtime_acceptance_manifest.json",
        ["python3", "-m", "json.tool", "labs_runtime_acceptance/generated/labs_runtime_acceptance_manifest.json"],
    ),
    Check(
        "Compile cross-repo alignment tools",
        [
            "python3",
            "-m",
            "py_compile",
            "cross_repo_alignment/tools/build_cross_repo_status_manifest.py",
            "cross_repo_alignment/tools/run_cross_repo_alignment_acceptance.py",
        ],
    ),
    Check(
        "Validate JSON: cross_repo_alignment_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/cross_repo_alignment_summary.json"],
    ),
    Check(
        "Validate JSON: cross_repo_status_manifest.json",
        ["python3", "-m", "json.tool", "cross_repo_alignment/generated/cross_repo_status_manifest.json"],
    ),
    Check(
        "Validate JSON: cross_repo_alignment_summary generated",
        ["python3", "-m", "json.tool", "cross_repo_alignment/generated/cross_repo_alignment_summary.json"],
    ),
    Check(
        "Compile labs live readiness builder",
        ["python3", "-m", "py_compile", "labs_live_readiness/tools/build_live_readiness_report.py"],
    ),
    Check(
        "Validate JSON: live_readiness_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/live_readiness_summary.json"],
    ),
    Check(
        "Validate JSON: live_readiness_report.json",
        ["python3", "-m", "json.tool", "labs_live_readiness/generated/live_readiness_report.json"],
    ),
    Check(
        "Validate JSON: transition_backlog.json",
        ["python3", "-m", "json.tool", "labs_live_readiness/generated/transition_backlog.json"],
    ),
    Check(
        "Validate JSON: live_readiness_manifest.json",
        ["python3", "-m", "json.tool", "labs_live_readiness/generated/live_readiness_manifest.json"],
    ),
    Check(
        "Compile labs live boundary builder",
        ["python3", "-m", "py_compile", "labs_live_boundary/tools/build_live_boundary_manifest.py"],
    ),
    Check(
        "Validate JSON: live_boundary_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/live_boundary_summary.json"],
    ),
    Check(
        "Validate JSON: live_boundary_manifest.json",
        ["python3", "-m", "json.tool", "labs_live_boundary/generated/live_boundary_manifest.json"],
    ),
    Check(
        "Validate JSON: live_boundary_summary generated",
        ["python3", "-m", "json.tool", "labs_live_boundary/generated/live_boundary_summary.json"],
    ),
    Check(
        "Validate JSON: live_transition_checklist.json",
        ["python3", "-m", "json.tool", "labs_live_boundary/generated/live_transition_checklist.json"],
    ),
    Check(
        "Compile labs CIEU runtime boundary builder",
        ["python3", "-m", "py_compile", "labs_cieu_runtime_boundary/tools/build_cieu_runtime_boundary.py"],
    ),
    Check(
        "Validate JSON: cieu_boundary_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/cieu_boundary_summary.json"],
    ),
    Check(
        "Validate JSON: cieu_runtime_boundary_manifest.json",
        ["python3", "-m", "json.tool", "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json"],
    ),
    Check(
        "Validate JSON: cieu_runtime_boundary_summary generated",
        ["python3", "-m", "json.tool", "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json"],
    ),
    Check(
        "Validate JSON: sample_cieu_runtime_event.json",
        ["python3", "-m", "json.tool", "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json"],
    ),
    Check(
        "Validate JSON: sample_prediction_delta_fixture.json",
        ["python3", "-m", "json.tool", "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json"],
    ),
    Check(
        "Compile company autonomy inventory builder",
        ["python3", "-m", "py_compile", "company_autonomy_inventory/tools/build_company_autonomy_inventory.py"],
    ),
    Check(
        "Validate JSON: autonomy_inventory_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/autonomy_inventory_summary.json"],
    ),
    Check(
        "Validate JSON: repo_discovery_manifest.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/repo_discovery_manifest.json"],
    ),
    Check(
        "Validate JSON: existing_asset_inventory.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/existing_asset_inventory.json"],
    ),
    Check(
        "Validate JSON: observation_capability_map.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/observation_capability_map.json"],
    ),
    Check(
        "Validate JSON: resource_sensing_map.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/resource_sensing_map.json"],
    ),
    Check(
        "Validate JSON: action_capability_map.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/action_capability_map.json"],
    ),
    Check(
        "Validate JSON: governed_tool_registry_candidates.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/governed_tool_registry_candidates.json"],
    ),
    Check(
        "Validate JSON: agent_role_capability_matrix.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/agent_role_capability_matrix.json"],
    ),
    Check(
        "Validate JSON: company_autonomy_readiness_summary.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json"],
    ),
    Check(
        "Validate JSON: inventory_size_guard.json",
        ["python3", "-m", "json.tool", "company_autonomy_inventory/generated/inventory_size_guard.json"],
    ),
    Check(
        "Compile autonomous work cycle builder",
        ["python3", "-m", "py_compile", "company_autonomous_work_cycle/tools/build_autonomous_work_cycle.py"],
    ),
    Check(
        "Validate JSON: autonomous_cycle_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/autonomous_cycle_summary.json"],
    ),
    Check(
        "Validate JSON: mission_profile.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/mission_profile.json"],
    ),
    Check(
        "Validate JSON: company_observation_snapshot.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/company_observation_snapshot.json"],
    ),
    Check(
        "Validate JSON: autonomous_work_backlog.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/autonomous_work_backlog.json"],
    ),
    Check(
        "Validate JSON: selected_work_item.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/selected_work_item.json"],
    ),
    Check(
        "Validate JSON: role_delegation_plan.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/role_delegation_plan.json"],
    ),
    Check(
        "Validate JSON: governed_tool_selection.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/governed_tool_selection.json"],
    ),
    Check(
        "Validate JSON: pre_u_packet_simulation.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/pre_u_packet_simulation.json"],
    ),
    Check(
        "Validate JSON: governance_decision_simulation.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/governance_decision_simulation.json"],
    ),
    Check(
        "Validate JSON: simulated_action_plan.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/simulated_action_plan.json"],
    ),
    Check(
        "Validate JSON: simulated_cieu_event.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/simulated_cieu_event.json"],
    ),
    Check(
        "Validate JSON: residual_delta_simulation.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/residual_delta_simulation.json"],
    ),
    Check(
        "Validate JSON: next_task_recommendations.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/next_task_recommendations.json"],
    ),
    Check(
        "Validate JSON: autonomous_work_cycle_summary.json",
        ["python3", "-m", "json.tool", "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json"],
    ),
    Check(
        "Compile legacy asset triage builder",
        ["python3", "-m", "py_compile", "legacy_asset_triage/tools/build_legacy_asset_triage.py"],
    ),
    Check(
        "Validate JSON: legacy_triage_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/legacy_triage_summary.json"],
    ),
    Check(
        "Validate JSON: legacy_asset_triage_manifest.json",
        ["python3", "-m", "json.tool", "legacy_asset_triage/generated/legacy_asset_triage_manifest.json"],
    ),
    Check(
        "Validate JSON: asset_value_risk_matrix.json",
        ["python3", "-m", "json.tool", "legacy_asset_triage/generated/asset_value_risk_matrix.json"],
    ),
    Check(
        "Validate JSON: asset_absorption_buckets.json",
        ["python3", "-m", "json.tool", "legacy_asset_triage/generated/asset_absorption_buckets.json"],
    ),
    Check(
        "Validate JSON: governed_absorption_backlog.json",
        ["python3", "-m", "json.tool", "legacy_asset_triage/generated/governed_absorption_backlog.json"],
    ),
    Check(
        "Validate JSON: top_absorption_candidates.json",
        ["python3", "-m", "json.tool", "legacy_asset_triage/generated/top_absorption_candidates.json"],
    ),
    Check(
        "Validate JSON: legacy_asset_triage_summary.json",
        ["python3", "-m", "json.tool", "legacy_asset_triage/generated/legacy_asset_triage_summary.json"],
    ),
    Check(
        "Compile governed observation loop builder",
        ["python3", "-m", "py_compile", "governed_observation_loop/tools/build_governed_observation_loop.py"],
    ),
    Check(
        "Validate JSON: observation_loop_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/observation_loop_summary.json"],
    ),
    Check(
        "Validate JSON: observation_source_registry.json",
        ["python3", "-m", "json.tool", "governed_observation_loop/generated/observation_source_registry.json"],
    ),
    Check(
        "Validate JSON: observation_tick_001.json",
        ["python3", "-m", "json.tool", "governed_observation_loop/generated/observation_tick_001.json"],
    ),
    Check(
        "Validate JSON: mission_dashboard_snapshot.json",
        ["python3", "-m", "json.tool", "governed_observation_loop/generated/mission_dashboard_snapshot.json"],
    ),
    Check(
        "Validate JSON: company_state_digest.json",
        ["python3", "-m", "json.tool", "governed_observation_loop/generated/company_state_digest.json"],
    ),
    Check(
        "Validate JSON: observation_to_work_item_candidates.json",
        ["python3", "-m", "json.tool", "governed_observation_loop/generated/observation_to_work_item_candidates.json"],
    ),
    Check(
        "Validate JSON: governed_observation_loop_summary.json",
        ["python3", "-m", "json.tool", "governed_observation_loop/generated/governed_observation_loop_summary.json"],
    ),
    Check(
        "Compile governed read-only observation tool",
        [
            "python3",
            "-m",
            "py_compile",
            "governed_readonly_observation_tool/tools/build_readonly_observation_tool_artifacts.py",
            "governed_readonly_observation_tool/tools/run_readonly_observation_tool.py",
        ],
    ),
    Check(
        "Validate JSON: readonly_tool_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/readonly_tool_summary.json"],
    ),
    Check(
        "Validate JSON: tool_contract.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/tool_contract.json"],
    ),
    Check(
        "Validate JSON: allowed_source_registry.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/allowed_source_registry.json"],
    ),
    Check(
        "Validate JSON: sample_tool_invocation.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/sample_tool_invocation.json"],
    ),
    Check(
        "Validate JSON: sample_tool_result.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/sample_tool_result.json"],
    ),
    Check(
        "Validate JSON: rejected_unsafe_invocation.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/rejected_unsafe_invocation.json"],
    ),
    Check(
        "Validate JSON: tool_invocation_trace.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/tool_invocation_trace.json"],
    ),
    Check(
        "Validate JSON: tool_cieu_event.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/tool_cieu_event.json"],
    ),
    Check(
        "Validate JSON: tool_readiness_summary.json",
        ["python3", "-m", "json.tool", "governed_readonly_observation_tool/generated/tool_readiness_summary.json"],
    ),
    Check(
        "Compile governed tool invocation bridge",
        [
            "python3",
            "-m",
            "py_compile",
            "governed_tool_invocation_bridge/tools/build_tool_invocation_bridge.py",
            "governed_tool_invocation_bridge/tools/run_governed_tool_bridge.py",
        ],
    ),
    Check(
        "Validate JSON: tool_bridge_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/tool_bridge_summary.json"],
    ),
    Check(
        "Validate JSON: bridge_contract.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/bridge_contract.json"],
    ),
    Check(
        "Validate JSON: agent_tool_request.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/agent_tool_request.json"],
    ),
    Check(
        "Validate JSON: pre_u_tool_packet.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/pre_u_tool_packet.json"],
    ),
    Check(
        "Validate JSON: governance_decision_envelope.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/governance_decision_envelope.json"],
    ),
    Check(
        "Validate JSON: bridge_authorization.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/bridge_authorization.json"],
    ),
    Check(
        "Validate JSON: bridge_invocation_trace.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/bridge_invocation_trace.json"],
    ),
    Check(
        "Validate JSON: bridged_tool_result.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/bridged_tool_result.json"],
    ),
    Check(
        "Validate JSON: bridge_cieu_event.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/bridge_cieu_event.json"],
    ),
    Check(
        "Validate JSON: bridge_residual_delta.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/bridge_residual_delta.json"],
    ),
    Check(
        "Validate JSON: rejected_direct_tool_invocation.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/rejected_direct_tool_invocation.json"],
    ),
    Check(
        "Validate JSON: rejected_unsafe_bridge_request.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/rejected_unsafe_bridge_request.json"],
    ),
    Check(
        "Validate JSON: tool_bridge_readiness_summary.json",
        ["python3", "-m", "json.tool", "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json"],
    ),
    Check(
        "Compile agent team work proposal tools",
        [
            "python3",
            "-m",
            "py_compile",
            "agent_team_work_proposal/tools/build_agent_team_work_proposal.py",
            "agent_team_work_proposal/tools/run_work_proposal_to_bridge.py",
        ],
    ),
    Check(
        "Validate JSON: work_proposal_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/work_proposal_summary.json"],
    ),
    Check(
        "Validate JSON: mission_context_snapshot.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/mission_context_snapshot.json"],
    ),
    Check(
        "Validate JSON: agent_team_observation_input.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/agent_team_observation_input.json"],
    ),
    Check(
        "Validate JSON: autonomous_work_proposals.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/autonomous_work_proposals.json"],
    ),
    Check(
        "Validate JSON: selected_agent_work_proposal.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/selected_agent_work_proposal.json"],
    ),
    Check(
        "Validate JSON: role_review_board.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/role_review_board.json"],
    ),
    Check(
        "Validate JSON: tool_need_analysis.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/tool_need_analysis.json"],
    ),
    Check(
        "Validate JSON: generated_tool_request.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/generated_tool_request.json"],
    ),
    Check(
        "Validate JSON: work_proposal_to_bridge_trace.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/work_proposal_to_bridge_trace.json"],
    ),
    Check(
        "Validate JSON: bridged_tool_result_ref.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/bridged_tool_result_ref.json"],
    ),
    Check(
        "Validate JSON: work_proposal_cieu_event.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/work_proposal_cieu_event.json"],
    ),
    Check(
        "Validate JSON: work_proposal_residual_delta.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/work_proposal_residual_delta.json"],
    ),
    Check(
        "Validate JSON: next_agent_work_recommendations.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/next_agent_work_recommendations.json"],
    ),
    Check(
        "Validate JSON: agent_team_work_proposal_summary.json",
        ["python3", "-m", "json.tool", "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json"],
    ),
    Check(
        "Compile mission dashboard refresh loop tools",
        [
            "python3",
            "-m",
            "py_compile",
            "mission_dashboard_refresh_loop/tools/build_mission_dashboard_refresh_loop.py",
            "mission_dashboard_refresh_loop/tools/run_dashboard_refresh_loop.py",
        ],
    ),
    Check(
        "Validate JSON: dashboard_refresh_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/dashboard_refresh_summary.json"],
    ),
    Check(
        "Validate JSON: refresh_loop_contract.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refresh_loop_contract.json"],
    ),
    Check(
        "Validate JSON: previous_dashboard_snapshot.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/previous_dashboard_snapshot.json"],
    ),
    Check(
        "Validate JSON: current_observation_input.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/current_observation_input.json"],
    ),
    Check(
        "Validate JSON: refreshed_mission_dashboard.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json"],
    ),
    Check(
        "Validate JSON: company_state_delta.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/company_state_delta.json"],
    ),
    Check(
        "Validate JSON: refreshed_autonomous_backlog.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refreshed_autonomous_backlog.json"],
    ),
    Check(
        "Validate JSON: refresh_loop_trace.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refresh_loop_trace.json"],
    ),
    Check(
        "Validate JSON: refresh_cieu_event.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refresh_cieu_event.json"],
    ),
    Check(
        "Validate JSON: refresh_residual_delta.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refresh_residual_delta.json"],
    ),
    Check(
        "Validate JSON: next_loop_recommendations.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/next_loop_recommendations.json"],
    ),
    Check(
        "Validate JSON: refresh_loop_readiness_summary.json",
        ["python3", "-m", "json.tool", "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json"],
    ),
    Check(
        "Compile recurring observation loop contract tools",
        [
            "python3",
            "-m",
            "py_compile",
            "recurring_observation_loop_contract/tools/build_recurring_observation_contract.py",
            "recurring_observation_loop_contract/tools/simulate_recurring_observation_tick.py",
        ],
    ),
    Check(
        "Validate JSON: recurring_loop_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/recurring_loop_summary.json"],
    ),
    Check(
        "Validate JSON: recurring_loop_contract.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/recurring_loop_contract.json"],
    ),
    Check(
        "Validate JSON: recurrence_schedule_draft.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/recurrence_schedule_draft.json"],
    ),
    Check(
        "Validate JSON: allowed_observation_sources.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/allowed_observation_sources.json"],
    ),
    Check(
        "Validate JSON: tick_governance_gate.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/tick_governance_gate.json"],
    ),
    Check(
        "Validate JSON: simulated_observation_tick_001.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/simulated_observation_tick_001.json"],
    ),
    Check(
        "Validate JSON: simulated_tick_dashboard_delta.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/simulated_tick_dashboard_delta.json"],
    ),
    Check(
        "Validate JSON: simulated_tick_work_candidates.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/simulated_tick_work_candidates.json"],
    ),
    Check(
        "Validate JSON: simulated_tick_cieu_event.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/simulated_tick_cieu_event.json"],
    ),
    Check(
        "Validate JSON: simulated_tick_residual_delta.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/simulated_tick_residual_delta.json"],
    ),
    Check(
        "Validate JSON: stop_abort_conditions.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/stop_abort_conditions.json"],
    ),
    Check(
        "Validate JSON: escalation_conditions.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/escalation_conditions.json"],
    ),
    Check(
        "Validate JSON: manual_enablement_checklist.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/manual_enablement_checklist.json"],
    ),
    Check(
        "Validate JSON: recurring_loop_readiness_summary.json",
        ["python3", "-m", "json.tool", "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json"],
    ),
    Check(
        "Compile manual recurring observation tick runner tools",
        [
            "python3",
            "-m",
            "py_compile",
            "manual_recurring_observation_tick_runner/tools/build_manual_tick_runner.py",
            "manual_recurring_observation_tick_runner/tools/run_manual_observation_tick.py",
        ],
    ),
    Check(
        "Validate JSON: manual_tick_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/manual_tick_summary.json"],
    ),
    Check(
        "Validate JSON: manual_tick_runner_contract.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_runner_contract.json"],
    ),
    Check(
        "Validate JSON: manual_tick_request.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_request.json"],
    ),
    Check(
        "Validate JSON: manual_tick_preflight.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_preflight.json"],
    ),
    Check(
        "Validate JSON: manual_tick_source_validation.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_source_validation.json"],
    ),
    Check(
        "Validate JSON: manual_tick_governance_decision.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_governance_decision.json"],
    ),
    Check(
        "Validate JSON: manual_tick_result.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_result.json"],
    ),
    Check(
        "Validate JSON: manual_tick_dashboard_delta.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_dashboard_delta.json"],
    ),
    Check(
        "Validate JSON: manual_tick_work_candidates.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_work_candidates.json"],
    ),
    Check(
        "Validate JSON: manual_tick_cieu_event.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_cieu_event.json"],
    ),
    Check(
        "Validate JSON: manual_tick_residual_delta.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_residual_delta.json"],
    ),
    Check(
        "Validate JSON: manual_tick_run_receipt.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_run_receipt.json"],
    ),
    Check(
        "Validate JSON: manual_tick_history_index.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_history_index.json"],
    ),
    Check(
        "Validate JSON: manual_tick_next_recommendations.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_next_recommendations.json"],
    ),
    Check(
        "Validate JSON: manual_tick_runner_readiness_summary.json",
        ["python3", "-m", "json.tool", "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json"],
    ),
    Check(
        "Compile field functional archaeology builder",
        [
            "python3",
            "-m",
            "py_compile",
            "field_functional_archaeology/tools/build_field_functional_archaeology.py",
        ],
    ),
    Check(
        "Validate JSON: field_functional_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/field_functional_summary.json"],
    ),
    Check(
        "Validate JSON: search_manifest.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/search_manifest.json"],
    ),
    Check(
        "Validate JSON: field_functional_asset_inventory.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/field_functional_asset_inventory.json"],
    ),
    Check(
        "Validate JSON: field_functional_concept_map.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/field_functional_concept_map.json"],
    ),
    Check(
        "Validate JSON: old_to_new_architecture_alignment.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/old_to_new_architecture_alignment.json"],
    ),
    Check(
        "Validate JSON: merge_decision_matrix.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/merge_decision_matrix.json"],
    ),
    Check(
        "Validate JSON: reuse_candidates.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/reuse_candidates.json"],
    ),
    Check(
        "Validate JSON: rewrite_candidates.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/rewrite_candidates.json"],
    ),
    Check(
        "Validate JSON: do_not_absorb_candidates.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/do_not_absorb_candidates.json"],
    ),
    Check(
        "Validate JSON: mission_projection_merge_plan.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/mission_projection_merge_plan.json"],
    ),
    Check(
        "Validate JSON: field_functional_archaeology_summary.json",
        ["python3", "-m", "json.tool", "field_functional_archaeology/generated/field_functional_archaeology_summary.json"],
    ),
    Check(
        "Compile mission field projection harness builder",
        [
            "python3",
            "-m",
            "py_compile",
            "mission_field_projection_contract/tools/build_mission_field_projection_harness.py",
        ],
    ),
    Check(
        "Validate JSON: mission_projection_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/mission_projection_summary.json"],
    ),
    Check(
        "Validate JSON: projection_contract_v0.json",
        ["python3", "-m", "json.tool", "mission_field_projection_contract/projection_contract_v0.json"],
    ),
    Check(
        "Validate JSON: projection_input_fixture.json",
        ["python3", "-m", "json.tool", "mission_field_projection_contract/projection_input_fixture.json"],
    ),
    Check(
        "Validate JSON: projection_policy_v0.json",
        ["python3", "-m", "json.tool", "mission_field_projection_contract/projection_policy_v0.json"],
    ),
    Check(
        "Validate JSON: projection_contract_summary.json",
        ["python3", "-m", "json.tool", "mission_field_projection_contract/projection_contract_summary.json"],
    ),
    Check(
        "Validate JSON: layered_projection_trace.json",
        ["python3", "-m", "json.tool", "layered_y_star_projection_trace/layered_projection_trace.json"],
    ),
    Check(
        "Validate JSON: field_source_map.json",
        ["python3", "-m", "json.tool", "layered_y_star_projection_trace/field_source_map.json"],
    ),
    Check(
        "Validate JSON: contraction_map.json",
        ["python3", "-m", "json.tool", "layered_y_star_projection_trace/contraction_map.json"],
    ),
    Check(
        "Validate JSON: unresolved_gap_map.json",
        ["python3", "-m", "json.tool", "layered_y_star_projection_trace/unresolved_gap_map.json"],
    ),
    Check(
        "Validate JSON: projection_trace_summary.json",
        ["python3", "-m", "json.tool", "layered_y_star_projection_trace/projection_trace_summary.json"],
    ),
    Check(
        "Validate JSON: pre_u_packet_candidate.json",
        ["python3", "-m", "json.tool", "projection_to_pre_u_packet_adapter/pre_u_packet_candidate.json"],
    ),
    Check(
        "Validate JSON: pre_u_adapter_mapping.json",
        ["python3", "-m", "json.tool", "projection_to_pre_u_packet_adapter/pre_u_adapter_mapping.json"],
    ),
    Check(
        "Validate JSON: pre_u_adapter_summary.json",
        ["python3", "-m", "json.tool", "projection_to_pre_u_packet_adapter/pre_u_adapter_summary.json"],
    ),
    Check(
        "Validate JSON: projection_predicted_outcome.json",
        ["python3", "-m", "json.tool", "projection_residual_delta_fixture/projection_predicted_outcome.json"],
    ),
    Check(
        "Validate JSON: projection_mock_actual_outcome.json",
        ["python3", "-m", "json.tool", "projection_residual_delta_fixture/projection_mock_actual_outcome.json"],
    ),
    Check(
        "Validate JSON: projection_residual_delta_fixture.json",
        ["python3", "-m", "json.tool", "projection_residual_delta_fixture/projection_residual_delta_fixture.json"],
    ),
    Check(
        "Validate JSON: projection_residual_delta_summary.json",
        ["python3", "-m", "json.tool", "projection_residual_delta_fixture/projection_residual_delta_summary.json"],
    ),
    Check(
        "Compile field functional auto-projection core builder",
        [
            "python3",
            "-m",
            "py_compile",
            "field_functional_auto_projection_core/tools/build_field_functional_auto_projection_core.py",
        ],
    ),
    Check(
        "Validate JSON: field_projection_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/field_projection_summary.json"],
    ),
    Check(
        "Validate JSON: field_projection_operator_contract.json",
        ["python3", "-m", "json.tool", "field_functional_auto_projection_core/field_projection_operator_contract.json"],
    ),
    Check(
        "Validate JSON: field_projection_operator_policy.json",
        ["python3", "-m", "json.tool", "field_functional_auto_projection_core/field_projection_operator_policy.json"],
    ),
    Check(
        "Validate JSON: field_projection_input_fixture.json",
        ["python3", "-m", "json.tool", "field_functional_auto_projection_core/field_projection_input_fixture.json"],
    ),
    Check(
        "Validate JSON: field_projection_operator_summary.json",
        ["python3", "-m", "json.tool", "field_functional_auto_projection_core/field_projection_operator_summary.json"],
    ),
    Check(
        "Validate JSON: mission_y_star_input.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/mission_y_star_input.json"],
    ),
    Check(
        "Validate JSON: projection_context_field_fixture.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/projection_context_field_fixture.json"],
    ),
    Check(
        "Validate JSON: mission_to_company_y_star.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/mission_to_company_y_star.json"],
    ),
    Check(
        "Validate JSON: company_to_milestone_y_star.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/company_to_milestone_y_star.json"],
    ),
    Check(
        "Validate JSON: milestone_to_session_y_star.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/milestone_to_session_y_star.json"],
    ),
    Check(
        "Validate JSON: session_to_task_y_star.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/session_to_task_y_star.json"],
    ),
    Check(
        "Validate JSON: task_to_behavior_y_star.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/task_to_behavior_y_star.json"],
    ),
    Check(
        "Validate JSON: mission_to_behavior_projection_trace.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json"],
    ),
    Check(
        "Validate JSON: y_star_inheritance_map.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/y_star_inheritance_map.json"],
    ),
    Check(
        "Validate JSON: y_star_contraction_map.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/y_star_contraction_map.json"],
    ),
    Check(
        "Validate JSON: context_binding_map.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/context_binding_map.json"],
    ),
    Check(
        "Validate JSON: unresolved_projection_gap_map.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/unresolved_projection_gap_map.json"],
    ),
    Check(
        "Validate JSON: behavior_level_y_star_candidate.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"],
    ),
    Check(
        "Validate JSON: mission_to_behavior_projection_summary.json",
        ["python3", "-m", "json.tool", "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json"],
    ),
    Check(
        "Validate JSON: behavior_to_pre_u_mapping.json",
        ["python3", "-m", "json.tool", "behavior_y_star_to_pre_u_candidate/behavior_to_pre_u_mapping.json"],
    ),
    Check(
        "Validate JSON: pre_u_packet_candidate_from_behavior_y_star.json",
        ["python3", "-m", "json.tool", "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json"],
    ),
    Check(
        "Validate JSON: pre_u_candidate_summary.json",
        ["python3", "-m", "json.tool", "behavior_y_star_to_pre_u_candidate/pre_u_candidate_summary.json"],
    ),
    Check(
        "Validate JSON: projected_behavior_expected_outcome.json",
        ["python3", "-m", "json.tool", "projection_behavior_residual_loop_fixture/projected_behavior_expected_outcome.json"],
    ),
    Check(
        "Validate JSON: mock_behavior_actual_outcome.json",
        ["python3", "-m", "json.tool", "projection_behavior_residual_loop_fixture/mock_behavior_actual_outcome.json"],
    ),
    Check(
        "Validate JSON: behavior_projection_residual_delta.json",
        ["python3", "-m", "json.tool", "projection_behavior_residual_loop_fixture/behavior_projection_residual_delta.json"],
    ),
    Check(
        "Validate JSON: projection_learning_candidate_stub.json",
        ["python3", "-m", "json.tool", "projection_behavior_residual_loop_fixture/projection_learning_candidate_stub.json"],
    ),
    Check(
        "Validate JSON: projection_residual_loop_summary.json",
        ["python3", "-m", "json.tool", "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json"],
    ),
    Check(
        "Validate JSON: field_projection_cycle_readiness.json",
        ["python3", "-m", "json.tool", "field_projection_cycle_readiness/field_projection_cycle_readiness.json"],
    ),
    Check(
        "Validate JSON: l5_3_recommended_next_step.json",
        ["python3", "-m", "json.tool", "field_projection_cycle_readiness/l5_3_recommended_next_step.json"],
    ),
    Check(
        "Compile projection-checked autonomous work cycle builder",
        [
            "python3",
            "-m",
            "py_compile",
            "projection_checked_autonomous_work_cycle/tools/build_projection_checked_autonomous_work_cycle.py",
        ],
    ),
    Check(
        "Validate JSON: projection_cycle_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/projection_cycle_summary.json"],
    ),
    Check(
        "Validate JSON: projection_checked_cycle_contract.json",
        ["python3", "-m", "json.tool", "projection_checked_autonomous_work_cycle/projection_checked_cycle_contract.json"],
    ),
    Check(
        "Validate JSON: projection_checked_cycle_input_fixture.json",
        ["python3", "-m", "json.tool", "projection_checked_autonomous_work_cycle/projection_checked_cycle_input_fixture.json"],
    ),
    Check(
        "Validate JSON: projection_checked_cycle_run.json",
        ["python3", "-m", "json.tool", "projection_checked_autonomous_work_cycle/projection_checked_cycle_run.json"],
    ),
    Check(
        "Validate JSON: projection_checked_cycle_summary.json",
        ["python3", "-m", "json.tool", "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json"],
    ),
    Check(
        "Validate JSON: projection_checked_work_intent.json",
        ["python3", "-m", "json.tool", "projection_checked_work_proposal/projection_checked_work_intent.json"],
    ),
    Check(
        "Validate JSON: autonomous_work_proposal_candidate.json",
        ["python3", "-m", "json.tool", "projection_checked_work_proposal/autonomous_work_proposal_candidate.json"],
    ),
    Check(
        "Validate JSON: work_proposal_to_behavior_y_star_alignment.json",
        ["python3", "-m", "json.tool", "projection_checked_work_proposal/work_proposal_to_behavior_y_star_alignment.json"],
    ),
    Check(
        "Validate JSON: work_proposal_projection_gate_decision.json",
        ["python3", "-m", "json.tool", "projection_checked_work_proposal/work_proposal_projection_gate_decision.json"],
    ),
    Check(
        "Validate JSON: cycle_pre_u_packet_candidate.json",
        ["python3", "-m", "json.tool", "behavior_projection_pre_u_cycle_gate/cycle_pre_u_packet_candidate.json"],
    ),
    Check(
        "Validate JSON: cycle_pre_u_mapping_from_behavior_y_star.json",
        ["python3", "-m", "json.tool", "behavior_projection_pre_u_cycle_gate/cycle_pre_u_mapping_from_behavior_y_star.json"],
    ),
    Check(
        "Validate JSON: cycle_pre_u_gate_decision.json",
        ["python3", "-m", "json.tool", "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_decision.json"],
    ),
    Check(
        "Validate JSON: cycle_pre_u_gate_summary.json",
        ["python3", "-m", "json.tool", "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json"],
    ),
    Check(
        "Validate JSON: dry_run_work_execution_plan.json",
        ["python3", "-m", "json.tool", "projection_checked_dry_run_work_result/dry_run_work_execution_plan.json"],
    ),
    Check(
        "Validate JSON: dry_run_work_result.json",
        ["python3", "-m", "json.tool", "projection_checked_dry_run_work_result/dry_run_work_result.json"],
    ),
    Check(
        "Validate JSON: dry_run_work_receipt.json",
        ["python3", "-m", "json.tool", "projection_checked_dry_run_work_result/dry_run_work_receipt.json"],
    ),
    Check(
        "Validate JSON: projection_checked_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "projection_checked_cieu_residual_cycle/projection_checked_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: projection_checked_residual_delta.json",
        ["python3", "-m", "json.tool", "projection_checked_cieu_residual_cycle/projection_checked_residual_delta.json"],
    ),
    Check(
        "Validate JSON: projection_checked_learning_candidate.json",
        ["python3", "-m", "json.tool", "projection_checked_learning_review_queue/projection_checked_learning_candidate.json"],
    ),
    Check(
        "Validate JSON: projection_checked_cycle_readiness.json",
        ["python3", "-m", "json.tool", "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json"],
    ),
    Check(
        "Validate JSON: l5_4_recommended_next_step.json",
        ["python3", "-m", "json.tool", "projection_checked_cycle_readiness/l5_4_recommended_next_step.json"],
    ),
    Check(
        "Compile review-gated shadow learning cycle builder",
        [
            "python3",
            "-m",
            "py_compile",
            "review_gated_shadow_learning_cycle/tools/build_review_gated_shadow_learning_cycle.py",
        ],
    ),
    Check(
        "Validate JSON: shadow_learning_cycle_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/shadow_learning_cycle_summary.json"],
    ),
    Check(
        "Validate JSON: review_gated_shadow_learning_contract.json",
        ["python3", "-m", "json.tool", "review_gated_shadow_learning_cycle/review_gated_shadow_learning_contract.json"],
    ),
    Check(
        "Validate JSON: review_gated_shadow_learning_input_fixture.json",
        ["python3", "-m", "json.tool", "review_gated_shadow_learning_cycle/review_gated_shadow_learning_input_fixture.json"],
    ),
    Check(
        "Validate JSON: review_gated_shadow_learning_run.json",
        ["python3", "-m", "json.tool", "review_gated_shadow_learning_cycle/review_gated_shadow_learning_run.json"],
    ),
    Check(
        "Validate JSON: normalized_projection_residual.json",
        ["python3", "-m", "json.tool", "residual_review_gate/normalized_projection_residual.json"],
    ),
    Check(
        "Validate JSON: residual_review_gate_decision.json",
        ["python3", "-m", "json.tool", "residual_review_gate/residual_review_gate_decision.json"],
    ),
    Check(
        "Validate JSON: residual_review_decision_packet.json",
        ["python3", "-m", "json.tool", "residual_review_gate/residual_review_decision_packet.json"],
    ),
    Check(
        "Validate JSON: learning_target_classification.json",
        ["python3", "-m", "json.tool", "learning_target_classifier/learning_target_classification.json"],
    ),
    Check(
        "Validate JSON: learning_scope_matrix.json",
        ["python3", "-m", "json.tool", "learning_target_classifier/learning_scope_matrix.json"],
    ),
    Check(
        "Validate JSON: projection_policy_update_candidate.json",
        ["python3", "-m", "json.tool", "projection_policy_update_candidate/projection_policy_update_candidate.json"],
    ),
    Check(
        "Validate JSON: behavior_y_star_generation_update_candidate.json",
        ["python3", "-m", "json.tool", "projection_policy_update_candidate/behavior_y_star_generation_update_candidate.json"],
    ),
    Check(
        "Validate JSON: shadow_projection_policy_patch.json",
        ["python3", "-m", "json.tool", "shadow_projection_policy_patch/shadow_projection_policy_patch.json"],
    ),
    Check(
        "Validate JSON: shadow_patch_denied_operations.json",
        ["python3", "-m", "json.tool", "shadow_projection_policy_patch/shadow_patch_denied_operations.json"],
    ),
    Check(
        "Validate JSON: next_cycle_projection_input_candidate.json",
        ["python3", "-m", "json.tool", "shadow_reprojection_preview/next_cycle_projection_input_candidate.json"],
    ),
    Check(
        "Validate JSON: shadow_reprojected_behavior_y_star_preview.json",
        ["python3", "-m", "json.tool", "shadow_reprojection_preview/shadow_reprojected_behavior_y_star_preview.json"],
    ),
    Check(
        "Validate JSON: original_vs_shadow_behavior_y_star_comparison.json",
        ["python3", "-m", "json.tool", "shadow_reprojection_preview/original_vs_shadow_behavior_y_star_comparison.json"],
    ),
    Check(
        "Validate JSON: shadow_cycle_contract.json",
        ["python3", "-m", "json.tool", "shadow_updated_projection_cycle/shadow_cycle_contract.json"],
    ),
    Check(
        "Validate JSON: shadow_cycle_pre_u_packet_candidate.json",
        ["python3", "-m", "json.tool", "shadow_updated_projection_cycle/shadow_cycle_pre_u_packet_candidate.json"],
    ),
    Check(
        "Validate JSON: shadow_cycle_pre_u_gate_decision.json",
        ["python3", "-m", "json.tool", "shadow_updated_projection_cycle/shadow_cycle_pre_u_gate_decision.json"],
    ),
    Check(
        "Validate JSON: shadow_dry_run_work_result.json",
        ["python3", "-m", "json.tool", "shadow_updated_projection_cycle/shadow_dry_run_work_result.json"],
    ),
    Check(
        "Validate JSON: shadow_dry_run_work_receipt.json",
        ["python3", "-m", "json.tool", "shadow_updated_projection_cycle/shadow_dry_run_work_receipt.json"],
    ),
    Check(
        "Validate JSON: shadow_cycle_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "shadow_cycle_cieu_residual/shadow_cycle_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: shadow_cycle_residual_delta.json",
        ["python3", "-m", "json.tool", "shadow_cycle_cieu_residual/shadow_cycle_residual_delta.json"],
    ),
    Check(
        "Validate JSON: original_vs_shadow_cycle_comparison.json",
        ["python3", "-m", "json.tool", "original_vs_shadow_cycle_comparison/original_vs_shadow_cycle_comparison.json"],
    ),
    Check(
        "Validate JSON: shadow_learning_effect_summary.json",
        ["python3", "-m", "json.tool", "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json"],
    ),
    Check(
        "Validate JSON: integrated_learning_cycle_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: integrated_learning_cycle_residual_delta.json",
        ["python3", "-m", "json.tool", "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_residual_delta.json"],
    ),
    Check(
        "Validate JSON: integrated_shadow_learning_readiness.json",
        ["python3", "-m", "json.tool", "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json"],
    ),
    Check(
        "Py compile: build_cross_repo_governance_contract_proof.py",
        [
            "python3",
            "-m",
            "py_compile",
            "cross_repo_governance_contract_proof/tools/build_cross_repo_governance_contract_proof.py",
        ],
    ),
    Check(
        "Validate JSON: cross_repo_governance_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/cross_repo_governance_summary.json"],
    ),
    Check(
        "Validate JSON: cross_repo_contract_proof_contract.json",
        ["python3", "-m", "json.tool", "cross_repo_governance_contract_proof/cross_repo_contract_proof_contract.json"],
    ),
    Check(
        "Validate JSON: cross_repo_contract_proof_summary.json",
        ["python3", "-m", "json.tool", "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json"],
    ),
    Check(
        "Validate JSON: y_star_gov_readonly_scan_manifest.json",
        ["python3", "-m", "json.tool", "y_star_gov_contract_surface_inventory/y_star_gov_readonly_scan_manifest.json"],
    ),
    Check(
        "Validate JSON: y_star_gov_contract_surface_inventory.json",
        ["python3", "-m", "json.tool", "y_star_gov_contract_surface_inventory/y_star_gov_contract_surface_inventory.json"],
    ),
    Check(
        "Validate JSON: behavior_y_star_to_governance_contract_map.json",
        ["python3", "-m", "json.tool", "ystar_company_to_y_star_gov_alignment/behavior_y_star_to_governance_contract_map.json"],
    ),
    Check(
        "Validate JSON: labs_vs_kernel_responsibility_boundary.json",
        ["python3", "-m", "json.tool", "ystar_company_to_y_star_gov_alignment/labs_vs_kernel_responsibility_boundary.json"],
    ),
    Check(
        "Validate JSON: gov_mcp_readonly_scan_manifest.json",
        ["python3", "-m", "json.tool", "gov_mcp_boundary_inventory/gov_mcp_readonly_scan_manifest.json"],
    ),
    Check(
        "Validate JSON: gov_mcp_bypass_risk_inventory.json",
        ["python3", "-m", "json.tool", "gov_mcp_boundary_inventory/gov_mcp_bypass_risk_inventory.json"],
    ),
    Check(
        "Validate JSON: governed_mcp_interface_contract.json",
        ["python3", "-m", "json.tool", "governed_mcp_interface_contract/governed_mcp_interface_contract.json"],
    ),
    Check(
        "Validate JSON: mcp_non_bypass_invariant_map.json",
        ["python3", "-m", "json.tool", "governed_mcp_interface_contract/mcp_non_bypass_invariant_map.json"],
    ),
    Check(
        "Validate JSON: required_gate_sequence.json",
        ["python3", "-m", "json.tool", "cross_repo_non_bypass_proof/required_gate_sequence.json"],
    ),
    Check(
        "Validate JSON: forbidden_bypass_path_matrix.json",
        ["python3", "-m", "json.tool", "cross_repo_non_bypass_proof/forbidden_bypass_path_matrix.json"],
    ),
    Check(
        "Validate JSON: cross_repo_governance_readiness.json",
        ["python3", "-m", "json.tool", "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json"],
    ),
    Check(
        "Py compile: build_governed_mcp_dry_run_adapter.py",
        [
            "python3",
            "-m",
            "py_compile",
            "governed_mcp_dry_run_adapter/tools/build_governed_mcp_dry_run_adapter.py",
        ],
    ),
    Check(
        "Validate JSON: governed_mcp_adapter_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/governed_mcp_adapter_summary.json"],
    ),
    Check(
        "Validate JSON: governed_mcp_dry_run_adapter_contract.json",
        ["python3", "-m", "json.tool", "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_contract.json"],
    ),
    Check(
        "Validate JSON: governed_mcp_dry_run_input_fixture.json",
        ["python3", "-m", "json.tool", "governed_mcp_dry_run_adapter/governed_mcp_dry_run_input_fixture.json"],
    ),
    Check(
        "Validate JSON: mcp_request_intent.json",
        ["python3", "-m", "json.tool", "mcp_request_intent_projection/mcp_request_intent.json"],
    ),
    Check(
        "Validate JSON: mcp_call_pre_u_packet_candidate.json",
        ["python3", "-m", "json.tool", "mcp_pre_u_packet_candidate/mcp_call_pre_u_packet_candidate.json"],
    ),
    Check(
        "Validate JSON: mcp_governance_decision_envelope.json",
        ["python3", "-m", "json.tool", "mcp_governance_decision_envelope/mcp_governance_decision_envelope.json"],
    ),
    Check(
        "Validate JSON: mcp_bridge_authorization_receipt.json",
        ["python3", "-m", "json.tool", "mcp_bridge_authorization_receipt/mcp_bridge_authorization_receipt.json"],
    ),
    Check(
        "Validate JSON: governed_mcp_call_candidate.json",
        ["python3", "-m", "json.tool", "governed_mcp_call_candidate/governed_mcp_call_candidate.json"],
    ),
    Check(
        "Validate JSON: mcp_dry_run_receipt.json",
        ["python3", "-m", "json.tool", "mcp_dry_run_receipt_and_cieu/mcp_dry_run_receipt.json"],
    ),
    Check(
        "Validate JSON: mcp_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "mcp_dry_run_receipt_and_cieu/mcp_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: mcp_residual_delta.json",
        ["python3", "-m", "json.tool", "mcp_residual_and_learning_candidate/mcp_residual_delta.json"],
    ),
    Check(
        "Validate JSON: mcp_learning_candidate.json",
        ["python3", "-m", "json.tool", "mcp_residual_and_learning_candidate/mcp_learning_candidate.json"],
    ),
    Check(
        "Validate JSON: governed_mcp_adapter_readiness.json",
        ["python3", "-m", "json.tool", "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json"],
    ),
    Check(
        "Py compile: build_controlled_canonical_learning_design.py",
        [
            "python3",
            "-m",
            "py_compile",
            "controlled_canonical_learning_design/tools/build_controlled_canonical_learning_design.py",
        ],
    ),
    Check(
        "Validate JSON: controlled_canonical_learning_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/controlled_canonical_learning_summary.json"],
    ),
    Check(
        "Validate JSON: controlled_canonical_learning_contract.json",
        ["python3", "-m", "json.tool", "controlled_canonical_learning_design/controlled_canonical_learning_contract.json"],
    ),
    Check(
        "Validate JSON: y_star_non_mutation_invariant.json",
        ["python3", "-m", "json.tool", "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json"],
    ),
    Check(
        "Validate JSON: canonical_learning_target_registry.json",
        ["python3", "-m", "json.tool", "canonical_learning_target_registry/canonical_learning_target_registry.json"],
    ),
    Check(
        "Validate JSON: canonical_promotion_evidence_bundle.json",
        ["python3", "-m", "json.tool", "canonical_promotion_evidence_bundle/canonical_promotion_evidence_bundle.json"],
    ),
    Check(
        "Validate JSON: canonical_promotion_eligibility_decision.json",
        ["python3", "-m", "json.tool", "canonical_promotion_eligibility_gate/canonical_promotion_eligibility_decision.json"],
    ),
    Check(
        "Validate JSON: canonical_update_package_candidate.json",
        ["python3", "-m", "json.tool", "canonical_update_package_candidate/canonical_update_package_candidate.json"],
    ),
    Check(
        "Validate JSON: versioned_canonical_patch_plan.json",
        ["python3", "-m", "json.tool", "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json"],
    ),
    Check(
        "Validate JSON: rollback_plan.json",
        ["python3", "-m", "json.tool", "rollback_and_audit_lineage/rollback_plan.json"],
    ),
    Check(
        "Validate JSON: post_promotion_validation_plan.json",
        ["python3", "-m", "json.tool", "post_promotion_validation_plan/post_promotion_validation_plan.json"],
    ),
    Check(
        "Validate JSON: dry_run_promotion_decision_fixture.json",
        ["python3", "-m", "json.tool", "dry_run_promotion_decision_fixture/dry_run_promotion_decision_fixture.json"],
    ),
    Check(
        "Validate JSON: controlled_canonical_learning_readiness.json",
        ["python3", "-m", "json.tool", "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json"],
    ),
    Check(
        "Py compile: build_approved_canonical_update_sandbox.py",
        [
            "python3",
            "-m",
            "py_compile",
            "approved_canonical_update_sandbox/tools/build_approved_canonical_update_sandbox.py",
        ],
    ),
    Check(
        "Validate JSON: approved_sandbox_update_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/approved_sandbox_update_summary.json"],
    ),
    Check(
        "Validate JSON: approved_canonical_update_sandbox_contract.json",
        ["python3", "-m", "json.tool", "approved_canonical_update_sandbox/approved_canonical_update_sandbox_contract.json"],
    ),
    Check(
        "Validate JSON: sandbox_approval_decision_fixture.json",
        ["python3", "-m", "json.tool", "sandbox_approval_fixture/sandbox_approval_decision_fixture.json"],
    ),
    Check(
        "Validate JSON: sandbox_patch_application_result.json",
        ["python3", "-m", "json.tool", "sandbox_patch_application/sandbox_patch_application_result.json"],
    ),
    Check(
        "Validate JSON: sandbox_post_update_validation_result.json",
        ["python3", "-m", "json.tool", "sandbox_post_update_validation/sandbox_post_update_validation_result.json"],
    ),
    Check(
        "Validate JSON: sandbox_reprojected_behavior_y_star.json",
        ["python3", "-m", "json.tool", "sandbox_reprojection_and_mcp_preview/sandbox_reprojected_behavior_y_star.json"],
    ),
    Check(
        "Validate JSON: sandbox_update_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "sandbox_update_cieu_residual/sandbox_update_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: sandbox_rollback_result.json",
        ["python3", "-m", "json.tool", "sandbox_rollback_validation/sandbox_rollback_result.json"],
    ),
    Check(
        "Validate JSON: approved_sandbox_update_readiness.json",
        ["python3", "-m", "json.tool", "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json"],
    ),
    Check(
        "Py compile: build_real_approval_workflow_boundary.py",
        [
            "python3",
            "-m",
            "py_compile",
            "real_approval_workflow_boundary/tools/build_real_approval_workflow_boundary.py",
        ],
    ),
    Check(
        "Validate JSON: real_approval_workflow_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/real_approval_workflow_summary.json"],
    ),
    Check(
        "Validate JSON: real_approval_workflow_boundary_contract.json",
        ["python3", "-m", "json.tool", "real_approval_workflow_boundary/real_approval_workflow_boundary_contract.json"],
    ),
    Check(
        "Validate JSON: approval_authority_model.json",
        ["python3", "-m", "json.tool", "approval_authority_model/approval_authority_model.json"],
    ),
    Check(
        "Validate JSON: approval_evidence_dossier.json",
        ["python3", "-m", "json.tool", "approval_evidence_dossier/approval_evidence_dossier.json"],
    ),
    Check(
        "Validate JSON: durable_approval_record_contract.json",
        ["python3", "-m", "json.tool", "durable_approval_record_contract/durable_approval_record_contract.json"],
    ),
    Check(
        "Validate JSON: real_approval_decision_packet_fixture.json",
        ["python3", "-m", "json.tool", "real_approval_decision_packet_fixture/real_approval_decision_packet_fixture.json"],
    ),
    Check(
        "Validate JSON: approval_validity_policy.json",
        ["python3", "-m", "json.tool", "approval_validity_revocation_policy/approval_validity_policy.json"],
    ),
    Check(
        "Validate JSON: pre_application_snapshot_policy.json",
        ["python3", "-m", "json.tool", "pre_application_snapshot_policy/pre_application_snapshot_policy.json"],
    ),
    Check(
        "Validate JSON: real_application_blocker.json",
        ["python3", "-m", "json.tool", "real_application_boundary_gate/real_application_blocker.json"],
    ),
    Check(
        "Validate JSON: post_approval_preflight_validation_plan.json",
        ["python3", "-m", "json.tool", "post_approval_preflight_validation/post_approval_preflight_validation_plan.json"],
    ),
    Check(
        "Validate JSON: approval_workflow_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "approval_workflow_cieu_audit_fixture/approval_workflow_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: real_approval_workflow_readiness.json",
        ["python3", "-m", "json.tool", "real_approval_workflow_readiness/real_approval_workflow_readiness.json"],
    ),
    Check(
        "Compile controlled approval record sandbox builder",
        [
            "python3",
            "-m",
            "py_compile",
            "controlled_approval_record_sandbox/tools/build_controlled_approval_record_sandbox.py",
        ],
    ),
    Check(
        "Validate JSON: approval_record_sandbox_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/approval_record_sandbox_summary.json"],
    ),
    Check(
        "Validate JSON: controlled_approval_record_sandbox_contract.json",
        ["python3", "-m", "json.tool", "controlled_approval_record_sandbox/controlled_approval_record_sandbox_contract.json"],
    ),
    Check(
        "Validate JSON: sandbox_approval_record_instance.json",
        ["python3", "-m", "json.tool", "sandbox_approval_record_instance/sandbox_approval_record_instance.json"],
    ),
    Check(
        "Validate JSON: approval_record_integrity_validation_result.json",
        ["python3", "-m", "json.tool", "approval_record_integrity_validation/approval_record_integrity_validation_result.json"],
    ),
    Check(
        "Validate JSON: approval_record_validity_result.json",
        ["python3", "-m", "json.tool", "approval_record_validity_state_machine/approval_record_validity_result.json"],
    ),
    Check(
        "Validate JSON: invalid_record_gate_results.json",
        ["python3", "-m", "json.tool", "expiration_revocation_replay/invalid_record_gate_results.json"],
    ),
    Check(
        "Validate JSON: valid_record_gate_replay_result.json",
        ["python3", "-m", "json.tool", "approval_record_pre_application_gate_replay/valid_record_gate_replay_result.json"],
    ),
    Check(
        "Validate JSON: sandbox_approval_record_audit_lineage.json",
        ["python3", "-m", "json.tool", "approval_record_audit_lineage/sandbox_approval_record_audit_lineage.json"],
    ),
    Check(
        "Validate JSON: approval_record_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "approval_record_cieu_residual/approval_record_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: controlled_approval_record_readiness.json",
        ["python3", "-m", "json.tool", "controlled_approval_record_readiness/controlled_approval_record_readiness.json"],
    ),
    Check(
        "Compile controlled real release preflight builder",
        [
            "python3",
            "-m",
            "py_compile",
            "controlled_real_release_preflight/tools/build_controlled_real_release_preflight.py",
        ],
    ),
    Check(
        "Validate JSON: real_release_preflight_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/real_release_preflight_summary.json"],
    ),
    Check(
        "Validate JSON: controlled_real_release_preflight_contract.json",
        ["python3", "-m", "json.tool", "controlled_real_release_preflight/controlled_real_release_preflight_contract.json"],
    ),
    Check(
        "Validate JSON: release_candidate_package.json",
        ["python3", "-m", "json.tool", "release_candidate_package/release_candidate_package.json"],
    ),
    Check(
        "Validate JSON: release_scope_validation_result.json",
        ["python3", "-m", "json.tool", "release_scope_validation/release_scope_validation_result.json"],
    ),
    Check(
        "Validate JSON: approval_record_preflight_validation_result.json",
        ["python3", "-m", "json.tool", "approval_record_preflight_validation/approval_record_preflight_validation_result.json"],
    ),
    Check(
        "Validate JSON: snapshot_preflight_validation_result.json",
        ["python3", "-m", "json.tool", "snapshot_and_rollback_preflight/snapshot_preflight_validation_result.json"],
    ),
    Check(
        "Validate JSON: y_star_non_mutation_preflight_result.json",
        ["python3", "-m", "json.tool", "invariant_preflight_validation/y_star_non_mutation_preflight_result.json"],
    ),
    Check(
        "Validate JSON: post_release_validation_matrix.json",
        ["python3", "-m", "json.tool", "post_release_validation_matrix/post_release_validation_matrix.json"],
    ),
    Check(
        "Validate JSON: release_operator_handoff_packet.json",
        ["python3", "-m", "json.tool", "release_operator_handoff_packet/release_operator_handoff_packet.json"],
    ),
    Check(
        "Validate JSON: release_blocker_decision.json",
        ["python3", "-m", "json.tool", "release_blocker_decision/release_blocker_decision.json"],
    ),
    Check(
        "Validate JSON: release_preflight_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "release_preflight_cieu_residual/release_preflight_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: controlled_real_release_preflight_readiness.json",
        ["python3", "-m", "json.tool", "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json"],
    ),
    Check(
        "Compile real release simulation sandbox builder",
        [
            "python3",
            "-m",
            "py_compile",
            "real_release_simulation_sandbox/tools/build_real_release_simulation_sandbox.py",
        ],
    ),
    Check(
        "Validate JSON: real_release_simulation_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/real_release_simulation_summary.json"],
    ),
    Check(
        "Validate JSON: real_release_simulation_sandbox_contract.json",
        ["python3", "-m", "json.tool", "real_release_simulation_sandbox/real_release_simulation_sandbox_contract.json"],
    ),
    Check(
        "Validate JSON: sandbox_release_authority_fixture.json",
        ["python3", "-m", "json.tool", "sandbox_release_authority_fixture/sandbox_release_authority_fixture.json"],
    ),
    Check(
        "Validate JSON: simulated_durable_approval_record.json",
        ["python3", "-m", "json.tool", "simulated_durable_approval_record/simulated_durable_approval_record.json"],
    ),
    Check(
        "Validate JSON: sandbox_release_snapshot_manifest.json",
        ["python3", "-m", "json.tool", "sandbox_release_snapshot/sandbox_release_snapshot_manifest.json"],
    ),
    Check(
        "Validate JSON: sandbox_release_execution_result.json",
        ["python3", "-m", "json.tool", "sandbox_release_execution_result/sandbox_release_execution_result.json"],
    ),
    Check(
        "Validate JSON: sandbox_post_release_validation_result.json",
        ["python3", "-m", "json.tool", "sandbox_post_release_validation/sandbox_post_release_validation_result.json"],
    ),
    Check(
        "Validate JSON: sandbox_post_release_behavior_y_star.json",
        ["python3", "-m", "json.tool", "sandbox_release_projection_and_mcp_preview/sandbox_post_release_behavior_y_star.json"],
    ),
    Check(
        "Validate JSON: sandbox_release_rollback_result.json",
        ["python3", "-m", "json.tool", "sandbox_release_rollback_drill/sandbox_release_rollback_result.json"],
    ),
    Check(
        "Validate JSON: release_simulation_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "release_simulation_cieu_residual/release_simulation_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: real_release_simulation_readiness.json",
        ["python3", "-m", "json.tool", "real_release_simulation_readiness/real_release_simulation_readiness.json"],
    ),
    Check(
        "Compile live boundary no-go framework builder",
        [
            "python3",
            "-m",
            "py_compile",
            "live_boundary_no_go_framework/tools/build_live_boundary_no_go_framework.py",
        ],
    ),
    Check(
        "Validate JSON: live_boundary_no_go_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/live_boundary_no_go_summary.json"],
    ),
    Check(
        "Validate JSON: live_boundary_no_go_contract.json",
        ["python3", "-m", "json.tool", "live_boundary_no_go_framework/live_boundary_no_go_contract.json"],
    ),
    Check(
        "Validate JSON: live_capability_domain_registry.json",
        ["python3", "-m", "json.tool", "live_capability_domain_registry/live_capability_domain_registry.json"],
    ),
    Check(
        "Validate JSON: no_go_invariant_matrix.json",
        ["python3", "-m", "json.tool", "no_go_invariant_matrix/no_go_invariant_matrix.json"],
    ),
    Check(
        "Validate JSON: l5_chain_evidence_map.json",
        ["python3", "-m", "json.tool", "live_readiness_evidence_index/l5_chain_evidence_map.json"],
    ),
    Check(
        "Validate JSON: live_blocker_risk_register.json",
        ["python3", "-m", "json.tool", "live_blocker_risk_register/live_blocker_risk_register.json"],
    ),
    Check(
        "Validate JSON: l6_meta_development_entry_gate.json",
        ["python3", "-m", "json.tool", "l6_meta_development_entry_gate/l6_meta_development_entry_gate.json"],
    ),
    Check(
        "Validate JSON: system_no_go_decision_packet.json",
        ["python3", "-m", "json.tool", "system_no_go_decision_packet/system_no_go_decision_packet.json"],
    ),
    Check(
        "Validate JSON: live_boundary_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "live_boundary_cieu_residual/live_boundary_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: live_boundary_readiness.json",
        ["python3", "-m", "json.tool", "live_boundary_readiness/live_boundary_readiness.json"],
    ),
    Check(
        "Compile L6 meta-development generative selection engine builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_meta_development_generative_selection_engine/tools/build_l6_meta_development_generative_selection_engine.py",
        ],
    ),
    Check(
        "Validate JSON: l6_meta_development_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_meta_development_summary.json"],
    ),
    Check(
        "Validate JSON: l6_generative_selection_engine_contract.json",
        ["python3", "-m", "json.tool", "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_contract.json"],
    ),
    Check(
        "Validate JSON: self_model_v0.json",
        ["python3", "-m", "json.tool", "self_model_and_unique_asset_field/self_model_v0.json"],
    ),
    Check(
        "Validate JSON: unique_asset_field.json",
        ["python3", "-m", "json.tool", "self_model_and_unique_asset_field/unique_asset_field.json"],
    ),
    Check(
        "Validate JSON: world_value_field_schema.json",
        ["python3", "-m", "json.tool", "world_value_field_model/world_value_field_schema.json"],
    ),
    Check(
        "Validate JSON: value_conversion_operator_library.json",
        ["python3", "-m", "json.tool", "value_conversion_operator_library/value_conversion_operator_library.json"],
    ),
    Check(
        "Validate JSON: generated_value_hypotheses.json",
        ["python3", "-m", "json.tool", "open_value_hypothesis_generator/generated_value_hypotheses.json"],
    ),
    Check(
        "Validate JSON: value_conversion_physics_schema.json",
        ["python3", "-m", "json.tool", "value_conversion_physics/value_conversion_physics_schema.json"],
    ),
    Check(
        "Validate JSON: redeemability_selection_policy.json",
        ["python3", "-m", "json.tool", "redeemability_selection_engine/redeemability_selection_policy.json"],
    ),
    Check(
        "Validate JSON: selected_hypothesis_mvp_plans.json",
        ["python3", "-m", "json.tool", "minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json"],
    ),
    Check(
        "Validate JSON: governed_experiment_portfolio.json",
        ["python3", "-m", "json.tool", "governed_meta_development_experiment_portfolio/governed_experiment_portfolio.json"],
    ),
    Check(
        "Validate JSON: meta_development_cieu_event_fixture.json",
        ["python3", "-m", "json.tool", "strategic_residual_meta_learning_loop/meta_development_cieu_event_fixture.json"],
    ),
    Check(
        "Validate JSON: l6_meta_development_design_readiness.json",
        ["python3", "-m", "json.tool", "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json"],
    ),
    Check(
        "Compile L6.1 MVP artifact sandbox builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_meta_development_mvp_artifact_sandbox/tools/build_l6_meta_development_mvp_artifact_sandbox.py",
        ],
    ),
    Check(
        "Validate JSON: l6_mvp_artifact_sandbox_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_mvp_artifact_sandbox_summary.json"],
    ),
    Check(
        "Validate JSON: l6_1_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_meta_development_mvp_artifact_sandbox/l6_1_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_hypotheses_for_mvp_artifacts.json",
        ["python3", "-m", "json.tool", "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json"],
    ),
    Check(
        "Validate JSON: selected_case_index.json",
        ["python3", "-m", "json.tool", "selected_mvp_artifact_cases/selected_case_index.json"],
    ),
    Check(
        "Validate JSON: mvp_artifact_validation_matrix.json",
        ["python3", "-m", "json.tool", "mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json"],
    ),
    Check(
        "Validate JSON: review_gate_contract.json",
        ["python3", "-m", "json.tool", "mvp_artifact_review_gate/review_gate_contract.json"],
    ),
    Check(
        "Validate JSON: externalization_blocker.json",
        ["python3", "-m", "json.tool", "mvp_artifact_externalization_boundary/externalization_blocker.json"],
    ),
    Check(
        "Validate JSON: l6_1_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.2 governed external observation boundary builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_governed_external_observation_boundary/tools/build_l6_governed_external_observation_boundary.py",
        ],
    ),
    Check(
        "Validate JSON: l6_external_observation_boundary_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_external_observation_boundary_summary.json"],
    ),
    Check(
        "Validate JSON: l6_2_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_governed_external_observation_boundary/l6_2_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: pre_observation_packet_schema.json",
        ["python3", "-m", "json.tool", "pre_observation_packet_schema/pre_observation_packet_schema.json"],
    ),
    Check(
        "Validate JSON: source_type_registry.json",
        ["python3", "-m", "json.tool", "external_source_registry_and_policy/source_type_registry.json"],
    ),
    Check(
        "Validate JSON: observation_permission_gate_contract.json",
        ["python3", "-m", "json.tool", "external_observation_permission_gate/observation_permission_gate_contract.json"],
    ),
    Check(
        "Validate JSON: manual_import_contract.json",
        ["python3", "-m", "json.tool", "manual_external_evidence_import_sandbox/manual_import_contract.json"],
    ),
    Check(
        "Validate JSON: no_network_receipt.json",
        ["python3", "-m", "json.tool", "external_observation_no_action_receipts/no_network_receipt.json"],
    ),
    Check(
        "Validate JSON: l6_2_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.3 controlled external observation sandbox builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_external_observation_sandbox/tools/build_l6_controlled_external_observation_sandbox.py",
        ],
    ),
    Check(
        "Validate JSON: l6_controlled_observation_sandbox_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_controlled_observation_sandbox_summary.json"],
    ),
    Check(
        "Validate JSON: l6_3_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_external_observation_sandbox/l6_3_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_observation_cases.json",
        ["python3", "-m", "json.tool", "l6_observation_case_selector/selected_observation_cases.json"],
    ),
    Check(
        "Validate JSON: pre_observation_packet_index.json",
        ["python3", "-m", "json.tool", "controlled_pre_observation_packets/pre_observation_packet_index.json"],
    ),
    Check(
        "Validate JSON: packet_permission_decisions.json",
        ["python3", "-m", "json.tool", "sandbox_observation_permission_replay/packet_permission_decisions.json"],
    ),
    Check(
        "Validate JSON: observation_fixture_index.json",
        ["python3", "-m", "json.tool", "static_manual_observation_fixtures/observation_fixture_index.json"],
    ),
    Check(
        "Validate JSON: fixture_validation_results.json",
        ["python3", "-m", "json.tool", "observation_evidence_validation_sandbox/fixture_validation_results.json"],
    ),
    Check(
        "Validate JSON: refinement_candidate_index.json",
        ["python3", "-m", "json.tool", "observation_to_artifact_refinement_candidates/refinement_candidate_index.json"],
    ),
    Check(
        "Validate JSON: l6_3_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.4 real read-only observation preflight builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_real_read_only_external_observation_preflight/tools/build_l6_real_read_only_external_observation_preflight.py",
        ],
    ),
    Check(
        "Validate JSON: l6_real_observation_preflight_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_real_observation_preflight_summary.json"],
    ),
    Check(
        "Validate JSON: l6_4_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_real_read_only_external_observation_preflight/l6_4_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_real_observation_candidates.json",
        ["python3", "-m", "json.tool", "real_observation_candidate_selector/selected_real_observation_candidates.json"],
    ),
    Check(
        "Validate JSON: preflight_requirement_registry.json",
        ["python3", "-m", "json.tool", "real_read_only_observation_preflight_contract/preflight_requirement_registry.json"],
    ),
    Check(
        "Validate JSON: approval_packet_examples_blocked_now.json",
        ["python3", "-m", "json.tool", "real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json"],
    ),
    Check(
        "Validate JSON: network_isolation_requirement.json",
        ["python3", "-m", "json.tool", "observation_network_isolation_preflight/network_isolation_requirement.json"],
    ),
    Check(
        "Validate JSON: evidence_capture_contract.json",
        ["python3", "-m", "json.tool", "observation_evidence_capture_preflight/evidence_capture_contract.json"],
    ),
    Check(
        "Validate JSON: candidate_preflight_decisions.json",
        ["python3", "-m", "json.tool", "real_observation_preflight_decision_gate/candidate_preflight_decisions.json"],
    ),
    Check(
        "Validate JSON: l6_4_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.5 controlled real read-only observation pilot design builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_real_read_only_observation_pilot_design/tools/build_l6_controlled_real_read_only_observation_pilot_design.py",
        ],
    ),
    Check(
        "Validate JSON: l6_pilot_design_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_pilot_design_summary.json"],
    ),
    Check(
        "Validate JSON: l6_5_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_real_read_only_observation_pilot_design/l6_5_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_pilot_candidates.json",
        ["python3", "-m", "json.tool", "pilot_candidate_selector/selected_pilot_candidates.json"],
    ),
    Check(
        "Validate JSON: pilot_approval_packet_index.json",
        ["python3", "-m", "json.tool", "pilot_approval_packet_candidates/pilot_approval_packet_index.json"],
    ),
    Check(
        "Validate JSON: operator_step_sequence.json",
        ["python3", "-m", "json.tool", "pilot_operator_runbook/operator_step_sequence.json"],
    ),
    Check(
        "Validate JSON: pilot_evidence_packet_template.json",
        ["python3", "-m", "json.tool", "pilot_evidence_packet_templates/pilot_evidence_packet_template.json"],
    ),
    Check(
        "Validate JSON: no_real_observation_execution_receipt.json",
        ["python3", "-m", "json.tool", "pilot_no_action_and_execution_blockers/no_real_observation_execution_receipt.json"],
    ),
    Check(
        "Validate JSON: pilot_candidate_decisions.json",
        ["python3", "-m", "json.tool", "pilot_design_decision_gate/pilot_candidate_decisions.json"],
    ),
    Check(
        "Validate JSON: l6_5_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_pilot_design_readiness/l6_5_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.6 controlled observation pilot approval packet builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_observation_pilot_approval_packet/tools/build_l6_controlled_observation_pilot_approval_packet.py",
        ],
    ),
    Check(
        "Validate JSON: l6_pilot_approval_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_pilot_approval_summary.json"],
    ),
    Check(
        "Validate JSON: l6_6_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_observation_pilot_approval_packet/l6_6_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_approval_candidates.json",
        ["python3", "-m", "json.tool", "pilot_approval_candidate_selector/selected_approval_candidates.json"],
    ),
    Check(
        "Validate JSON: approval_packet_index.json",
        ["python3", "-m", "json.tool", "pilot_approval_packet_assembler/approval_packet_index.json"],
    ),
    Check(
        "Validate JSON: evidence_dossier_index.json",
        ["python3", "-m", "json.tool", "pilot_approval_evidence_dossier/evidence_dossier_index.json"],
    ),
    Check(
        "Validate JSON: approval_packet_risk_matrix.json",
        ["python3", "-m", "json.tool", "pilot_approval_risk_review/approval_packet_risk_matrix.json"],
    ),
    Check(
        "Validate JSON: approval_packet_decision_matrix.json",
        ["python3", "-m", "json.tool", "pilot_approval_decision_sandbox/approval_packet_decision_matrix.json"],
    ),
    Check(
        "Validate JSON: l6_6_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_pilot_approval_readiness/l6_6_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.7 integrated approval record and pilot readiness sandbox builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_integrated_approval_record_and_pilot_readiness_sandbox/tools/build_l6_integrated_approval_record_and_pilot_readiness_sandbox.py",
        ],
    ),
    Check(
        "Validate JSON: l6_integrated_pilot_readiness_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_integrated_pilot_readiness_summary.json"],
    ),
    Check(
        "Validate JSON: l6_7_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: sandbox_approval_record_index.json",
        ["python3", "-m", "json.tool", "sandbox_approval_record_lifecycle/sandbox_approval_record_index.json"],
    ),
    Check(
        "Validate JSON: pilot_run_package_index.json",
        ["python3", "-m", "json.tool", "pilot_run_package_assembler/pilot_run_package_index.json"],
    ),
    Check(
        "Validate JSON: manual_evidence_import_readiness_contract.json",
        ["python3", "-m", "json.tool", "manual_evidence_import_readiness/manual_evidence_import_readiness_contract.json"],
    ),
    Check(
        "Validate JSON: integrated_candidate_decision_matrix.json",
        ["python3", "-m", "json.tool", "pilot_integrated_decision_gate/integrated_candidate_decision_matrix.json"],
    ),
    Check(
        "Validate JSON: l6_7_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.8 agentic evidence discovery trust engine builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_agentic_evidence_discovery_trust_engine/tools/build_l6_agentic_evidence_discovery_trust_engine.py",
        ],
    ),
    Check(
        "Validate JSON: l6_agentic_evidence_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_agentic_evidence_summary.json"],
    ),
    Check(
        "Validate JSON: l6_8_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_agentic_evidence_discovery_trust_engine/l6_8_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: inferred_evidence_needs.json",
        ["python3", "-m", "json.tool", "evidence_need_inference_engine/inferred_evidence_needs.json"],
    ),
    Check(
        "Validate JSON: source_hypothesis_index.json",
        ["python3", "-m", "json.tool", "autonomous_source_hypothesis_generator/source_hypothesis_index.json"],
    ),
    Check(
        "Validate JSON: trust_judgment_matrix.json",
        ["python3", "-m", "json.tool", "evidence_trust_judgment_model/trust_judgment_matrix.json"],
    ),
    Check(
        "Validate JSON: evidence_need_voi_matrix.json",
        ["python3", "-m", "json.tool", "evidence_value_of_information_model/evidence_need_voi_matrix.json"],
    ),
    Check(
        "Validate JSON: ranked_source_hypotheses.json",
        ["python3", "-m", "json.tool", "source_prioritization_and_ranking_engine/ranked_source_hypotheses.json"],
    ),
    Check(
        "Validate JSON: observation_work_order_index.json",
        ["python3", "-m", "json.tool", "observation_work_order_generator/observation_work_order_index.json"],
    ),
    Check(
        "Validate JSON: evidence_discovery_decision_matrix.json",
        ["python3", "-m", "json.tool", "agentic_evidence_decision_gate/evidence_discovery_decision_matrix.json"],
    ),
    Check(
        "Validate JSON: l6_8_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_agentic_evidence_readiness_report/l6_8_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.9 controlled agentic evidence pilot approval dry-run builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_agentic_evidence_pilot_approval_dry_run/tools/build_l6_controlled_agentic_evidence_pilot_approval_dry_run.py",
        ],
    ),
    Check(
        "Validate JSON: l6_agentic_pilot_dry_run_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_agentic_pilot_dry_run_summary.json"],
    ),
    Check(
        "Validate JSON: l6_9_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_agentic_pilot_work_orders.json",
        ["python3", "-m", "json.tool", "agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json"],
    ),
    Check(
        "Validate JSON: approval_eligibility_matrix.json",
        ["python3", "-m", "json.tool", "agentic_pilot_approval_eligibility_gate/approval_eligibility_matrix.json"],
    ),
    Check(
        "Validate JSON: agentic_pilot_approval_packet_index.json",
        ["python3", "-m", "json.tool", "agentic_pilot_approval_packet_assembler/agentic_pilot_approval_packet_index.json"],
    ),
    Check(
        "Validate JSON: sandbox_approval_record_index.json",
        ["python3", "-m", "json.tool", "agentic_pilot_sandbox_approval_records/sandbox_approval_record_index.json"],
    ),
    Check(
        "Validate JSON: dry_run_trace_index.json",
        ["python3", "-m", "json.tool", "agentic_pilot_dry_run_executor/dry_run_trace_index.json"],
    ),
    Check(
        "Validate JSON: simulated_empty_evidence_packet_index.json",
        ["python3", "-m", "json.tool", "agentic_pilot_empty_evidence_capture_simulator/simulated_empty_evidence_packet_index.json"],
    ),
    Check(
        "Validate JSON: l6_9_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_agentic_pilot_dry_run_readiness_report/l6_9_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.10 tiny real read-only observation pilot builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_tiny_real_read_only_agentic_evidence_observation_pilot/tools/build_l6_tiny_real_read_only_agentic_evidence_observation_pilot.py",
        ],
    ),
    Check(
        "Validate JSON: l6_tiny_observation_pilot_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_tiny_observation_pilot_summary.json"],
    ),
    Check(
        "Validate JSON: l6_10_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_tiny_observation_work_order.json",
        ["python3", "-m", "json.tool", "tiny_observation_work_order_selector/selected_tiny_observation_work_order.json"],
    ),
    Check(
        "Validate JSON: tiny_observation_trace.json",
        ["python3", "-m", "json.tool", "tiny_real_read_only_observation_trace/tiny_observation_trace.json"],
    ),
    Check(
        "Validate JSON: tiny_evidence_packet.json",
        ["python3", "-m", "json.tool", "tiny_evidence_capture_packet/tiny_evidence_packet.json"],
    ),
    Check(
        "Validate JSON: l6_10_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_tiny_observation_readiness_report/l6_10_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.10R controlled locator retry builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_source_locator_resolution_tiny_observation_retry/tools/build_l6_controlled_source_locator_resolution_tiny_observation_retry.py",
        ],
    ),
    Check(
        "Validate JSON: l6_10r_locator_retry_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_10r_locator_retry_summary.json"],
    ),
    Check(
        "Validate JSON: l6_10r_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: selected_locator_retry_work_order.json",
        ["python3", "-m", "json.tool", "locator_retry_work_order_selector/selected_locator_retry_work_order.json"],
    ),
    Check(
        "Validate JSON: locator_resolution_trace.json",
        ["python3", "-m", "json.tool", "controlled_locator_resolution_trace/locator_resolution_trace.json"],
    ),
    Check(
        "Validate JSON: retry_observation_trace.json",
        ["python3", "-m", "json.tool", "tiny_observation_retry_trace/retry_observation_trace.json"],
    ),
    Check(
        "Validate JSON: retry_evidence_packet.json",
        ["python3", "-m", "json.tool", "tiny_retry_evidence_capture_packet/retry_evidence_packet.json"],
    ),
    Check(
        "Validate JSON: l6_10r_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_10r_readiness_report/l6_10r_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.10T governed toolmaking builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_governed_capability_gap_toolmaking_locator_resolver/tools/build_l6_governed_capability_gap_toolmaking_locator_resolver.py",
        ],
    ),
    Check(
        "Compile L6.10T controlled locator resolver stub",
        [
            "python3",
            "-m",
            "py_compile",
            "controlled_locator_resolver_interface/controlled_locator_resolver_python_stub.py",
        ],
    ),
    Check(
        "Validate JSON: l6_10t_toolmaking_locator_resolver_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_10t_toolmaking_locator_resolver_summary.json"],
    ),
    Check(
        "Validate JSON: l6_10t_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: l6_10_l6_10r_blocker_analysis.json",
        ["python3", "-m", "json.tool", "capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json"],
    ),
    Check(
        "Validate JSON: resolver_capability_probe_result.json",
        ["python3", "-m", "json.tool", "locator_resolver_capability_probe/resolver_capability_probe_result.json"],
    ),
    Check(
        "Validate JSON: adapter_trace.json",
        ["python3", "-m", "json.tool", "locator_resolution_adapter_trace/adapter_trace.json"],
    ),
    Check(
        "Validate JSON: l6_10t_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_10t_readiness_report/l6_10t_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.10U controlled locator resolver builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_locator_resolver_enablement/tools/build_l6_controlled_locator_resolver_enablement.py",
        ],
    ),
    Check(
        "Compile L6.10U controlled locator resolver runtime",
        [
            "python3",
            "-m",
            "py_compile",
            "controlled_locator_resolver_runtime/controlled_locator_resolver.py",
        ],
    ),
    Check(
        "Validate JSON: l6_10u_locator_resolver_enablement_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_10u_locator_resolver_enablement_summary.json"],
    ),
    Check(
        "Validate JSON: l6_10u_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_locator_resolver_enablement/l6_10u_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: l6_10u_locator_resolution_result.json",
        ["python3", "-m", "json.tool", "controlled_locator_resolution_attempt/locator_resolution_result.json"],
    ),
    Check(
        "Validate JSON: l6_10u_tiny_observation_trace.json",
        ["python3", "-m", "json.tool", "controlled_locator_observation_result/tiny_observation_trace.json"],
    ),
    Check(
        "Validate JSON: l6_10u_readiness_assessment.json",
        ["python3", "-m", "json.tool", "controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.10V controlled seed/search resolver builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_controlled_seed_locator_or_search_resolver_enablement/tools/build_l6_controlled_seed_locator_or_search_resolver_enablement.py",
        ],
    ),
    Check(
        "Compile L6.10V explicit controlled search resolver runtime",
        [
            "python3",
            "-m",
            "py_compile",
            "explicit_controlled_search_resolver/explicit_search_resolver_runtime.py",
        ],
    ),
    Check(
        "Validate JSON: l6_10v_seed_or_search_resolver_enablement_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_10v_seed_or_search_resolver_enablement_summary.json"],
    ),
    Check(
        "Validate JSON: l6_10v_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: l6_10v_locator_resolution_v_result.json",
        ["python3", "-m", "json.tool", "locator_resolution_v_attempt/locator_resolution_v_result.json"],
    ),
    Check(
        "Validate JSON: l6_10v_tiny_observation_v_trace.json",
        ["python3", "-m", "json.tool", "tiny_observation_v_result/tiny_observation_v_trace.json"],
    ),
    Check(
        "Validate JSON: l6_10v_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_10v_read_model/l6_10v_readiness_assessment.json"],
    ),
    Check(
        "Compile L6.10W reviewed seed locator injection builder",
        [
            "python3",
            "-m",
            "py_compile",
            "l6_reviewed_seed_locator_injection_tiny_retry/tools/build_l6_reviewed_seed_locator_injection_tiny_retry.py",
        ],
    ),
    Check(
        "Validate JSON: l6_10w_reviewed_seed_locator_injection_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/l6_10w_reviewed_seed_locator_injection_summary.json"],
    ),
    Check(
        "Validate JSON: l6_10w_milestone_contract.json",
        ["python3", "-m", "json.tool", "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_milestone_contract.json"],
    ),
    Check(
        "Validate JSON: l6_10w_reviewed_seed_locator_candidate.json",
        ["python3", "-m", "json.tool", "reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json"],
    ),
    Check(
        "Validate JSON: l6_10w_user_action_required.json",
        ["python3", "-m", "json.tool", "seed_locator_user_action_request/user_action_required.json"],
    ),
    Check(
        "Validate JSON: l6_10w_tiny_seed_observation_trace.json",
        ["python3", "-m", "json.tool", "seed_locator_retry_result/tiny_seed_observation_trace.json"],
    ),
    Check(
        "Validate JSON: l6_10w_readiness_assessment.json",
        ["python3", "-m", "json.tool", "l6_10w_read_model/l6_10w_readiness_assessment.json"],
    ),
    Check(
        "Validate JSON: markdown_report_candidates.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"],
    ),
    Check(
        "Validate JSON: mining_manifest.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json"],
    ),
    Check(
        "Validate JSON: candidate_review_queue.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json"],
    ),
    Check(
        "Validate JSON: review_queue_manifest.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/safe_mining/review_queue/generated/review_queue_manifest.json"],
    ),
    Check(
        "Validate JSON: artifact_disposition_index.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json"],
    ),
    Check(
        "Validate JSON: disposition_manifest.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/backlog_disposition/generated/disposition_manifest.json"],
    ),
    Check(
        "Validate JSON: evidence_scores.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json"],
    ),
    Check(
        "Validate JSON: review_decision_stub.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json"],
    ),
    Check(
        "Validate JSON: hint_routing_index.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json"],
    ),
    Check(
        "Validate JSON: evidence_review_manifest.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/evidence_review/generated/evidence_review_manifest.json"],
    ),
    Check(
        "Validate JSON: sample_hook_envelope.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/generated/sample_hook_envelope.json"],
    ),
    Check(
        "Validate JSON: envelope_manifest.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/generated/envelope_manifest.json"],
    ),
    Check(
        "Validate JSON: governance_decision_snapshot.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/generated/governance_decision_snapshot.json"],
    ),
    Check(
        "Validate JSON: bridge_run_manifest.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/generated/bridge_run_manifest.json"],
    ),
    Check(
        "Validate JSON: pre_u_packet_manifest.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/pre_u_generator/generated/pre_u_packet_manifest.json"],
    ),
    Check(
        "Validate JSON: hook_envelope_manifest.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/pre_u_generator/generated/hook_envelope_manifest.json"],
    ),
    Check(
        "Validate JSON: governance_decision_snapshots.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json"],
    ),
    Check(
        "Validate JSON: pre_u_governance_run_manifest.json",
        ["python3", "-m", "json.tool", "labs_governance_bridge/pre_u_generator/generated/pre_u_governance_run_manifest.json"],
    ),
    Check(
        "Validate JSON: generation_manifest.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/generation_manifest.json"],
    ),
    Check(
        "Validate JSON: readiness_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/readiness_summary.json"],
    ),
    Check(
        "Static team read model validator",
        ["python3", "console_read_model/validation/validate_team_read_model.py"],
    ),
    Check(
        "Team console validate-local",
        ["python3", "console_read_model/cli/team_console.py", "validate-local"],
    ),
    Check(
        "CLI smoke: quarantine",
        ["python3", "console_read_model/cli/team_console.py", "quarantine"],
    ),
    Check(
        "CLI smoke: mining-candidates",
        ["python3", "console_read_model/cli/team_console.py", "mining-candidates"],
    ),
    Check(
        "CLI smoke: review-queue",
        ["python3", "console_read_model/cli/team_console.py", "review-queue"],
    ),
    Check(
        "CLI smoke: artifact-disposition",
        ["python3", "console_read_model/cli/team_console.py", "artifact-disposition"],
    ),
    Check(
        "CLI smoke: evidence-review",
        ["python3", "console_read_model/cli/team_console.py", "evidence-review"],
    ),
    Check(
        "CLI smoke: governance-bridge",
        ["python3", "console_read_model/cli/team_console.py", "governance-bridge"],
    ),
    Check(
        "CLI smoke: pre-u-governance",
        ["python3", "console_read_model/cli/team_console.py", "pre-u-governance"],
    ),
    Check(
        "CLI smoke: labs-acceptance",
        ["python3", "console_read_model/cli/team_console.py", "labs-acceptance"],
    ),
    Check(
        "CLI smoke: cross-repo-alignment",
        ["python3", "console_read_model/cli/team_console.py", "cross-repo-alignment"],
    ),
    Check(
        "CLI smoke: live-readiness",
        ["python3", "console_read_model/cli/team_console.py", "live-readiness"],
    ),
    Check(
        "CLI smoke: live-boundary",
        ["python3", "console_read_model/cli/team_console.py", "live-boundary"],
    ),
    Check(
        "CLI smoke: cieu-boundary",
        ["python3", "console_read_model/cli/team_console.py", "cieu-boundary"],
    ),
    Check(
        "CLI smoke: autonomy-inventory",
        ["python3", "console_read_model/cli/team_console.py", "autonomy-inventory"],
    ),
    Check(
        "CLI smoke: autonomous-cycle",
        ["python3", "console_read_model/cli/team_console.py", "autonomous-cycle"],
    ),
    Check(
        "CLI smoke: legacy-triage",
        ["python3", "console_read_model/cli/team_console.py", "legacy-triage"],
    ),
    Check(
        "CLI smoke: observation-loop",
        ["python3", "console_read_model/cli/team_console.py", "observation-loop"],
    ),
    Check(
        "CLI smoke: readonly-tool",
        ["python3", "console_read_model/cli/team_console.py", "readonly-tool"],
    ),
    Check(
        "CLI smoke: tool-bridge",
        ["python3", "console_read_model/cli/team_console.py", "tool-bridge"],
    ),
    Check(
        "CLI smoke: work-proposal",
        ["python3", "console_read_model/cli/team_console.py", "work-proposal"],
    ),
    Check(
        "CLI smoke: dashboard-refresh",
        ["python3", "console_read_model/cli/team_console.py", "dashboard-refresh"],
    ),
    Check(
        "CLI smoke: recurring-loop",
        ["python3", "console_read_model/cli/team_console.py", "recurring-loop"],
    ),
    Check(
        "CLI smoke: manual-tick",
        ["python3", "console_read_model/cli/team_console.py", "manual-tick"],
    ),
    Check(
        "CLI smoke: field-functional",
        ["python3", "console_read_model/cli/team_console.py", "field-functional"],
    ),
    Check(
        "CLI smoke: mission-projection",
        ["python3", "console_read_model/cli/team_console.py", "mission-projection"],
    ),
    Check(
        "CLI smoke: field-projection",
        ["python3", "console_read_model/cli/team_console.py", "field-projection"],
    ),
    Check(
        "CLI smoke: projection-cycle",
        ["python3", "console_read_model/cli/team_console.py", "projection-cycle"],
    ),
    Check(
        "CLI smoke: shadow-learning-cycle",
        ["python3", "console_read_model/cli/team_console.py", "shadow-learning-cycle"],
    ),
    Check(
        "CLI smoke: cross-repo-governance",
        ["python3", "console_read_model/cli/team_console.py", "cross-repo-governance"],
    ),
    Check(
        "CLI smoke: governed-mcp-adapter",
        ["python3", "console_read_model/cli/team_console.py", "governed-mcp-adapter"],
    ),
    Check(
        "CLI smoke: controlled-canonical-learning",
        ["python3", "console_read_model/cli/team_console.py", "controlled-canonical-learning"],
    ),
    Check(
        "CLI smoke: approved-sandbox-update",
        ["python3", "console_read_model/cli/team_console.py", "approved-sandbox-update"],
    ),
    Check(
        "CLI smoke: real-approval-boundary",
        ["python3", "console_read_model/cli/team_console.py", "real-approval-boundary"],
    ),
    Check(
        "CLI smoke: approval-record-sandbox",
        ["python3", "console_read_model/cli/team_console.py", "approval-record-sandbox"],
    ),
    Check(
        "CLI smoke: real-release-preflight",
        ["python3", "console_read_model/cli/team_console.py", "real-release-preflight"],
    ),
    Check(
        "CLI smoke: release-simulation-sandbox",
        ["python3", "console_read_model/cli/team_console.py", "release-simulation-sandbox"],
    ),
    Check(
        "CLI smoke: live-boundary-no-go",
        ["python3", "console_read_model/cli/team_console.py", "live-boundary-no-go"],
    ),
    Check(
        "CLI smoke: meta-development-design",
        ["python3", "console_read_model/cli/team_console.py", "meta-development-design"],
    ),
    Check(
        "CLI smoke: meta-development-mvp-artifact-sandbox",
        ["python3", "console_read_model/cli/team_console.py", "meta-development-mvp-artifact-sandbox"],
    ),
    Check(
        "CLI smoke: governed-external-observation-boundary",
        ["python3", "console_read_model/cli/team_console.py", "governed-external-observation-boundary"],
    ),
    Check(
        "CLI smoke: controlled-external-observation-sandbox",
        ["python3", "console_read_model/cli/team_console.py", "controlled-external-observation-sandbox"],
    ),
    Check(
        "CLI smoke: real-read-only-observation-preflight",
        ["python3", "console_read_model/cli/team_console.py", "real-read-only-observation-preflight"],
    ),
    Check(
        "CLI smoke: controlled-real-read-only-observation-pilot-design",
        ["python3", "console_read_model/cli/team_console.py", "controlled-real-read-only-observation-pilot-design"],
    ),
    Check(
        "CLI smoke: controlled-observation-pilot-approval-packet",
        ["python3", "console_read_model/cli/team_console.py", "controlled-observation-pilot-approval-packet"],
    ),
    Check(
        "CLI smoke: integrated-approval-record-and-pilot-readiness",
        ["python3", "console_read_model/cli/team_console.py", "integrated-approval-record-and-pilot-readiness"],
    ),
    Check(
        "CLI smoke: agentic-evidence-discovery-trust-engine",
        ["python3", "console_read_model/cli/team_console.py", "agentic-evidence-discovery-trust-engine"],
    ),
    Check(
        "CLI smoke: controlled-agentic-evidence-pilot-approval-dry-run",
        ["python3", "console_read_model/cli/team_console.py", "controlled-agentic-evidence-pilot-approval-dry-run"],
    ),
    Check(
        "CLI smoke: tiny-real-read-only-agentic-evidence-observation-pilot",
        ["python3", "console_read_model/cli/team_console.py", "tiny-real-read-only-agentic-evidence-observation-pilot"],
    ),
    Check(
        "CLI smoke: controlled-source-locator-resolution-tiny-observation-retry",
        ["python3", "console_read_model/cli/team_console.py", "controlled-source-locator-resolution-tiny-observation-retry"],
    ),
    Check(
        "CLI smoke: governed-capability-gap-toolmaking-locator-resolver",
        ["python3", "console_read_model/cli/team_console.py", "governed-capability-gap-toolmaking-locator-resolver"],
    ),
    Check(
        "CLI smoke: controlled-locator-resolver-enable-first-attempt",
        ["python3", "console_read_model/cli/team_console.py", "controlled-locator-resolver-enable-first-attempt"],
    ),
    Check(
        "CLI smoke: controlled-seed-locator-or-search-resolver-enablement",
        ["python3", "console_read_model/cli/team_console.py", "controlled-seed-locator-or-search-resolver-enablement"],
    ),
    Check(
        "CLI smoke: reviewed-seed-locator-injection-tiny-retry",
        ["python3", "console_read_model/cli/team_console.py", "reviewed-seed-locator-injection-tiny-retry"],
    ),
    Check(
        "CLI smoke: sources",
        ["python3", "console_read_model/cli/team_console.py", "sources"],
    ),
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run safe local checks for curated console/quarantine read-model files."
    )
    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="Skip generated-file rebuild steps and validate current generated files only.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print stdout/stderr for every check.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Run all checks and report failures at the end.",
    )
    return parser.parse_args(argv)


def run_check(check: Check, verbose: bool) -> tuple[bool, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", "/tmp/ystar_company_pycache")
    result = subprocess.run(
        check.command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    if verbose and output:
        print(output)
    return result.returncode == 0, output


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    checks = ([] if args.no_rebuild else REBUILD_CHECKS) + VALIDATION_CHECKS
    failures: list[tuple[Check, str]] = []

    print("Y* Company Local Safety Checks")
    print()

    total = len(checks)
    for index, check in enumerate(checks, start=1):
        print(f"[{index}/{total}] {check.label} ... ", end="", flush=True)
        ok, output = run_check(check, args.verbose)
        if ok:
            print("PASS")
            continue

        print("FAIL")
        failures.append((check, output))
        if not args.continue_on_failure:
            break

    print()
    if failures:
        print("Result: FAIL")
        print()
        print("Failures:")
        for check, output in failures:
            print(f"- {check.label}")
            if output and not args.verbose:
                print("  Output:")
                for line in output.splitlines()[:20]:
                    print(f"  {line}")
        return 1

    print("Result: PASS")
    print(
        "Safety note: This wrapper uses only curated read-model inputs and generated "
        "summaries. It does not read DB/log/runtime artifact contents."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
