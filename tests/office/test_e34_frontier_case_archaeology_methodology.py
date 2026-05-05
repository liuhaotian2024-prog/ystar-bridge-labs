from office.mission_command.e34_frontier_case_archaeology_methodology import build_frontier_case_archaeology_methodology


def test_case_archaeology_schema_has_required_categories_and_dimensions():
    artifact = build_frontier_case_archaeology_methodology()
    assert artifact["case_categories_supported_count"] >= 9
    assert artifact["extraction_dimensions_count"] >= 12
    assert "what primitive changed" in artifact["extraction_dimensions"]
    assert "what evidence is needed before acting" in artifact["extraction_dimensions"]
    assert artifact["not_a_final_opportunity_conclusion"] is True
