from office.mission_command.e48_real_code_interface_discovery import discover_real_code_interfaces


def test_e48_discovers_real_gov_mcp_code_surface():
    data = discover_real_code_interfaces()
    assert set(['install', 'uninstall', 'status', 'restart']).issubset(set(data['gov_mcp']['cli_subcommands']))
    assert data['gov_mcp']['proof_tools_present']['gov_check'] is True
    assert data['gov_mcp']['proof_tools_present']['gov_demo'] is True
    assert data['gov_mcp']['install_side_effects']['starts_background_server'] is True
    assert data['gov_mcp']['install_side_effects']['may_call_claude_mcp_add'] is True
    assert data['selected_demo_strategy'] in {'in_process_tool_call', 'in_process_ystar_kernel_proof_with_server_transport_blocker', 'blocked_with_exact_missing_code_path'}
    assert data['no_external_action'] is True
