from office.mission_command.e51_capability_centerline_binding_audit import build_capability_centerline_binding_audit


def test_capability_binding_audit_covers_all_functional_classes_and_key_assets():
    audit = build_capability_centerline_binding_audit()
    assert audit['all_required_functional_classes_represented'] is True
    by_id = {record['capability_id']: record for record in audit['records']}
    assert by_id['e50b_counterfactual_runtime']['functional_class'] == 'cognitive_capability'
    assert by_id['e50a_gov_mcp_tool_layer_harness']['functional_class'] == 'behavior_control_capability'
    assert by_id['e50b_czl_closure']['functional_class'] == 'evidence_closure_capability'
    assert by_id['e50c_no_go_boundary_policy']['functional_class'] == 'boundary_capability'
    assert by_id['e49_money_route_decision']['functional_class'] == 'reference_only_artifact'
