from office.mission_command.e56_internal_cycle_scenario_builder import build_internal_cycle_scenario


def test_scenario_selects_internal_self_test_and_denies_external_review():
    data = build_internal_cycle_scenario()
    assert data["selected_action"] == "run_internal_operating_loop_self_test"
    assert data["external_first_user_review_action"] == "denied"
    assert any(c["action_id"] == "execute_external_first_user_review_now" and c["disposition"] == "deny" for c in data["candidate_actions"])

