from office.mission_command.e52_gov_mcp_validation_harness import run_gov_mcp_validation_harness


def test_e52_gov_mcp_validation_harness_allows_and_denies():
    data = run_gov_mcp_validation_harness()
    assert data['passed'] is True
    assert data['allow_results']['anti_drift_gate']['status'] == 'ALLOW'
    assert data['deny_results']['missing_proof_packet_reader']['status'] == 'DENY'
    assert data['deny_results']['behavior_bypassing_owner_approval']['status'] == 'DENY'
