from office.mission_command.e55_gov_mcp_validation_harness import run_e55_gov_mcp_validation_harness

def test_gov_mcp_harness_allows_valid_and_denies_broken_fixtures():
    data = run_e55_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_internal_dry_run_action"]["status"] == "ALLOW"
    assert data["deny_results"]["ceo_brain_direct_execution"]["status"] == "DENY"
    assert data["deny_results"]["pending_owner_decision_treated_as_approval"]["status"] == "DENY"
