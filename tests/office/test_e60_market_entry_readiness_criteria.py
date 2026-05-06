from office.mission_command.e60_market_entry_readiness_criteria import run_market_entry_readiness_criteria


def test_e60_readiness_level_is_structural_not_execution_ready():
    data = run_market_entry_readiness_criteria()
    assert data["current_readiness_level"] == "L3_external_intelligence_structurally_ready"
    assert data["market_entry_execution_ready"] is False
    assert data["controlled_review_execution_ready"] is False
    assert "no explicit owner approval" in data["not_L4_because"]
