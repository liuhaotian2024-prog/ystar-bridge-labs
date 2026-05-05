from office.mission_command.e40_no_fake_evidence_overclaim_audit import build_no_fake_evidence_overclaim_audit


def test_no_fake_evidence_audit_passes_and_forbids_overclaims():
    audit = build_no_fake_evidence_overclaim_audit()
    assert audit["audit_passed"] is True
    assert audit["customer_validation_claimed"] is False
    assert audit["paid_signal_claimed"] is False
    assert audit["expert_feedback_claimed"] is False
    assert audit["send_occurred"] is False
    assert audit["public_evidence_remains_public_evidence"] is True
