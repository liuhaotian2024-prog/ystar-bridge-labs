from office.mission_command.e44a_e43_replay_comparator import build_e43_task_replay_with_activated_cognition, compare_e43_route_with_activated_cognition

TASK = {
    "task_title": "E43 replay",
    "task_description": "Prepare the fastest credible path toward one real external user successfully installing and understanding Y*gov / gov-mcp / Y*Bridge Labs' agent-company runtime value.",
}

def test_replay_compares_old_and_new_routes():
    comparison = compare_e43_route_with_activated_cognition(TASK)
    assert comparison["old_route"]["path"]
    assert comparison["new_route"]["technical_substrate"] == "gov-mcp + Y-star-gov governed execution in 5 minutes"
    assert comparison["route_improved"] is True
    assert len(comparison["referenced_prior_artifacts"]) >= 3
    assert comparison["concrete_next_action"] == "E45_run_activated_ceo_loop_on_real_local_first_value_demo"
    replay = build_e43_task_replay_with_activated_cognition(TASK)
    assert replay["answers"]["selected_route_remains_gov_mcp_plus_Y_star_gov"] is True
    assert replay["no_external_action"] is True
