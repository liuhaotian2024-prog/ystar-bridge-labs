from office.mission_command.e42_ceo_runtime_reuse_router_integration import build_ceo_runtime_reuse_router_integration


def test_ceo_runtime_reuse_router_integration_sequence_and_boundaries():
    artifact = build_ceo_runtime_reuse_router_integration()
    assert artifact["future_CEO_task_start_sequence"][:3] == ["task interpretation", "task-capability match", "reuse-first gate"]
    assert artifact["not_second_brain"] is True
    assert artifact["not_second_KG"] is True
    assert artifact["external_action_occurred"] is False
