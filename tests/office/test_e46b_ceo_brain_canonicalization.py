from office.mission_command.e46b_ceo_brain_canonicalization import build_ceo_brain_canonical_model, build_ceo_brain_operationalization_gap_matrix


def test_ceo_brain_canonicalization_defines_single_active_source():
    model = build_ceo_brain_canonical_model()
    assert model["active_task_time_ceo_brain_source"].endswith("load_ceo_brain_context")
    assert model["no_second_ceo_brain"] is True
    assert model["no_second_ceo_kg"] is True
    assert model["relationships"]
    matrix = build_ceo_brain_operationalization_gap_matrix()
    assert len(matrix["rows"]) >= 4
