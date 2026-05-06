from office.mission_command.e49_semantic_graph_builder import build_semantic_graph


def test_e49_semantic_graph_includes_required_runtime_semantics():
    graph = build_semantic_graph()
    node_ids = {node['id'] for node in graph['nodes']}
    assert 'projection:e49' in node_ids
    assert 'ceo_brain:e46b_context' in node_ids
    assert 'value_object:governed_agent_action_proof_packet' in node_ids
    assert 'execution:gov_mcp_ystar' in node_ids
    assert 'blocker:ystar_doctor' in node_ids
    assert 'blocker:missing_mcp_client_path' in node_ids
    assert any(node['type'] == 'route' for node in graph['nodes'])
    assert graph['no_orphan_selected_route'] is True
    assert graph['selected_route_has_evidence_semantics'] is True
    assert graph['selected_route_has_blocker_semantics'] is True
