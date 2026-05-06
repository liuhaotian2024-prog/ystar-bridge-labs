from office.mission_command.e51_labs_runtime_linkage_graph import build_labs_runtime_linkage_graph


def test_e51_labs_runtime_linkage_graph_has_required_current_state_edges():
    graph = build_labs_runtime_linkage_graph()
    edge_types = {edge['edge_type'] for edge in graph['edges']}
    assert {'reads', 'writes', 'consumes_next', 'validated_by_y_star_gov', 'exposed_by_gov_mcp'}.issubset(edge_types)
    assert graph['answers']['current_selected_route']['value'] == 'package_governed_agent_action_proof_packet'
    assert graph['answers']['current_nearest_alternative']['value'] == 'external_commercial_observation_now'
    assert graph['answers']['written_but_not_read'] == []
