from office.mission_command.e54_ceo_next_action_reasoner import build_next_action_reasoning_packet

def test_next_action_reasoner_denies_external_review_now():
    data=build_next_action_reasoning_packet()
    assert data['selected_next_action'] == 'E55_behavior_control_center_L5_convergence'
    assert data['counterfactual_analysis']['execute_controlled_first_user_review_now']['decision'] == 'deny'
    assert data['external_action_allowed'] is False
    assert data['behavior_execution_required'] is False
