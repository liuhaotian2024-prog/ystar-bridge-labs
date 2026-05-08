from __future__ import annotations

from e101_adaptive_governance_discovery_and_correct_path_navigator import (
    build_adaptive_governance_result,
    discover_adaptive_governance_obligations,
)


def test_market_strategy_discovers_required_navigation_obligations():
    result = discover_adaptive_governance_obligations(
        action_context={
            "action_id": "strategy",
            "action_type": "market_strategy",
            "market_strategy_required": True,
            "external_observation_required": True,
            "provider_tool_boundary": True,
        },
        runtime_artifact={"price": "$500-$2,000", "competitor_analysis": True, "brain": "6D"},
    )

    ids = {item["obligation_id"] for item in result["required_obligations"]}
    assert "six_d_brain_review" in ids
    assert "pricing_hypothesis_source_audit" in ids
    assert "right_to_win_analysis" in ids
    assert "strongest_validation_question" in ids
    assert "external_observation_or_staleness_boundary" in ids
    assert "gov_mcp_dry_run_preflight" in ids


def test_missing_required_obligations_get_correct_path_navigation():
    result = build_adaptive_governance_result(
        action_context={
            "action_id": "strategy",
            "action_type": "market_strategy",
            "market_strategy_required": True,
            "external_observation_required": True,
        },
        runtime_artifact={"price": "$500-$2,000"},
    )

    assert result["correct_path_navigator"]["missing_obligation_count"] > 0
    assert any(step["missing_obligation"] == "six_d_brain_review" for step in result["correct_path_navigator"]["steps"])
    assert all(step["next_allowed_action"] == "repair_packet_only" for step in result["correct_path_navigator"]["steps"])


def test_complete_invocation_proof_allows_no_missing_navigation_steps():
    result = build_adaptive_governance_result(
        action_context={
            "action_id": "strategy",
            "action_type": "market_strategy",
            "market_strategy_required": True,
            "external_observation_required": True,
            "provider_tool_boundary": True,
        },
        runtime_artifact={"price": "$500-$2,000", "brain": "6D", "competitor": True},
        invocation_proof={
            "satisfied_obligations": [
                "six_d_brain_review",
                "pricing_hypothesis_source_audit",
                "right_to_win_analysis",
                "strongest_validation_question",
                "competitor_differentiation_map",
                "external_observation_or_staleness_boundary",
                "gov_mcp_dry_run_preflight",
                "post_action_residual",
            ]
        },
    )

    assert result["obligation_invocation_proof"]["missing_obligations"] == []
    assert result["correct_path_navigator"]["missing_obligation_count"] == 0
