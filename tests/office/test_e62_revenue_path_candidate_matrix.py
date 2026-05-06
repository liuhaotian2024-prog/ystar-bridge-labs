from office.mission_command.e62_revenue_path_candidate_matrix import run_revenue_path_candidate_matrix


def test_e62_revenue_path_matrix_is_repo_grounded_and_selects_runtime_harness():
    data = run_revenue_path_candidate_matrix()
    selected = [item for item in data["candidates"] if item["selected"]]
    assert len(selected) == 1
    assert selected[0]["route_id"] == "AI_agent_company_runtime_harness_deployment_service"
    assert selected[0]["source_asset_path_or_new_reason"]
    assert data["snapshot_not_permanent_strategy"] is True
    assert data["no_customer_validation_claimed"] is True
