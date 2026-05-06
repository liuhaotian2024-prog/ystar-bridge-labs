from office.mission_command.e50b_counterfactual_disconnection_diagnosis import diagnose_counterfactual_disconnection


def test_e49_counterfactual_disconnection_detected_or_disproven_with_evidence():
    data = diagnose_counterfactual_disconnection()
    assert data['final_status'] in {
        'counterfactual_assets_present_but_runtime_disconnected',
        'counterfactual_governance_connected_but_commercial_route_disconnected',
        'counterfactual_wisdom_loaded_but_not_decision_active',
        'counterfactual_runtime_connected',
    }
    assert data['questions']
    assert any(item['question_id'] == 'e49_route_has_xt_y_star_u_predicted_y_rt' for item in data['questions'])
    assert data['counterfactual_router_present'] is True
