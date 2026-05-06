from office.mission_command.e56_gov_mcp_validation_harness import run_e56_gov_mcp_validation_harness


def test_gov_mcp_harness_allows_valid_and_denies_broken():
    data = run_e56_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_internal_loop_manifest"]["status"] == "ALLOW"
    assert data["deny_results"]["external_action_allowed"]["status"] == "DENY"
    assert data["deny_results"]["brain_direct_execution"]["allowed"] is False
    assert data["deny_results"]["pending_owner_decision_treated_as_approval"]["allowed"] is False

