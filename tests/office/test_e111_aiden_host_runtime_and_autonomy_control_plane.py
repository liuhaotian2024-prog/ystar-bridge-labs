from __future__ import annotations

from pathlib import Path

from office.mission_command.e108_live_global_open_world_strategy_runtime import FixtureGlobalPublicReadProvider
from office.aiden_meeting_room.chat_router import route_chat_message_to_aiden_meeting_room
from office.mission_command.e111_aiden_host_runtime_and_autonomy_control_plane import (
    build_aiden_company_mission_anchor,
    build_autonomy_policy,
    build_existing_capability_orchestration_map,
    classify_autonomy_tier,
    run_aiden_host_runtime_cycle,
)


def test_mission_anchor_targets_autonomous_governed_company_runtime() -> None:
    anchor = build_aiden_company_mission_anchor()
    assert "autonomous_value_discovery" in anchor["must_optimize_for"]
    assert "governed_value_creation" in anchor["must_optimize_for"]
    assert "residual_learning" in anchor["must_optimize_for"]
    assert "L5-D" in " ".join(anchor["must_not_claim"])


def test_existing_capability_map_orchestrates_mainline_systems() -> None:
    capability_ids = {
        item["capability_id"]
        for item in build_existing_capability_orchestration_map()["capabilities"]
    }
    assert "E110_labs_universal_operating_control_plane" in capability_ids
    assert "E89_ceo_intelligence_loop_runtime_compiler" in capability_ids
    assert "E90_ceo_strategic_intelligence_benchmark" in capability_ids
    assert "E108_live_global_open_world_strategy_runtime" in capability_ids
    assert "E92_CEOImplementationOrder" in capability_ids
    assert "Y_star_gov_deterministic_governance" in capability_ids
    assert "CIEUStore_formal_memory" in capability_ids
    assert "gov_mcp_dry_run_no_send_boundary" in capability_ids


def test_autonomy_policy_reduces_owner_burden_without_authorizing_high_risk_actions() -> None:
    tiers = {item["tier_id"]: item for item in build_autonomy_policy()["tiers"]}
    assert tiers["autonomous_internal_low_risk"]["allowed"] is True
    assert tiers["codex_executor_order_required"]["allowed"] is True
    assert tiers["gov_mcp_dry_run_only"]["allowed"] is True
    assert tiers["owner_decision_required"]["allowed"] is False
    assert tiers["hard_deny"]["allowed"] is False

    assert classify_autonomy_tier({"repo_mutation": True})["tier_id"] == "codex_executor_order_required"
    assert classify_autonomy_tier({"provider_tool_boundary": True})["tier_id"] == "gov_mcp_dry_run_only"
    assert classify_autonomy_tier({"customer_contact": True})["tier_id"] == "owner_decision_required"
    assert classify_autonomy_tier({"payment_related": True})["tier_id"] == "hard_deny"


def test_host_runtime_cycle_runs_through_e110_order_prompt_ystar_and_cieustore(tmp_path: Path) -> None:
    db = tmp_path / "aiden_host_runtime.db"
    result = run_aiden_host_runtime_cycle(
        cieu_db=db,
        owner_intent="Operate Y*Bridge Labs autonomously and find the next governed value creation target.",
        provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
        seal_session=False,
    )

    assert result["host_runtime_cycle_proven"] is True
    assert result["strategy_result"]["end_to_end_controlled_strategy_proven"] is True
    assert result["order_write"]["governance_decision"]["decision"] == "ALLOW"
    assert result["codex_handoff_prompt_generation"]["prompt_generation_decision"]["decision"] == "ALLOW"
    assert result["host_runtime_write"]["governance_decision"]["decision"] == "ALLOW"
    assert result["CIEUStore_summary"]["event_count"] >= 5
    assert "AIDEN_HOST_RUNTIME_CYCLE_DECISION" in result["CIEUStore_summary"]["event_types"]

    order = result["CEO_implementation_order"]
    assert order["artifact_id"] == "CEOImplementationOrder"
    assert order["CEO_decision_actor"] != "Codex"
    assert order["executor_actor"] == "Codex"

    next_action = result["next_action_recommendation"]
    assert next_action["autonomy_tier"] == "codex_executor_order_required"
    assert next_action["external_action_candidate"] is False
    assert result["safety_statement"]["no_external_action_executed"] is True
    assert result["L5_truth_table_after"]["L5-D"] == "absent_or_not_executed"


def test_aiden_autonomous_message_routes_to_host_runtime(tmp_path: Path) -> None:
    route = route_chat_message_to_aiden_meeting_room(
        "Aiden: operate as an autonomous company runtime and find the next value target",
        cieu_db=tmp_path / "aiden_router_host_runtime.db",
        live_public_read_provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )
    assert route.route == "aiden_ceo_host_runtime"
    assert route.protocol == "AidenHostRuntimeV1"
    assert "Host runtime proven: true" in (route.response_text or "")
