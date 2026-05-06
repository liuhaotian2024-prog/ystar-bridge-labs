from office.mission_command.e61_public_read_receipts import run_public_read_receipts


def test_e61_receipts_are_live_or_blocker_but_never_validation_claims():
    data = run_public_read_receipts()
    assert data["receipt_count"] >= 1
    assert data["not_customer_validation"] is True
    assert data["not_paid_signal"] is True
    assert data["not_expert_feedback"] is True
    assert data["receipt_mode"] in {"live_receipts", "blocker_receipts"}
