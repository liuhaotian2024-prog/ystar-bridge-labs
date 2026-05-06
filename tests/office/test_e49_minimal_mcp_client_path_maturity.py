from office.mission_command.e49_minimal_mcp_client_path_maturity import inspect_minimal_mcp_client_path


def test_e49_mcp_client_path_maturity_is_code_grounded():
    data = inspect_minimal_mcp_client_path()
    assert 'gov_check' in data['tool_names_sample'] or data['questions']['exposes_direct_python_callable_for_gov_check_gov_demo'] != 'not_found'
    assert data['pyproject_declares_mcp_dependency'] is True
    assert data['classification'] in {'client_path_available_with_existing_dependency', 'blocked_missing_local_mcp_dependency', 'blocked_missing_test_client_helper', 'blocked_unknown_client_path_gap'}
    assert data['no_internet_install'] is True
    assert data['no_external_action'] is True
