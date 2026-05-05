from office.mission_command.e34_primitive_shift_detector import build_primitive_shift_detector


def test_primitive_shift_detector_has_expandable_shifts():
    artifact = build_primitive_shift_detector()
    assert artifact["primitive_shifts_identified"] >= 10
    assert artifact["most_important_primitive_shift"] == "software tool -> accountable economic actor"
    for shift in artifact["primitive_shifts"]:
        assert shift["old_primitive"]
        assert shift["new_primitive"]
        assert shift["evidence_requirement"]
