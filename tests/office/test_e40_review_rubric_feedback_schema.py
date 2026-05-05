from office.mission_command.e40_review_rubric_feedback_schema import build_expert_review_rubric, build_feedback_capture_schema


def test_feedback_schema_defaults_to_expert_opinion_only():
    rubric = build_expert_review_rubric()
    schema = build_feedback_capture_schema()
    assert len(rubric["dimensions"]) >= 14
    assert rubric["default_feedback_classification"] == "expert opinion only"
    assert rubric["customer_validation_by_default"] is False
    assert rubric["paid_signal_by_default"] is False
    assert schema["default_for_E40_E41"] == "expert opinion only"
    assert schema["not_paid_signal_unless_money_changes_hands"] is True
