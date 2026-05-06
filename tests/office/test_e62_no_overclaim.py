from office.mission_command.e62_completion_gate import run_e62_completion_gate
from office.mission_command.e62_first_cash_path_selection import run_first_cash_path_selection


def test_e62_does_not_claim_validation_revenue_or_external_execution():
    selection = run_first_cash_path_selection()
    gate = run_e62_completion_gate()
    for key in ["customer_validation_claimed", "paid_signal_claimed", "expert_feedback_claimed"]:
        assert selection[key] is False
        assert gate[key] is False
    assert gate["production_readiness_claimed"] is False
    assert gate["real_mcp_transport_claimed"] is False
    assert gate["autonomous_revenue_achieved"] is False
    assert gate["external_action_allowed"] is False
