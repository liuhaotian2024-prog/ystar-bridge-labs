from office.mission_command.e55_behavior_center_maturity_diagnosis import run_behavior_center_maturity_diagnosis

def test_behavior_center_maturity_diagnosis_identifies_l3_plus_start():
    data = run_behavior_center_maturity_diagnosis()
    assert data["current_overall_behavior_level"] == "L3_plus"
    assert data["target_level"] == "L5 behavior control center"
    assert data["no_external_action"] is True
