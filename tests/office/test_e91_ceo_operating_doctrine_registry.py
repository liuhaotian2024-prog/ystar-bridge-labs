from __future__ import annotations

from office.mission_command.e91_ceo_operating_doctrine_registry import (
    build_ceo_operating_doctrine_registry,
    build_default_action_context,
    build_doctrine_invocation_plan,
    build_doctrine_invocation_proof,
    explain_missing_doctrine_requirements,
    resolve_required_doctrines_for_action,
    validate_doctrine_invocation_plan_local,
)


def test_registry_is_data_driven_from_open_world_spec():
    registry = build_ceo_operating_doctrine_registry()

    assert registry["prompt_categories_used_as_closed_ontology"] is False
    assert registry["ontology_source"] == "open_world_asset_graph_clusters"
    assert len(registry["doctrines"]) >= 15
    assert "unseeded_brain_capability_cluster" in {cluster for d in registry["doctrines"] for cluster in d["source_cluster_ids"]}


def test_market_strategy_requires_external_observation_and_commercial_doctrines():
    context = build_default_action_context(
        action_id="market_strategy",
        action_type="market_strategy",
        mission_type="market_strategy",
        market_strategy_required=True,
        external_observation_required=True,
        test_mode=True,
    )

    required = resolve_required_doctrines_for_action(context)

    assert "external_observation_public_read_evidence" in required
    assert "market_dynamics_and_buyer_pain" in required
    assert "strategy_benchmark_and_commercial_sharpness" in required
    assert "counterfactual_candidate_selection" in required


def test_provider_action_requires_gov_mcp_doctrine():
    context = build_default_action_context(
        action_id="provider_action",
        action_type="provider_tool_action",
        mission_type="runtime_boundary",
        provider_tool_boundary=True,
    )

    required = resolve_required_doctrines_for_action(context)

    assert "gov_mcp_dry_run_provider_boundary" in required


def test_revenue_payment_action_requires_revenue_gate_and_cannot_silently_allow():
    context = build_default_action_context(
        action_id="revenue_action",
        action_type="revenue_or_payment",
        mission_type="revenue_path",
        revenue_or_payment_related=True,
    )

    required = resolve_required_doctrines_for_action(context)

    assert "revenue_payment_customer_gate" in required


def test_static_evidence_map_cannot_satisfy_non_test_external_observation_locally():
    context = build_default_action_context(
        action_id="live_market_strategy",
        action_type="market_strategy",
        mission_type="market_strategy",
        market_strategy_required=True,
        external_observation_required=True,
        test_mode=False,
    )
    plan = build_doctrine_invocation_plan(context)

    local = validate_doctrine_invocation_plan_local(context, plan)

    assert local["decision"] == "REQUIRE_REVISION"
    assert "live_external_observation_runtime" in local["missing_doctrines"]


def test_invocation_proof_builds_open_world_doctrine_metadata():
    context = build_default_action_context(
        action_id="e91_provider_plan",
        action_type="provider_tool_action",
        mission_type="runtime_boundary",
        provider_tool_boundary=True,
        test_mode=True,
    )
    plan = build_doctrine_invocation_plan(context)
    proof = build_doctrine_invocation_proof(context)
    explanation = explain_missing_doctrine_requirements(context, plan)

    assert explanation["decision"] == "ALLOW"
    assert proof["required_doctrines_satisfied"] is True
    assert proof["doctrine_invocations"]
    assert proof["registry_id"] == "ceo_operating_doctrine_registry_open_world_v1"
