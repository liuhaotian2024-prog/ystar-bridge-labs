from office.mission_command.e47_full_capability_coverage_gate import build_full_capability_coverage_gate, build_capability_final_status_matrix


def test_full_capability_coverage_gate_passes_without_unknowns():
    gate = build_full_capability_coverage_gate()
    assert gate["coverage_gate_passed"] is True
    assert gate["unknown_status_count"] == 0
    assert gate["all_spine_layers_represented"] is True
    for layer in ["field_functional_projection_layer", "ceo_brain_layer", "commercial_value_layer", "evidence_audit_layer", "execution_boundary_layer"]:
        assert gate["spine_layer_counts"].get(layer, 0) > 0
    assert gate["expert_route_quarantined"] is True
    assert gate["get_artifact_only_not_active_runtime"] is True
    matrix = build_capability_final_status_matrix()
    assert matrix["no_unknown_status"] is True
    assert matrix["resource_count"] == gate["resource_count"]
