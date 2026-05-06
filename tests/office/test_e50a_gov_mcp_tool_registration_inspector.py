from office.mission_command.e50a_gov_mcp_tool_registration_inspector import inspect_gov_mcp_tool_registration


def test_e50a_inspector_finds_nested_fastmcp_tools_and_missing_real_mcp():
    result = inspect_gov_mcp_tool_registration()
    assert result["tool_locations"]["gov_check"]["nested_fastmcp_registration"] is True
    assert result["tool_locations"]["gov_demo"]["nested_fastmcp_registration"] is True
    assert result["tool_locations"]["gov_check"]["module_level_function"] is False
    assert result["server_import_without_local_mcp"]["missing_import"] in {"mcp", "yaml"}
    assert result["server_import_with_fake_yaml_without_local_mcp"]["missing_import"] == "mcp"
    assert result["fake_fastmcp_can_capture_registration"] is True
    assert result["fake_fastmcp_required_tools_present"]["gov_check"] is True
    assert result["no_external_action"] is True
