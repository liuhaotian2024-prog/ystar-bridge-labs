from office.mission_command.e42_reuse_first_no_rebuild_gate import build_reuse_first_no_rebuild_gate, evaluate_reuse_first_gate


def test_reuse_first_gate_blocks_wrong_layer_and_report_pile():
    gate = build_reuse_first_no_rebuild_gate()
    assert "blocked_wrong_layer" in gate["decisions"]
    external = evaluate_reuse_first_gate("Plan external execution and MCP tool use")
    assert external["decision"] == "blocked_wrong_layer"
    report = evaluate_reuse_first_gate("Create another report instead of using existing runtime")
    assert report["decision"] == "blocked_report_pile"
