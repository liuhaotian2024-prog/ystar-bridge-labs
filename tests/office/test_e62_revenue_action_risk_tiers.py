from office.mission_command.e62_revenue_action_risk_tiers import run_revenue_action_risk_tiers


def test_e62_revenue_action_tiers_keep_external_business_owner_gated():
    data = run_revenue_action_risk_tiers()
    tiers = {item["tier"]: item for item in data["tiers"]}
    assert tiers["T0_internal_only"]["behavior_authorization"] == "ALLOW"
    assert tiers["T1_public_read_only"]["external_action"] is False
    assert tiers["T3_owner_approved_external_contact"]["owner_approval_required"] is True
    assert tiers["T4_owner_approved_commercial_transaction"]["behavior_authorization"].startswith("DENY")
    assert data["pending_owner_decision_is_not_approval"] is True
