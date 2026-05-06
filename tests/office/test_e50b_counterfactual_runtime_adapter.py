from office.mission_command.e50b_counterfactual_runtime_adapter import build_counterfactual_route_matrix, summarize_counterfactual_connection_status


def test_counterfactual_route_matrix_is_machine_readable_and_valid():
    matrix = build_counterfactual_route_matrix('test route decision')
    assert matrix['validation']['valid'] is True
    assert matrix['selected_route']
    assert matrix['nearest_rejected_or_deferred_route']
    for route in matrix['routes']:
        assert route['Xt_current_state']
        assert route['Y_star_target']
        assert route['U_intervention']
        assert route['predicted_Yt_plus_1']
        assert route['predicted_Rt_plus_1']
        assert route['decision'] in {'select', 'defer', 'quarantine', 'deny'}


def test_immediate_outreach_is_denied_or_quarantined():
    matrix = build_counterfactual_route_matrix('test route decision')
    outreach = next(route for route in matrix['routes'] if route['route_id'] == 'immediate_customer_expert_outreach')
    assert outreach['decision'] in {'deny', 'quarantine'}
    assert matrix['validation']['immediate_outreach_denied'] is True


def test_adapter_status_reports_reconnection():
    status = summarize_counterfactual_connection_status()
    assert status['status'] == 'counterfactual_runtime_reconnected'
    assert status['matrix_valid'] is True
