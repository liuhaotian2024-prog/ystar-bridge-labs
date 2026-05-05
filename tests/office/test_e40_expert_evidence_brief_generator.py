from office.mission_command.e40_expert_evidence_brief_generator import build_expert_evidence_briefs


def test_evidence_briefs_preserve_claim_boundaries():
    briefs = build_expert_evidence_briefs()
    assert briefs["brief_count"] == 3
    assert briefs["invented_evidence"] is False
    for brief in briefs["briefs"]:
        assert brief["no_customer_validation"] is True
        assert brief["no_paid_signal"] is True
        assert brief["no_final_product_selection"] is True
        assert "customer validation" in brief["what_expert_cannot_prove"]
