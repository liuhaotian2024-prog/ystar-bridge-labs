from office.mission_command.e42_ceo_brain_reuse_router_update import build_ceo_brain_reuse_router_update


def test_ceo_brain_reuse_router_update_records_practical_capability():
    artifact = build_ceo_brain_reuse_router_update()
    assert "task-time internal capability awareness" in artifact["practical_capability_added"]
    assert artifact["second_CEO_brain_created"] is False
    assert artifact["second_CEO_KG_created"] is False
