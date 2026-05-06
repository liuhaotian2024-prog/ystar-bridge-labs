from office.mission_command.e56_counterfactual_internal_action_selector import run_counterfactual_internal_action_selection


def test_counterfactual_selector_defers_e57_until_loop_proof():
    data = run_counterfactual_internal_action_selection()
    assert data["selected_action"] == "run_internal_operating_loop_self_test"
    assert data["nearest_alternative"] == "prepare_E57_post_L5_money_route_retest"
    assert "wait until the internal loop proof" in data["why_not_alternative"]
    assert data["external_action_allowed"] is False

