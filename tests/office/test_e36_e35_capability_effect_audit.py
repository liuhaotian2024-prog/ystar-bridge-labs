from office.mission_command.e36_e35_capability_effect_audit import build_e35_capability_effect_audit


def test_e35_capability_effect_audit_shows_improvement_and_watchouts():
    data = build_e35_capability_effect_audit()
    assert data["improvement_found"] is True
    assert data["sufficient_to_run_strategy_trial"] is True
    assert data["comparison"]["non_governance_opportunity_coverage"] >= 10
    assert data["comparison"]["cross_repo_alignment_discipline"] is True
    assert data["remaining_shallow_reasoning_patterns"]
