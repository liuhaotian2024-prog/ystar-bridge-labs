from pathlib import Path

from office.mission_command.e2_money_path_evaluator import evaluate_money_paths


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_money_path_evaluation_compares_at_least_five_paths():
    evaluation = evaluate_money_paths(REPO_ROOT)
    assert len(evaluation["paths"]) >= 5


def test_default_path_comes_from_evaluation_gate_not_hardcoded_single_seed():
    evaluation = evaluate_money_paths(REPO_ROOT)
    paths = {row["path"] for row in evaluation["paths"]}
    assert evaluation["default_path"] in paths
    assert "Founder AI Workflow Audit / CEO Command Brief" in paths
    assert len(paths) >= 5


def test_each_path_has_required_dimensions():
    evaluation = evaluate_money_paths(REPO_ROOT)
    for row in evaluation["paths"]:
        for key in [
            "buyer",
            "urgent_pain",
            "budget_demand_signal",
            "internal_assets",
            "behavior_capability",
            "owner_burden",
            "channel_access",
            "proof_assets",
            "48h_validation_experiment",
            "kill_condition",
            "counterfactual_risks",
            "residual_plan",
        ]:
            assert row[key]


def test_no_external_side_effects():
    evaluation = evaluate_money_paths(REPO_ROOT)
    assert evaluation["external_action_executed"] is False
    assert evaluation["live_research_executed"] is False
