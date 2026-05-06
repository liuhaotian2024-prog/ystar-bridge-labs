from office.mission_command.e59_gov_mcp_validation_harness import run_e59_gov_mcp_validation_harness


def test_e59_gov_mcp_allows_valid_and_denies_broken_fixtures():
    data = run_e59_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_E59_external_intelligence_manifest"]["status"] == "ALLOW"
    for key in [
        "contact_scraping",
        "login_required_source",
        "provider_private_api_source",
        "source_receipt_missing_reader",
        "evidence_atom_claiming_customer_validation",
        "paid_signal_claim_from_public_evidence",
        "expert_feedback_claim_from_public_evidence",
        "external_action_allowed",
        "stale_source_consumed_as_current_without_label",
        "hardcoded_category_only_discovery",
    ]:
        assert data["deny_results"][key]["allowed"] is False

