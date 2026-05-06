from office.mission_command.e59_source_receipt_builder import build_source_receipts


def test_source_receipts_are_produced_for_safe_fixture_reads():
    receipts = build_source_receipts()
    assert len(receipts) >= 8
    assert all(receipt["retrieval_status"] == "fixture_read" for receipt in receipts)
    assert all(receipt["no_contact_info_extracted"] is True for receipt in receipts)
    assert all(receipt["no_login"] is True for receipt in receipts)
    assert all(receipt["no_external_action"] is True for receipt in receipts)

