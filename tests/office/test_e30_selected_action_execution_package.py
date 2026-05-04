import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_execution_package_is_specific_and_no_send():
    data = json.loads((ROOT / "operations/external_validation/e30_selected_action_execution_package.json").read_text())
    assert data["selected_route"] == "paid_readiness_review_signal_package"
    assert data["branch"] == "revenue_mode_shortest_cash_path"
    assert "proof-bound claims register" in data["produced_outputs_for_next_milestone"]
    assert "no contact" in data["safety_constraints"]
    assert data["external_action_executed"] is False
