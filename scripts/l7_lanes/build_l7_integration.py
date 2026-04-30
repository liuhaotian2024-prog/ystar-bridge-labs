#!/usr/bin/env python3
"""Build L7.0P integration manifest from lane outputs."""

from __future__ import annotations

from common import LANES, MILESTONE_ID, MILESTONE_NAME, RUN_ID, base_no_action_receipt, lane_status, simple_md, write_json, write_text


OUTPUT_DIR = "l7_parallel_commercial_agent_team_orchestrator"


def build() -> None:
    status = lane_status()
    lane_map = {lane["lane_id"]: lane for lane in status["lanes"]}
    receipt = base_no_action_receipt(MILESTONE_ID, MILESTONE_NAME)
    receipt.update(
        {
            "parallel_orchestration_script_created": True,
            "worktree_setup_automation_created": True,
            "lane_builders_created": True,
            "lane_prompts_created": True,
        }
    )

    summary = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "run_id": RUN_ID,
        "mode": "parallel_commercial_agent_team_orchestrator",
        "l7a_agent_team_runtime_created": lane_map["L7A"]["status"] == "complete",
        "l7b_revenue_radar_created": lane_map["L7B"]["status"] == "complete",
        "l7c_human_approved_action_gate_created": lane_map["L7C"]["status"] == "complete",
        "l7d_writeback_protocol_created": lane_map["L7D"]["status"] == "complete",
        "l7e_owner_cockpit_created": lane_map["L7E"]["status"] == "complete",
        "parallel_orchestration_script_created": True,
        "lane_builder_scripts_created": True,
        "lane_prompt_files_created": True,
        "all_lanes_complete": status["all_lanes_complete"],
        "external_actions_still_blocked": True,
        "core_writebacks_still_blocked": True,
        "next_recommended_safe_command": "bash scripts/run_l7_parallel_lanes.sh --mode local-parallel",
        "then": "run_revenue_opportunity_radar_read_only",
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
    }

    manifest = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "run_id": RUN_ID,
        "lanes": LANES,
        "lane_status": status["lanes"],
        "orchestration_script": "scripts/run_l7_parallel_lanes.sh",
        "supported_modes": ["scaffold", "local-parallel", "worktree-setup", "status"],
        "default_mode": "local-parallel",
        "future_one_command_runner": "bash scripts/run_l7_parallel_lanes.sh",
        "manual_codex_windows_required": False,
        "manual_worktree_creation_required": False,
        "manual_prompt_distribution_required": False,
        "manual_branch_merge_required": False,
        "network_required": False,
        "api_keys_required": False,
    }

    write_json(f"{OUTPUT_DIR}/l7_0p_lane_status.json", status)
    write_json(f"{OUTPUT_DIR}/l7_0p_integration_manifest.json", manifest)
    write_json(f"{OUTPUT_DIR}/l7_0p_no_action_receipt.json", receipt)
    write_json(f"{OUTPUT_DIR}/l7_0p_summary.json", summary)
    write_text(f"{OUTPUT_DIR}/l7_0p_summary.md", simple_md("L7.0P Parallel Commercial Agent Team Orchestrator", summary))


if __name__ == "__main__":
    build()
