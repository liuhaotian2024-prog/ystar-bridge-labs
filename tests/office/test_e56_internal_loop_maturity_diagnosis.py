from office.mission_command.e56_internal_loop_maturity_diagnosis import run_internal_loop_maturity_diagnosis


def test_internal_loop_maturity_diagnosis_targets_l5():
    data = run_internal_loop_maturity_diagnosis()
    assert data["current_overall_internal_loop_level"] == "L4_plus"
    assert data["target_level"] == "L5"
    assert len(data["dimensions"]) == 18
    assert data["external_action_allowed"] is False

