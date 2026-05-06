from office.mission_command.e57_gov_mcp_validation_harness import run_e57_gov_mcp_validation_harness


def test_gov_mcp_harness_allows_valid_and_denies_broken_route_fixtures():
    data = run_e57_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_post_l5_route_decision_manifest"]["status"] == "ALLOW"
    assert data["deny_results"]["direct_outreach_selected"]["status"] == "DENY"
    assert data["deny_results"]["customer_validation_claimed"]["allowed"] is False
    assert data["deny_results"]["pending_owner_decision_treated_as_approval"]["allowed"] is False

