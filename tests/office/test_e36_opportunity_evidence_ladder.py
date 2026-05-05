from office.mission_command.e36_opportunity_evidence_ladder import build_opportunity_evidence_ladder


def test_evidence_ladder_has_entry_per_opportunity_and_no_fake_validation():
    data = build_opportunity_evidence_ladder()
    assert len(data["entries"]) >= 60
    assert data["imagination_only_count"] > 0
    assert data["safe_public_read_only_next_count"] > 0
    assert data["owner_approved_review_next_count"] > 0
    for entry in data["entries"]:
        assert 0 <= entry["current_evidence_level"] <= 8
        assert entry["customer_validation_claimed"] is False
        assert entry["paid_signal_claimed"] is False
