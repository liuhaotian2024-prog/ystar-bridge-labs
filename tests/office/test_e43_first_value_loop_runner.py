from office.mission_command.e43_first_value_loop_runner import build_first_value_loop_run_result, discover_first_value_assets


def test_first_value_loop_runner_uses_existing_assets_without_external_execution():
    assets = discover_first_value_assets()
    assert assets["gov-mcp"]["has_install_command"] is True
    assert assets["gov-mcp"]["has_status_command"] is True
    assert assets["Y-star-gov"]["cli_entrypoint"] is True
    result = build_first_value_loop_run_result()
    assert result["passed"] is True
    assert result["external_action_occurred"] is False
    assert result["provider_api_or_tool_execution_occurred"] is False
