from office.mission_command.e8_ai_transparency_policy import validate_ai_disclosure, validate_external_message_transparency


def test_ai_transparency_requires_ai_or_ai_assisted_disclosure():
    assert "missing_ai_or_ai_assisted_disclosure" in validate_ai_disclosure("Hello, I want feedback.")
    assert not validate_ai_disclosure("I’m Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs.")


def test_ai_transparency_rejects_fake_human_identity():
    errors = validate_ai_disclosure("I am a human founder, not an AI, asking for feedback.")
    assert "forbidden_or_deceptive_identity_pattern" in errors


def test_ai_transparency_rejects_false_customer_validation_claim():
    errors = validate_external_message_transparency("This is AI-assisted. Customer validation already happened. Please reply.")
    assert "misleading_problem_or_validation_claim" in errors


def test_ai_transparency_requires_opt_out_or_ignore_language_for_outreach():
    errors = validate_external_message_transparency("This is an AI-assisted validation request from Y*Bridge Labs.")
    assert "missing_opt_out_or_ignore_language" in errors
    assert not validate_external_message_transparency(
        "This is an AI-assisted validation request from Y*Bridge Labs. Please ignore this if it is not useful; no automated follow-up will happen."
    )
