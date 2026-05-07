import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_current_state_synthesis_names_autonomy_gap_and_owner_gate():
    data = json.loads((ROOT / "operations/external_validation/e69_ceo_current_strategic_state_synthesis.json").read_text())
    assert data["current_primary_first_cash_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["CIEU_high_defensibility_vertical"] == "CIEU_high_risk_AI_agent_audit_log"
    assert "not fully autonomous in external business execution" in data["autonomy_statement"]
    assert "outreach" in data["CEO_cannot_do_without_owner_approval"]
    assert data["external_action_allowed"] is False

