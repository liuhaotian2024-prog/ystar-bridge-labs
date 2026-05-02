from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _packet() -> str:
    return (ROOT / "reports" / "integration" / "e8_owner_decision_packet.md").read_text(encoding="utf-8")


def test_owner_packet_reports_no_unapproved_external_action():
    text = _packet()
    assert "no_unapproved_external_action: True" in text
    assert "customer_contact_occurred: False" in text
    assert "publication_occurred: False" in text


def test_owner_packet_has_exact_next_owner_action():
    text = _packet()
    assert "exact_owner_action:" in text
    assert "manifest and target seed files" in text


def test_owner_packet_does_not_recommend_paid_pilot_without_feedback():
    text = _packet()
    assert "validation_signal_classification: blocked_no_feedback" in text
    assert "approve_E9_paid_pilot_prep" not in text
