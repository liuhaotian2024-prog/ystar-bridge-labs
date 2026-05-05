from office.mission_command.e44a_capability_archaeology import build_full_ceo_capability_archaeology

def test_archaeology_discovers_required_milestones_and_accessors():
    artifact = build_full_ceo_capability_archaeology()
    assert artifact["resources_inspected"] > 100
    for milestone in ["E35", "E36", "E39", "E41", "E42", "E43"]:
        assert artifact["required_milestone_discovery"][milestone]
    assert artifact["artifact_accessor_examples"]
    assert all(item["resource_type"] == "artifact_accessor" for item in artifact["artifact_accessor_examples"])
    assert any(item["path"].startswith("office/mission_command/e35") for item in artifact["resources"])
    assert any(item["path"].startswith("office/mission_command/e36") for item in artifact["resources"])
