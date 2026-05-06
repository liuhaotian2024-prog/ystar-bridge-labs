from office.mission_command.e50a_fake_fastmcp_harness import run_fake_fastmcp_harness


def test_e50a_fake_harness_closes_tool_layer_allow_deny_without_real_mcp():
    result = run_fake_fastmcp_harness()
    assert result["external_mcp_dependency_required"] is False
    assert result["required_tools_present"]["gov_check"] is True
    assert result["required_tools_present"]["gov_demo"] is True
    assert result["allow_result"]["passed"] is True
    assert result["allow_result"]["actual"] == "ALLOW"
    assert result["deny_result"]["passed"] is True
    assert result["deny_result"]["actual"] == "DENY"
    assert result["final_status"] == "tool_layer_allow_deny_closed"
    assert result["started_real_server"] is False
    assert result["mutated_real_client_config"] is False
    assert result["ports_opened"] == []
    assert result["no_external_action"] is True
