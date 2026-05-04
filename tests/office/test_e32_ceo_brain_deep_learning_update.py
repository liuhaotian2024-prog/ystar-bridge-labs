import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_brain_deep_learning_update_sets_primary_path_and_horizon():
    data = json.loads((ROOT / "operations/external_validation/e32_ceo_brain_deep_learning_update.json").read_text())
    assert data["selected_primary_monetization_path"] == "path_paid_readiness_review_service"
    assert data["secondary_path"] == "path_partner_validation_packet"
    assert "owner must choose" in data["current_bottleneck"]
    assert data["next_decision_horizon"] == "E33_owner_strategy_decision_packet_to_low_risk_external_signal_route"
    assert data["production_live_receipt_count"] == 0
