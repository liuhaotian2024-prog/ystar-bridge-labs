from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context


def test_e50b_decision_packet_is_consumed_by_load_ceo_brain_context():
    brain = load_ceo_brain_context({'task_title': 'E50C test', 'task_description': 'Load E50B state.'})
    assert brain['brain_centerline_status'] == 'ceo_brain_centerline_connected'
    assert brain['current_selected_route'] == 'package_governed_agent_action_proof_packet'
    assert brain['current_nearest_alternative'] == 'external_commercial_observation_now'
    assert brain['current_next_milestone'] == 'E51_package_governed_agent_action_proof_packet_for_first_user_review'
    assert brain['current_e50a_status'] == 'tool_layer_allow_deny_closed'
    assert 'real_mcp_transport_not_closed' in brain['current_blocker_state']
    assert brain['current_no_go_boundaries']['no_outreach'] is True
    assert brain['current_no_go_boundaries']['no_publication'] is True
    assert brain['current_no_go_boundaries']['no_customer_validation_claim'] is True
    assert brain['current_no_go_boundaries']['no_paid_signal_claim'] is True
    assert brain['current_no_go_boundaries']['brain_may_not_bypass_governance'] is True
