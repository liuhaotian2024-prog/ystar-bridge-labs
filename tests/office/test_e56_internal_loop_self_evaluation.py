from office.mission_command.e56_internal_loop_self_evaluation import run_internal_loop_self_evaluation


def test_self_evaluation_proposes_e57():
    data = run_internal_loop_self_evaluation()
    assert data["self_evaluation_status"] == "passed"
    assert data["next_milestone_justified"] == "E57_post_L5_money_route_retest"
    assert data["checks"]["no_go_boundaries_held"] is True

