from office.mission_command.e46b_field_projection_adapter import project_task_from_m_triangle


def test_field_projection_adapter_projects_task_to_action_and_closure():
    result = project_task_from_m_triangle({"task_title": "first user", "task_description": "prepare first real user value demo"}, {})
    assert result["projection_maturity"] == "partial_adapter"
    assert result["governance_gate_needed"] is True
    assert result["action_candidates"]
    assert result["cieu_closure_expectation"]
    assert result["no_external_action"] is True
