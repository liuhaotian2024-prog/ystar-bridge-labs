from office.mission_command.e51_gov_mcp_runtime_linkage_tool_harness import run_gov_mcp_runtime_linkage_tool_harness


def test_e51_gov_mcp_tool_harness_allows_valid_and_denies_broken_manifest():
    result = run_gov_mcp_runtime_linkage_tool_harness()
    assert result['passed'] is True
    assert result['required_tools_present'] is True
    assert result['allow_proof']['status'] == 'ALLOW'
    assert result['deny_proof']['status'] == 'DENY'
    assert result['no_server_started'] is True
    assert result['no_real_client_config_mutation'] is True
