from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _offer_text() -> str:
    return (ROOT / "reports" / "integration" / "e7_validation_ready_offer_packet.md").read_text(encoding="utf-8")


def test_offer_packet_has_target_buyer_job_pain_wedge_scope_exclusions():
    text = _offer_text()
    assert "Technical founder, AI-heavy small team" in text
    assert "Buyer Job-To-Be-Done" in text
    assert "Urgent Pain" in text
    assert "Y*Bridge Wedge" in text
    assert "Delivery Scope" in text
    assert "What Is Excluded" in text


def test_offer_packet_does_not_claim_customer_validation():
    text = _offer_text()
    assert "customer_validation_claimed: False" in text
    assert "No claim here says customer validation has happened." in text


def test_offer_packet_labels_pricing_as_hypothesis():
    text = _offer_text()
    assert "Pricing Hypothesis" in text
    assert "pricing_claim_type: hypothesis" in text
    assert "not direct willingness-to-pay proof" in text
