from office.mission_command.e60_gov_mcp_validation_harness import run_e60_gov_mcp_validation_harness


def test_e60_gov_mcp_allows_valid_and_denies_broken_fixtures():
    data = run_e60_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_E60_market_readiness_manifest"]["status"] == "ALLOW"
    for key in ["direct_outreach_selected", "publication_selected", "controlled_review_execution_without_owner_approval", "pending_owner_decision_treated_as_approval", "live_fixture_evidence_treated_as_live_market_freshness"]:
        assert data["deny_results"][key]["status"] == "DENY"
