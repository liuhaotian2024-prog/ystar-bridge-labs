from office.mission_command.e34_ceo_decision_failure_diagnosis import build_ceo_decision_failure_diagnosis


def test_decision_failure_diagnosis_uses_history_and_finds_biases():
    artifact = build_ceo_decision_failure_diagnosis()
    modes = {item["failure_mode"] for item in artifact["failure_modes"]}
    assert "asset_to_product_bias" in modes
    assert "insufficient_non_obvious_opportunity_generation" in modes
    assert "architecture_core_vs_market_wedge_blur" in modes
    assert artifact["customer_validation_claimed"] is False
    assert artifact["paid_signal_claimed"] is False
