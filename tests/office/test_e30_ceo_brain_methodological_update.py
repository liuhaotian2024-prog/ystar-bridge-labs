import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_brain_updates_bottleneck_and_horizon():
    data = json.loads((ROOT / "operations/external_validation/e30_ceo_brain_methodological_update.json").read_text())
    assert data["selected_route"] == "paid_readiness_review_signal_package"
    assert data["next_decision_horizon"] == "E31_paid_readiness_review_signal_package"
    assert data["branch_optionality_preserved"] is True
    assert data["production_live_remains_disabled"] is True
    assert data["production_live_receipt_count"] == 0
