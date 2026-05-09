from __future__ import annotations

import os
import sys
from pathlib import Path

from office.mission_command.e110_labs_universal_operating_control_plane import (
    build_operation_context,
    enforce_labs_universal_control_before_runtime,
    resolve_required_capabilities_for_operation,
)
from office.mission_command.e113_no_new_wheel_runtime_law import (
    build_default_e113_action_context,
    build_capability_utilization_matrix,
    build_full_system_capability_index,
    build_no_new_wheel_runtime_law_packet,
    infer_mandatory_capability_domains,
    run_no_new_wheel_runtime_law_session,
)


BRIDGE_ROOT = Path(os.environ.get("E113_TEST_BRIDGE_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs"))
YSTAR_ROOT = Path(os.environ.get("E113_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("E113_TEST_GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))


def test_capability_index_scans_three_repos_and_finds_existing_czl():
    index = build_full_system_capability_index(
        bridge_root=BRIDGE_ROOT,
        ystar_gov_root=YSTAR_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )
    discovery = index["repository_discovery"]
    domains = {row["domain_id"]: row for row in index["capability_domains"]}

    assert set(discovery["repos_scanned"]) == {"bridge-labs", "Y-star-gov", "gov-mcp"}
    assert discovery["tracked_file_counts"]["bridge-labs"] > 0
    assert discovery["tracked_file_counts"]["Y-star-gov"] > 0
    assert discovery["tracked_file_counts"]["gov-mcp"] > 0
    assert domains["czl_residual_loop_engine"]["runtime_status"] == "runtime_active"
    assert "ystar/governance/residual_loop_engine.py" in domains["czl_residual_loop_engine"]["existing_source_paths"]


def test_residual_goal_brain_strategy_context_requires_reuse_of_existing_systems():
    context = build_default_e113_action_context()
    mandatory = infer_mandatory_capability_domains(context)

    for domain_id in (
        "czl_residual_loop_engine",
        "czl_message_protocol",
        "cieu_prediction_delta",
        "goal_tree_and_y_star_field",
        "aiden_brain_runtime",
        "open_world_strategy_runtime",
        "ceo_implementation_order",
        "gov_mcp_dry_run_boundary",
        "cieu_store_formal_memory",
    ):
        assert domain_id in mandatory


def test_capability_utilization_matrix_exposes_existing_system_universe():
    context = build_default_e113_action_context()
    index = build_full_system_capability_index(
        bridge_root=BRIDGE_ROOT,
        ystar_gov_root=YSTAR_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )
    matrix = build_capability_utilization_matrix(context, capability_index=index, bridge_root=BRIDGE_ROOT)
    relevant = {row["domain_id"]: row for row in matrix["action_relevant_capability_groups"]}

    assert matrix["code_index_loaded"] is True
    assert matrix["indexed_capability_counts"]["total_functions"] > 1000
    assert matrix["unreviewed_runtime_active_capability_count"] == 0
    assert "czl_residual_loop_engine" in relevant
    assert "open_world_strategy_runtime" in relevant
    assert "aiden_brain_runtime" in relevant
    assert "available_for_future_activation" in matrix
    assert matrix["all_registered_capability_groups"]


def test_no_new_wheel_runtime_law_writes_cieu_and_closes_rt_zero(tmp_path):
    result = run_no_new_wheel_runtime_law_session(
        cieu_db=tmp_path / "e113_no_new_wheel.db",
        ystar_gov_root=YSTAR_ROOT,
        seal_session=False,
    )

    assert result["runtime_law_proven"] is True
    assert result["Rt_plus_1"] == 0.0
    assert result["no_new_wheel_gate"]["Y_star_gov_no_new_wheel_decision"] == "ALLOW"
    assert result["no_new_wheel_gate"]["runtime_law_packet"]["capability_utilization_matrix"]["code_index_loaded"] is True
    assert "NO_NEW_WHEEL_RUNTIME_LAW_DECISION" in result["CIEUStore_summary"]["event_types"]


def test_parallel_rebuild_attempt_is_denied_by_y_star_validator():
    packet = build_no_new_wheel_runtime_law_packet(
        build_default_e113_action_context(),
        bridge_root=BRIDGE_ROOT,
        ystar_gov_root=YSTAR_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )
    packet["reuse_plan"][0]["reuse_mode"] = "new_parallel_system"
    packet["no_new_wheel_proof"]["parallel_rebuild_detected"] = True
    packet["CZL_closure"]["Y_t_plus_1"]["parallel_rebuild_detected"] = True
    packet["CZL_closure"]["R_t_plus_1"] = 1.0

    if str(YSTAR_ROOT) not in sys.path:
        sys.path.insert(0, str(YSTAR_ROOT))
    from ystar.governance.no_new_wheel_runtime_law import validate_no_new_wheel_runtime_law_packet

    decision = validate_no_new_wheel_runtime_law_packet(packet).to_dict()
    assert decision["decision"] == "DENY"
    assert "parallel rebuild is forbidden" in decision["reason"]


def test_e110_universal_control_plane_requires_no_new_wheel_runtime_law(tmp_path):
    context = build_operation_context(
        owner_intent="Aiden: global money strategy with residual learning and Codex implementation",
        operation_id="e113_e110_gate_session",
        market_strategy_required=True,
        codex_prompt_generation=True,
        provider_tool_boundary=True,
        memory_write_requested=True,
    )
    required = resolve_required_capabilities_for_operation(context)
    result = enforce_labs_universal_control_before_runtime(
        operation_context=context,
        cieu_db=tmp_path / "e113_e110_gate.db",
        ystar_gov_root=YSTAR_ROOT,
        session_id="e113_e110_gate_session",
    )

    assert "no_new_wheel_runtime_law" in required
    assert result["runtime_may_continue"] is True
    assert result["no_new_wheel_runtime_law_gate"]["Y_star_gov_no_new_wheel_decision"] == "ALLOW"
    assert result["Y_star_gov_universal_control_decision"] == "ALLOW"
