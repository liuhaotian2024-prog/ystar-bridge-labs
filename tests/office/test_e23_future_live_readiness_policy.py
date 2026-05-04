import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_future_live_readiness_policy_has_required_gates():
    data=load("operations/external_validation/e23_future_live_readiness_policy.json")
    required=data["future_live_readiness_milestone_must_include"]
    assert "evidence sufficiency gate" in required
    assert "suppression registry check" in required
    assert "provider live capability check" in required
    assert "explicit live/no-live decision" in required
    assert data["owner_manual_send_is_default"] is False
