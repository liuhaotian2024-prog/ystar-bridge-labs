from office.mission_command.e54_gov_mcp_validation_harness import run_e54_gov_mcp_validation_harness

def test_gov_mcp_harness_allows_and_denies():
    data=run_e54_gov_mcp_validation_harness()
    assert data['passed'] is True
    assert all(v['status']=='ALLOW' for v in data['allow_results'].values())
    assert all(v['status']=='DENY' for v in data['deny_results'].values())
    assert data['no_server_started'] is True
