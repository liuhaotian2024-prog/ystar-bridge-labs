from office.mission_command.e8_validation_result_evaluator import evaluate_e8_validation_result


def test_result_evaluator_does_not_recommend_paid_pilot_without_positive_signal():
    result = evaluate_e8_validation_result(
        manifest_present=False,
        targets_present=False,
        provider_available=False,
        preflight_allowed=False,
        execution_gate={"executed": False, "owner_operated_handoff_ready": False},
        feedback_signal="blocked_no_feedback",
    )
    assert result["recommended_next_decision"] != "approve_E9_paid_pilot_prep"


def test_result_evaluator_recommends_provider_or_handoff_when_provider_missing():
    result = evaluate_e8_validation_result(
        manifest_present=True,
        targets_present=True,
        provider_available=False,
        preflight_allowed=True,
        execution_gate={"executed": False, "owner_operated_handoff_ready": False},
        feedback_signal="blocked_no_feedback",
    )
    assert result["recommended_next_decision"] == "provide_safe_execution_provider"


def test_result_evaluator_recommends_paid_prep_only_after_positive_signal():
    result = evaluate_e8_validation_result(
        manifest_present=True,
        targets_present=True,
        provider_available=True,
        preflight_allowed=True,
        execution_gate={"executed": True, "owner_operated_handoff_ready": False},
        feedback_signal="strong_positive",
    )
    assert result["recommended_next_decision"] == "approve_E9_paid_pilot_prep"
