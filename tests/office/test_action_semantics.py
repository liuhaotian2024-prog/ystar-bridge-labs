from office.mission_command.action_semantics import (
    classify_structured_action,
    decision_from_structured_action,
)


def _classify(title: str, source: str = "test"):
    return classify_structured_action(
        {
            "action_id": "action_test",
            "action_title": title,
            "action_source": source,
        }
    )


def test_approval_packet_creation_is_internal():
    action = _classify("Create approval packet for any external action, but do not execute it.")
    assert action.approval_packet_only is True
    assert action.external_side_effect is False
    assert decision_from_structured_action(action) == "ALLOW_INTERNAL"


def test_external_word_alone_does_not_trigger_external_action():
    action = _classify("Aiden Liu: keep all external actions approval-gated.", "team_task")
    assert action.external_side_effect is False
    assert decision_from_structured_action(action) == "ALLOW_INTERNAL"


def test_customer_contact_requires_approval():
    action = _classify("customer contact / select exact external recipient")
    assert action.customer_contact is True
    assert decision_from_structured_action(action) == "NEEDS_OWNER_APPROVAL"


def test_email_requires_approval():
    action = _classify("send email/message")
    assert action.email_or_message is True
    assert decision_from_structured_action(action) == "NEEDS_OWNER_APPROVAL"


def test_payment_blocked():
    action = _classify("create payment path")
    assert action.payment is True
    assert decision_from_structured_action(action) == "BLOCKED"


def test_core_writeback_review_gated():
    action = _classify("write to core DB/brain/memory/CIEU")
    assert action.core_writeback is True
    assert decision_from_structured_action(action) == "REVIEW_GATED"


def test_residual_candidate_review_gated():
    action = _classify("Residual review candidate: opp_external_pain_agent_bottleneck", "residual_candidate")
    assert action.residual_candidate is True
    assert action.external_side_effect is False
    assert decision_from_structured_action(action) == "REVIEW_GATED"


def test_obligation_dry_run_review_gated():
    action = _classify("Obligation dry-run draft: Mission owner decision brief", "obligation_draft")
    assert action.obligation_dry_run is True
    assert decision_from_structured_action(action) == "REVIEW_GATED"


def test_live_read_only_research_requires_budget_and_owner_approval():
    action = _classify(
        "Collect public pain-language and pricing-reference evidence under explicit Tier 1 budget; no login, no contact, no submit.",
        "experiment_tier1_research",
    )
    assert action.research_read_only is True
    assert action.external_side_effect is False
    assert action.requires_owner_approval is True
    assert decision_from_structured_action(action) == "NEEDS_OWNER_APPROVAL"


def test_without_publication_is_internal_preparation():
    action = _classify("Turn the first-revenue offer into clear founder/operator language without publication.", "team_task")
    assert action.publication is False
    assert action.external_side_effect is False
    assert decision_from_structured_action(action) == "ALLOW_INTERNAL"


def test_no_external_side_effects():
    action = _classify("Prepare exact manual-send validation draft; owner must approve before any send.", "experiment_external_validation")
    assert action.artifact_only is True
    assert action.external_side_effect is False
