from office.mission_command.e38_claim_extraction_evidence_grading import build_claim_extraction_evidence_grading


def test_claims_are_public_observation_and_unsupported_claims_removed():
    data = build_claim_extraction_evidence_grading()
    assert data["claim_count"] >= 40
    assert data["supported_claims"] > 0
    assert data["contradicted_claims"] > 0
    assert "customers are ready to pay Y*" in data["unsupported_claims_removed_or_downgraded"]
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    for claim in data["claims"]:
        assert claim["public_observation_only"] is True
        assert "customer validation exists" in claim["what_cannot_be_claimed"]
