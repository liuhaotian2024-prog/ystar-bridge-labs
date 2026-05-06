from office.mission_command.e50b_ceo_commercial_decision_packet_builder import build_ceo_commercial_decision_packet


def test_commercial_decision_packet_selects_one_next_milestone():
    packet = build_ceo_commercial_decision_packet()
    assert packet['final_status'].startswith('counterfactual_runtime_reconnected')
    assert packet['selected_route']['route_id'] == 'package_governed_agent_action_proof_packet'
    assert packet['nearest_rejected_or_deferred_alternative']['route_id']
    assert packet['next_executable_milestone'] == 'E51_package_governed_agent_action_proof_packet_for_first_user_review'
    assert packet['customer_validation_claimed'] is False
    assert packet['paid_signal_claimed'] is False
