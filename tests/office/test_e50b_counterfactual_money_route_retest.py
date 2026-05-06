from office.mission_command.e50b_counterfactual_money_route_retest import run_counterfactual_money_route_retest


def test_e50a_status_consumed_not_recomputed():
    data = run_counterfactual_money_route_retest()
    assert data['e50a_status_path'].endswith('e50a_mcp_client_blocker_update.json')
    assert data['e50a_status_consumed'] in {'tool_layer_allow_deny_closed', 'missing_e50a_status'}


def test_money_route_selection_has_nearest_counterfactual_alternative():
    data = run_counterfactual_money_route_retest()
    assert data['selected_route']['route_id'] == 'package_governed_agent_action_proof_packet'
    assert data['nearest_rejected_or_deferred_route']['route_id']
    assert data['why_selected_beats_nearest']
    assert data['customer_validation_claimed'] is False
    assert data['paid_signal_claimed'] is False
