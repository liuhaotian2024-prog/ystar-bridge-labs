from office.mission_command.e41_frontier_capability_import_loop import build_frontier_capability_import_loop


def test_e41_frontier_capability_import_loop_contract():
    artifact = build_frontier_capability_import_loop()
    assert artifact["permanent_CEO_brain_method"] is True
    assert artifact["second_brain_created"] is False
    assert len(artifact["stages"]) == 12
    assert "post-import capability evaluation" in [stage["name"] for stage in artifact["stages"]]

