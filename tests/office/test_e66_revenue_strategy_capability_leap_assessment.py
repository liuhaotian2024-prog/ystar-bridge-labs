import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_capability_leap_is_claimed_without_validation_overclaim():
    data = json.loads((ROOT / "operations/external_validation/e66_revenue_strategy_capability_leap_assessment.json").read_text())
    assert data["assessment"] == "capability leap toward market strategy intelligence"
    assert data["CEO_can_select_portfolio_instead_of_single_route"] is True
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False

