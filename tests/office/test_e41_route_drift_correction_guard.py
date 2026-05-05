from office.mission_command.e41_route_drift_correction_guard import build_route_drift_correction_guard


def test_e41_route_drift_correction_guard_contract():
    artifact = build_route_drift_correction_guard()
    assert artifact["E40_route_drift_recorded"] is True
    assert artifact["expert_contact_route_progression_stopped"] is True
    assert artifact["guard_passed"] is True
    assert artifact["customer_validation_claimed"] is False
    assert artifact["expert_feedback_claimed"] is False
    assert artifact["paid_signal_claimed"] is False
    assert artifact["message_send_occurred"] is False

