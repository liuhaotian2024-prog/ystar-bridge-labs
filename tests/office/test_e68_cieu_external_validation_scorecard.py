import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_cieu_external_validation_scorecard_keeps_ev5_ev8_unachieved():
    data = json.loads((ROOT / "operations/external_validation/e68_cieu_external_validation_scorecard.json").read_text())
    assert data["route_id"] == "CIEU_high_risk_AI_agent_audit_log"
    assert data["highest_achieved_EV_level"] in {
        "EV0_internal_assumption",
        "EV2_competitor_or_adjacent_product_presence",
        "EV4_public_demand_or_behavior_proxy",
    }
    assert data["EV5_EV8_achieved"] is False
    assert data["legal_compliance_claimed"] is False
    assert data["medical_readiness_claimed"] is False

