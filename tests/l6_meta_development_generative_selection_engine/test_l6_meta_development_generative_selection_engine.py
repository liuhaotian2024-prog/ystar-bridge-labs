from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "l6_meta_development_generative_selection_engine"
    / "tools"
    / "build_l6_meta_development_generative_selection_engine.py"
)

REQUIRED_DIRECTORIES = [
    "l6_meta_development_generative_selection_engine",
    "self_model_and_unique_asset_field",
    "world_value_field_model",
    "value_conversion_operator_library",
    "open_value_hypothesis_generator",
    "value_conversion_physics",
    "redeemability_selection_engine",
    "minimum_viable_proof_designer",
    "governed_meta_development_experiment_portfolio",
    "strategic_residual_meta_learning_loop",
    "l6_meta_development_design_readiness",
]

REQUIRED_FILES = [
    "l6_meta_development_generative_selection_engine/README.md",
    "l6_meta_development_generative_selection_engine/tools/build_l6_meta_development_generative_selection_engine.py",
    "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_contract.json",
    "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_input_fixture.json",
    "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_run.json",
    "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_summary.json",
    "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_report.md",
    "self_model_and_unique_asset_field/self_model_v0.json",
    "self_model_and_unique_asset_field/unique_asset_field.json",
    "self_model_and_unique_asset_field/asset_lineage_map.json",
    "self_model_and_unique_asset_field/asset_constraint_map.json",
    "self_model_and_unique_asset_field/self_asset_summary.json",
    "self_model_and_unique_asset_field/self_asset_report.md",
    "world_value_field_model/world_value_field_schema.json",
    "world_value_field_model/world_value_need_surface_map.json",
    "world_value_field_model/value_recipient_archetype_map.json",
    "world_value_field_model/world_value_uncertainty_map.json",
    "world_value_field_model/world_value_field_summary.json",
    "world_value_field_model/world_value_field_report.md",
    "value_conversion_operator_library/value_conversion_operator_library.json",
    "value_conversion_operator_library/asset_to_value_operator_map.json",
    "value_conversion_operator_library/residual_to_value_operator.json",
    "value_conversion_operator_library/identity_to_differentiation_operator.json",
    "value_conversion_operator_library/process_to_asset_operator.json",
    "value_conversion_operator_library/evidence_to_trust_operator.json",
    "value_conversion_operator_library/operator_library_summary.json",
    "value_conversion_operator_library/operator_library_report.md",
    "open_value_hypothesis_generator/value_hypothesis_schema.json",
    "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "open_value_hypothesis_generator/seed_hypothesis_examples.json",
    "open_value_hypothesis_generator/hypothesis_generation_trace.json",
    "open_value_hypothesis_generator/hypothesis_non_hardcoding_check.json",
    "open_value_hypothesis_generator/hypothesis_generator_summary.json",
    "open_value_hypothesis_generator/hypothesis_generator_report.md",
    "value_conversion_physics/value_conversion_physics_schema.json",
    "value_conversion_physics/conversion_path_variable_registry.json",
    "value_conversion_physics/conversion_path_length_model.json",
    "value_conversion_physics/conversion_certainty_stability_model.json",
    "value_conversion_physics/conversion_time_horizon_model.json",
    "value_conversion_physics/conversion_physics_summary.json",
    "value_conversion_physics/conversion_physics_report.md",
    "redeemability_selection_engine/redeemability_selection_policy.json",
    "redeemability_selection_engine/hypothesis_redeemability_matrix.json",
    "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "redeemability_selection_engine/rejected_or_deferred_hypotheses.json",
    "redeemability_selection_engine/selection_engine_summary.json",
    "redeemability_selection_engine/selection_engine_report.md",
    "minimum_viable_proof_designer/minimum_viable_proof_schema.json",
    "minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json",
    "minimum_viable_proof_designer/mvp_evidence_requirement_map.json",
    "minimum_viable_proof_designer/mvp_non_execution_boundary.json",
    "minimum_viable_proof_designer/mvp_design_summary.json",
    "minimum_viable_proof_designer/mvp_design_report.md",
    "governed_meta_development_experiment_portfolio/governed_experiment_portfolio.json",
    "governed_meta_development_experiment_portfolio/experiment_portfolio_balance_matrix.json",
    "governed_meta_development_experiment_portfolio/experiment_portfolio_risk_boundary.json",
    "governed_meta_development_experiment_portfolio/experiment_portfolio_review_gate.json",
    "governed_meta_development_experiment_portfolio/experiment_portfolio_summary.json",
    "governed_meta_development_experiment_portfolio/experiment_portfolio_report.md",
    "strategic_residual_meta_learning_loop/strategic_residual_schema.json",
    "strategic_residual_meta_learning_loop/meta_development_cieu_event_fixture.json",
    "strategic_residual_meta_learning_loop/meta_development_predicted_outcome.json",
    "strategic_residual_meta_learning_loop/meta_development_mock_actual_outcome.json",
    "strategic_residual_meta_learning_loop/strategic_residual_delta.json",
    "strategic_residual_meta_learning_loop/meta_learning_update_candidate.json",
    "strategic_residual_meta_learning_loop/strategic_residual_summary.json",
    "strategic_residual_meta_learning_loop/strategic_residual_report.md",
    "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json",
    "l6_meta_development_design_readiness/l6_meta_development_design_readiness.md",
    "l6_meta_development_design_readiness/l6_1_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_13_l6_entry_gate",
    "load_l5_readiness_and_no_go_boundaries",
    "build_self_model",
    "build_unique_asset_field",
    "build_world_value_field",
    "define_value_conversion_operators",
    "generate_open_value_hypotheses",
    "estimate_conversion_path_physics",
    "evaluate_redeemability_and_stability",
    "design_minimum_viable_proofs",
    "build_governed_experiment_portfolio",
    "rank_design_only_meta_development_candidates",
    "generate_strategic_residual_framework",
    "define_meta_learning_update_candidate",
    "produce_l6_1_recommendation",
]

SAFETY_FLAGS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "mcp_server_execution_enabled",
    "mcp_tool_execution_enabled",
    "cieu_persistence_enabled",
    "durable_approval_persistence_enabled",
    "real_approval_record_write_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "strategy_mutation_enabled",
    "candidate_auto_approval_enabled",
    "real_candidate_approval_enabled",
    "real_canonical_policy_mutation_enabled",
    "real_canonical_update_application_enabled",
    "real_release_execution_enabled",
    "real_y_star_direct_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "revenue_execution_enabled",
    "external_market_scan_enabled",
    "public_content_publication_enabled",
    "payment_enabled",
}

FALSE_FIELDS = SAFETY_FLAGS | {
    "l6_external_execution_enabled",
    "l6_network_enabled",
    "l6_publication_enabled",
    "l6_payment_enabled",
    "l6_revenue_execution_enabled",
    "external_execution_performed",
    "network_used",
    "publication_performed",
    "payment_performed",
    "revenue_execution_performed",
    "authorized_for_execution",
    "external_execution_required_now",
    "external_contact_authorized",
    "external_action_authorized",
    "execution_authorized",
    "l6_execution_authorized",
    "persistence_enabled",
    "db_write_performed",
    "l6_execution_enabled",
    "probabilistic_scoring_used",
    "semantic_truth_scoring_used",
    "eligible_for_direct_brain_writeback",
    "eligible_for_direct_memory_ingestion",
    "eligible_for_candidate_auto_approval",
    "approved",
    "applied",
    "ready_for_l6_revenue_opportunity_execution",
}

REQUIRED_INPUT_REFS = {
    "live_boundary_readiness/live_boundary_readiness.json",
    "l6_meta_development_entry_gate/l6_meta_development_entry_gate.json",
    "l6_meta_development_entry_gate/l6_generative_principles.json",
    "l6_meta_development_entry_gate/l6_forbidden_hardcoding_policy.json",
    "system_no_go_decision_packet/system_no_go_decision_packet.json",
    "live_blocker_risk_register/live_blocker_risk_register.json",
    "live_readiness_evidence_index/l5_chain_evidence_map.json",
    "no_go_invariant_matrix/no_go_invariant_matrix.json",
    "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
    "real_release_simulation_readiness/real_release_simulation_readiness.json",
}

ASSET_DIMENSIONS = {
    "normative_architecture_asset",
    "y_star_projection_asset",
    "governance_boundary_asset",
    "cieu_residual_learning_asset",
    "approval_release_sandbox_asset",
    "mcp_non_bypass_asset",
    "process_history_asset",
    "failure_residual_asset",
    "ai_identity_asset",
    "founder_ai_coevolution_asset",
    "evidence_chain_asset",
    "trust_signal_asset",
    "methodology_asset",
    "narrative_asset",
    "experiment_system_asset",
}

VALUE_SURFACES = {
    "attention_value",
    "trust_value",
    "operational_efficiency_value",
    "risk_reduction_value",
    "compliance_value",
    "education_value",
    "entertainment_value",
    "evidence_generation_value",
    "governance_assurance_value",
    "tooling_value",
    "community_value",
    "strategic_option_value",
    "direct_cash_value",
    "indirect_lead_value",
    "brand_value",
    "methodology_value",
}

OPERATORS = {
    "residual_to_story_value",
    "process_to_methodology_value",
    "evidence_chain_to_trust_value",
    "governance_boundary_to_risk_reduction_value",
    "mcp_non_bypass_to_tooling_assurance_value",
    "y_star_projection_to_operational_alignment_value",
    "approval_sandbox_to_compliance_value",
    "ai_identity_to_differentiation_value",
    "founder_ai_coevolution_to_narrative_value",
    "experiment_system_to_learning_value",
    "failure_history_to_authenticity_value",
    "artifact_chain_to_audit_value",
}

PHYSICS_VARIABLES = {
    "conversion_path_length",
    "time_to_first_signal",
    "time_to_first_cash",
    "payer_clarity",
    "acceptance_criteria_clarity",
    "evidence_clarity",
    "distribution_friction",
    "execution_complexity",
    "competitive_pressure",
    "advantage_fit",
    "certainty_of_acceptance",
    "stability_of_demand",
    "repeatability",
    "compounding_value",
    "downside_risk",
    "option_value",
    "strategic_stability",
    "learning_value",
    "reversibility",
    "governance_complexity",
}

TIME_HORIZONS = {
    "immediate_signal",
    "seven_day_signal",
    "thirty_day_cash_or_commitment",
    "ninety_day_repeatability",
    "one_year_compounding",
    "long_term_option_only",
    "too_long_for_current_priority",
}

DEFER_REASONS = {
    "path_too_long",
    "payer_unclear",
    "acceptance_unclear",
    "too_much_external_dependency",
    "high_distribution_friction",
    "weak_advantage_fit",
    "high_risk",
    "execution_not_authorized",
    "useful_as_long_term_option_only",
}

RESIDUAL_CLASSES = {
    "self_model_gap",
    "asset_field_gap",
    "world_value_uncertainty_gap",
    "hypothesis_generation_gap",
    "conversion_physics_gap",
    "redeemability_selection_gap",
    "mvp_design_gap",
    "hardcoding_risk_gap",
    "execution_boundary_gap",
    "evidence_gap",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load_json(relative_path: str) -> Any:
    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def test_builder_regenerates_l6_0_artifacts() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stderr
    assert "Built L6.0" in result.stdout


def test_required_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_FILES:
        assert (ROOT / path).is_file(), path


def test_all_json_artifacts_parse() -> None:
    for path in JSON_FILES:
        assert load_json(path), path


def test_contract_stages_and_flags() -> None:
    contract = load_json(
        "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_contract.json"
    )
    assert contract["engine_stages"] == REQUIRED_STAGES
    assert set(contract["safety_flags"]) >= SAFETY_FLAGS
    assert all(contract["safety_flags"][flag] is False for flag in SAFETY_FLAGS)
    assert contract["l6_flags"]["l6_design_only_enabled"] is True
    assert contract["l6_flags"]["l6_hypothesis_generation_enabled"] is True
    assert contract["l6_flags"]["l6_selection_design_enabled"] is True
    assert contract["l6_flags"]["l6_sandbox_experiment_design_enabled"] is True
    for field in [
        "l6_external_execution_enabled",
        "l6_network_enabled",
        "l6_publication_enabled",
        "l6_payment_enabled",
        "l6_revenue_execution_enabled",
    ]:
        assert contract["l6_flags"][field] is False


def test_no_forbidden_flags_are_true_anywhere() -> None:
    for path in JSON_FILES:
        data = load_json(path)
        for key, value in walk_values(data):
            if key in FALSE_FIELDS:
                assert value is False, f"{path}: {key} must remain false"


def test_input_fixture_references_l5_13_entry_gate_and_no_go_artifacts() -> None:
    fixture = load_json(
        "l6_meta_development_generative_selection_engine/l6_generative_selection_engine_input_fixture.json"
    )
    refs = {entry["path"] for entry in fixture["input_refs"]}
    assert REQUIRED_INPUT_REFS <= refs
    assert fixture["gap_aware_readiness"] is True
    assert fixture["safe_to_continue"] is True


def test_self_model_and_unique_asset_field() -> None:
    self_model = load_json("self_model_and_unique_asset_field/self_model_v0.json")
    assets = load_json("self_model_and_unique_asset_field/unique_asset_field.json")
    lineage = load_json("self_model_and_unique_asset_field/asset_lineage_map.json")
    assert self_model["self_model_id"]
    assert ASSET_DIMENSIONS <= set(assets["asset_dimensions"])
    assert ASSET_DIMENSIONS <= set(lineage["asset_lineage"])
    for asset in assets["assets"]:
        assert asset["asset_id"] in ASSET_DIMENSIONS
        assert asset["forbidden_overclaims"]
        assert asset["constraints"]


def test_world_value_field_is_abstract_and_uncertainty_aware() -> None:
    schema = load_json("world_value_field_model/world_value_field_schema.json")
    uncertainty = load_json("world_value_field_model/world_value_uncertainty_map.json")
    assert VALUE_SURFACES <= set(schema["value_surfaces"])
    assert schema["surface_type"] == "abstract_value_surface_not_fixed_opportunity_category"
    assert "hypothesized_external_need" in uncertainty["uncertainty_classes"]
    assert "unverified_market_signal" in uncertainty["uncertainty_classes"]
    assert "design_only_placeholder" in uncertainty["uncertainty_classes"]
    assert uncertainty["requires_future_external_observation"] is True


def test_conversion_operator_library() -> None:
    library = load_json("value_conversion_operator_library/value_conversion_operator_library.json")
    assert OPERATORS <= set(library["operator_ids"])
    assert library["operators_are_not_opportunity_types"] is True
    for path in [
        "value_conversion_operator_library/residual_to_value_operator.json",
        "value_conversion_operator_library/identity_to_differentiation_operator.json",
        "value_conversion_operator_library/process_to_asset_operator.json",
        "value_conversion_operator_library/evidence_to_trust_operator.json",
    ]:
        assert load_json(path)["operator"]["operator_id"]


def test_generated_hypotheses_and_seed_examples_are_non_executing() -> None:
    generated = load_json("open_value_hypothesis_generator/generated_value_hypotheses.json")
    seeds = load_json("open_value_hypothesis_generator/seed_hypothesis_examples.json")
    check = load_json("open_value_hypothesis_generator/hypothesis_non_hardcoding_check.json")
    hypotheses = generated["hypotheses"]
    assert len(hypotheses) >= 12
    for hypothesis in hypotheses:
        for field in [
            "source_assets",
            "conversion_operators",
            "hypothesized_value_surface",
            "conversion_path",
            "minimum_viable_proof",
            "uncertainty_class",
            "why_execution_is_not_authorized",
        ]:
            assert hypothesis[field]
        assert hypothesis["authorized_for_execution"] is False
    for seed in seeds["seed_examples"]:
        assert seed["example_only"] is True
        assert seed["not_exhaustive"] is True
        assert seed["not_authorized_for_execution"] is True
    assert check["examples_are_not_exhaustive"] is True
    assert check["no_external_execution_authorized"] is True


def test_conversion_physics_and_selection_are_structural_only() -> None:
    schema = load_json("value_conversion_physics/value_conversion_physics_schema.json")
    horizon = load_json("value_conversion_physics/conversion_time_horizon_model.json")
    policy = load_json("redeemability_selection_engine/redeemability_selection_policy.json")
    matrix = load_json("redeemability_selection_engine/hypothesis_redeemability_matrix.json")
    ranking = load_json("redeemability_selection_engine/hypothesis_selection_ranking.json")
    deferred = load_json("redeemability_selection_engine/rejected_or_deferred_hypotheses.json")
    generated = load_json("open_value_hypothesis_generator/generated_value_hypotheses.json")
    assert PHYSICS_VARIABLES <= set(schema["variables"])
    assert schema["semantic_truth_scoring_used"] is False
    assert TIME_HORIZONS <= set(horizon["time_horizon_classes"])
    assert horizon["too_long_for_current_priority"] is True
    assert "prioritize shorter path to signal" in policy["deterministic_selection_logic"]
    assert "penalize external-action dependency" in policy["deterministic_selection_logic"]
    assert matrix["scored_hypothesis_count"] == len(generated["hypotheses"])
    assert DEFER_REASONS <= set(deferred["allowed_defer_reasons"])
    for candidate in ranking["selected_candidates"]:
        assert candidate["selected_for_sandbox_design"] is True
        assert candidate["authorized_for_execution"] is False


def test_mvp_plans_and_portfolio_are_design_only() -> None:
    plans = load_json("minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json")
    boundary = load_json("minimum_viable_proof_designer/mvp_non_execution_boundary.json")
    portfolio = load_json(
        "governed_meta_development_experiment_portfolio/governed_experiment_portfolio.json"
    )
    denied = set(boundary["denied_actions"])
    assert {
        "external publication",
        "customer outreach",
        "payment",
        "network/API call",
        "platform upload",
        "bounty/RFP/grant submission",
        "YouTube upload",
        "social media post",
        "email/message sending",
    } <= denied
    for plan in plans["mvp_plans"]:
        assert plan["l6_execution_authorized"] is False
        assert plan["review_gate_required"] is True
    for experiment in portfolio["experiments"]:
        assert experiment["execution_authorized"] is False
        assert experiment["external_action_authorized"] is False


def test_strategic_residual_loop_and_meta_learning_candidate() -> None:
    event = load_json("strategic_residual_meta_learning_loop/meta_development_cieu_event_fixture.json")
    residual = load_json("strategic_residual_meta_learning_loop/strategic_residual_delta.json")
    candidate = load_json("strategic_residual_meta_learning_loop/meta_learning_update_candidate.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "l6_meta_development_design_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    assert event["l6_execution_enabled"] is False
    assert RESIDUAL_CLASSES <= set(residual["residual_classes"])
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_readiness_blocks_l6_execution_and_all_external_lanes() -> None:
    readiness = load_json(
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json"
    )
    for field in [
        "self_model_generated",
        "unique_asset_field_generated",
        "world_value_field_generated",
        "conversion_operator_library_generated",
        "value_hypotheses_generated",
        "non_hardcoding_check_generated",
        "conversion_physics_defined",
        "redeemability_selection_generated",
        "minimum_viable_proof_plans_generated",
        "governed_experiment_portfolio_generated",
        "strategic_residual_loop_generated",
        "l6_execution_still_blocked",
        "external_action_still_blocked",
        "network_still_blocked",
        "publication_still_blocked",
        "payment_still_blocked",
        "revenue_execution_still_blocked",
        "ready_for_l6_1_meta_development_mvp_artifact_sandbox",
    ]:
        assert readiness[field] is True
    assert readiness["ready_for_l6_revenue_opportunity_execution"] is False


def test_console_command_surfaces_l6_0_read_model() -> None:
    result = run_command(["python3", "console_read_model/cli/team_console.py", "meta-development-design"])
    assert result.returncode == 0, result.stderr
    assert "L6.0 meta-development generative selection engine defined: True" in result.stdout
    assert "L6 is design-only: True" in result.stdout
    assert "ready for L6 revenue opportunity execution: False" in result.stdout
