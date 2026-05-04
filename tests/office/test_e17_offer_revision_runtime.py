import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_offer_revision_keeps_48h_review_before_first_send():
    data = json.loads((ROOT / "operations/external_validation/e17_offer_revision_packet.json").read_text())
    assert data["lead_offer"] == "48h AI Agent Implementation Readiness Review"
    assert data["lead_offer_should_remain"] is True
    assert data["revision_priority"] == "none_before_first_manual_send"
    assert data["external_action_executed"] is False


def test_offer_revision_has_paths_for_weak_response_later():
    data = json.loads((ROOT / "operations/external_validation/e17_offer_revision_packet.json").read_text())
    assert data["pain_framing_improvement"]
    assert data["cta_improvement"]
    assert data["pricing_packaging_rule"].startswith("Pricing remains hypothesis")
