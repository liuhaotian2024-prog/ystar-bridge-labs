from office.mission_command.e35_superhuman_ceo_cognition_challenge import build_superhuman_ceo_cognition_challenge


def test_superhuman_challenge_adds_non_pm_questions():
    artifact = build_superhuman_ceo_cognition_challenge()
    questions = artifact["challenge_questions"]
    assert len(questions) >= 12
    assert "What would a normal founder miss?" in questions
    assert "What could become a new institution rather than a product?" in questions
    assert artifact["questions_are_prompts_not_answers"] is True
