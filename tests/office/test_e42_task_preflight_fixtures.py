from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_task_preflight_fixtures_route_to_expected_resources():
    artifact = get_artifact("e42_task_preflight_fixture_results")
    assert artifact["fixture_count"] >= 6
    assert artifact["all_expected_behaviors_met"] is True
    assert artifact["external_execution_fixture_routes_to_gov_mcp_boundary"] is True
    assert artifact["delivery_fixture_avoids_strategy_evidence_machinery"] is True
    delivery = next(item for item in artifact["fixtures"] if item["task_title"] == "Fix delivery bridge/status issue")
    assert delivery["does_not_invoke_unnecessary_strategy_evidence_machinery"] is True
