from office.mission_command.e17_response_classifier import classify_e17_response


def test_response_classifier_maps_positive_interest_to_commercial_route():
    result = classify_e17_response({"action_id": "a1", "feedback_type": "positive_interest", "positive_interest_present": True})
    assert result.paid_signal_strength >= 4
    assert result.buyer_pain_confirmed is True
    assert result.route_recommendation == "E18_commercial_acceleration_candidate"
    assert result.suppression_required is False


def test_response_classifier_maps_pricing_question_to_budget_signal():
    result = classify_e17_response({"action_id": "a1", "feedback_type": "pricing_question", "price_question_present": True})
    assert result.budget_signal == 4
    assert result.route_recommendation == "E17_manual_follow_up_allowed_after_owner_review"


def test_response_classifier_suppresses_do_not_contact():
    result = classify_e17_response({"action_id": "a1", "feedback_type": "unsubscribe_or_do_not_contact", "do_not_contact_requested": True})
    assert result.suppression_required is True
    assert result.next_action_allowed == "suppress_only"


def test_response_classifier_does_not_claim_signal_for_empty_state():
    result = classify_e17_response({"action_id": "a1", "feedback_type": "no_response_yet"})
    assert result.paid_signal_strength == 0
    assert result.route_recommendation == "E17_manual_send_ready"
    assert "no_response_yet_no_customer_signal_claimed" in result.reason_codes
