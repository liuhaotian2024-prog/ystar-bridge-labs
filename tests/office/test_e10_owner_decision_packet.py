from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _packet() -> str:
    return (REPORTS / "e10_owner_decision_packet.md").read_text(encoding="utf-8")


def test_owner_packet_recommends_approve_or_edit_E11_validation_batch():
    assert "recommended_next_decision: approve_or_edit_E11_validation_batch" in _packet()


def test_owner_packet_does_not_claim_contact_executed():
    text = _packet()
    assert "contact_executed: False" in text
    assert "no contact executed" in text


def test_owner_packet_does_not_recommend_paid_pilot_without_feedback():
    text = _packet()
    assert "paid_pilot_recommended: False" in text
    assert "paid pilot is not recommended without positive E11 feedback" in text
