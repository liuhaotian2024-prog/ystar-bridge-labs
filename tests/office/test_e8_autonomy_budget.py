from office.mission_command.e8_autonomy_budget import E8AutonomyBudget, render_e8_autonomy_budget_template, validate_e8_autonomy_budget
from office.mission_command.e8_risk_controlled_action_model import RiskTier


def test_autonomy_budget_rejects_missing_count():
    budget = E8AutonomyBudget(allowed_risk_tiers=[RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION], stop_conditions=["stop"], max_targets=1)
    assert "missing_external_action_count" in validate_e8_autonomy_budget(budget)


def test_autonomy_budget_rejects_missing_stop_conditions():
    budget = E8AutonomyBudget(max_external_messages=1, max_targets=1, allowed_risk_tiers=[RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION])
    assert "missing_stop_conditions" in validate_e8_autonomy_budget(budget)


def test_autonomy_budget_blocks_unapproved_risk_tier():
    budget = render_e8_autonomy_budget_template()
    assert "risk_tier_not_in_budget" in validate_e8_autonomy_budget(budget, requested_tier=RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING)
