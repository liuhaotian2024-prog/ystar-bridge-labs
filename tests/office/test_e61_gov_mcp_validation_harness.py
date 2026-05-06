from office.mission_command.e61_gov_mcp_validation_harness import run_e61_gov_mcp_validation_harness


def test_e61_gov_mcp_allows_valid_manifest_and_denies_broken_fixtures():
    data = run_e61_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_E61_live_public_read_manifest"]["status"] == "ALLOW"
    for key in ["contact_scraping", "login_or_form_submission", "private_provider_api", "customer_validation_claimed", "fixture_treated_as_live_freshness"]:
        assert data["deny_results"][key]["status"] == "DENY"
