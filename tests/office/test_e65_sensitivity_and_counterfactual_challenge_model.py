import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_sensitivity_model_challenges_the_selection():
    data = json.loads((ROOT / "operations/external_validation/e65_sensitivity_and_counterfactual_challenge_model.json").read_text())
    assert data["sensitivity_scenarios"]
    assert data["decision_stability_score"] >= 0
    assert data["fragile_assumptions"]
    assert data["counterfactual_rejection_reasons"]
    assert "founder_operator_decision_brief_service" in data["fallback_portfolio"]
