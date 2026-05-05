from office.mission_command.e42_ceo_task_preflight_packet import build_ceo_task_preflight_packet, task_preflight_packet_schema


def test_ceo_task_preflight_packet_is_compact_and_reuse_first():
    schema = task_preflight_packet_schema()
    assert schema["compact"] is True
    packet = build_ceo_task_preflight_packet("Continue frontier capability import", "Continue frontier capability import using E41 loop and E38 backlog; no expert route.")
    assert packet["compact"] is True
    assert packet["relevant_existing_resources"]
    assert packet["no_rebuild_gate_result"]["inventory_searched"] is True
    assert packet["recommended_execution_path"] in {"reuse_existing", "extend_existing", "thin_adapter_allowed"}
