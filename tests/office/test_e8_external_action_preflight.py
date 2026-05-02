from office.mission_command.e8_autonomy_budget import render_e8_autonomy_budget_template
from office.mission_command.e8_external_action_preflight import E8ExternalValidationAction, preflight_e8_external_action
from office.mission_command.e8_risk_controlled_action_model import ActionType, RiskTier
from office.mission_command.e8_target_registry import E8ValidationTarget
from office.mission_command.e8_validation_approval import E8ExternalValidationManifest


def _draft():
    return {"draft_id": "draft1", "content_hash": "abc", "ai_disclosure_present": True, "opt_out_present": True}


def _target():
    return E8ValidationTarget("target1", "known_contact", "Peer", "owner_selected_email", "x@example.com", "known", "relevant", True, 1, False, "")


def _manifest(action_type=ActionType.SEND_VALIDATION_MESSAGE):
    return E8ExternalValidationManifest(
        manifest_id="m1",
        approved_by="Haotian",
        approved_at="2026-05-01T00:00:00Z",
        top_offer="48h AI Ops Operating Room Blueprint",
        validation_mode="contact_validation",
        autonomy_budget=render_e8_autonomy_budget_template(),
        approved_draft_ids=["draft1"],
        approved_target_seed_ids=["target1"],
        approved_channels=["owner_selected_email"],
        allowed_action_types=[action_type],
        forbidden_action_types=[],
    )


def _action(action_type=ActionType.SEND_VALIDATION_MESSAGE, tier=RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION, draft_hash="abc"):
    return E8ExternalValidationAction(
        "a1",
        action_type,
        tier,
        "target1",
        "owner_selected_email",
        "draft1",
        draft_hash,
        "m1",
        True,
        "I’m Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs.",
        ["opt-out"],
        "owner_operated_handoff",
    )


def test_preflight_allows_tier2_only_with_manifest_target_draft_disclosure_budget():
    result = preflight_e8_external_action(_action(), _manifest(), [_target()], [_draft()])
    assert result.allowed is True


def test_preflight_blocks_publication_without_tier3_approval():
    result = preflight_e8_external_action(_action(ActionType.PUBLISH_POST, RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING), _manifest(), [_target()], [_draft()])
    assert result.blocked is True


def test_preflight_blocks_payment_form_account_core_writeback():
    for action_type in [ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.SUBMIT_FORM, ActionType.CORE_WRITEBACK]:
        result = preflight_e8_external_action(_action(action_type, RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK), _manifest(action_type), [_target()], [_draft()])
        assert result.blocked is True


def test_preflight_blocks_draft_hash_mismatch():
    result = preflight_e8_external_action(_action(draft_hash="wrong"), _manifest(), [_target()], [_draft()])
    assert "draft_invalid_or_hash_mismatch" in result.blocked_reason
