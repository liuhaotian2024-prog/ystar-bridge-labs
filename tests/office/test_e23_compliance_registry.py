import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_compliance_registry_allows_agent_with_limits_not_owner_default():
    data=load("operations/external_validation/e23_compliance_registry.json")
    assert data["compliance_blocked_count"] == 0
    assert data["owner_approval_required_by_risk_count"] == 0
    assert data["owner_manual_send_is_default"] is False
    assert all(row["classification"] == "policy_allows_agent_with_limits" for row in data["rows"])
