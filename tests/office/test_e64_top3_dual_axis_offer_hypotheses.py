import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_top3_offers_include_market_unique_and_hybrid():
    data = json.loads((ROOT / "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json").read_text())
    offers = data["offers"]
    route_types = {offer["route_type"] for offer in offers}
    names = {offer["offer_name"] for offer in offers}
    assert data["offer_count"] == 3
    assert {"hybrid", "market_optimal", "YBridge_unique"}.issubset(route_types)
    assert "AI Agent Company Runtime Harness Deployment Blueprint" in names
    assert all(offer["owner_approval_required_before_external_use"] is True for offer in offers)
