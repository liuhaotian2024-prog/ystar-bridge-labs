from office.mission_command.e41_frontier_capability_import_scope import build_frontier_capability_import_scope


def test_e41_frontier_capability_import_scope_contract():
    artifact = build_frontier_capability_import_scope()
    assert artifact["selected_import_count"] >= 7
    names = {item["capability"] for item in artifact["selected_imports"]}
    assert "Synthetic Reviewer Simulation Protocol" in names
    assert "provider/API/tool integration" in artifact["forbidden_in_E41"]
    assert artifact["external_action_occurred"] is False

