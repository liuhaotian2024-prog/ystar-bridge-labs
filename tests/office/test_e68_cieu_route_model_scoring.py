import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_cieu_route_scoring_uses_e65_e67_context_and_profiles():
    data = json.loads((ROOT / "operations/external_validation/e68_cieu_route_model_scoring.json").read_text())
    assert data["CIEU_route_score"]["route_id"] == "CIEU_high_risk_AI_agent_audit_log"
    assert data["profile_rankings"]["high_risk_vertical_profile"]["top_route"] == "CIEU_high_risk_AI_agent_audit_log"
    assert "decision_stability" in data["E65_E67_API_invocations"]
    assert data["compliance_claimed"] is False

