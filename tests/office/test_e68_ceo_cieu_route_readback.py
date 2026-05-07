from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e68_ceo_cieu_route_readback import (
    explain_cieu_overclaim_limits,
    get_cieu_external_validation,
    get_cieu_portfolio_role,
    get_cieu_product_wedge,
    get_cieu_route_score,
)


def test_e68_ceo_readback_exposes_cieu_route_state():
    assert get_cieu_route_score()["route_id"] == "CIEU_high_risk_AI_agent_audit_log"
    assert get_cieu_external_validation()["EV5_EV8_achieved"] is False
    assert get_cieu_portfolio_role()["high_defensibility_vertical"] == "CIEU_high_risk_AI_agent_audit_log"
    assert get_cieu_product_wedge()["offer_name"] == "Governed Business Operations Blueprint + CIEU Audit Module"
    assert "CIEU ensures EU AI Act compliance" in explain_cieu_overclaim_limits()["prohibited_claims"]
    context = load_ceo_brain_context({"task_title": "e68 cieu readback smoke", "task_description": "read E68 CIEU state"})
    assert context["current_cieu_external_action_allowed"] is False
    assert context["current_cieu_product_wedge"] == "Governed Business Operations Blueprint + CIEU Audit Module"
