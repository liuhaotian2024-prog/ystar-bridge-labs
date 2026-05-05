from office.mission_command.e35_multi_hop_abstraction_jump_engine import build_multi_hop_abstraction_jump_engine


def test_multi_hop_jump_engine_has_deep_ladders_and_probe_examples():
    artifact = build_multi_hop_abstraction_jump_engine()
    assert artifact["seed_theme_count"] >= 8
    for record in artifact["hop_records"]:
        assert record["hop_count"] >= 7
        assert record["status"] in {"hypothesis_probe", "fantasy_probe", "near_term_probe"}
    assert any("healthier waking" in item for item in artifact["deepest_jump_examples"])
    assert artifact["product_selected"] is False
