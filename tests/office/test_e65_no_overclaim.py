import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_no_overclaim_fields_are_false():
    data = json.loads((ROOT / "operations/external_validation/e65_no_overclaim_validation_result.json").read_text())
    assert data["passed"] is True
    state = json.loads((ROOT / "operations/external_validation/e65_ceo_brain_market_dynamics_update.json").read_text())
    for field in [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "autonomous_revenue_achieved",
        "global_optimality_proven",
        "perfect_model_claimed",
        "pricing_validation_claimed",
        "external_action_allowed",
    ]:
        assert state[field] is False
