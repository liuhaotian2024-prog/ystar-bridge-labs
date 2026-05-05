from office.mission_command.e37_public_readonly_evidence_sprint_design import build_public_readonly_evidence_sprint_design


def test_public_readonly_sprint_is_prepared_not_executed():
    data = build_public_readonly_evidence_sprint_design()
    assert data["execution_status"] == "prepared_not_executed"
    assert data["customer_contact_occurred"] is False
    assert data["form_submitted"] is False
    assert data["published_externally"] is False
    assert data["provider_api_called"] is False
    assert data["plans"]
    assert "evidence_receipt_schema" in data["plans"][0]
