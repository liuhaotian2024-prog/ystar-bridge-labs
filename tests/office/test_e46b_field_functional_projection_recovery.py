from office.mission_command.e46b_field_functional_projection_recovery import recover_field_functional_projection, build_projection_chain_gap_matrix


def test_field_functional_projection_recovery_has_chain():
    recovery = recover_field_functional_projection()
    assert recovery["existing_projection_chain_found"] is True
    stages = {row["stage"]: row for row in recovery["projection_stages"]}
    for key in ["mission", "company", "milestone", "task", "action", "pre_u_governance_gate", "cieu_czl_closure", "residual_learning"]:
        assert key in stages
    assert recovery["adapter_needed"].endswith("project_task_from_m_triangle")
    matrix = build_projection_chain_gap_matrix()
    assert matrix["rows"]
