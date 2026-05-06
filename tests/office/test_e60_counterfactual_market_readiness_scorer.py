from office.mission_command.e60_counterfactual_market_readiness_scorer import run_counterfactual_market_readiness_matrix


def test_e60_counterfactual_matrix_selects_live_read_repair_and_penalizes_limitations():
    data = run_counterfactual_market_readiness_matrix()
    assert data["selected_next_milestone"] == "E61_live_public_read_adapter_repair_or_host_network_refresh"
    assert data["nearest_alternative"] == "E61_owner_decision_gate_for_case_study_review"
    selected = next(row for row in data["rows"] if row["decision"] == "select")
    assert selected["route_id"] == data["selected_next_milestone"]
    assert selected["deterministic_score_components"]["live_read_repair_targets_blocker_boost"] > 0
    assert any("fixture-only evidence" in note for note in data["scoring_notes"])
