from office.mission_command.e49_semantic_route_scorer import score_semantic_routes


def test_e49_selected_route_has_no_unresolved_fatal_blocker():
    data = score_semantic_routes()
    selected = data['selected_route']
    assert selected['route_id'] == 'governed_agent_action_proof_packet'
    assert selected['unresolved_fatal_blocker'] is False
    assert selected['blocker_class'].startswith('major_manageable')


def test_e49_high_revenue_overclaim_routes_not_blindly_selected():
    data = score_semantic_routes()
    assert data['selected_route']['route_id'] != 'enterprise_compliance_pilot'
    enterprise = next(row for row in data['routes'] if row['route_id'] == 'enterprise_compliance_pilot')
    assert enterprise['overclaim_risk'] > .7
    assert enterprise['recommended_action'] == 'parked'


def test_e49_plugin_can_outrank_when_packaging_readiness_improves():
    data = score_semantic_routes(packaging_readiness_override=True)
    plugin = next(row for row in data['routes'] if row['route_id'] == 'claude_desktop_mcpb_packaging')
    assert plugin['proof_readiness'] > .8
    assert plugin['semantic_score'] >= data['selected_route']['semantic_score'] or plugin['recommended_action'] == 'package_first'


def test_e49_route_decision_explains_why_not_other_routes():
    data = score_semantic_routes()
    assert data['why_not_other_routes']
    assert data['semantic_route_decision']['next_milestone'] == 'E50_build_minimal_gov_mcp_local_test_client'
    assert data['semantic_route_decision']['evidence_semantics']
    assert data['semantic_route_decision']['blocker_semantics']
