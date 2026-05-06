from office.mission_command.e47_mainline_integration_adapters import build_mainline_adapter_registry


def test_all_mainline_adapter_families_invoke_without_external_action():
    registry = build_mainline_adapter_registry({"task_title": "money route", "task_description": "find credible paid signal route"})
    assert registry["adapter_count"] == 12
    assert registry["all_invoked"] is True
    assert registry["no_external_action"] is True
    ids = {item["adapter_id"] for item in registry["adapter_results"]}
    for expected in ["field_projection_mainline", "ceo_brain_mainline", "wisdom_mainline", "working_memory_mainline", "article_11_mainline", "commercial_route_mainline", "evidence_intelligence_mainline", "execution_demo_mainline", "governance_boundary_mainline", "audit_closure_mainline", "notification_board_loop", "recovery_delivery_mainline"]:
        assert expected in ids
