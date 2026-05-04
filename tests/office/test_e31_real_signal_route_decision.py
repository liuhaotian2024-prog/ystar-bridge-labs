import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_next_route_prefers_low_risk_publication_review_not_provider_default():
    data = json.loads((ROOT / "operations/external_validation/e31_real_signal_route_decision.json").read_text())
    assert data["selected_next_route"] == "proceed_to_owner_review_for_external_publication"
    assert data["external_contact_recommended_next"] is False
    assert data["production_live_enabled"] is False
    assert data["production_live_receipt_count"] == 0
