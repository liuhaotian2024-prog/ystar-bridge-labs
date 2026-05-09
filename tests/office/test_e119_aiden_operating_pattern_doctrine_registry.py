from __future__ import annotations

from office.mission_command.e119_aiden_operating_pattern_doctrine_registry import (
    build_aiden_operating_pattern_doctrine_registry,
    build_operating_pattern_invocation_plan,
    resolve_required_operating_patterns,
)


def test_registry_mechanizes_codex_success_methods():
    registry = build_aiden_operating_pattern_doctrine_registry()
    pattern_ids = {item["pattern_id"] for item in registry["patterns"]}

    assert "no_new_wheel_preflight" in pattern_ids
    assert "class_level_extrapolation_gate" in pattern_ids
    assert "correct_path_navigation" in pattern_ids
    assert "CEOImplementationOrder_before_Codex_prompt" in pattern_ids
    assert "production_brain_write_owner_backup_gate" in pattern_ids
    assert len(pattern_ids) >= 18


def test_market_codex_brain_action_requires_all_relevant_patterns():
    context = {
        "action_id": "e119_pattern_test",
        "market_strategy_required": True,
        "codex_execution_required": True,
        "brain_write_related": True,
        "external_action_related": True,
        "self_governance_related": True,
    }

    required = resolve_required_operating_patterns(context)

    assert "competitive_landscape_current_signal" in required
    assert "CodexExecutionReceipt_return_path" in required
    assert "learning_quality_scoring_v2" in required
    assert "gov_mcp_no_send_preflight" in required
    assert "owner_review_before_contract_patch" in required


def test_invocation_plan_marks_patterns_invoked_and_governed():
    plan = build_operating_pattern_invocation_plan(
        {
            "action_id": "e119_pattern_test",
            "market_strategy_required": True,
            "codex_execution_required": True,
            "brain_write_related": True,
            "external_action_related": True,
            "self_governance_related": True,
        }
    )

    assert plan["truth_constraints"]["skipped_no_new_wheel"] is False
    assert plan["truth_constraints"]["raw_codex_prompt_without_order"] is False
    assert all(item["invocation_status"] == "invoked" for item in plan["pattern_invocations"])
    assert all(item["runtime_governance_required"] is True for item in plan["pattern_invocations"])
