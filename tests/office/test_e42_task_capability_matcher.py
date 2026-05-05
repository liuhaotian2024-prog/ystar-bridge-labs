from office.mission_command.e42_task_capability_matcher import build_task_capability_matcher_model, match_task_to_capabilities


def test_task_capability_matcher_routes_without_llm():
    model = build_task_capability_matcher_model()
    assert model["requires_llm"] is False
    matches = match_task_to_capabilities("Plan external execution and MCP tool use with provider API boundary", top_n=12)
    assert matches
    assert any(match["owner_layer"] == "gov_mcp_execution_boundary" for match in matches)
    assert any(match["recommended_action"] == "blocked_by_boundary" for match in matches)


def test_task_capability_matcher_finds_delivery_resources():
    matches = match_task_to_capabilities("Fix delivery bridge status issue", top_n=12)
    assert any("repository_delivery" in match["resource_path"] or "check_repository_delivery" in match["resource_path"] for match in matches)
