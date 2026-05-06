from office.mission_command.e49_deep_semantic_operating_runtime import run_deep_semantic_operating_runtime


def test_e49_deep_semantic_runtime_invokes_main_components():
    result = run_deep_semantic_operating_runtime('What is the fastest credible route for Y*Bridge Labs to make real money or obtain the strongest near-term real user / usage / paid signal, using existing assets and without overclaiming?')
    assert result['status'] == 'completed'
    assert result['interpretation']['semantic_task_validation']['valid'] is True
    assert result['field_projection']['projection_maturity'] == 'partial_adapter'
    assert result['ceo_brain_context']['active_task_time_source'] == 'e46b_ceo_brain_adapter.load_ceo_brain_context'
    assert result['semantic_graph_summary']['no_orphan_selected_route'] is True
    assert result['coverage_gate']['passed'] is True
    assert result['canonical_runtime_v2']['no_external_action'] is True
    assert result['route_decision']['next_milestone'] == 'E50_build_minimal_gov_mcp_local_test_client'
    assert result['side_effect_report']['send'] is False
    assert result['no_external_action'] is True
