from office.mission_command.action_semantics import classify_structured_action


def test_approval_packet_creation_is_internal():
    action = classify_structured_action({"action_title": "Create approval packet for any external action, but do not execute it."})
    assert action.decision == "ALLOW_INTERNAL"
    assert action.external_side_effect is False


def test_word_external_alone_does_not_make_external_side_effect():
    action = classify_structured_action({"action_title": "keep all external actions approval-gated", "action_source": "team_task"})
    assert action.decision == "ALLOW_INTERNAL"
    assert action.external_side_effect is False


def test_residual_candidate_is_review_gated():
    action = classify_structured_action({"action_title": "Residual review candidate: opp_external_pain_agent_bottleneck", "action_source": "residual_candidate"})
    assert action.decision == "REVIEW_GATED"


def test_obligation_draft_is_dry_run_review_gated():
    action = classify_structured_action({"action_title": "Obligation dry-run draft", "action_source": "obligation_draft"})
    assert action.obligation_dry_run is True
    assert action.decision == "REVIEW_GATED"


def test_payment_is_blocked():
    action = classify_structured_action({"action_title": "create payment path"})
    assert action.payment is True
    assert action.decision == "BLOCKED"


def test_core_writeback_is_review_gated():
    action = classify_structured_action({"action_title": "write to core DB/brain/memory/CIEU"})
    assert action.core_writeback is True
    assert action.decision == "REVIEW_GATED"


def test_no_external_sending_customer_contact_email_publication_account_or_form():
    actions = [
        classify_structured_action({"action_title": "send email/message"}),
        classify_structured_action({"action_title": "customer contact"}),
        classify_structured_action({"action_title": "publish public content"}),
        classify_structured_action({"action_title": "create account"}),
        classify_structured_action({"action_title": "submit form"}),
    ]
    assert all(action.decision == "NEEDS_OWNER_APPROVAL" for action in actions)
