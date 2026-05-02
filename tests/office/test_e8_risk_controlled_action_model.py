from office.mission_command.e8_risk_controlled_action_model import ActionType, RiskTier, action_type_is_allowed_in_e8, classify_external_action, required_controls_for_tier


def test_e8_inspection_report_exists():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    assert (root / "reports" / "integration" / "e8_implementation_inspection.md").exists()


def test_risk_model_classifies_tier0_internal():
    assert classify_external_action(ActionType.INTERNAL_PREPARE) == RiskTier.TIER_0_INTERNAL


def test_risk_model_classifies_tier1_public_read():
    assert classify_external_action(ActionType.PUBLIC_READ) == RiskTier.TIER_1_PUBLIC_READ_ONLY


def test_risk_model_classifies_tier2_validation_message():
    assert classify_external_action(ActionType.SEND_VALIDATION_MESSAGE) == RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION


def test_risk_model_classifies_tier3_publication():
    assert classify_external_action(ActionType.PUBLISH_POST) == RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING


def test_risk_model_blocks_tier4_payment_account_core_writeback():
    for action in [ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.CORE_WRITEBACK]:
        assert classify_external_action(action) == RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK
        assert action_type_is_allowed_in_e8(action) is False


def test_tier2_requires_disclosure_budget_ledgers_and_targets():
    controls = required_controls_for_tier(RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION)
    assert "ai_disclosure_required" in controls
    assert "target_seed_required" in controls
    assert "action_ledger_required" in controls
    assert "feedback_ledger_required" in controls
