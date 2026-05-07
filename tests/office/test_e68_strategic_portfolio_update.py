import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_portfolio_keeps_current_first_cash_and_adds_cieu_module():
    data = json.loads((ROOT / "operations/external_validation/e68_strategic_portfolio_update.json").read_text())
    portfolio = data["best_portfolio_after_E68"]
    assert data["should_CIEU_replace_current_primary_route"] is False
    assert data["should_CIEU_become_vertical_module_inside_current_selected_route"] is True
    assert portfolio["primary_first_cash_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert portfolio["high_defensibility_vertical"] == "CIEU_high_risk_AI_agent_audit_log"

