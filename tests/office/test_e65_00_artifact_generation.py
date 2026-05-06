from office.mission_command.e65_market_dynamics_model import write_all_e65_artifacts


def test_e65_artifacts_generate_end_to_end():
    gate = write_all_e65_artifacts()
    assert gate["gate_passed"] is True
    assert gate["final_status"] == "e65_ceo_market_dynamics_intelligence_model_v1_integrated"
