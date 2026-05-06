from office.mission_command.e58_gov_mcp_validation_harness import run_e58_gov_mcp_validation_harness


def test_gov_mcp_harness_allows_valid_e58_and_denies_broken_fixtures():
    data = run_e58_gov_mcp_validation_harness()
    assert data["passed"] is True
    assert data["allow_results"]["valid_E58_case_study_manifest"]["status"] == "ALLOW"
    assert data["deny_results"]["outreach_selected"]["status"] == "DENY"
    assert data["deny_results"]["publication_selected"]["status"] == "DENY"
    assert data["deny_results"]["customer_validation_claimed"]["status"] == "DENY"
    assert data["deny_results"]["paid_signal_claimed"]["status"] == "DENY"
    assert data["deny_results"]["real_mcp_transport_claimed"]["status"] == "DENY"
    assert data["deny_results"]["external_intelligence_L5_claimed"]["status"] == "DENY"
    assert data["deny_results"]["missing_case_study_reader"]["allowed"] is False
    assert data["deny_results"]["missing_E59_next_runtime_reader"]["allowed"] is False
    assert data["deny_results"]["pending_owner_decision_treated_as_approval"]["allowed"] is False

