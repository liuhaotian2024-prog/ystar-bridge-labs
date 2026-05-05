from office.mission_command.e40_expert_review_question_bank import build_expert_review_question_bank


def test_question_bank_is_nonleading_and_does_not_prove_validation():
    bank = build_expert_review_question_bank()
    assert bank["question_count"] >= 80
    assert bank["assumes_Y_star_superiority"] is False
    for q in bank["questions"][:10]:
        assert q["leading_question"] is False
        assert "customer validation" in q["what_answer_would_not_prove"]
    assert bank["customer_validation_claimed"] is False
    assert bank["paid_signal_claimed"] is False
