from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _packet() -> str:
    return (ROOT / "reports" / "integration" / "e7_owner_decision_packet.md").read_text(encoding="utf-8")


def test_owner_packet_does_not_approve_customer_contact_by_default():
    text = _packet()
    assert "no_customer_contact_approved_by_default: True" in text
    assert "no_publication_approved_by_default: True" in text
    assert "no_payment_form_account_approved_by_default: True" in text


def test_owner_packet_has_exact_e8_approval_options():
    text = _packet()
    assert "approve 3-person qualitative validation" in text
    assert "approve 5-10 targeted outreach validation" in text
    assert "approve public landing/post draft publication" in text
    assert "request revision of offer packet" in text
    assert "hold" in text


def test_owner_packet_defines_what_approval_covers_and_does_not_cover():
    text = _packet()
    assert "What Approval Covers" in text
    assert "only the exact validation mode/count/channel/message/stop condition selected by owner" in text
    assert "What Approval Does Not Cover" in text
    assert "core DB/brain/memory/CIEU writeback" in text


def test_owner_packet_requires_preflight_before_external_action():
    text = _packet()
    assert "Preflight Requirements Before External Action" in text
    assert "semantic action classification" in text
    assert "action-wide governance preflight" in text
