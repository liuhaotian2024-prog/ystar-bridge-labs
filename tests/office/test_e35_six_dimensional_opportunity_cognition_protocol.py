from office.mission_command.e35_six_dimensional_opportunity_cognition_protocol import build_six_dimensional_opportunity_cognition_protocol


def test_six_dimensional_protocol_preserves_faculty_tensions():
    artifact = build_six_dimensional_opportunity_cognition_protocol()
    schema = artifact["record_schema"]
    outputs = schema["six_faculty_outputs"]
    assert set(outputs) == {"logical_causal", "innovation_invention", "strategic", "systems", "human_emotional_relational", "execution_commercial"}
    assert artifact["naive_score_collapse_allowed"] is False
    assert "high innovation but weak execution" in artifact["tension_examples"]
    assert "high emotional pain but weak Y* fit" in artifact["tension_examples"]
