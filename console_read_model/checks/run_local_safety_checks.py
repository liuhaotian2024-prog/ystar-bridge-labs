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
        "Refresh team console snapshot after mission projection harness",
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
