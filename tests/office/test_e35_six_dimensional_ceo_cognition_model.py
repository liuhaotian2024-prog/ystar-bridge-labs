from office.mission_command.e35_six_dimensional_ceo_cognition_model import build_six_dimensional_ceo_cognition_model


def test_six_dimensional_model_is_one_provisional_brain_model():
    model = build_six_dimensional_ceo_cognition_model()
    assert model["canonical_model_discovered"] is False
    assert model["model_status"] == "provisional_methodology_not_canonical_learning"
    assert model["one_brain_model"] is True
    faculties = {item["faculty"] for item in model["six_faculties"]}
    assert faculties == {"logical_causal", "innovation_invention", "strategic", "systems", "human_emotional_relational", "execution_commercial"}
    assert model["faculties_are_not_separate_brains"] is True
