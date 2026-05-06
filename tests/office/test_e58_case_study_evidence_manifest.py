from office.mission_command.e58_case_study_evidence_manifest import build_case_study_evidence_manifest


def test_case_study_evidence_manifest_spans_e50a_through_e57():
    data = build_case_study_evidence_manifest()
    milestones = {item["source_milestone"] for item in data["evidence_items"]}
    assert {"E50A", "E50B", "E50C", "E51", "E52", "E53", "E54", "E55", "E56", "E57"} <= milestones
    assert data["evidence_count"] >= 10
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["real_mcp_transport_claimed"] is False

