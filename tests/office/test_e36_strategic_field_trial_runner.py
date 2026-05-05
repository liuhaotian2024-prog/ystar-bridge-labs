from office.mission_command.e36_strategic_field_trial_runner import build_strategic_field_trial_results


def test_strategic_field_trial_processes_all_opportunities_without_route_selection():
    data = build_strategic_field_trial_results()
    assert data["opportunities_processed"] >= 60
    assert data["final_product_selected"] is False
    assert data["examples_promoted_to_route"] is False
    for record in data["records"]:
        assert record["faculty_tension_map"]
        assert record["cross_repo_governance_requirement"]
        assert record["gov_mcp_execution_requirement"]
        assert record["route_selected"] is False
